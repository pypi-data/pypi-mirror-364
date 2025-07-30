"""
Chunked Summarization System

This module provides intelligent text chunking and progressive summarization
for large documents, with proper threading and progress reporting.
"""

import logging
import time
import re
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from PySide6.QtCore import QThread, Signal, QObject

@dataclass
class TextChunk:
    """Represents a chunk of text for processing."""
    index: int
    text: str
    start_pos: int
    end_pos: int
    word_count: int
    estimated_tokens: int

@dataclass
class ChunkSummary:
    """Represents a summary of a text chunk."""
    chunk_index: int
    summary: str
    word_count: int
    processing_time: float
    success: bool
    error_message: Optional[str] = None

class TextChunker:
    """Intelligent text chunking for large documents."""
    
    def __init__(self, max_chunk_size: int = 3000, overlap_size: int = 200):
        """
        Initialize the text chunker.
        
        Args:
            max_chunk_size: Maximum number of words per chunk
            overlap_size: Number of words to overlap between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.logger = logging.getLogger("gguf_loader.chunked_summarization.chunker")
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        """
        Split text into intelligent chunks.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of TextChunk objects
        """
        if not text or not text.strip():
            return []
        
        # Clean and normalize text
        text = self._clean_text(text)
        words = text.split()
        total_words = len(words)
        
        self.logger.info(f"Chunking text: {total_words} words, max chunk size: {self.max_chunk_size}")
        
        if total_words <= self.max_chunk_size:
            # Text is small enough for single chunk
            return [TextChunk(
                index=0,
                text=text,
                start_pos=0,
                end_pos=len(text),
                word_count=total_words,
                estimated_tokens=self._estimate_tokens(text)
            )]
        
        chunks = []
        chunk_index = 0
        start_word = 0
        
        while start_word < total_words:
            # Calculate end word for this chunk
            end_word = min(start_word + self.max_chunk_size, total_words)
            
            # Try to find a good breaking point (sentence boundary)
            if end_word < total_words:
                end_word = self._find_sentence_boundary(words, start_word, end_word)
            
            # Extract chunk text
            chunk_words = words[start_word:end_word]
            chunk_text = ' '.join(chunk_words)
            
            # Calculate positions in original text
            start_pos = len(' '.join(words[:start_word])) if start_word > 0 else 0
            end_pos = start_pos + len(chunk_text)
            
            # Create chunk
            chunk = TextChunk(
                index=chunk_index,
                text=chunk_text,
                start_pos=start_pos,
                end_pos=end_pos,
                word_count=len(chunk_words),
                estimated_tokens=self._estimate_tokens(chunk_text)
            )
            
            chunks.append(chunk)
            
            self.logger.debug(f"Created chunk {chunk_index}: {chunk.word_count} words, {chunk.estimated_tokens} tokens")
            
            # Move to next chunk with overlap
            chunk_index += 1
            start_word = max(end_word - self.overlap_size, start_word + 1)
            
            # Prevent infinite loop
            if start_word >= end_word:
                break
        
        self.logger.info(f"Created {len(chunks)} chunks from {total_words} words")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for processing."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('—', '-').replace('–', '-')
        
        return text.strip()
    
    def _find_sentence_boundary(self, words: List[str], start: int, preferred_end: int) -> int:
        """Find a good sentence boundary near the preferred end."""
        # Look for sentence endings within a reasonable range
        search_start = max(start + self.max_chunk_size // 2, preferred_end - 100)
        search_end = min(preferred_end + 50, len(words))
        
        sentence_endings = ['.', '!', '?', '.\n', '!\n', '?\n']
        
        # Search backwards from preferred end
        for i in range(min(preferred_end, search_end) - 1, search_start - 1, -1):
            if i < len(words) and any(words[i].endswith(ending) for ending in sentence_endings):
                return i + 1
        
        # If no sentence boundary found, use preferred end
        return preferred_end
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: 1 token ≈ 0.75 words for English
        word_count = len(text.split())
        return int(word_count * 1.33)

class ChunkedSummarizationWorker(QThread):
    """Worker thread for chunked summarization processing."""
    
    # Signals
    progress_updated = Signal(int, str)  # progress_percent, status_message
    chunk_completed = Signal(int, str, float)  # chunk_index, summary, processing_time
    chunk_failed = Signal(int, str)  # chunk_index, error_message
    all_completed = Signal(str)  # final_summary
    error_occurred = Signal(str)  # error_message
    
    def __init__(self, chunks: List[TextChunk], style: str, backend_manager, parent=None):
        """
        Initialize the chunked summarization worker.
        
        Args:
            chunks: List of text chunks to process
            style: Summarization style
            backend_manager: Backend manager for AI generation
            parent: Parent QObject
        """
        super().__init__(parent)
        self.chunks = chunks
        self.style = style
        self.backend_manager = backend_manager
        self.chunk_summaries: List[ChunkSummary] = []
        self.should_stop = False
        self.logger = logging.getLogger("gguf_loader.chunked_summarization.worker")
    
    def stop(self):
        """Stop the summarization process."""
        self.should_stop = True
        self.logger.info("Chunked summarization stop requested")
    
    def run(self):
        """Run the chunked summarization process."""
        try:
            self.logger.info(f"Starting chunked summarization: {len(self.chunks)} chunks, style: {self.style}")
            
            # Phase 1: Summarize individual chunks
            self.progress_updated.emit(0, f"Processing {len(self.chunks)} chunks...")
            
            for i, chunk in enumerate(self.chunks):
                if self.should_stop:
                    self.logger.info("Summarization stopped by user")
                    return
                
                # Update progress
                progress = int((i / len(self.chunks)) * 80)  # 80% for chunk processing
                self.progress_updated.emit(progress, f"Processing chunk {i+1}/{len(self.chunks)}...")
                
                # Process chunk
                chunk_summary = self._process_chunk(chunk)
                self.chunk_summaries.append(chunk_summary)
                
                if chunk_summary.success:
                    self.chunk_completed.emit(chunk.index, chunk_summary.summary, chunk_summary.processing_time)
                    self.logger.info(f"Chunk {i+1} completed: {chunk_summary.word_count} words in {chunk_summary.processing_time:.2f}s")
                else:
                    self.chunk_failed.emit(chunk.index, chunk_summary.error_message or "Unknown error")
                    self.logger.error(f"Chunk {i+1} failed: {chunk_summary.error_message}")
                
                # Small delay to prevent overwhelming the system
                self.msleep(100)
            
            if self.should_stop:
                return
            
            # Phase 2: Combine chunk summaries into final summary
            self.progress_updated.emit(85, "Combining chunk summaries...")
            
            successful_summaries = [cs for cs in self.chunk_summaries if cs.success]
            
            if not successful_summaries:
                self.error_occurred.emit("All chunks failed to process")
                return
            
            if len(successful_summaries) == 1:
                # Only one successful chunk, use it directly
                final_summary = successful_summaries[0].summary
            else:
                # Combine multiple chunk summaries
                final_summary = self._combine_summaries(successful_summaries)
            
            if self.should_stop:
                return
            
            # Complete
            self.progress_updated.emit(100, "Summarization completed")
            self.all_completed.emit(final_summary)
            
            total_chunks = len(self.chunks)
            successful_chunks = len(successful_summaries)
            self.logger.info(f"Chunked summarization completed: {successful_chunks}/{total_chunks} chunks successful")
            
        except Exception as e:
            self.logger.error(f"Chunked summarization error: {e}")
            self.error_occurred.emit(f"Summarization error: {str(e)}")
    
    def _process_chunk(self, chunk: TextChunk) -> ChunkSummary:
        """Process a single chunk."""
        start_time = time.time()
        
        try:
            # Create chunk-specific prompt
            prompt = self._create_chunk_prompt(chunk)
            
            # Generate summary using backend
            from llmtoolkit.app.core.model_backends import GenerationConfig
            config = GenerationConfig(
                max_tokens=300 if self.style == "detailed" else 200,
                temperature=0.3,
                top_p=0.9,
                top_k=40,
                stop_sequences=["</s>", "<|im_end|>", "\n\n---"]
            )
            
            if hasattr(self.backend_manager, 'generate_text_optimized'):
                response = self.backend_manager.generate_text_optimized(prompt, config)
            else:
                response = self.backend_manager.generate_text(prompt, config)
            
            processing_time = time.time() - start_time
            
            if response and response.strip():
                # Clean up response
                summary = self._clean_summary(response.strip())
                
                return ChunkSummary(
                    chunk_index=chunk.index,
                    summary=summary,
                    word_count=len(summary.split()),
                    processing_time=processing_time,
                    success=True
                )
            else:
                return ChunkSummary(
                    chunk_index=chunk.index,
                    summary="",
                    word_count=0,
                    processing_time=processing_time,
                    success=False,
                    error_message="Empty response from AI model"
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            return ChunkSummary(
                chunk_index=chunk.index,
                summary="",
                word_count=0,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def _create_chunk_prompt(self, chunk: TextChunk) -> str:
        """Create a prompt for chunk summarization."""
        if self.style == "bullet_points":
            return f"""Please provide a bullet-point summary of the following text section:

