"""
pdfkit — Free PDF Toolkit
Merge, split, extract, compress, rotate, watermark, encrypt PDFs.
"""

__version__ = "1.0.0"

from .core import (
    PDFMerger,
    PDFSplitter,
    PDFExtractor,
    PDFCompressor,
    PDFRotator,
    PDFWatermarker,
    PDFEncryptor,
    PDFInfo,
)
from .converters import ImageToPDF, PDFToImage
from .cli import main

__all__ = [
    "PDFMerger",
    "PDFSplitter", 
    "PDFExtractor",
    "PDFCompressor",
    "PDFRotator",
    "PDFWatermarker",
    "PDFEncryptor",
    "PDFInfo",
    "ImageToPDF",
    "PDFToImage",
    "main",
]
