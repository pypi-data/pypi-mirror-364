# Cloud Processing Test Suite

This directory contains comprehensive test scripts for the Nanonets Document Extractor cloud processing functionality.

## Files

- `test_cloud_extraction.py` - Main test script for all cloud processing options
- `save_resume_image.py` - Helper script to create a test resume image
- `TEST_README.md` - This file

## Prerequisites

1. **API Key**: You need a **FREE** Nanonets API key
   - Get your FREE API key from: [https://app.nanonets.com/#/keys](https://app.nanonets.com/#/keys)
   - Set it as an environment variable: `export NANONETS_API_KEY='your_key_here'`

2. **Python Dependencies**: Install the required packages
   ```bash
   pip install Pillow
   ```

## Quick Start

### Step 1: Create Test Image
```bash
python save_resume_image.py
```
This creates a `resume.jpg` file with the test resume content.

### Step 2: Run Cloud Tests
```bash
python test_cloud_extraction.py
```

## Test Coverage

The test script covers all cloud processing options:

### 1. Markdown Output
- Extracts text in markdown format
- Tests basic text extraction capabilities

### 2. Flat JSON Output
- Extracts all available fields as key-value pairs
- Shows comprehensive field extraction

### 3. Specified Fields Output
- Extracts only requested fields:
  - name, email, phone, address
  - education, experience, skills, objective

### 4. Custom JSON Schema Output
- Tests structured data extraction with custom schema
- Includes nested objects and arrays

### 5. Resume-Specific Schema
- Tests specialized resume parsing
- Extracts structured resume data

### 6. Batch Processing
- Simulates processing multiple files
- Tests batch extraction capabilities

### 7. Error Handling
- Tests error handling with invalid API keys
- Validates proper error responses

## Output Files

The test script generates JSON files with results:

- `test1_markdown.json` - Markdown extraction results
- `test2_flat_json.json` - Flat JSON extraction results
- `test3_specified_fields.json` - Specified fields results
- `test4_custom_schema.json` - Custom schema results
- `test5_resume_specific.json` - Resume-specific schema results
- `test6_batch_processing.json` - Batch processing results

## Expected Results

Based on the resume content, you should see extracted data like:

### Personal Information
- **Name**: SYLVIE (XIAOTONG) HUANG
- **Email**: xhuang5@luc.edu
- **Phone**: (312) 608-8011
- **Address**: Milpitas, CA 95035

### Education
- **Loyola University Chicago**: Master of Science in Human Resources (2014-2016)
- **Northeast Agricultural University**: Bachelor degrees (2009-2013)

### Experience
- **SiFive, Inc.**: HRBP/Global HR Operations (July 2021-Present)
- **Intellipro Group Inc.**: HR/Account Manager (August 2018-July 2021)

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   ❌ Error: NANONETS_API_KEY environment variable not set
   ```
   **Solution**: Set your API key: `export NANONETS_API_KEY='your_key_here'`

2. **Image File Not Found**
   ```
   ❌ Error: Image file 'resume.jpg' not found
   ```
   **Solution**: Run `python save_resume_image.py` first

3. **Network Issues**
   ```
   ❌ Cloud API request failed: Connection error
   ```
   **Solution**: Check your internet connection and API endpoint accessibility

4. **Invalid API Key**
   ```
   ❌ Cloud API request failed: HTTP 401: Unauthorized
   ```
   **Solution**: Verify your API key is correct and has proper permissions

### Debug Mode

To see more detailed output, you can modify the test script to add debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Customization

### Testing Different Documents

To test with different documents:

1. Replace the resume image with your own document
2. Update the schema in the test script to match your document type
3. Modify the specified fields list for your use case

### Testing Different Schemas

You can create custom schemas for different document types:

```python
invoice_schema = {
    "invoice_number": "string",
    "customer_name": "string",
    "total_amount": "number",
    "date": "string",
    "items": [
        {
            "description": "string",
            "quantity": "number",
            "price": "number"
        }
    ]
}
```

## Performance Notes

- Cloud processing typically takes 2-10 seconds per document
- Batch processing processes files sequentially
- Large documents may take longer to process
- Network latency affects response times

## Support

If you encounter issues:

1. Check the error messages in the test output
2. Verify your API key and permissions
3. Test with a simple document first
4. Check the generated JSON files for detailed results 