{chunk.text}

Bullet-point summary:"""
        elif self.style == "detailed":
            return f"""Please provide a detailed summary of the following text section:

{chunk.text}

Detailed summary:"""
        else:  # concise
            return f"""Please provide a concise summary of the following text section:

{chunk.text}

Summary:"""
    
    def _clean_summary(self, summary: str) -> str:
        """Clean up the generated summary."""
        # Remove prompt echoing
        summary_markers = ["Summary:", "summary:", "Bullet-point summary:", "Detailed summary:"]
        for marker in summary_markers:
            if marker in summary:
                parts = summary.split(marker, 1)
                if len(parts) > 1:
                    summary = parts[1].strip()
                    break
        
        # Remove excessive newlines
        summary = re.sub(r'\n{3,}', '\n\n', summary)
        
        return summary.strip()
    
    def _combine_summaries(self, summaries: List[ChunkSummary]) -> str:
        """Combine multiple chunk summaries into a final summary."""
        try:
            # Combine all chunk summaries
            combined_text = "\n\n".join([cs.summary for cs in summaries])
            
            # If combined text is still reasonable length, create final summary
            if len(combined_text.split()) <= 2000:  # Less than 2000 words
                final_prompt = f"""Please create a comprehensive summary by combining these section summaries:

{combined_text}

