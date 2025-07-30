"""
Background Processor

This module contains the BackgroundProcessor class, which is responsible for
managing background tasks, providing progress reporting, and implementing
task prioritization.
"""

import os
import logging
import threading
import queue
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set, Any, Union, Callable

from PySide6.QtCore import QObject, Signal, Slot, QThread, QTimer, QMutex, QWaitCondition

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class TaskStatus(Enum):
    """Task status values."""
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4

class Task:
    """Represents a background task."""
    
    def __init__(self, 
                 task_id: str,
                 name: str,
                 function: Callable,
                 args: tuple = (),
                 kwargs: dict = None,
                 priority: TaskPriority = TaskPriority.NORMAL):
        """
        Initialize a task.
        
        Args:
            task_id: Unique identifier for the task
            name: Human-readable name for the task
            function: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            priority: Task priority
        """
        self.id = task_id
        self.name = name
        self.function = function
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.progress = 0
        self.created_time = time.time()
        self.start_time = None
        self.end_time = None
        self.cancelled = False
    
    def __lt__(self, other):
        """
        Compare tasks for priority queue ordering.
        
        Higher priority tasks come first. For tasks with the same priority,
        older tasks come first (FIFO within priority levels).
        """
        if self.priority.value != other.priority.value:
            # Higher priority value means higher priority
            return self.priority.value > other.priority.value
        else:
            # Earlier creation time means higher priority
            return self.created_time < other.created_time

