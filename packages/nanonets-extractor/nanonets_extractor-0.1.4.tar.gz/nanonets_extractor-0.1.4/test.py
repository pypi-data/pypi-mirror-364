from nanonets_extractor import DocumentExtractor

# Initialize with cloud processing (requires API key)
extractor = DocumentExtractor(
    mode="cloud",
    api_key="1d609a62-f813-11ef-b897-8a0398946c58"  # Get your FREE API key from https://app.nanonets.com/#/keys
)

# Extract data from a document
result = extractor.extract(
    file_path="sample.png",
    output_type="flat-json"
)

print(result)