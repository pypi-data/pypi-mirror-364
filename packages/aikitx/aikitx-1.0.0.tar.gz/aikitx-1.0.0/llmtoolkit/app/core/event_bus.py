"""
Event Bus

This module implements an advanced event bus (publisher-subscriber pattern)
for decoupled communication between application components.

Features:
- Synchronous and asynchronous event publishing
- Support for event priorities
- Wildcard event subscriptions
- Event filtering
- Proper async coroutine support
- Enhanced model integration events
- Universal model loading event support
"""

import logging
import asyncio
import threading
import queue
import uuid
import re
import inspect
from enum import IntEnum
from typing import Dict, List, Callable, Any, Optional, Union, Pattern, Set, Tuple

class EventPriority(IntEnum):
    """Priority levels for event subscribers."""
    LOWEST = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    HIGHEST = 100

class EventFilter:
    """Filter for event subscriptions."""
    
    def __init__(self, filter_func: Callable[[str, tuple, dict], bool]):
        """
        Initialize an event filter.
        
        Args:
            filter_func: Function that takes event_name, args, kwargs and returns
                         True if the event should be processed, False otherwise
        """
        self.filter_func = filter_func
    
    def matches(self, event_name: str, args: tuple, kwargs: dict) -> bool:
        """
        Check if an event matches this filter.
        
        Args:
            event_name: Name of the event
            args: Event arguments
            kwargs: Event keyword arguments
            
        Returns:
            True if the event matches the filter, False otherwise
        """
        try:
            return self.filter_func(event_name, args, kwargs)
        except Exception:
            # If filter raises an exception, assume it doesn't match
            return False

class EventSubscription:
    """Represents a subscription to an event."""
    
    def __init__(self, 
                 callback: Callable, 
                 priority: EventPriority = EventPriority.NORMAL,
                 filter_: Optional[EventFilter] = None,
                 is_async: bool = False):
        """
        Initialize an event subscription.
        
        Args:
            callback: Function to call when the event is published
            priority: Priority of this subscription
            filter_: Optional filter for this subscription
            is_async: Whether the callback is an async coroutine
        """
        self.callback = callback
        self.priority = priority
        self.filter = filter_
        self.is_async = is_async or asyncio.iscoroutinefunction(callback)

