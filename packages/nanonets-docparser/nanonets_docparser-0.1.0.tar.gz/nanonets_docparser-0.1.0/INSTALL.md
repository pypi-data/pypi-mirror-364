# Installation Guide

This guide will help you install and set up the Nanonets Document Extractor package.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Options

### 1. Basic Installation

Install the package with basic dependencies:

```bash
pip install nanonets-document-extractor
```

### 2. Installation with GPU Support

If you have a CUDA-compatible GPU and want to use GPU acceleration:

```bash
pip install nanonets-document-extractor[gpu]
```

**Note**: This requires CUDA toolkit and compatible GPU drivers to be installed on your system.

### 3. Development Installation

For development and testing:

```bash
git clone https://github.com/nanonets/document-extractor.git
cd document-extractor
pip install -e .[dev]
```

## System Dependencies

### For OCR Processing (CPU/GPU modes)

The package uses Tesseract OCR for text extraction from images. You may need to install it separately:

#### Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-eng  # English language pack
```

#### macOS:
```bash
brew install tesseract
```

#### Windows:
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### For GPU Processing

If you want to use GPU acceleration:

1. Install CUDA Toolkit (version 11.6 or higher recommended)
2. Install cuDNN
3. Install PyTorch with CUDA support

## Configuration

### API Key Setup (for Cloud Mode)

To use cloud processing, you need a **FREE** API key from Nanonets:

1. Visit [https://app.nanonets.com/#/keys](https://app.nanonets.com/#/keys)
2. Sign up for free and generate an API key
3. Set it as an environment variable:

```bash
export NANONETS_API_KEY="your_api_key_here"
```

Or use it directly in your code:

```python
from nanonets_extractor import DocumentExtractor

extractor = DocumentExtractor(
    mode="cloud",
    api_key="your_api_key_here"
)
```

### Configuration File

You can also create a configuration file at `~/.nanonets/config.json`:

```json
{
    "api_key": "your_api_key_here",
    "default_mode": "cloud",
    "model_path": "/path/to/custom/models"
}
```

## Verification

After installation, verify that everything is working:

```python
from nanonets_extractor import DocumentExtractor

# Test CPU mode
extractor = DocumentExtractor(mode="cpu")
print(extractor.get_processing_info())

# Test cloud mode (if you have API key)
try:
    extractor = DocumentExtractor(mode="cloud", api_key="your_key")
    print("Cloud mode available")
except:
    print("Cloud mode not configured")
```

## Troubleshooting

### Common Issues

1. **ImportError for OCR libraries**
   - Make sure Tesseract is installed and in your PATH
   - For EasyOCR, ensure you have the required system dependencies

2. **CUDA/GPU issues**
   - Verify CUDA installation: `nvidia-smi`
   - Check PyTorch CUDA support: `python -c "import torch; print(torch.cuda.is_available())"`

3. **API key issues**
   - Verify your API key is correct
   - Check network connectivity
   - Ensure the API key has the necessary permissions

### Getting Help

- Check the [documentation](https://docs.nanonets.com)
- Visit the [GitHub repository](https://github.com/nanonets/document-extractor)
- Report issues on [GitHub Issues](https://github.com/nanonets/document-extractor/issues)

## Next Steps

After installation, check out the examples in the `examples/` directory:

- `examples/basic_usage.py` - Basic usage examples
- `examples/batch_processing.py` - Batch processing examples

Or try the command-line interface:

```bash
docextractor --help
``` 