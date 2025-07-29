# Nanonets Document Extractor

A Python library for extracting data from any document using AI. Supports cloud API, local CPU, and GPU processing.

## Quick Start

### Installation

```bash
# For cloud processing only (recommended)
pip install nanonets-extractor

# For local CPU processing
pip install nanonets-extractor[cpu]

# For local GPU processing  
pip install nanonets-extractor[gpu]
```

### Get Your Free API Key
Get your free API key from [https://app.nanonets.com/#/keys](https://app.nanonets.com/#/keys)

## Usage

### Basic Example

```python
from nanonets_extractor import DocumentExtractor

# Initialize extractor
extractor = DocumentExtractor(
    mode="cloud",
    api_key="your_api_key_here"
)

# Extract data from any document
result = extractor.extract(
    file_path="invoice.pdf",
    output_type="flat-json"
)

print(result)
```

## Initialization Parameters

### DocumentExtractor()

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mode` | str | Yes | Processing mode: `"cloud"`, `"cpu"`, or `"gpu"` |
| `api_key` | str | Yes (cloud mode) | Your Nanonets API key |
| `model_path` | str | No | Custom model path for local processing |
| `device` | str | No | GPU device (e.g., "cuda:0") for GPU mode |

### Processing Modes

#### 1. Cloud Mode (Recommended)
```python
extractor = DocumentExtractor(
    mode="cloud",
    api_key="your_api_key"
)
```
- ✅ No setup required
- ✅ Fastest processing
- ✅ Most accurate
- ✅ Supports all document types

#### 2. CPU Mode
```python
extractor = DocumentExtractor(mode="cpu")
```
- ✅ Works offline
- ⚠️ Slower processing
- ⚠️ Requires local dependencies

#### 3. GPU Mode
```python
extractor = DocumentExtractor(
    mode="gpu",
    device="cuda:0"  # optional
)
```
- ✅ Faster than CPU
- ✅ Works offline
- ⚠️ Requires CUDA-capable GPU

## Extract Method

### extractor.extract()

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | str | Yes | Path to your document |
| `output_type` | str | No | Output format (default: "flat-json") |
| `specified_fields` | list | No | Extract only specific fields |
| `json_schema` | dict | No | Custom JSON schema for output |

### Output Types

| Type | Description | Example |
|------|-------------|---------|
| `"flat-json"` | Simple key-value pairs | `{"invoice_number": "123", "total": "100.00"}` |
| `"markdown"` | Formatted markdown text | `# Invoice\n**Total:** $100.00` |
| `"specified-fields"` | Only requested fields | Must provide `specified_fields` parameter |
| `"specified-json"` | Custom JSON structure | Must provide `json_schema` parameter |

## Supported Document Types

Works with **any document type**:
- 📄 **PDFs** - Invoices, contracts, reports
- 🖼️ **Images** - Screenshots, photos, scans  
- 📊 **Spreadsheets** - Excel, CSV files
- 📝 **Text Documents** - Word docs, text files
- 🆔 **ID Documents** - Passports, licenses, certificates
- 🧾 **Receipts** - Any receipt or bill
- 📋 **Forms** - Tax forms, applications, surveys

## Examples

### Extract Invoice Data
```python
extractor = DocumentExtractor(mode="cloud", api_key="your_key")

result = extractor.extract(
    file_path="invoice.pdf",
    output_type="flat-json"
)
# Returns: {"invoice_number": "INV-001", "total": "150.00", "date": "2024-01-15", ...}
```

### Extract Specific Fields
```python
result = extractor.extract(
    file_path="resume.pdf",
    output_type="specified-fields",
    specified_fields=["name", "email", "phone", "experience"]
)
# Returns: {"name": "John Doe", "email": "john@email.com", ...}
```

### Get Markdown Output
```python
result = extractor.extract(
    file_path="report.pdf",
    output_type="markdown"
)
# Returns formatted markdown text
```

### Custom JSON Schema
```python
schema = {
    "personal_info": {
        "name": "string",
        "email": "string"
    },
    "skills": ["string"]
}

result = extractor.extract(
    file_path="resume.pdf",
    output_type="specified-json",
    json_schema=schema
)
```

## Command Line Usage

```bash
# Extract to JSON
nanonets-extractor document.pdf --output-type flat-json

# Extract specific fields
nanonets-extractor invoice.pdf --output-type specified-fields --fields invoice_number,total,date

# Use cloud API
nanonets-extractor document.pdf --mode cloud --api-key your_key

# Save to file
nanonets-extractor document.pdf --output result.json
```

## Error Handling

```python
from nanonets_extractor import DocumentExtractor
from nanonets_extractor.exceptions import ExtractionError, APIError

try:
    extractor = DocumentExtractor(mode="cloud", api_key="your_key")
    result = extractor.extract("document.pdf")
    print(result)
except APIError as e:
    print(f"API error: {e}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
```

## Environment Variables

Set your API key as an environment variable:

```bash
export NANONETS_API_KEY="your_api_key_here"
```

Then use without specifying the key:
```python
extractor = DocumentExtractor(mode="cloud")  # Uses env variable
```

## License

MIT License - see LICENSE file for details.

## Support

- 📧 Email: support@nanonets.com
- 🌐 Website: https://nanonets.com
- 📖 Documentation: https://nanonets.com/documentation 