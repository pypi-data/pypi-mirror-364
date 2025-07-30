"""Custom chat bubble widget"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

# Configuration constants
CHAT_BUBBLE_MIN_WIDTH = 100
CHAT_BUBBLE_MAX_WIDTH = 600
CHAT_BUBBLE_FONT_SIZE = 14

def detect_persian_text(text: str) -> bool:
    """Detect if text contains Persian/Arabic characters"""
    if not text:
        return False
    
    # Persian/Arabic Unicode ranges
    persian_ranges = [
        (0x0600, 0x06FF),  # Arabic
        (0x0750, 0x077F),  # Arabic Supplement
        (0x08A0, 0x08FF),  # Arabic Extended-A
        (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
        (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
    ]
    
    persian_count = 0
    total_chars = 0
    
    for char in text:
        if char.isalpha():
            total_chars += 1
            char_code = ord(char)
            for start, end in persian_ranges:
                if start <= char_code <= end:
                    persian_count += 1
                    break
    
    # Consider RTL if more than 30% of alphabetic characters are Persian/Arabic
    return total_chars > 0 and (persian_count / total_chars) > 0.3

class ChatBubble(QFrame):
    """Custom chat bubble widget with automatic RTL/LTR detection"""
    
    def __init__(self, text: str, is_user: bool, force_rtl: bool = None):
        super().__init__()
        self.is_user = is_user
        self.text = text
        
        # Auto-detect RTL if not forced
        self.is_rtl = force_rtl if force_rtl is not None else detect_persian_text(text)
        self.setup_ui(text)
    
    def setup_ui(self, text: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Create text label
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Set responsive sizing based on content
        self._set_responsive_size(text)
        
        # Set font with better rendering
        font = self.label.font()
        font.setPointSize(CHAT_BUBBLE_FONT_SIZE)
        # Set font family for better rendering
        font.setFamily("Segoe UI, Arial, sans-serif")
        self.label.setFont(font)
        
        # Set alignment based on RTL/LTR detection
        layout.addWidget(self.label)
        self.update_alignment()
        
        # Apply default styling
        self.update_style(is_dark_mode=False)
    
    def _set_responsive_size(self, text: str):
        """Set responsive bubble size based on text content"""
        # Set font first so we can measure accurately
        font = self.label.font()
        font.setPointSize(CHAT_BUBBLE_FONT_SIZE)
        self.label.setFont(font)
        
        # Calculate text metrics with the actual font
        font_metrics = self.label.fontMetrics()
        text_width = font_metrics.horizontalAdvance(text)
        
        # Count words and lines
        word_count = len(text.split())
        lines = text.split('\n')
        max_line_width = max(font_metrics.horizontalAdvance(line) for line in lines) if lines else text_width
        
        # Set size policy for better responsiveness
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        # Responsive sizing based on content
        if word_count <= 2 and max_line_width < 150:
            # Very short messages: tight fit
            self.setMinimumWidth(max(60, max_line_width + 30))
            self.setMaximumWidth(max_line_width + 50)
        elif word_count <= 5 and max_line_width < 250:
            # Short messages: natural width
            self.setMinimumWidth(max(80, max_line_width + 30))
            self.setMaximumWidth(max_line_width + 60)
        elif word_count <= 15 and max_line_width < 400:
            # Medium messages: allow reasonable width
            self.setMinimumWidth(CHAT_BUBBLE_MIN_WIDTH)
            self.setMaximumWidth(min(450, max_line_width + 80))
        else:
            # Long messages: use standard responsive width
            self.setMinimumWidth(CHAT_BUBBLE_MIN_WIDTH)
            self.setMaximumWidth(CHAT_BUBBLE_MAX_WIDTH)
        
        # Ensure label can expand properly
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
    
    def update_text(self, text: str):
        """Update text and re-detect RTL if needed"""
        self.text = text
        
        # Re-detect RTL for the new text
        self.is_rtl = detect_persian_text(text)
        
        if not self.is_user:
            # Style reasoning sections differently
            if "<استدلال>" in text or "<reasoning>" in text:
                styled_text = text
                # Persian reasoning
                styled_text = styled_text.replace("<استدلال>", '<span style="color:#888; font-style:italic">')
                styled_text = styled_text.replace("</استدلال>", '</span>')
                # English reasoning
                styled_text = styled_text.replace("<reasoning>", '<span style="color:#888; font-style:italic">')
                styled_text = styled_text.replace("</reasoning>", '</span>')
                # Answer styling
                styled_text = styled_text.replace("<پاسخ>", '<span style="color:black; font-weight:bold">')
                styled_text = styled_text.replace("</پاسخ>", '</span>')
                styled_text = styled_text.replace("<answer>", '<span style="color:black; font-weight:bold">')
                styled_text = styled_text.replace("</answer>", '</span>')
                
                # Set the styled text with rich text support
                self.label.setTextFormat(Qt.RichText)
                self.label.setText(styled_text)
            else:
                # Default text display
                self.label.setTextFormat(Qt.PlainText)
                self.label.setText(text)
        else:
            # User messages are always plain text
            self.label.setTextFormat(Qt.PlainText)
            self.label.setText(text)
        
        # Update alignment after text change
        self.update_alignment()
    
    def update_alignment(self):
        """Update text alignment based on RTL detection"""
        if self.is_rtl:
            self.label.setAlignment(Qt.AlignRight | Qt.AlignTop)
            self.label.setLayoutDirection(Qt.RightToLeft)
        else:
            self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.label.setLayoutDirection(Qt.LeftToRight)
    
    def update_style(self, is_dark_mode: bool):
        """Apply styling based on theme with better text rendering"""
        if self.is_user:
            if is_dark_mode:
                self.setStyleSheet("""
                QFrame {
                    background-color: #2d5a2d;
                    border-radius: 18px;
                    margin: 3px;
                    padding: 0px;
                }
                QLabel { 
                    color: white; 
                    font-size: 14px; 
                    padding: 10px 14px;
                    line-height: 1.4;
                    word-wrap: break-word;
                    text-rendering: optimizeLegibility;
                    font-weight: 400;
                }
                """)
            else:
                self.setStyleSheet("""
                QFrame {
                    background-color: #007bff;
                    border-radius: 18px;
                    margin: 3px;
                    padding: 0px;
                }
                QLabel { 
                    color: white; 
                    font-size: 14px; 
                    padding: 10px 14px;
                    line-height: 1.4;
                    word-wrap: break-word;
                    text-rendering: optimizeLegibility;
                    font-weight: 400;
                }
                """)
        else:
            if is_dark_mode:
                self.setStyleSheet("""
                QFrame {
                    background-color: #404040;
                    border-radius: 18px;
                    margin: 3px;
                    padding: 0px;
                }
                QLabel { 
                    color: white; 
                    font-size: 14px; 
                    padding: 10px 14px;
                    line-height: 1.4;
                    word-wrap: break-word;
                    text-rendering: optimizeLegibility;
                    font-weight: 400;
                }
                """)
            else:
                self.setStyleSheet("""
                QFrame {
                    background-color: #f1f3f4;
                    border-radius: 18px;
                    margin: 3px;
                    padding: 0px;
                }
                QLabel { 
                    color: #202124; 
                    font-size: 14px; 
                    padding: 10px 14px;
                    line-height: 1.4;
                    word-wrap: break-word;
                    text-rendering: optimizeLegibility;
                    font-weight: 400;
                }
                """)
    
    def set_rtl_mode(self, is_rtl: bool):
        """Manually set RTL mode"""
        self.is_rtl = is_rtl
        self.update_alignment()
    
    def get_text(self) -> str:
        """Get the current text content"""
        return self.text
    
    def is_rtl_text(self) -> bool:
        """Check if current text is RTL"""
        return self.is_rtl