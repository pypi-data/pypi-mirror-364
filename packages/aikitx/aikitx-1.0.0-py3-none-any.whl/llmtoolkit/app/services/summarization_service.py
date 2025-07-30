"""
Summarization Service

Processes document summarization requests using the ModelService.
Supports various input formats and configurable summarization options.
Includes streaming support for background processing with progress updates.
"""

import logging
import os
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from PySide6.QtCore import QObject, Signal, QThread

from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.interfaces.i_summarization_service import ISummarizationService


class QObjectMeta(type(QObject), type(ISummarizationService)):
    """Metaclass that resolves the conflict between QObject and ABC metaclasses."""
    pass


class SummarizationThread(QThread):
    """Thread for processing document summarization in the background with progress updates."""
    
    # Signals
    progress = Signal(str)  # Progress message
    chunk_progress = Signal(int, int)  # Current chunk, total chunks
    partial_summary = Signal(str)  # Partial summary for streaming display
    finished = Signal(str)  # Complete summary on success
    error = Signal(str)  # Error message on failure
    cancelled = Signal()  # Summarization was cancelled
    
    def __init__(self, summarization_service, text: str = None, file_path: str = None, 
                 style: str = "concise", encoding: str = "utf-8", **kwargs):
        """
        Initialize the summarization thread.
        
        Args:
            summarization_service: The SummarizationService instance
            text: Text to summarize (for text-based summarization)
            file_path: Path to file to summarize (for file-based summarization)
            style: Summarization style
            encoding: File encoding (for file-based summarization)
            **kwargs: Additional generation parameters
        """
        super().__init__()
        self.summarization_service = summarization_service
        self.text = text
        self.file_path = file_path
        self.style = style
        self.encoding = encoding
        self.kwargs = kwargs
        self._cancelled = False
        self.logger = logging.getLogger("gguf_loader.summarization_service.thread")
    
    def cancel(self):
        """Cancel the summarization process."""
        self._cancelled = True
    
    def run(self):
        """Run the summarization process with progress updates."""
        try:
            if self._cancelled:
                self.cancelled.emit()
                return
            
            # Determine if we're processing text or file
            if self.file_path:
                self.progress.emit("Reading file...")
                try:
                    # Read file content
                    text_content = self.summarization_service._read_file(self.file_path, self.encoding)
                    self.progress.emit(f"Loaded {len(text_content)} characters from file")
                except Exception as e:
                    self.error.emit(f"Failed to read file: {str(e)}")
                    return
            else:
                text_content = self.text
            
            if self._cancelled:
                self.cancelled.emit()
                return
            
            # Clean and prepare text
            self.progress.emit("Preparing text for summarization...")
            cleaned_text = self.summarization_service._clean_text(text_content)
            
            if self._cancelled:
                self.cancelled.emit()
                return
            
            # Check if text needs to be chunked
            if len(cleaned_text) > self.summarization_service.max_input_length:
                self.progress.emit("Processing large document in chunks...")
                summary = self._summarize_long_text_with_progress(cleaned_text)
            else:
                self.progress.emit("Generating summary...")
                summary = self._summarize_single_text_with_progress(cleaned_text)
            
            if self._cancelled:
                self.cancelled.emit()
                return
            
            if summary:
                self.progress.emit("Summarization completed")
                self.finished.emit(summary)
            else:
                self.error.emit("Failed to generate summary")
                
        except Exception as e:
            if not self._cancelled:
                self.logger.error(f"Error in summarization thread: {e}")
                self.error.emit(str(e))
    
    def _summarize_single_text_with_progress(self, text: str) -> str:
        """
        Summarize a single text with progress updates.
        
        Args:
            text: Text to summarize
            
        Returns:
            Summary text
        """
        try:
            # Prepare the prompt
            style_prompt = self.summarization_service.SUMMARIZATION_STYLES[self.style]
            full_prompt = f"{style_prompt}\n\n{text}\n\nSummary:"
            
            # Prepare generation parameters
            params = {
                "temperature": self.kwargs.get("temperature", self.summarization_service.default_temperature),
                "max_tokens": self.kwargs.get("max_tokens", self.summarization_service.default_max_tokens),
                "top_p": self.kwargs.get("top_p", self.summarization_service.default_top_p),
                "top_k": self.kwargs.get("top_k", self.summarization_service.default_top_k),
                "stop": self.kwargs.get("stop", ["\n\n", "Human:", "User:"])
            }
            
            if self._cancelled:
                return None
            
            # Generate summary using model service
            summary = self.summarization_service.model_service.generate_text(full_prompt, **params)
            
            if not summary:
                raise RuntimeError("Failed to generate summary")
            
            return summary.strip()
            
        except Exception as e:
            self.logger.error(f"Error in single text summarization: {e}")
            raise
    
    def _summarize_long_text_with_progress(self, text: str) -> str:
        """
        Summarize long text by chunking with progress updates.
        
        Args:
            text: Long text to summarize
            
        Returns:
            Final summary
        """
        try:
            # Split text into chunks
            chunks = self.summarization_service._split_text_into_chunks(text)
            total_chunks = len(chunks)
            
            self.progress.emit(f"Processing {total_chunks} chunks...")
            self.logger.info(f"Split text into {total_chunks} chunks for summarization")
            
            # Summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                if self._cancelled:
                    return None
                
                self.chunk_progress.emit(i + 1, total_chunks)
                self.progress.emit(f"Summarizing chunk {i+1}/{total_chunks}...")
                
                try:
                    chunk_summary = self._summarize_single_text_with_progress(chunk)
                    if chunk_summary:
                        chunk_summaries.append(chunk_summary)
                        # Emit partial summary for streaming display
                        partial_text = f"Processed {i+1}/{total_chunks} chunks:\n\n" + "\n\n".join(chunk_summaries)
                        self.partial_summary.emit(partial_text)
                except Exception as e:
                    self.logger.warning(f"Failed to summarize chunk {i+1}: {e}")
                    # Continue with other chunks
            
            if self._cancelled:
                return None
            
            if not chunk_summaries:
                raise RuntimeError("Failed to summarize any chunks")
            
            # Combine chunk summaries
            combined_summary = "\n\n".join(chunk_summaries)
            
            # Final summarization step
            self.progress.emit("Creating final summary...")
            
            # If the combined summary is still too long, summarize it again
            if len(combined_summary) > self.summarization_service.max_input_length:
                self.progress.emit("Combined summary is long, performing final summarization...")
                final_summary = self._summarize_single_text_with_progress(combined_summary)
            else:
                # Apply the requested style to the combined summary
                # Temporarily change the text for final summarization
                original_style = self.style
                final_summary = self._summarize_single_text_with_progress(combined_summary)
            
            return final_summary
            
        except Exception as e:
            self.logger.error(f"Error in long text summarization: {e}")
            raise


