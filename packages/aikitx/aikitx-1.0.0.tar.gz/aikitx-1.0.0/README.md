# LLM Toolkit

[![PyPI version](https://badge.fury.io/py/llmtoolkit.svg)](https://badge.fury.io/py/llmtoolkit)
[![Python Support](https://img.shields.io/pypi/pyversions/llmtoolkit.svg)](https://pypi.org/project/llmtoolkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive toolkit for working with Large Language Models (LLMs) that provides an intuitive GUI interface for model loading, chat interactions, document summarization, and email automation. Built with modern Python technologies and designed for both developers and end-users.

## Features

### 🤖 Multiple Model Backends
- **GGUF Support**: Optimized inference with ctransformers and llama-cpp-python
- **Hugging Face Integration**: Direct model loading from HF Hub (optional)
- **Hardware Detection**: Automatic GPU/CPU optimization
- **Memory Management**: Intelligent resource allocation

### 💬 Advanced Chat Interface
- **Interactive Conversations**: Real-time chat with loaded models
- **History Management**: Persistent conversation storage
- **Parameter Control**: Fine-tune generation settings
- **Context Awareness**: Maintain conversation context

### 📄 Document Processing
- **Multi-format Support**: PDF, Word, and text documents
- **Intelligent Summarization**: AI-powered content extraction
- **Chunked Processing**: Handle large documents efficiently
- **Batch Operations**: Process multiple files simultaneously

### 📧 Email Automation
- **Gmail Integration**: Secure OAuth2 authentication
- **AI-Powered Drafting**: Generate professional emails
- **Smart Replies**: Context-aware response generation
- **Bulk Operations**: Marketing and communication automation

### 🎨 Modern User Interface
- **Cross-Platform**: Windows, macOS, and Linux support
- **Theme Support**: Dark and light mode options
- **Responsive Design**: Adaptive layout for different screen sizes
- **Accessibility**: Keyboard shortcuts and screen reader support

### ⚡ Performance & Reliability
- **Multi-threading**: Non-blocking UI operations
- **Resource Monitoring**: Real-time memory and CPU tracking
- **Error Recovery**: Graceful handling of failures
- **Logging System**: Comprehensive debugging information

## Quick Start

1. **Install the package:**
   ```bash
   pip install llmtoolkit
   ```

2. **Launch the application:**
   ```bash
   llmtoolkit
   ```

3. **Load a model and start chatting!**

## Installation

### Basic Installation

```bash
pip install llmtoolkit
```

### With Optional Dependencies

For Hugging Face transformers support:
```bash
pip install llmtoolkit[transformers]
```

For GPU acceleration:
```bash
pip install llmtoolkit[gpu]
```

For all features:
```bash
pip install llmtoolkit[all]
```

## Usage

### Command Line

After installation, you can launch the application with:

```bash
llmtoolkit
```

### Command Line Options

```bash
llmtoolkit --help          # Show help message
llmtoolkit --version       # Show version information
llmtoolkit --model PATH    # Load a specific model on startup
llmtoolkit --debug         # Enable debug logging
```

### Python Module

You can also run it as a Python module:

```bash
python -m llmtoolkit
```

### Programmatic Usage

```python
import llmtoolkit

# Launch the GUI application
llmtoolkit.main()

# Or access specific components
from llmtoolkit.app.core import ModelService
model_service = ModelService()
```

## Supported Model Formats

- **GGUF** (.gguf) - Recommended format for efficient inference
- **GGML** (.ggml) - Legacy format support
- **Hugging Face** - Direct model loading from HF Hub (with transformers extra)
- **PyTorch** (.bin, .pt, .pth) - PyTorch model files
- **Safetensors** (.safetensors) - Safe tensor format

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB+ recommended for larger models)
- **Storage**: 2GB free space (plus space for models)
- **GPU** (optional): NVIDIA CUDA, AMD ROCm, or Apple Metal support

## Configuration

The application stores configuration and data in:
- **Windows**: `%APPDATA%\llmtoolkit\`
- **macOS**: `~/Library/Application Support/llmtoolkit/`
- **Linux**: `~/.config/llmtoolkit/`

## Troubleshooting

### Common Issues

**Installation Problems:**
- Ensure you have Python 3.8+ installed
- Try upgrading pip: `pip install --upgrade pip`
- For GPU support issues, check your CUDA/ROCm installation

**Model Loading Issues:**
- Verify model file format is supported (GGUF recommended)
- Check available system memory
- Ensure model file is not corrupted

**GUI Not Starting:**
- Install GUI dependencies: `pip install llmtoolkit[all]`
- On Linux, ensure X11 forwarding is enabled if using SSH
- Check system compatibility with PySide6

**Performance Issues:**
- Close other memory-intensive applications
- Use smaller models for limited hardware
- Enable GPU acceleration if available

## Development

### Setting up Development Environment

```bash
git clone https://github.com/hussainnazary2/LLM-Toolkit.git
cd LLM-Toolkit
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black llmtoolkit/
isort llmtoolkit/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) for the GUI framework
- Model loading powered by [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) and [ctransformers](https://github.com/marella/ctransformers)
- Optional Hugging Face integration via [transformers](https://github.com/huggingface/transformers)

## Changelog

See [CHANGELOG.md](https://github.com/hussainnazary2/LLM-Toolkit/releases) for version history and updates.

## Support

If you encounter any issues or have questions:

1. Check the [documentation](https://github.com/hussainnazary2/LLM-Toolkit#readme)
2. Search [existing issues](https://github.com/hussainnazary2/LLM-Toolkit/issues)
3. Create a [new issue](https://github.com/hussainnazary2/LLM-Toolkit/issues/new) if needed
4. Contact the developer: [hussainnazary475@gmail.com](mailto:hussainnazary475@gmail.com)

## Author

**Hussain Nazary**
- Email: [hussainnazary475@gmail.com](mailto:hussainnazary475@gmail.com)
- GitHub: [@hussainnazary2](https://github.com/hussainnazary2)
- Project: [LLM-Toolkit](https://github.com/hussainnazary2/LLM-Toolkit)

---

**Made with ❤️ for the AI community**