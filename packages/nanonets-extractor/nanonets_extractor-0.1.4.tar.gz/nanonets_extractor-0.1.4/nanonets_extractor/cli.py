"""
Command-line interface for the Nanonets Document Extractor.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .extractor import DocumentExtractor
from .exceptions import ExtractionError, ConfigurationError, UnsupportedFileError
from .utils import get_api_key


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        run_extraction(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract data from documents using Nanonets Document Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic extraction
  nanonets-extractor document.pdf --output-type flat-json

  # Extract specific fields
  nanonets-extractor invoice.pdf --output-type specified-fields --fields invoice_number,customer_name,total_amount

  # Use cloud processing
  nanonets-extractor document.pdf --mode cloud --api-key your_key

  # Save output to file
  nanonets-extractor document.pdf --output result.json

  # Batch processing
  nanonets-extractor *.pdf --output-dir results/
        """
    )
    
    # File input
    parser.add_argument(
        'files',
        nargs='+',
        help='Document files to process (supports glob patterns)'
    )
    
    # Processing mode
    parser.add_argument(
        '--mode',
        choices=['cloud', 'cpu', 'gpu'],
        default='cloud',
        help='Processing mode (default: cloud)'
    )
    
    # API key
    parser.add_argument(
        '--api-key',
        help='FREE API key for cloud processing (get from https://app.nanonets.com/#/keys or set NANONETS_API_KEY env var)'
    )
    
    # Output type
    parser.add_argument(
        '--output-type',
        choices=['markdown', 'flat-json', 'specified-fields', 'specified-json'],
        default='flat-json',
        help='Output format (default: flat-json)'
    )
    
    # Specified fields
    parser.add_argument(
        '--fields',
        help='Comma-separated list of fields to extract (for specified-fields output)'
    )
    
    # JSON schema
    parser.add_argument(
        '--schema',
        help='Path to JSON schema file (for specified-json output)'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for batch processing'
    )
    
    # Device specification
    parser.add_argument(
        '--device',
        help='GPU device specification (e.g., cuda:0)'
    )
    
    # Model path
    parser.add_argument(
        '--model-path',
        help='Path to custom models for local processing'
    )
    
    # Verbosity
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    # Quiet mode
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress output except errors'
    )
    
    return parser


def run_extraction(args):
    """Run the extraction based on command line arguments."""
    # Get API key
    api_key = args.api_key or get_api_key()
    
    # Initialize extractor
    try:
        extractor = DocumentExtractor(
            mode=args.mode,
            api_key=api_key,
            model_path=args.model_path,
            device=args.device
        )
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse specified fields
    specified_fields = None
    if args.fields:
        specified_fields = [field.strip() for field in args.fields.split(',')]
    
    # Load JSON schema
    json_schema = None
    if args.schema:
        try:
            with open(args.schema, 'r') as f:
                json_schema = json.load(f)
        except Exception as e:
            print(f"Error loading schema file: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Expand file patterns
    files = expand_file_patterns(args.files)
    
    if not files:
        print("No files found matching the specified patterns.", file=sys.stderr)
        sys.exit(1)
    
    # Process files
    if len(files) == 1:
        # Single file processing
        process_single_file(
            extractor, files[0], args.output_type, specified_fields, 
            json_schema, args.output, args.verbose, args.quiet
        )
    else:
        # Batch processing
        process_batch_files(
            extractor, files, args.output_type, specified_fields,
            json_schema, args.output_dir, args.verbose, args.quiet
        )


def expand_file_patterns(patterns):
    """Expand glob patterns to actual file paths."""
    import glob
    files = []
    for pattern in patterns:
        matched_files = glob.glob(pattern)
        if matched_files:
            files.extend(matched_files)
        else:
            # If no glob matches, treat as literal file path
            if Path(pattern).exists():
                files.append(pattern)
    
    return sorted(set(files))  # Remove duplicates and sort


def process_single_file(
    extractor, file_path, output_type, specified_fields, 
    json_schema, output_file, verbose, quiet
):
    """Process a single file."""
    if verbose and not quiet:
        print(f"Processing: {file_path}")
    
    try:
        result = extractor.extract(
            file_path=file_path,
            output_type=output_type,
            specified_fields=specified_fields,
            json_schema=json_schema
        )
        
        # Output result
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            if not quiet:
                print(f"Results saved to: {output_file}")
        else:
            if not quiet:
                print(json.dumps(result, indent=2))
                
    except (ExtractionError, UnsupportedFileError) as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def process_batch_files(
    extractor, files, output_type, specified_fields,
    json_schema, output_dir, verbose, quiet
):
    """Process multiple files in batch."""
    if verbose and not quiet:
        print(f"Processing {len(files)} files...")
    
    results = {}
    errors = []
    
    for file_path in files:
        try:
            if verbose and not quiet:
                print(f"Processing: {file_path}")
            
            result = extractor.extract(
                file_path=file_path,
                output_type=output_type,
                specified_fields=specified_fields,
                json_schema=json_schema
            )
            
            results[file_path] = result
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            if not quiet:
                print(error_msg, file=sys.stderr)
            errors.append(error_msg)
            results[file_path] = {"error": str(e)}
    
    # Output results
    if output_dir:
        # Save individual files
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for file_path, result in results.items():
            filename = Path(file_path).stem
            output_file = output_path / f"{filename}_extracted.json"
            
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
        
        if not quiet:
            print(f"Results saved to directory: {output_dir}")
            if errors:
                print(f"Completed with {len(errors)} errors.")
    else:
        # Output to stdout
        if not quiet:
            print(json.dumps(results, indent=2))
    
    # Exit with error code if there were errors
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main() 