Final comprehensive summary:"""
                
                from llmtoolkit.app.core.model_backends import GenerationConfig
                config = GenerationConfig(
                    max_tokens=400 if self.style == "detailed" else 250,
                    temperature=0.3,
                    top_p=0.9,
                    top_k=40
                )
                
                if hasattr(self.backend_manager, 'generate_text_optimized'):
                    response = self.backend_manager.generate_text_optimized(final_prompt, config)
                else:
                    response = self.backend_manager.generate_text(final_prompt, config)
                
                if response and response.strip():
                    return self._clean_summary(response.strip())
            
            # Fallback: just concatenate the summaries
            return combined_text
            
        except Exception as e:
            self.logger.error(f"Error combining summaries: {e}")
            # Fallback: concatenate summaries
            return "\n\n".join([cs.summary for cs in summaries])

class ChunkedSummarizationManager(QObject):
    """Manager for chunked summarization with progress reporting."""
    
    # Signals
    progress_updated = Signal(int, str)  # progress_percent, status_message
    chunk_completed = Signal(int, str)  # chunk_index, summary
    summarization_completed = Signal(str)  # final_summary
    summarization_error = Signal(str)  # error_message
    
    def __init__(self, parent=None):
        """Initialize the chunked summarization manager."""
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.chunked_summarization.manager")
        self.chunker = TextChunker()
        self.worker: Optional[ChunkedSummarizationWorker] = None
    
    def start_summarization(self, text: str, style: str, backend_manager) -> bool:
        """
        Start chunked summarization process.
        
        Args:
            text: Text to summarize
            style: Summarization style
            backend_manager: Backend manager for AI generation
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Stop any existing process
            self.stop_summarization()
            
            # Create chunks
            self.logger.info(f"Starting chunked summarization: {len(text)} characters")
            chunks = self.chunker.chunk_text(text)
            
            if not chunks:
                self.summarization_error.emit("No text to summarize")
                return False
            
            self.logger.info(f"Created {len(chunks)} chunks for processing")
            
            # Create and start worker
            self.worker = ChunkedSummarizationWorker(chunks, style, backend_manager)
            
            # Connect signals
            self.worker.progress_updated.connect(self.progress_updated.emit)
            self.worker.chunk_completed.connect(self._on_chunk_completed)
            self.worker.chunk_failed.connect(self._on_chunk_failed)
            self.worker.all_completed.connect(self.summarization_completed.emit)
            self.worker.error_occurred.connect(self.summarization_error.emit)
            
            # Start processing
            self.worker.start()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start chunked summarization: {e}")
            self.summarization_error.emit(f"Failed to start summarization: {str(e)}")
            return False
    
    def stop_summarization(self):
        """Stop the current summarization process."""
        if self.worker and self.worker.isRunning():
            self.logger.info("Stopping chunked summarization...")
            self.worker.stop()
            self.worker.wait(5000)  # Wait up to 5 seconds
            if self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait(2000)
            self.worker = None
    
    def _on_chunk_completed(self, chunk_index: int, summary: str, processing_time: float):
        """Handle chunk completion."""
        self.logger.debug(f"Chunk {chunk_index} completed in {processing_time:.2f}s")
        self.chunk_completed.emit(chunk_index, summary)
    
    def _on_chunk_failed(self, chunk_index: int, error_message: str):
        """Handle chunk failure."""
        self.logger.warning(f"Chunk {chunk_index} failed: {error_message}")
        # Continue with other chunks - don't fail the entire process