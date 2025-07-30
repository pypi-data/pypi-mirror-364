"""
Threaded PDF Reader

This module provides background PDF processing with progress reporting
to prevent UI freezing during large PDF file processing.
"""

import logging
import os
import time
from typing import Optional, Dict, Any
from pathlib import Path
from PySide6.QtCore import QThread, Signal

class PDFReaderWorker(QThread):
    """Worker thread for PDF content extraction."""
    
    # Signals
    progress_updated = Signal(int, str)  # progress_percent, status_message
    page_processed = Signal(int, int, str)  # page_number, total_pages, preview_text
    extraction_completed = Signal(str)  # extracted_text
    extraction_failed = Signal(str)  # error_message
    
    def __init__(self, file_path: str, parent=None):
        """
        Initialize the PDF reader worker.
        
        Args:
            file_path: Path to the PDF file
            parent: Parent QObject
        """
        super().__init__(parent)
        self.file_path = file_path
        self.should_stop = False
        self.logger = logging.getLogger("gguf_loader.threaded_pdf_reader")
    
    def stop(self):
        """Stop the PDF extraction process."""
        self.should_stop = True
        self.logger.info("PDF extraction stop requested")
    
    def run(self):
        """Run the PDF extraction process."""
        try:
            self.logger.info(f"Starting PDF extraction: {self.file_path}")
            
            # Validate file
            if not self._validate_file():
                return
            
            # Extract content
            extracted_text = self._extract_pdf_content()
            
            if self.should_stop:
                return
            
            if extracted_text and extracted_text.strip():
                self.progress_updated.emit(100, "PDF extraction completed")
                self.extraction_completed.emit(extracted_text.strip())
                self.logger.info(f"PDF extraction completed: {len(extracted_text)} characters")
            else:
                self.extraction_failed.emit("PDF appears to contain no extractable text (may be image-based)")
                
        except Exception as e:
            self.logger.error(f"PDF extraction error: {e}")
            self.extraction_failed.emit(f"PDF extraction failed: {str(e)}")
    
    def _validate_file(self) -> bool:
        """Validate the PDF file."""
        try:
            self.progress_updated.emit(5, "Validating PDF file...")
            
            if not os.path.exists(self.file_path):
                self.extraction_failed.emit(f"PDF file does not exist: {self.file_path}")
                return False
            
            if not os.access(self.file_path, os.R_OK):
                self.extraction_failed.emit(f"PDF file is not readable: {self.file_path}")
                return False
            
            file_size = os.path.getsize(self.file_path)
            self.logger.info(f"PDF file size: {file_size} bytes")
            
            if file_size == 0:
                self.extraction_failed.emit("PDF file is empty")
                return False
            
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                self.extraction_failed.emit("PDF file is too large (>100MB). Please use a smaller file.")
                return False
            
            return True
            
        except Exception as e:
            self.extraction_failed.emit(f"File validation error: {str(e)}")
            return False
    
    def _extract_pdf_content(self) -> str:
        """Extract content from PDF with progress reporting."""
        text = ""
        
        # Try pdfplumber first (generally better)
        try:
            text = self._extract_with_pdfplumber()
            if text and text.strip():
                return text
        except ImportError:
            self.logger.info("pdfplumber not available, trying PyPDF2...")
        except Exception as e:
            self.logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2...")
        
        # Fallback to PyPDF2
        try:
            text = self._extract_with_pypdf2()
            if text and text.strip():
                return text
        except ImportError:
            raise Exception("PDF reading requires PyPDF2 or pdfplumber. Install with: pip install PyPDF2 pdfplumber")
        except Exception as e:
            raise Exception(f"PyPDF2 extraction failed: {str(e)}")
        
        return text
    
    def _extract_with_pdfplumber(self) -> str:
        """Extract text using pdfplumber with progress reporting."""
        import pdfplumber
        
        self.progress_updated.emit(10, "Opening PDF with pdfplumber...")
        
        text = ""
        with pdfplumber.open(self.file_path) as pdf:
            total_pages = len(pdf.pages)
            self.logger.info(f"PDF has {total_pages} pages")
            
            if total_pages == 0:
                raise Exception("PDF has no pages")
            
            for i, page in enumerate(pdf.pages):
                if self.should_stop:
                    return text
                
                # Update progress
                progress = 10 + int((i / total_pages) * 80)  # 10-90% for page processing
                self.progress_updated.emit(progress, f"Extracting text from page {i+1}/{total_pages}...")
                
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
                        # Emit page processed signal with preview
                        preview = page_text[:200] + "..." if len(page_text) > 200 else page_text
                        self.page_processed.emit(i+1, total_pages, preview)
                    
                    # Report progress for every 10 pages or at the end
                    if (i + 1) % 10 == 0 or i == total_pages - 1:
                        self.logger.info(f"Processed {i+1}/{total_pages} pages...")
                    
                    # Small delay to prevent overwhelming the system
                    self.msleep(10)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract text from page {i+1}: {e}")
                    continue
        
        self.progress_updated.emit(95, "Finalizing text extraction...")
        return text
    
    def _extract_with_pypdf2(self) -> str:
        """Extract text using PyPDF2 with progress reporting."""
        import PyPDF2
        
        self.progress_updated.emit(10, "Opening PDF with PyPDF2...")
        
        text = ""
        with open(self.file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            self.logger.info(f"PDF has {total_pages} pages")
            
            if total_pages == 0:
                raise Exception("PDF has no pages")
            
            for i, page in enumerate(pdf_reader.pages):
                if self.should_stop:
                    return text
                
                # Update progress
                progress = 10 + int((i / total_pages) * 80)  # 10-90% for page processing
                self.progress_updated.emit(progress, f"Extracting text from page {i+1}/{total_pages}...")
                
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
                        # Emit page processed signal with preview
                        preview = page_text[:200] + "..." if len(page_text) > 200 else page_text
                        self.page_processed.emit(i+1, total_pages, preview)
                    
                    # Report progress for every 10 pages or at the end
                    if (i + 1) % 10 == 0 or i == total_pages - 1:
                        self.logger.info(f"Processed {i+1}/{total_pages} pages...")
                    
                    # Small delay to prevent overwhelming the system
                    self.msleep(10)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract text from page {i+1}: {e}")
                    continue
        
        self.progress_updated.emit(95, "Finalizing text extraction...")
        return text

class ThreadedPDFReader:
    """Manager for threaded PDF reading operations."""
    
    def __init__(self):
        """Initialize the threaded PDF reader."""
        self.logger = logging.getLogger("gguf_loader.threaded_pdf_reader.manager")
        self.worker: Optional[PDFReaderWorker] = None
    
    def start_extraction(self, file_path: str, 
                        progress_callback=None,
                        page_callback=None,
                        success_callback=None,
                        error_callback=None) -> bool:
        """
        Start PDF extraction in background thread.
        
        Args:
            file_path: Path to PDF file
            progress_callback: Callback for progress updates (progress_percent, status_message)
            page_callback: Callback for page processing (page_number, total_pages, preview_text)
            success_callback: Callback for successful extraction (extracted_text)
            error_callback: Callback for extraction errors (error_message)
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Stop any existing extraction
            self.stop_extraction()
            
            # Create worker
            self.worker = PDFReaderWorker(file_path)
            
            # Connect callbacks
            if progress_callback:
                self.worker.progress_updated.connect(progress_callback)
            if page_callback:
                self.worker.page_processed.connect(page_callback)
            if success_callback:
                self.worker.extraction_completed.connect(success_callback)
            if error_callback:
                self.worker.extraction_failed.connect(error_callback)
            
            # Start extraction
            self.worker.start()
            self.logger.info(f"Started PDF extraction: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start PDF extraction: {e}")
            if error_callback:
                error_callback(f"Failed to start PDF extraction: {str(e)}")
            return False
    
    def stop_extraction(self):
        """Stop the current PDF extraction."""
        if self.worker and self.worker.isRunning():
            self.logger.info("Stopping PDF extraction...")
            self.worker.stop()
            self.worker.wait(5000)  # Wait up to 5 seconds
            if self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait(2000)
            self.worker = None
    
    def is_extracting(self) -> bool:
        """Check if PDF extraction is currently running."""
        return self.worker is not None and self.worker.isRunning()