class SummarizationService(ISummarizationService, QObject, metaclass=QObjectMeta):
    """Service for document summarization using AI models with streaming support."""
    
    # Signals for streaming support
    summarization_started = Signal()
    summarization_progress = Signal(str)  # Progress message
    summarization_chunk_progress = Signal(int, int)  # Current chunk, total chunks
    summarization_partial = Signal(str)  # Partial summary for streaming display
    summarization_finished = Signal(str)  # Complete summary
    summarization_error = Signal(str)  # Error message
    summarization_cancelled = Signal()  # Summarization was cancelled
    
    # Base supported file formats
    _BASE_SUPPORTED_FORMATS = [
        '.txt', '.md', '.markdown', '.rst', '.rtf',
        '.csv', '.tsv', '.json', '.xml', '.html', '.htm',
        '.py', '.js', '.css', '.java', '.cpp', '.c', '.h',
        '.log', '.cfg', '.ini', '.conf', '.yaml', '.yml'
    ]
    
    # Summarization styles and their prompts
    SUMMARIZATION_STYLES = {
        "concise": "Provide a brief, concise summary of the following text in 2-3 sentences:",
        "detailed": "Provide a detailed summary of the following text, covering all main points and key details:",
        "bullet_points": "Summarize the following text as a list of key bullet points:",
        "executive": "Provide an executive summary of the following text, focusing on key insights and actionable items:",
        "technical": "Provide a technical summary of the following text, focusing on technical details and specifications:",
        "abstract": "Write an abstract-style summary of the following text, suitable for academic or professional use:"
    }
    
    def __init__(self, model_service=None, event_bus: EventBus = None, config_manager=None):
        """
        Initialize the summarization service.
        
        Args:
            model_service: ModelService instance for text generation
            event_bus: EventBus instance for communication
            config_manager: Configuration manager for settings
        """
        super().__init__()
        self.logger = logging.getLogger("gguf_loader.summarization_service")
        self.model_service = model_service
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        # Configuration
        self.max_input_length = 8000  # Maximum input text length (approximate tokens)
        self.chunk_size = 4000  # Size of text chunks for long documents
        self.chunk_overlap = 200  # Overlap between chunks
        
        # Generation parameters for summarization
        self.default_temperature = 0.3  # Lower temperature for more focused summaries
        self.default_max_tokens = 512
        self.default_top_p = 0.9
        self.default_top_k = 40
        
        # Streaming support
        self.current_thread: Optional[SummarizationThread] = None
        
        # Connect signals to event bus
        if self.event_bus:
            self.summarization_started.connect(lambda: self.event_bus.publish("summarization.generating"))
            self.summarization_progress.connect(lambda msg: self.event_bus.publish("summarization.progress", msg))
            self.summarization_chunk_progress.connect(lambda curr, total: self.event_bus.publish("summarization.chunk_progress", {"current": curr, "total": total}))
            self.summarization_partial.connect(lambda partial: self.event_bus.publish("summarization.partial", partial))
            self.summarization_finished.connect(lambda summary: self.event_bus.publish("summarization.completed", summary))
            self.summarization_error.connect(lambda error: self.event_bus.publish("summarization.error", error))
            self.summarization_cancelled.connect(lambda: self.event_bus.publish("summarization.cancelled"))
        
        # Subscribe to events if event bus is available
        if self.event_bus:
            self.event_bus.subscribe("model.loaded", self._on_model_loaded)
            self.event_bus.subscribe("model.unloaded", self._on_model_unloaded)
            self.event_bus.subscribe("summarization.cancel", self._on_cancel_request)
        
        self.logger.info("SummarizationService initialized")
    
    def _on_cancel_request(self, cancel_data):
        """Handle cancellation request from UI."""
        self.logger.info("Received cancellation request from UI")
        self.cancel_summarization()
    
    def cancel_summarization(self) -> bool:
        """
        Cancel the current summarization process.
        
        Returns:
            True if cancellation was requested, False if no summarization is running
        """
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.cancel()
            self.logger.info("Summarization cancellation requested")
            return True
        return False
    
    def summarize_text_async(self, text: str, style: str = "concise", **kwargs) -> bool:
        """
        Summarize provided text asynchronously with progress updates.
        
        This method starts summarization in a background thread and returns immediately.
        Listen to summarization signals for updates.
        
        Args:
            text: Text to summarize
            style: Summarization style (concise, detailed, bullet_points, etc.)
            **kwargs: Additional generation parameters
            
        Returns:
            True if summarization started successfully, False otherwise
        """
        if not text or not text.strip():
            self.summarization_error.emit("Text cannot be empty")
            return False
        
        if style not in self.SUMMARIZATION_STYLES:
            self.summarization_error.emit(f"Invalid style '{style}'. Supported styles: {list(self.SUMMARIZATION_STYLES.keys())}")
            return False
        
        if not self.model_service:
            self.summarization_error.emit("No model service available for summarization")
            return False
        
        # Cancel any existing summarization
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.cancel()
            self.current_thread.wait()
        
        try:
            # Create and configure the summarization thread
            self.current_thread = SummarizationThread(
                summarization_service=self,
                text=text,
                style=style,
                **kwargs
            )
            
            # Connect thread signals to service signals
            self.current_thread.progress.connect(self.summarization_progress.emit)
            self.current_thread.chunk_progress.connect(self.summarization_chunk_progress.emit)
            self.current_thread.partial_summary.connect(self.summarization_partial.emit)
            self.current_thread.finished.connect(self._on_thread_finished)
            self.current_thread.error.connect(self._on_thread_error)
            self.current_thread.cancelled.connect(self._on_thread_cancelled)
            
            # Start the thread
            self.current_thread.start()
            self.summarization_started.emit()
            
            self.logger.info(f"Started asynchronous text summarization with style: {style}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting asynchronous text summarization: {e}")
            self.summarization_error.emit(str(e))
            return False
    
    def summarize_file_async(self, file_path: str, style: str = "concise", encoding: str = "utf-8", **kwargs) -> bool:
        """
        Summarize text from file asynchronously with progress updates.
        
        This method starts summarization in a background thread and returns immediately.
        Listen to summarization signals for updates.
        
        Args:
            file_path: Path to the file to summarize
            style: Summarization style
            encoding: File encoding (default: utf-8)
            **kwargs: Additional generation parameters
            
        Returns:
            True if summarization started successfully, False otherwise
        """
        if not os.path.exists(file_path):
            self.summarization_error.emit(f"File not found: {file_path}")
            return False
        
        # Check if file format is supported
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            self.summarization_error.emit(f"Unsupported file format '{file_ext}'. Supported formats: {self.SUPPORTED_FORMATS}")
            return False
        
        if not self.model_service:
            self.summarization_error.emit("No model service available for summarization")
            return False
        
        # Cancel any existing summarization
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.cancel()
            self.current_thread.wait()
        
        try:
            # Create and configure the summarization thread
            self.current_thread = SummarizationThread(
                summarization_service=self,
                file_path=file_path,
                style=style,
                encoding=encoding,
                **kwargs
            )
            
            # Connect thread signals to service signals
            self.current_thread.progress.connect(self.summarization_progress.emit)
            self.current_thread.chunk_progress.connect(self.summarization_chunk_progress.emit)
            self.current_thread.partial_summary.connect(self.summarization_partial.emit)
            self.current_thread.finished.connect(self._on_thread_finished)
            self.current_thread.error.connect(self._on_thread_error)
            self.current_thread.cancelled.connect(self._on_thread_cancelled)
            
            # Start the thread
            self.current_thread.start()
            self.summarization_started.emit()
            
            self.logger.info(f"Started asynchronous file summarization: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting asynchronous file summarization: {e}")
            self.summarization_error.emit(str(e))
            return False
    
    def _on_thread_finished(self, summary: str):
        """Handle thread completion."""
        try:
            self.logger.info(f"Summarization completed: {len(summary)} characters")
            self.summarization_finished.emit(summary)
            
            # Publish event through event bus
            if self.event_bus:
                self.event_bus.publish("summarization.completed", summary)
            
        except Exception as e:
            self.logger.error(f"Error handling thread completion: {e}")
            self.summarization_error.emit(f"Error processing completed summary: {str(e)}")
    
    def _on_thread_error(self, error_message: str):
        """Handle thread error."""
        try:
            self.logger.error(f"Summarization thread error: {error_message}")
            self.summarization_error.emit(error_message)
            
            # Publish error event through event bus
            if self.event_bus:
                self.event_bus.publish("summarization.error", error_message)
                
        except Exception as e:
            self.logger.error(f"Error handling thread error: {e}")
    
    def _on_thread_cancelled(self):
        """Handle thread cancellation."""
        try:
            self.logger.info("Summarization was cancelled")
            self.summarization_cancelled.emit()
            
            # Publish cancellation event through event bus
            if self.event_bus:
                self.event_bus.publish("summarization.cancelled", True)
                
        except Exception as e:
            self.logger.error(f"Error handling thread cancellation: {e}")
    
    def is_summarizing(self) -> bool:
        """
        Check if summarization is currently in progress.
        
        Returns:
            True if summarization is running, False otherwise
        """
        return self.current_thread is not None and self.current_thread.isRunning()
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt from configuration.
        
        Returns:
            System prompt string
        """
        if self.config_manager:
            return self.config_manager.get_value(
                "summary_system_prompt", 
                "You are an AI assistant specialized in document summarization. Please provide clear, accurate summaries that capture the key points and main ideas."
            )
        return "You are an AI assistant specialized in document summarization."
    
    @property
    def SUPPORTED_FORMATS(self) -> List[str]:
        """
        Get list of supported file formats, including PDF if available.
        
        Returns:
            List of supported file extensions
        """
        formats = self._BASE_SUPPORTED_FORMATS.copy()
        if PDF_AVAILABLE:
            formats.append('.pdf')
        return formats
    
    def _on_model_loaded(self, model_id: str, model_info: Dict[str, Any]):
        """Handle model loaded event."""
        self.logger.info(f"Model loaded for summarization: {model_id}")
        if self.event_bus:
            self.event_bus.publish("summarization.model_ready", model_id)
    
    def _on_model_unloaded(self, model_id: str):
        """Handle model unloaded event."""
        self.logger.info(f"Model unloaded from summarization: {model_id}")
        if self.event_bus:
            self.event_bus.publish("summarization.model_unavailable", model_id)
    
    def summarize_text(self, text: str, style: str = "concise", **kwargs) -> str:
        """
        Summarize provided text.
        
        Args:
            text: Text to summarize
            style: Summarization style (concise, detailed, bullet_points, etc.)
            **kwargs: Additional generation parameters
            
        Returns:
            Summarized text
            
        Raises:
            ValueError: If text is empty or style is invalid
            RuntimeError: If no model service is available
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if style not in self.SUMMARIZATION_STYLES:
            raise ValueError(f"Invalid style '{style}'. Supported styles: {list(self.SUMMARIZATION_STYLES.keys())}")
        
        if not self.model_service:
            raise RuntimeError("No model service available for summarization")
        
        try:
            self.logger.info(f"Starting text summarization with style: {style}")
            
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Check if text needs to be chunked
            if len(cleaned_text) > self.max_input_length:
                self.logger.info("Text is long, using chunked summarization")
                summary = self._summarize_long_text(cleaned_text, style, **kwargs)
            else:
                summary = self._summarize_single_text(cleaned_text, style, **kwargs)
            
            # Note: Event publishing is handled by the app controller to avoid duplicate events
            
            self.logger.info(f"Text summarization completed. Input: {len(text)} chars, Output: {len(summary)} chars")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in text summarization: {e}")
            # Note: Error event publishing is handled by the app controller to avoid duplicate events
            raise
    
    def summarize_file(self, file_path: str, style: str = "concise", encoding: str = "utf-8", **kwargs) -> str:
        """
        Summarize text from file.
        
        Args:
            file_path: Path to the file to summarize
            style: Summarization style
            encoding: File encoding (default: utf-8)
            **kwargs: Additional generation parameters
            
        Returns:
            Summarized text
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
            UnicodeDecodeError: If file cannot be decoded with specified encoding
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if file format is supported
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format '{file_ext}'. Supported formats: {self.SUPPORTED_FORMATS}")
        
        try:
            self.logger.info(f"Starting file summarization: {file_path}")
            
            # Read file content
            text = self._read_file(file_path, encoding)
            
            # Summarize the text
            summary = self.summarize_text(text, style, **kwargs)
            
            # Publish file summarization event
            if self.event_bus:
                self.event_bus.publish("summarization.file_completed", {
                    "file_path": file_path,
                    "file_size": os.path.getsize(file_path),
                    "style": style
                })
            
            self.logger.info(f"File summarization completed: {file_path}")
            return summary
            
        except UnicodeDecodeError as e:
            self.logger.error(f"Error decoding file {file_path} with encoding {encoding}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error in file summarization: {e}")
            # Note: Error event publishing is handled by the app controller to avoid duplicate events
            raise
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported file extensions
        """
        return self.SUPPORTED_FORMATS.copy()
    
    def get_supported_styles(self) -> List[str]:
        """
        Get list of supported summarization styles.
        
        Returns:
            List of supported style names
        """
        return list(self.SUMMARIZATION_STYLES.keys())
    
    def get_style_description(self, style: str) -> Optional[str]:
        """
        Get description of a summarization style.
        
        Args:
            style: Style name
            
        Returns:
            Style description or None if style not found
        """
        return self.SUMMARIZATION_STYLES.get(style)
    
    def set_generation_parameters(self, **params) -> None:
        """
        Set default generation parameters for summarization.
        
        Args:
            **params: Generation parameters to update
        """
        if "temperature" in params:
            self.default_temperature = params["temperature"]
        if "max_tokens" in params:
            self.default_max_tokens = params["max_tokens"]
        if "top_p" in params:
            self.default_top_p = params["top_p"]
        if "top_k" in params:
            self.default_top_k = params["top_k"]
        
        self.logger.info(f"Summarization generation parameters updated: {params}")
    
    def get_generation_parameters(self) -> Dict[str, Any]:
        """
        Get current generation parameters.
        
        Returns:
            Dictionary of generation parameters
        """
        return {
            "temperature": self.default_temperature,
            "max_tokens": self.default_max_tokens,
            "top_p": self.default_top_p,
            "top_k": self.default_top_k
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and prepare text for summarization.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Split into lines first to handle long lines
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Skip very long lines that might be data dumps
            if len(line) < 1000:
                # Clean excessive whitespace within the line
                cleaned_line = ' '.join(line.split())
                if cleaned_line:  # Only add non-empty lines
                    filtered_lines.append(cleaned_line)
        
        return '\n'.join(filtered_lines)
    
    def _read_file(self, file_path: str, encoding: str) -> str:
        """
        Read file content with proper encoding handling.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
            
        Returns:
            File content as string
        """
        file_ext = Path(file_path).suffix.lower()
        
        # Handle PDF files
        if file_ext == '.pdf':
            return self._extract_pdf_text(file_path)
        
        # Handle regular text files
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try common encodings if the specified one fails
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            if encoding in encodings_to_try:
                encodings_to_try.remove(encoding)
            
            for enc in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        self.logger.warning(f"File {file_path} decoded with {enc} instead of {encoding}")
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, raise the original error
            raise
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """
        Extract text from PDF file using PyPDF2.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            RuntimeError: If PDF processing fails or PyPDF2 is not available
        """
        if not PDF_AVAILABLE:
            raise RuntimeError("PDF support is not available. Please install PyPDF2: pip install PyPDF2")
        
        try:
            text_content = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                self.logger.info(f"Processing PDF with {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():  # Only add non-empty pages
                            text_content.append(page_text)
                            self.logger.debug(f"Extracted text from page {page_num + 1}")
                    except Exception as e:
                        self.logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue
            
            if not text_content:
                raise RuntimeError("No text could be extracted from the PDF file")
            
            # Join all pages with double newlines
            full_text = '\n\n'.join(text_content)
            
            self.logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")
    
    def _summarize_single_text(self, text: str, style: str, **kwargs) -> str:
        """
        Summarize a single text that fits within context limits.
        
        Args:
            text: Text to summarize
            style: Summarization style
            **kwargs: Additional generation parameters
            
        Returns:
            Summary text
        """
        # Prepare the prompt
        style_prompt = self.SUMMARIZATION_STYLES[style]
        full_prompt = f"{style_prompt}\n\n{text}\n\nSummary:"
        
        # Prepare generation parameters
        params = {
            "temperature": kwargs.get("temperature", self.default_temperature),
            "max_tokens": kwargs.get("max_tokens", self.default_max_tokens),
            "top_p": kwargs.get("top_p", self.default_top_p),
            "top_k": kwargs.get("top_k", self.default_top_k),
            "stop": kwargs.get("stop", ["\n\n", "Human:", "User:"])
        }
        
        # Generate summary
        summary = self.model_service.generate_text(full_prompt, **params)
        
        if not summary:
            raise RuntimeError("Failed to generate summary")
        
        return summary.strip()
    
    def _summarize_long_text(self, text: str, style: str, **kwargs) -> str:
        """
        Summarize long text by chunking and then summarizing the summaries.
        
        Args:
            text: Long text to summarize
            style: Summarization style
            **kwargs: Additional generation parameters
            
        Returns:
            Final summary
        """
        # Split text into chunks
        chunks = self._split_text_into_chunks(text)
        
        self.logger.info(f"Split text into {len(chunks)} chunks for summarization")
        
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            self.logger.debug(f"Summarizing chunk {i+1}/{len(chunks)}")
            try:
                chunk_summary = self._summarize_single_text(chunk, "concise", **kwargs)
                chunk_summaries.append(chunk_summary)
            except Exception as e:
                self.logger.warning(f"Failed to summarize chunk {i+1}: {e}")
                # Continue with other chunks
        
        if not chunk_summaries:
            raise RuntimeError("Failed to summarize any chunks")
        
        # Combine chunk summaries
        combined_summary = "\n\n".join(chunk_summaries)
        
        # If the combined summary is still too long, summarize it again
        if len(combined_summary) > self.max_input_length:
            self.logger.info("Combined summary is still long, performing final summarization")
            final_summary = self._summarize_single_text(combined_summary, style, **kwargs)
        else:
            # Apply the requested style to the combined summary
            final_summary = self._summarize_single_text(combined_summary, style, **kwargs)
        
        return final_summary
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the overlap region
                search_start = max(start, end - self.chunk_overlap)
                sentence_end = -1
                
                for i in range(end - 1, search_start - 1, -1):
                    if text[i] in '.!?':
                        # Check if this is likely a sentence end (not an abbreviation)
                        if i + 1 < len(text) and text[i + 1].isspace():
                            sentence_end = i + 1
                            break
                
                if sentence_end > 0:
                    end = sentence_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Avoid infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def estimate_summary_length(self, text: str, style: str) -> int:
        """
        Estimate the length of the summary for given text and style.
        
        Args:
            text: Input text
            style: Summarization style
            
        Returns:
            Estimated summary length in characters
        """
        # Rough estimation based on style and input length
        input_length = len(text)
        
        if style == "concise":
            ratio = 0.1  # 10% of original
        elif style == "detailed":
            ratio = 0.3  # 30% of original
        elif style == "bullet_points":
            ratio = 0.2  # 20% of original
        elif style == "executive":
            ratio = 0.15  # 15% of original
        elif style == "technical":
            ratio = 0.25  # 25% of original
        elif style == "abstract":
            ratio = 0.12  # 12% of original
        else:
            ratio = 0.15  # Default
        
        estimated_length = int(input_length * ratio)
        
        # Apply reasonable bounds
        min_length = 50
        max_length = 2000
        
        return max(min_length, min(estimated_length, max_length))