class EventBus:
    """
    Advanced event bus implementation using the publisher-subscriber pattern.
    
    This class allows components to communicate without direct dependencies
    by publishing events that other components can subscribe to.
    
    Features:
    - Synchronous and asynchronous event publishing
    - Support for event priorities
    - Wildcard event subscriptions
    - Event filtering
    - Proper async coroutine support
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self.logger = logging.getLogger("gguf_loader.event_bus")
        # Map of event_name -> {subscriber_id -> EventSubscription}
        self.subscribers: Dict[str, Dict[str, EventSubscription]] = {}
        # Map of regex pattern -> {subscriber_id -> (compiled_pattern, EventSubscription)}
        self.wildcard_subscribers: Dict[str, Dict[str, Tuple[Pattern, EventSubscription]]] = {}
        self.async_loop = None
        self.async_thread = None
        self.async_queue = queue.Queue()
        self.running = False
        
        # Start the async event processing thread
        self._start_async_thread()
    
    def _start_async_thread(self):
        """Start the asynchronous event processing thread."""
        self.running = True
        self.async_thread = threading.Thread(target=self._async_thread_worker, daemon=True)
        self.async_thread.start()
    
    def _async_thread_worker(self):
        """Worker function for the async event thread."""
        # Create a new event loop for this thread
        self.async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_loop)
        
        # Process events until stopped
        while self.running:
            try:
                # Get the next event from the queue with a timeout
                event_data = self.async_queue.get(timeout=0.1)
                if event_data:
                    event_name, args, kwargs = event_data
                    self._process_event(event_name, args, kwargs)
                self.async_queue.task_done()
            except queue.Empty:
                # No events in the queue, continue waiting
                pass
            except Exception as e:
                self.logger.exception(f"Error processing async event: {e}")
    
    def _process_event(self, event_name: str, args: tuple, kwargs: dict):
        """Process an event by calling all subscribers."""
        # Collect all matching subscriptions
        subscriptions = []
        
        # Add direct subscribers
        if event_name in self.subscribers:
            for subscriber_id, subscription in list(self.subscribers[event_name].items()):
                # Check if the subscription has a filter
                if subscription.filter and not subscription.filter.matches(event_name, args, kwargs):
                    continue
                subscriptions.append((subscriber_id, subscription))
        
        # Add wildcard subscribers
        for pattern_str, subscribers in list(self.wildcard_subscribers.items()):
            for subscriber_id, (pattern, subscription) in list(subscribers.items()):
                if pattern.match(event_name):
                    # Check if the subscription has a filter
                    if subscription.filter and not subscription.filter.matches(event_name, args, kwargs):
                        continue
                    subscriptions.append((subscriber_id, subscription))
        
        # Sort subscriptions by priority (highest first)
        subscriptions.sort(key=lambda x: x[1].priority, reverse=True)
        
        # Call each subscriber
        for subscriber_id, subscription in subscriptions:
            try:
                if subscription.is_async:
                    # For async callbacks, schedule them in the async loop
                    if self.async_loop:
                        asyncio.run_coroutine_threadsafe(
                            subscription.callback(*args, **kwargs), 
                            self.async_loop
                        )
                else:
                    # For synchronous callbacks, call directly
                    subscription.callback(*args, **kwargs)
            except Exception as e:
                self.logger.exception(f"Error in event subscriber {subscriber_id} for event {event_name}: {e}")
    
    def subscribe(self, 
                  event_name: str, 
                  callback: Callable, 
                  subscriber_id: Optional[str] = None,
                  priority: EventPriority = EventPriority.NORMAL,
                  filter_: Optional[EventFilter] = None,
                  is_async: bool = False) -> str:
        """
        Subscribe to an event.
        
        Args:
            event_name: The name of the event to subscribe to
            callback: The function to call when the event is published
            subscriber_id: Optional unique identifier for the subscriber
            priority: Priority of this subscription
            filter_: Optional filter for this subscription
            is_async: Whether the callback is an async coroutine
            
        Returns:
            The subscriber ID (generated if not provided)
        """
        if not subscriber_id:
            subscriber_id = str(uuid.uuid4())
        
        # Create subscription object
        subscription = EventSubscription(
            callback=callback,
            priority=priority,
            filter_=filter_,
            is_async=is_async
        )
        
        # Check if this is a wildcard subscription
        if '*' in event_name or '?' in event_name or '+' in event_name:
            # Convert glob pattern to regex pattern
            pattern_str = event_name.replace('.', r'\.')
            pattern_str = pattern_str.replace('*', '.*')
            pattern_str = pattern_str.replace('?', '.')
            pattern_str = pattern_str.replace('+', r'\+')
            pattern_str = f"^{pattern_str}$"
            
            # Compile the regex pattern
            pattern = re.compile(pattern_str)
            
            # Add to wildcard subscribers
            if event_name not in self.wildcard_subscribers:
                self.wildcard_subscribers[event_name] = {}
            
            self.wildcard_subscribers[event_name][subscriber_id] = (pattern, subscription)
            self.logger.debug(f"Subscribed {subscriber_id} to wildcard event {event_name}")
        else:
            # Regular subscription
            if event_name not in self.subscribers:
                self.subscribers[event_name] = {}
                
            self.subscribers[event_name][subscriber_id] = subscription
            self.logger.debug(f"Subscribed {subscriber_id} to event {event_name}")
        
        return subscriber_id
    
    def unsubscribe(self, event_name: str, subscriber_id: str) -> bool:
        """
        Unsubscribe from an event.
        
        Args:
            event_name: The name of the event to unsubscribe from
            subscriber_id: The subscriber ID returned from subscribe()
            
        Returns:
            True if successfully unsubscribed, False otherwise
        """
        # Check regular subscriptions
        if event_name in self.subscribers and subscriber_id in self.subscribers[event_name]:
            del self.subscribers[event_name][subscriber_id]
            
            # Clean up empty event entries
            if not self.subscribers[event_name]:
                del self.subscribers[event_name]
                
            self.logger.debug(f"Unsubscribed {subscriber_id} from event {event_name}")
            return True
        
        # Check wildcard subscriptions
        if event_name in self.wildcard_subscribers and subscriber_id in self.wildcard_subscribers[event_name]:
            del self.wildcard_subscribers[event_name][subscriber_id]
            
            # Clean up empty event entries
            if not self.wildcard_subscribers[event_name]:
                del self.wildcard_subscribers[event_name]
                
            self.logger.debug(f"Unsubscribed {subscriber_id} from wildcard event {event_name}")
            return True
            
        return False
    
    def publish(self, event_name: str, *args, **kwargs) -> None:
        """
        Publish an event synchronously.
        
        Args:
            event_name: The name of the event to publish
            *args, **kwargs: Arguments to pass to the subscribers
        """
        self.logger.debug(f"Publishing event {event_name}")
        self._process_event(event_name, args, kwargs)
    
    def publish_async(self, event_name: str, *args, **kwargs) -> None:
        """
        Publish an event asynchronously.
        
        Args:
            event_name: The name of the event to publish
            *args, **kwargs: Arguments to pass to the subscribers
        """
        self.logger.debug(f"Publishing async event {event_name}")
        self.async_queue.put((event_name, args, kwargs))
    
    def wait_for_event(self, event_name: str, timeout: float = None) -> threading.Event:
        """
        Create an event that will be set when a specific event is published.
        
        Args:
            event_name: The name of the event to wait for
            timeout: Optional timeout in seconds
            
        Returns:
            A threading.Event object that will be set when the event is published
        """
        event = threading.Event()
        
        def event_callback(*args, **kwargs):
            event.set()
        
        subscriber_id = self.subscribe(event_name, event_callback)
        
        # If timeout is specified, start a timer to unsubscribe
        if timeout is not None:
            def timeout_callback():
                self.unsubscribe(event_name, subscriber_id)
            
            timer = threading.Timer(timeout, timeout_callback)
            timer.daemon = True
            timer.start()
        
        return event
    
    def get_subscriber_count(self, event_name: str = None) -> int:
        """
        Get the number of subscribers for an event.
        
        Args:
            event_name: Optional event name. If not provided, returns total subscribers.
            
        Returns:
            Number of subscribers
        """
        if event_name:
            # Count direct subscribers
            direct_count = len(self.subscribers.get(event_name, {}))
            
            # Count wildcard subscribers that match this event
            wildcard_count = 0
            for pattern_str, subscribers in self.wildcard_subscribers.items():
                for subscriber_id, (pattern, _) in subscribers.items():
                    if pattern.match(event_name):
                        wildcard_count += 1
            
            return direct_count + wildcard_count
        else:
            # Count all subscribers
            direct_count = sum(len(subscribers) for subscribers in self.subscribers.values())
            wildcard_count = sum(len(subscribers) for subscribers in self.wildcard_subscribers.values())
            return direct_count + wildcard_count
    
    def subscribe_to_universal_events(self, subscriber_id: str, callback: Callable, 
                                    event_patterns: List[str] = None) -> List[str]:
        """
        Subscribe to multiple universal model integration events with a single callback.
        
        Args:
            subscriber_id: Unique identifier for the subscriber
            callback: Function to call for all matching events
            event_patterns: List of event patterns to subscribe to (default: all universal events)
            
        Returns:
            List of subscription IDs
        """
        if event_patterns is None:
            # Default universal event patterns
            event_patterns = [
                "universal.model.*",
                "resource.monitor.*",
                "performance.*",
                "tab.*"
            ]
        
        subscription_ids = []
        for pattern in event_patterns:
            sub_id = self.subscribe(pattern, callback, f"{subscriber_id}_{pattern}")
            subscription_ids.append(sub_id)
        
        return subscription_ids
    
    def unsubscribe_from_universal_events(self, subscriber_id: str, event_patterns: List[str] = None):
        """
        Unsubscribe from multiple universal model integration events.
        
        Args:
            subscriber_id: Unique identifier for the subscriber
            event_patterns: List of event patterns to unsubscribe from
        """
        if event_patterns is None:
            event_patterns = [
                "universal.model.*",
                "resource.monitor.*", 
                "performance.*",
                "tab.*"
            ]
        
        for pattern in event_patterns:
            self.unsubscribe(pattern, f"{subscriber_id}_{pattern}")
    
    def publish_universal_event(self, event_type: str, data: Dict[str, Any], 
                              priority: EventPriority = EventPriority.NORMAL):
        """
        Publish a universal model integration event with enhanced data validation.
        
        Args:
            event_type: Type of event (should be from UniversalEventType)
            data: Event data dictionary
            priority: Event priority
        """
        # Add timestamp if not present
        if 'timestamp' not in data:
            import time
            data['timestamp'] = time.time()
        
        # Add event metadata
        data['event_type'] = event_type
        data['event_priority'] = priority.value
        
        # Publish the event
        self.publish(event_type, data)
        
        # Also publish to wildcard listeners
        event_parts = event_type.split('.')
        for i in range(len(event_parts)):
            wildcard_event = '.'.join(event_parts[:i+1]) + '.*'
            self.publish(wildcard_event, data)
    
    def get_universal_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about universal event subscriptions and activity."""
        universal_patterns = [
            "universal.model.*",
            "resource.monitor.*",
            "performance.*", 
            "tab.*"
        ]
        
        stats = {
            'total_subscribers': self.get_subscriber_count(),
            'universal_subscribers': {},
            'event_patterns': universal_patterns
        }
        
        for pattern in universal_patterns:
            stats['universal_subscribers'][pattern] = self.get_subscriber_count(pattern)
        
        return stats

    def shutdown(self):
        """Shut down the event bus and stop the async thread."""
        self.logger.info("Shutting down event bus")
        self.running = False
        if self.async_thread and self.async_thread.is_alive():
            self.async_thread.join(timeout=1.0)
        self.subscribers.clear()