class WorkerThread(QThread):
    """Thread for executing background tasks."""
    
    # Signals
    task_started_signal = Signal(str)  # task_id
    task_completed_signal = Signal(str, object)  # task_id, result
    task_failed_signal = Signal(str, str)  # task_id, error
    task_progress_signal = Signal(str, int)  # task_id, progress_percentage
    
    def __init__(self, task_queue, result_queue, parent=None):
        """
        Initialize the worker thread.
        
        Args:
            task_queue: Queue for receiving tasks
            result_queue: Queue for sending results
            parent: Parent object
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.background_processor.worker")
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True
        self.current_task = None
    
    def run(self):
        """Run the thread."""
        self.logger.info("Worker thread started")
        
        while self.running:
            try:
                # Get a task from the queue
                task = self.task_queue.get(timeout=1.0)
                
                # Store the current task
                self.current_task = task
                
                # Mark the task as running
                task.status = TaskStatus.RUNNING
                task.start_time = time.time()
                
                # Emit signal
                self.task_started_signal.emit(task.id)
                
                # Execute the task
                try:
                    # Add progress callback to kwargs if the function accepts it
                    kwargs = task.kwargs.copy()
                    
                    # Check if the function accepts a progress_callback parameter
                    if 'progress_callback' in kwargs:
                        # Create a progress callback that emits a signal
                        def progress_callback(progress):
                            if not task.cancelled:
                                task.progress = progress
                                self.task_progress_signal.emit(task.id, progress)
                        
                        kwargs['progress_callback'] = progress_callback
                    
                    # Execute the function
                    result = task.function(*task.args, **kwargs)
                    
                    # Check if the task was cancelled
                    if task.cancelled:
                        task.status = TaskStatus.CANCELLED
                        self.logger.info(f"Task cancelled: {task.name} ({task.id})")
                    else:
                        # Mark the task as completed
                        task.status = TaskStatus.COMPLETED
                        task.result = result
                        task.end_time = time.time()
                        
                        # Emit signal
                        self.task_completed_signal.emit(task.id, result)
                        
                        # Put the result in the result queue
                        self.result_queue.put((task.id, result, None))
                        
                        self.logger.info(f"Task completed: {task.name} ({task.id})")
                
                except Exception as e:
                    # Mark the task as failed
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.end_time = time.time()
                    
                    # Emit signal
                    self.task_failed_signal.emit(task.id, str(e))
                    
                    # Put the error in the result queue
                    self.result_queue.put((task.id, None, str(e)))
                    
                    self.logger.error(f"Task failed: {task.name} ({task.id}): {e}")
                
                # Clear the current task
                self.current_task = None
                
                # Mark the task as done in the queue
                self.task_queue.task_done()
                
            except queue.Empty:
                # No tasks in the queue, just continue
                pass
            except Exception as e:
                self.logger.error(f"Error in worker thread: {e}")
        
        self.logger.info("Worker thread stopped")
    
    def stop(self):
        """Stop the worker thread."""
        self.running = False
        
        # Cancel the current task if there is one
        if self.current_task:
            self.current_task.cancelled = True

class BackgroundProcessor(QObject):
    """
    Manages background processing tasks.
    
    This class is responsible for:
    - Managing a pool of worker threads
    - Scheduling tasks based on priority
    - Reporting task progress
    - Handling task results and errors
    """
    
    # Signals
    task_started_signal = Signal(str)  # task_id
    task_completed_signal = Signal(str, object)  # task_id, result
    task_failed_signal = Signal(str, str)  # task_id, error
    task_progress_signal = Signal(str, int)  # task_id, progress_percentage
    task_cancelled_signal = Signal(str)  # task_id
    
    def __init__(self, event_bus=None, config_manager=None, parent=None):
        """
        Initialize the background processor.
        
        Args:
            event_bus: Optional event bus for publishing events
            config_manager: Optional configuration manager
            parent: Parent object
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.background_processor")
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        # Thread pool settings
        self.min_threads = 2
        self.max_threads = 4
        self.thread_idle_timeout = 60  # seconds
        
        # Task queues
        self.task_queue = queue.PriorityQueue()
        self.result_queue = queue.Queue()
        
        # Task registry
        self.tasks = {}
        self.active_tasks = set()
        
        # Worker threads
        self.workers = []
        
        # Mutex for thread-safe operations
        self.mutex = QMutex()
        
        # Timer for checking results
        self.result_timer = QTimer(self)
        self.result_timer.timeout.connect(self._check_results)
        self.result_timer.start(100)  # Check every 100ms
        
        # Load settings from configuration
        self._load_settings()
        
        # Initialize worker threads
        self._initialize_workers()
        
        self.logger.info("Background processor initialized")
    
    def _load_settings(self):
        """Load settings from configuration."""
        if self.config_manager:
            self.min_threads = self.config_manager.get_value("min_worker_threads", 2)
            self.max_threads = self.config_manager.get_value("max_worker_threads", 4)
            self.thread_idle_timeout = self.config_manager.get_value("thread_idle_timeout", 60)
    
    def _initialize_workers(self):
        """Initialize worker threads."""
        # Create initial worker threads
        for _ in range(self.min_threads):
            self._create_worker()
    
    def _create_worker(self):
        """Create a new worker thread."""
        worker = WorkerThread(self.task_queue, self.result_queue)
        
        # Connect signals
        worker.task_started_signal.connect(self._on_task_started)
        worker.task_completed_signal.connect(self._on_task_completed)
        worker.task_failed_signal.connect(self._on_task_failed)
        worker.task_progress_signal.connect(self._on_task_progress)
        
        # Start the thread
        worker.start()
        
        # Add to the list of workers
        self.workers.append(worker)
        
        self.logger.info(f"Created worker thread (total: {len(self.workers)})")
    
    def _check_results(self):
        """Check for task results."""
        try:
            # Check if there are any results
            while not self.result_queue.empty():
                # Get the result
                task_id, result, error = self.result_queue.get_nowait()
                
                # Update the task
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    
                    # Remove from active tasks
                    if task_id in self.active_tasks:
                        self.active_tasks.remove(task_id)
                    
                    # Update task status
                    if error:
                        task.status = TaskStatus.FAILED
                        task.error = error
                    else:
                        task.status = TaskStatus.COMPLETED
                        task.result = result
                    
                    # Update end time if not already set
                    if not task.end_time:
                        task.end_time = time.time()
                
                # Mark the result as processed
                self.result_queue.task_done()
        
        except Exception as e:
            self.logger.error(f"Error checking results: {e}")
    
    def _on_task_started(self, task_id):
        """
        Handle task started event from worker thread.
        
        Args:
            task_id: ID of the task
        """
        # Add to active tasks
        self.active_tasks.add(task_id)
        
        # Emit signal
        self.task_started_signal.emit(task_id)
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish("task.started", task_id)
    
    def _on_task_completed(self, task_id, result):
        """
        Handle task completed event from worker thread.
        
        Args:
            task_id: ID of the task
            result: Task result
        """
        # Emit signal
        self.task_completed_signal.emit(task_id, result)
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish("task.completed", task_id, result)
    
    def _on_task_failed(self, task_id, error):
        """
        Handle task failed event from worker thread.
        
        Args:
            task_id: ID of the task
            error: Error message
        """
        # Emit signal
        self.task_failed_signal.emit(task_id, error)
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish("task.failed", task_id, error)
    
    def _on_task_progress(self, task_id, progress):
        """
        Handle task progress event from worker thread.
        
        Args:
            task_id: ID of the task
            progress: Progress percentage (0-100)
        """
        # Update task progress
        if task_id in self.tasks:
            self.tasks[task_id].progress = progress
        
        # Emit signal
        self.task_progress_signal.emit(task_id, progress)
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish("task.progress", task_id, progress)
    
    def submit_task(self, 
                   name: str,
                   function: Callable,
                   args: tuple = (),
                   kwargs: dict = None,
                   priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """
        Submit a task for background processing.
        
        Args:
            name: Human-readable name for the task
            function: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            priority: Task priority
            
        Returns:
            Task ID
        """
        # Generate a unique ID for the task
        task_id = str(uuid.uuid4())
        
        # Create the task
        task = Task(
            task_id=task_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs or {},
            priority=priority
        )
        
        # Add to the registry
        self.tasks[task_id] = task
        
        # Add to the queue
        self.task_queue.put(task)
        
        self.logger.info(f"Submitted task: {name} ({task_id}) with priority {priority.name}")
        
        # Check if we need more worker threads
        if (self.task_queue.qsize() > len(self.workers) and 
            len(self.workers) < self.max_threads):
            self._create_worker()
        
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if the task was cancelled, False otherwise
        """
        # Check if the task exists
        if task_id not in self.tasks:
            self.logger.warning(f"Task not found: {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        # Check if the task can be cancelled
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            self.logger.warning(f"Task already finished: {task_id}")
            return False
        
        # Mark the task as cancelled
        task.cancelled = True
        task.status = TaskStatus.CANCELLED
        
        # Remove from active tasks
        if task_id in self.active_tasks:
            self.active_tasks.remove(task_id)
        
        # Emit signal
        self.task_cancelled_signal.emit(task_id)
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish("task.cancelled", task_id)
        
        self.logger.info(f"Cancelled task: {task.name} ({task_id})")
        
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task
            
        Returns:
            The task, or None if not found
        """
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        Get the status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task status, or None if the task doesn't exist
        """
        task = self.get_task(task_id)
        return task.status if task else None
    
    def get_task_progress(self, task_id: str) -> Optional[int]:
        """
        Get the progress of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task progress (0-100), or None if the task doesn't exist
        """
        task = self.get_task(task_id)
        return task.progress if task else None
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """
        Get the result of a completed task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task result, or None if the task doesn't exist or isn't completed
        """
        task = self.get_task(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result
        return None
    
    def get_task_error(self, task_id: str) -> Optional[str]:
        """
        Get the error message of a failed task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Error message, or None if the task doesn't exist or didn't fail
        """
        task = self.get_task(task_id)
        if task and task.status == TaskStatus.FAILED:
            return task.error
        return None
    
    def get_active_tasks(self) -> List[str]:
        """
        Get a list of active task IDs.
        
        Returns:
            List of task IDs
        """
        return list(self.active_tasks)
    
    def get_pending_tasks(self) -> List[str]:
        """
        Get a list of pending task IDs.
        
        Returns:
            List of task IDs
        """
        return [task_id for task_id, task in self.tasks.items() 
                if task.status == TaskStatus.PENDING]
    
    def get_completed_tasks(self) -> List[str]:
        """
        Get a list of completed task IDs.
        
        Returns:
            List of task IDs
        """
        return [task_id for task_id, task in self.tasks.items() 
                if task.status == TaskStatus.COMPLETED]
    
    def get_failed_tasks(self) -> List[str]:
        """
        Get a list of failed task IDs.
        
        Returns:
            List of task IDs
        """
        return [task_id for task_id, task in self.tasks.items() 
                if task.status == TaskStatus.FAILED]
    
    def get_cancelled_tasks(self) -> List[str]:
        """
        Get a list of cancelled task IDs.
        
        Returns:
            List of task IDs
        """
        return [task_id for task_id, task in self.tasks.items() 
                if task.status == TaskStatus.CANCELLED]
    
    def get_task_count(self) -> Dict[str, int]:
        """
        Get the count of tasks by status.
        
        Returns:
            Dictionary of status to count
        """
        counts = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "total": len(self.tasks)
        }
        
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                counts["pending"] += 1
            elif task.status == TaskStatus.RUNNING:
                counts["running"] += 1
            elif task.status == TaskStatus.COMPLETED:
                counts["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                counts["failed"] += 1
            elif task.status == TaskStatus.CANCELLED:
                counts["cancelled"] += 1
        
        return counts
    
    def clear_completed_tasks(self) -> int:
        """
        Clear completed tasks from the registry.
        
        Returns:
            Number of tasks cleared
        """
        # Get completed task IDs
        completed_tasks = self.get_completed_tasks()
        
        # Remove from registry
        for task_id in completed_tasks:
            del self.tasks[task_id]
        
        return len(completed_tasks)
    
    def clear_failed_tasks(self) -> int:
        """
        Clear failed tasks from the registry.
        
        Returns:
            Number of tasks cleared
        """
        # Get failed task IDs
        failed_tasks = self.get_failed_tasks()
        
        # Remove from registry
        for task_id in failed_tasks:
            del self.tasks[task_id]
        
        return len(failed_tasks)
    
    def clear_cancelled_tasks(self) -> int:
        """
        Clear cancelled tasks from the registry.
        
        Returns:
            Number of tasks cleared
        """
        # Get cancelled task IDs
        cancelled_tasks = self.get_cancelled_tasks()
        
        # Remove from registry
        for task_id in cancelled_tasks:
            del self.tasks[task_id]
        
        return len(cancelled_tasks)
    
    def clear_all_tasks(self) -> int:
        """
        Clear all tasks from the registry.
        
        Returns:
            Number of tasks cleared
        """
        # Cancel all active tasks
        for task_id in self.get_active_tasks():
            self.cancel_task(task_id)
        
        # Get the count
        count = len(self.tasks)
        
        # Clear the registry
        self.tasks.clear()
        self.active_tasks.clear()
        
        return count
    
    def shutdown(self):
        """Shut down the background processor."""
        self.logger.info("Shutting down background processor")
        
        # Stop the result timer
        self.result_timer.stop()
        
        # Cancel all active tasks
        for task_id in self.get_active_tasks():
            self.cancel_task(task_id)
        
        # Stop all worker threads
        for worker in self.workers:
            worker.stop()
            worker.wait()
        
        self.workers.clear()
        
        self.logger.info("Background processor shut down")