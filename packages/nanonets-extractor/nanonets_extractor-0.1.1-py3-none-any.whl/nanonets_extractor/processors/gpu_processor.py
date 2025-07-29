"""
GPU processor using local GPU models for document extraction.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

# GPU processing libraries
try:
    import torch
    import torchvision
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification, 
        AutoFeatureExtractor, AutoModelForImageClassification
    )
    import easyocr
    import cv2
    import numpy as np
    from PIL import Image
except ImportError as e:
    print(f"Warning: GPU dependencies not available: {e}")

from .base_processor import BaseProcessor
from .cpu_processor import CPUProcessor  # Fallback to CPU
from ..utils import OutputType, FileType
from ..exceptions import ModelError, ExtractionError


class GPUProcessor(BaseProcessor):
    """
    Processor that uses local GPU models for document extraction.
    Falls back to CPU processing if GPU is not available.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None, **kwargs):
        """
        Initialize the GPU processor.
        
        Args:
            model_path: Path to custom models
            device: GPU device specification (e.g., "cuda:0")
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self.model_path = model_path
        self.device = self._setup_device(device)
        self._models = {}
        self._cpu_fallback = None
        self._initialize_models()
    
    def _setup_device(self, device: Optional[str]) -> str:
        """Setup GPU device."""
        if device:
            return device
        
        # Auto-detect GPU
        if torch.cuda.is_available():
            return "cuda:0"
        else:
            return "cpu"
    
    def _initialize_models(self):
        """Initialize GPU models."""
        try:
            # Check if we're actually using GPU
            if self.device.startswith("cuda") and not torch.cuda.is_available():
                print("Warning: CUDA requested but not available, falling back to CPU")
                self.device = "cpu"
            
            # Initialize models based on device
            if self.device.startswith("cuda"):
                self._initialize_gpu_models()
            else:
                # Fallback to CPU processor
                self._cpu_fallback = CPUProcessor(model_path=self.model_path, **self.config)
                
        except Exception as e:
            print(f"Warning: GPU models initialization failed: {e}")
            self._cpu_fallback = CPUProcessor(model_path=self.model_path, **self.config)
    
    def _initialize_gpu_models(self):
        """Initialize GPU-specific models."""
        try:
            # Initialize EasyOCR with GPU support
            self._models['ocr'] = easyocr.Reader(['en'], gpu=True)
            
            # Initialize text processing models
            if self.model_path and os.path.exists(self.model_path):
                # Load custom models from path
                self._load_custom_models()
            else:
                # Use default models
                self._load_default_models()
                
        except Exception as e:
            print(f"Warning: GPU model initialization failed: {e}")
            # Fallback to CPU
            self._cpu_fallback = CPUProcessor(model_path=self.model_path, **self.config)
    
    def _load_custom_models(self):
        """Load custom models from specified path."""
        try:
            model_dir = Path(self.model_path)
            
            # Load text classification model
            text_model_path = model_dir / "text_classifier"
            if text_model_path.exists():
                self._models['text_classifier'] = AutoModelForSequenceClassification.from_pretrained(
                    str(text_model_path)
                ).to(self.device)
                self._models['text_tokenizer'] = AutoTokenizer.from_pretrained(str(text_model_path))
            
            # Load image classification model
            image_model_path = model_dir / "image_classifier"
            if image_model_path.exists():
                self._models['image_classifier'] = AutoModelForImageClassification.from_pretrained(
                    str(image_model_path)
                ).to(self.device)
                self._models['image_feature_extractor'] = AutoFeatureExtractor.from_pretrained(
                    str(image_model_path)
                )
                
        except Exception as e:
            print(f"Warning: Custom model loading failed: {e}")
    
    def _load_default_models(self):
        """Load default models for basic processing."""
        try:
            # For now, we'll use basic models
            # In a real implementation, you'd load pre-trained document understanding models
            pass
        except Exception as e:
            print(f"Warning: Default model loading failed: {e}")
    
    def is_available(self) -> bool:
        """Check if GPU processor is available."""
        if self.device.startswith("cuda"):
            return torch.cuda.is_available() and len(self._models) > 0
        else:
            return self._cpu_fallback is not None
    
    def extract(
        self,
        file_path: str,
        file_type: FileType,
        output_type: OutputType,
        specified_fields: Optional[List[str]] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract data using GPU processing with CPU fallback.
        
        Args:
            file_path: Path to the document file
            file_type: Type of the file
            output_type: Desired output format
            specified_fields: List of fields to extract
            json_schema: Custom JSON schema
            
        Returns:
            Dictionary containing extracted data
        """
        # If GPU processing is not available, fall back to CPU
        if not self.is_available() or self._cpu_fallback:
            if self._cpu_fallback:
                return self._cpu_fallback.extract(
                    file_path, file_type, output_type, specified_fields, json_schema
                )
            else:
                raise ExtractionError("Neither GPU nor CPU processing is available")
        
        try:
            # GPU processing
            if file_type == FileType.IMAGE:
                extracted_data = self._extract_from_image_gpu(file_path)
            elif file_type == FileType.PDF:
                extracted_data = self._extract_from_pdf_gpu(file_path)
            else:
                # For other file types, use CPU fallback
                return self._cpu_fallback.extract(
                    file_path, file_type, output_type, specified_fields, json_schema
                )
            
            # Format output
            return self._format_output(extracted_data, output_type, specified_fields, json_schema)
            
        except Exception as e:
            # Fallback to CPU on error
            if self._cpu_fallback:
                print(f"GPU processing failed, falling back to CPU: {e}")
                return self._cpu_fallback.extract(
                    file_path, file_type, output_type, specified_fields, json_schema
                )
            else:
                raise ExtractionError(f"GPU extraction failed: {str(e)}")
    
    def _extract_from_image_gpu(self, file_path: str) -> Dict[str, Any]:
        """Extract text from image using GPU-accelerated OCR."""
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ModelError(f"Could not load image: {file_path}")
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # GPU-accelerated OCR
            if 'ocr' in self._models:
                results = self._models['ocr'].readtext(image_rgb)
                text = " ".join([result[1] for result in results])
                confidence = np.mean([result[2] for result in results]) if results else 0.0
            else:
                # Fallback to CPU OCR
                import pytesseract
                text = pytesseract.image_to_string(image_rgb)
                confidence = 0.8  # Placeholder
            
            # Enhanced field extraction using GPU models
            enhanced_data = self._enhance_extraction_with_gpu(text, image_rgb)
            
            return {
                "text": text,
                "file_type": "image",
                "ocr_confidence": confidence,
                "gpu_processed": True,
                **enhanced_data
            }
            
        except Exception as e:
            raise ModelError(f"GPU image processing failed: {e}")
    
    def _extract_from_pdf_gpu(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF with GPU acceleration."""
        try:
            # For now, use CPU PDF extraction but enhance with GPU models
            # In a real implementation, you'd use GPU-accelerated PDF processing
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # Enhance extraction with GPU models
            enhanced_data = self._enhance_extraction_with_gpu(text)
            
            return {
                "text": text,
                "pages": len(pdf_reader.pages),
                "file_type": "pdf",
                "gpu_processed": True,
                **enhanced_data
            }
            
        except Exception as e:
            raise ModelError(f"GPU PDF processing failed: {e}")
    
    def _enhance_extraction_with_gpu(self, text: str, image: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Enhance text extraction using GPU models."""
        enhanced_data = {}
        
        try:
            # Document classification
            if 'text_classifier' in self._models and 'text_tokenizer' in self._models:
                doc_type = self._classify_document_type(text)
                enhanced_data['document_type'] = doc_type
            
            # Field extraction using GPU models
            if 'text_classifier' in self._models:
                extracted_fields = self._extract_fields_with_gpu(text)
                enhanced_data.update(extracted_fields)
            
            # Image analysis if available
            if image is not None and 'image_classifier' in self._models:
                image_features = self._analyze_image_features(image)
                enhanced_data['image_features'] = image_features
                
        except Exception as e:
            print(f"Warning: GPU enhancement failed: {e}")
        
        return enhanced_data
    
    def _classify_document_type(self, text: str) -> str:
        """Classify document type using GPU model."""
        try:
            if 'text_classifier' in self._models and 'text_tokenizer' in self._models:
                # Tokenize text
                inputs = self._models['text_tokenizer'](
                    text[:512],  # Limit length
                    return_tensors="pt",
                    truncation=True,
                    padding=True
                ).to(self.device)
                
                # Get prediction
                with torch.no_grad():
                    outputs = self._models['text_classifier'](**inputs)
                    predictions = torch.softmax(outputs.logits, dim=-1)
                    predicted_class = torch.argmax(predictions, dim=-1).item()
                
                # Map to document types (this would depend on your model)
                doc_types = ["invoice", "receipt", "contract", "form", "other"]
                return doc_types[predicted_class] if predicted_class < len(doc_types) else "other"
            
        except Exception as e:
            print(f"Warning: Document classification failed: {e}")
        
        return "unknown"
    
    def _extract_fields_with_gpu(self, text: str) -> Dict[str, Any]:
        """Extract fields using GPU models."""
        # This is a placeholder implementation
        # In a real implementation, you'd use fine-tuned models for field extraction
        return {}
    
    def _analyze_image_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image features using GPU models."""
        try:
            if 'image_classifier' in self._models and 'image_feature_extractor' in self._models:
                # Preprocess image
                inputs = self._models['image_feature_extractor'](
                    Image.fromarray(image), 
                    return_tensors="pt"
                ).to(self.device)
                
                # Get features
                with torch.no_grad():
                    outputs = self._models['image_classifier'](**inputs)
                    features = outputs.logits.cpu().numpy()
                
                return {
                    "feature_vector": features.tolist(),
                    "num_features": features.shape[-1]
                }
                
        except Exception as e:
            print(f"Warning: Image feature analysis failed: {e}")
        
        return {}
    
    def _format_output(
        self,
        extracted_data: Dict[str, Any],
        output_type: OutputType,
        specified_fields: Optional[List[str]] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format extracted data according to output type."""
        # Use CPU processor's formatting logic
        if self._cpu_fallback:
            return self._cpu_fallback._format_output(
                extracted_data, output_type, specified_fields, json_schema
            )
        else:
            # Basic formatting
            return extracted_data
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get GPU processor capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update({
            "device": self.device,
            "gpu_available": torch.cuda.is_available() if 'torch' in globals() else False,
            "models_loaded": len(self._models),
            "cpu_fallback_available": self._cpu_fallback is not None,
            "supports_gpu_acceleration": self.device.startswith("cuda"),
            "offline": True,
            "requires_internet": False,
        })
        return capabilities 