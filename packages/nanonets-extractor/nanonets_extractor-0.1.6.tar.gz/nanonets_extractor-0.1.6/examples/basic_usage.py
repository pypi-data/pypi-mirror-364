"""
Basic usage example for Nanonets Document Extractor.
"""

from nanonets_extractor import DocumentExtractor


def main():
    """Demonstrate basic usage of the document extractor."""
    
    # Example 1: Cloud processing (requires API key)
    print("=== Cloud Processing Example ===")
    try:
        # Initialize with cloud processing
        extractor = DocumentExtractor(
            mode="cloud",
            api_key="your_api_key_here"  # Get your FREE API key from https://app.nanonets.com/#/keys
        )
        
        # Extract data from a document
        result = extractor.extract(
            file_path="sample_invoice.pdf",  # Replace with actual file path
            output_type="flat-json"
        )
        
        print("Cloud extraction result:")
        print(result)
        
    except Exception as e:
        print(f"Cloud processing example failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: CPU processing (works offline)
    print("=== CPU Processing Example ===")
    try:
        # Initialize with CPU processing
        extractor = DocumentExtractor(mode="cpu")
        
        # Extract data from a document
        result = extractor.extract(
            file_path="sample_document.pdf",  # Replace with actual file path
            output_type="markdown"
        )
        
        print("CPU extraction result:")
        print(result)
        
    except Exception as e:
        print(f"CPU processing example failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: GPU processing (if available)
    print("=== GPU Processing Example ===")
    try:
        # Initialize with GPU processing
        extractor = DocumentExtractor(mode="gpu")
        
        # Extract specific fields
        result = extractor.extract(
            file_path="sample_invoice.pdf",  # Replace with actual file path
            output_type="specified-fields",
            specified_fields=["invoice_number", "customer_name", "total_amount", "date"]
        )
        
        print("GPU extraction result:")
        print(result)
        
    except Exception as e:
        print(f"GPU processing example failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Custom JSON schema
    print("=== Custom JSON Schema Example ===")
    try:
        extractor = DocumentExtractor(mode="cpu")
        
        # Define custom schema
        schema = {
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
        
        result = extractor.extract(
            file_path="sample_invoice.pdf",  # Replace with actual file path
            output_type="specified-json",
            json_schema=schema
        )
        
        print("Custom schema extraction result:")
        print(result)
        
    except Exception as e:
        print(f"Custom schema example failed: {e}")


if __name__ == "__main__":
    main() 