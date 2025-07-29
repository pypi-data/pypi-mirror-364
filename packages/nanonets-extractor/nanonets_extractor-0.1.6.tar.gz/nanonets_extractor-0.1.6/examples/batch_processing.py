"""
Batch processing example for Nanonets Document Extractor.
"""

import os
import json
from pathlib import Path
from nanonets_extractor import DocumentExtractor


def process_directory(directory_path: str, output_dir: str = None):
    """Process all documents in a directory."""
    
    # Initialize extractor
    extractor = DocumentExtractor(mode="cpu")  # Use CPU for batch processing
    
    # Get all supported files
    supported_extensions = extractor.get_supported_formats()
    files = []
    
    for ext in supported_extensions:
        files.extend(Path(directory_path).glob(f"*{ext}"))
    
    if not files:
        print(f"No supported files found in {directory_path}")
        return
    
    print(f"Found {len(files)} files to process")
    
    # Process files
    results = {}
    for file_path in files:
        try:
            print(f"Processing: {file_path.name}")
            
            result = extractor.extract(
                file_path=str(file_path),
                output_type="flat-json"
            )
            
            results[file_path.name] = result
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            results[file_path.name] = {"error": str(e)}
    
    # Save results
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save individual results
        for filename, result in results.items():
            output_file = output_path / f"{Path(filename).stem}_extracted.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
        
        # Save summary
        summary_file = output_path / "batch_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to: {output_dir}")
    else:
        # Print summary
        print("\nProcessing Summary:")
        for filename, result in results.items():
            if "error" in result:
                print(f"❌ {filename}: {result['error']}")
            else:
                print(f"✅ {filename}: Success")


def process_with_schema(directory_path: str, schema_file: str, output_dir: str = None):
    """Process documents using a custom JSON schema."""
    
    # Load schema
    with open(schema_file, 'r') as f:
        schema = json.load(f)
    
    # Initialize extractor
    extractor = DocumentExtractor(mode="cpu")
    
    # Get files
    files = list(Path(directory_path).glob("*.pdf"))  # Example: process PDFs
    
    print(f"Processing {len(files)} PDF files with custom schema")
    
    # Process files
    results = {}
    for file_path in files:
        try:
            print(f"Processing: {file_path.name}")
            
            result = extractor.extract(
                file_path=str(file_path),
                output_type="specified-json",
                json_schema=schema
            )
            
            results[file_path.name] = result
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            results[file_path.name] = {"error": str(e)}
    
    # Save results
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for filename, result in results.items():
            output_file = output_path / f"{Path(filename).stem}_schema_extracted.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
        
        print(f"Results saved to: {output_dir}")
    else:
        print("\nSchema-based extraction results:")
        for filename, result in results.items():
            print(f"{filename}: {result}")


def main():
    """Main function demonstrating batch processing."""
    
    # Example 1: Basic batch processing
    print("=== Basic Batch Processing ===")
    documents_dir = "documents/"  # Replace with your documents directory
    
    if os.path.exists(documents_dir):
        process_directory(documents_dir, "output/")
    else:
        print(f"Directory {documents_dir} not found")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Batch processing with custom schema
    print("=== Batch Processing with Custom Schema ===")
    
    # Create example schema
    schema = {
        "invoice_number": "string",
        "customer_name": "string",
        "total_amount": "number",
        "date": "string",
        "company_name": "string"
    }
    
    # Save schema to file
    schema_file = "invoice_schema.json"
    with open(schema_file, 'w') as f:
        json.dump(schema, f, indent=2)
    
    if os.path.exists(documents_dir):
        process_with_schema(documents_dir, schema_file, "output_schema/")
    else:
        print(f"Directory {documents_dir} not found")
    
    # Clean up
    if os.path.exists(schema_file):
        os.remove(schema_file)


if __name__ == "__main__":
    main() 