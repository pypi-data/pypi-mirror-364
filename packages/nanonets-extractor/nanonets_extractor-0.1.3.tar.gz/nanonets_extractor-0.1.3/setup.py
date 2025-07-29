from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nanonets-extractor",
    version="0.1.3",
    author="Nanonets",
    author_email="support@nanonets.com",
    description="A unified document extraction library supporting local CPU, GPU, and cloud processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nanonets/document-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "Pillow>=8.0.0",
        "PyPDF2>=2.0.0",
        "python-docx>=0.8.11",
        "openpyxl>=3.0.0",
        "pandas>=1.3.0",
        "pydantic>=1.9.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "cpu": [
            "numpy>=1.21.0,<2.0.0",
            "opencv-python>=4.5.0",
            "pytesseract>=0.3.8",
            "easyocr>=1.6.0",
        ],
        "gpu": [
            "numpy>=1.21.0,<2.0.0",
            "torch>=1.12.0",
            "torchvision>=0.13.0",
            "transformers>=4.20.0",
            "opencv-python>=4.5.0",
        ],
        "all": [
            "numpy>=1.21.0,<2.0.0",
            "opencv-python>=4.5.0",
            "pytesseract>=0.3.8",
            "easyocr>=1.6.0",
            "torch>=1.12.0",
            "torchvision>=0.13.0",
            "transformers>=4.20.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "nanonets-extractor=nanonets_extractor.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "nanonets_extractor": ["models/*", "configs/*"],
    },
) 