"""
Processors for different document extraction modes.
"""

from .base_processor import BaseProcessor
from .cloud_processor import CloudProcessor

# Optional imports for CPU and GPU processors
CPUProcessor = None
GPUProcessor = None

try:
    from .cpu_processor import CPUProcessor
except ImportError:
    pass

try:
    from .gpu_processor import GPUProcessor
except ImportError:
    pass

__all__ = [
    "BaseProcessor",
    "CloudProcessor", 
    "CPUProcessor",
    "GPUProcessor",
] 