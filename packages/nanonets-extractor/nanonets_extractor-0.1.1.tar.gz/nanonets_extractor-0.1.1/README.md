# Nanonets Document Extractor

A unified Python library for extracting data from any type of document with support for local CPU, GPU, and cloud processing.

🎉 **Get started for FREE** with our cloud API! No setup required - just get your free API key from [https://app.nanonets.com/#/keys](https://app.nanonets.com/#/keys) and start extracting data instantly.

## Features

- **Multiple Processing Options**: Choose between local CPU, local GPU, or cloud processing
- **FREE Cloud Processing**: Get started instantly with our free cloud API
- **Unified Interface**: Same API regardless of processing method
- **Multiple Output Formats**: Markdown, flat JSON, specified fields, or custom JSON schema
- **Wide Document Support**: PDFs, images, Word documents, Excel files, and more
- **Easy Integration**: Simple, minimal API design

## Installation

### Basic Installation
```bash
pip install nanonets-extractor
```

### With GPU Support
```bash
pip install nanonets-extractor[gpu]
```

### Development Installation
```bash
git clone https://github.com/nanonets/document-extractor.git
cd document-extractor
pip install -e .
```

## Quick Start

### Basic Usage

```python
from nanonets_extractor import DocumentExtractor

# Initialize with cloud processing (requires API key)
extractor = DocumentExtractor(
    mode="cloud",
    api_key="your_api_key_here"  # Get your FREE API key from https://app.nanonets.com/#/keys
)

# Extract data from a document
result = extractor.extract(
    file_path="invoice.pdf",
    output_type="flat-json"
)

print(result)
```

### Local Processing

```python
from nanonets_extractor import DocumentExtractor

# CPU processing
extractor = DocumentExtractor(mode="cpu")

# GPU processing (if available)
extractor = DocumentExtractor(mode="gpu")

result = extractor.extract("document.pdf", output_type="markdown")
```

## API Reference

### DocumentExtractor

The main class for document extraction.

#### Initialization

```python
DocumentExtractor(
    mode: str = "cloud",  # "cloud", "cpu", or "gpu"
    api_key: str = None,  # Required for cloud mode
    model_path: str = None,  # Optional: custom model path for local processing
    device: str = None,  # Optional: specify device for GPU processing
)
```

#### Methods

##### extract()

```python
extract(
    file_path: str,
    output_type: str = "flat-json",
    specified_fields: List[str] = None,
    json_schema: Dict = None
) -> Dict
```

**Parameters:**
- `file_path`: Path to the document file
- `output_type`: One of "markdown", "flat-json", "specified-fields", or "specified-json"
- `specified_fields`: List of field names to extract (for "specified-fields" output)
- `json_schema`: Custom JSON schema (for "specified-json" output)

**Returns:**
- Dictionary containing extracted data

## Output Types

### 1. Markdown
Returns structured markdown text from the document.

### 2. Flat JSON
Returns all extracted fields as key-value pairs.

```json
{
  "document_title": "Invoice #12345",
  "invoice_number": "12345",
  "date": "2024-01-15",
  "total_amount": "1500.00",
  "customer_name": "John Doe"
}
```

### 3. Specified Fields
Returns only the requested fields.

```python
result = extractor.extract(
    "invoice.pdf",
    output_type="specified-fields",
    specified_fields=["invoice_number", "customer_name", "total_amount"]
)
```

### 4. Custom JSON Schema
Returns data structured according to your schema.

```python
schema = {
    "invoice_number": "string",
    "customer_name": "string",
    "total_amount": "number",
    "items": [
        {
            "description": "string",
            "quantity": "number",
            "price": "number"
        }
    ]
}

result = extractor.extract(
    "invoice.pdf",
    output_type="specified-json",
    json_schema=schema
)
```

## Processing Modes

### Cloud Mode
- **Pros**: No setup required, high accuracy, handles all document types, **FREE to use**
- **Cons**: Requires internet connection and API key
- **Best for**: Production applications, high-volume processing, getting started quickly

```python
extractor = DocumentExtractor(
    mode="cloud",
    api_key="your_api_key"  # Get your FREE API key from https://app.nanonets.com/#/keys
)
```

### CPU Mode
- **Pros**: Works offline, no API costs
- **Cons**: Slower processing, requires model downloads
- **Best for**: Development, testing, low-volume processing

```python
extractor = DocumentExtractor(mode="cpu")
```

### GPU Mode
- **Pros**: Fast local processing, no API costs
- **Cons**: Requires GPU hardware, CUDA setup
- **Best for**: High-performance local processing

```python
extractor = DocumentExtractor(mode="gpu")
```

## Supported File Types

- **PDFs**: All PDF formats
- **Images**: PNG, JPEG, TIFF, BMP
- **Documents**: DOCX, DOC
- **Spreadsheets**: XLSX, XLS, CSV
- **Text Files**: TXT, RTF

## Examples

### Invoice Processing

```python
from nanonets_extractor import DocumentExtractor

extractor = DocumentExtractor(mode="cloud", api_key="your_key")

# Extract invoice data
result = extractor.extract(
    "invoice.pdf",
    output_type="specified-fields",
    specified_fields=[
        "invoice_number",
        "customer_name", 
        "total_amount",
        "date",
        "due_date"
    ]
)

print(f"Invoice: {result['invoice_number']}")
print(f"Customer: {result['customer_name']}")
print(f"Amount: ${result['total_amount']}")
```

### Receipt Processing

```python
# Extract receipt data with custom schema
schema = {
    "merchant_name": "string",
    "total_amount": "number",
    "date": "string",
    "items": [
        {
            "name": "string",
            "price": "number"
        }
    ]
}

result = extractor.extract(
    "receipt.jpg",
    output_type="specified-json",
    json_schema=schema
)
```

### Batch Processing

```python
import os
from nanonets_extractor import DocumentExtractor

extractor = DocumentExtractor(mode="cpu")

# Process all PDFs in a directory
pdf_dir = "documents/"
results = {}

for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        file_path = os.path.join(pdf_dir, filename)
        results[filename] = extractor.extract(file_path, output_type="flat-json")
```

## Error Handling

```python
from nanonets_extractor import DocumentExtractor, ExtractionError

try:
    extractor = DocumentExtractor(mode="cloud", api_key="invalid_key")
    result = extractor.extract("document.pdf")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
```

## Configuration

### Environment Variables

```bash
# Set API key as environment variable
export NANONETS_API_KEY="your_api_key_here"
```

### Configuration File

Create `~/.nanonets/config.json`:

```json
{
    "api_key": "your_api_key_here",
    "default_mode": "cloud",
    "model_path": "/path/to/custom/models"
}
```

## CLI Usage

```bash
# Basic extraction
nanonets-extractor document.pdf --output-type flat-json

# Extract specific fields
nanonets-extractor invoice.pdf --output-type specified-fields --fields invoice_number,customer_name,total_amount

# Use cloud processing
nanonets-extractor document.pdf --mode cloud --api-key your_key

# Save output to file
nanonets-extractor document.pdf --output result.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: [docs.nanonets.com](https://docs.nanonets.com)
- API Keys: [app.nanonets.com/#/keys](https://app.nanonets.com/#/keys)
- Issues: [GitHub Issues](https://github.com/nanonets/document-extractor/issues) 