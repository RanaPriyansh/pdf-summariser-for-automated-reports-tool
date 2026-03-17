"""
Core PDF operations: merge, split, extract, compress, rotate, watermark, encrypt.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Union
from dataclasses import dataclass

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    raise ImportError("pypdf not installed. Install with: pip install pypdf")


@dataclass
class PageInfo:
    """Information about a PDF page."""
    page_number: int
    width: float
    height: float
    rotation: int


@dataclass
class PDFMetadata:
    """PDF metadata."""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None


class PDFMerger:
    """Merge multiple PDFs into one."""
    
    @staticmethod
    def merge(input_files: List[Union[str, Path]], output_file: Union[str, Path],
              add_bookmarks: bool = False) -> str:
        """
        Merge multiple PDFs into a single file.
        
        Args:
            input_files: List of PDF file paths
            output_file: Output file path
            add_bookmarks: Add bookmarks for each merged file
        
        Returns:
            Output file path
        """
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        writer = PdfWriter()
        
        for pdf_file in input_files:
            pdf_path = Path(pdf_file)
            if not pdf_path.exists():
                raise FileNotFoundError(f"File not found: {pdf_path}")
            
            reader = PdfReader(str(pdf_path))
            
            for page in reader.pages:
                writer.add_page(page)
            
            # Add outline/bookmark for this file
            if add_bookmarks and reader.pages:
                writer.add_outline_item(pdf_path.stem, len(writer.pages) - len(reader.pages))
        
        # Copy metadata from first file
        if input_files:
            first_reader = PdfReader(str(input_files[0]))
            if first_reader.metadata:
                writer.add_metadata({
                    k: v for k, v in first_reader.metadata.items() 
                    if v is not None
                })
        
        with open(output, 'wb') as f:
            writer.write(f)
        
        return str(output)


class PDFSplitter:
    """Split PDFs into multiple files."""
    
    def __init__(self, input_file: Union[str, Path]):
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"File not found: {self.input_file}")
        self.reader = PdfReader(str(self.input_file))
        self.total_pages = len(self.reader.pages)
    
    def split_by_ranges(self, ranges: Dict[str, Tuple[int, int]], 
                        output_dir: Union[str, Path]) -> List[str]:
        """
        Split PDF by page ranges.
        
        Args:
            ranges: Dict mapping output name to (start, end) page numbers (1-indexed)
            output_dir: Output directory
        
        Returns:
            List of output file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        outputs = []
        for name, (start, end) in ranges.items():
            writer = PdfWriter()
            
            # Convert to 0-indexed
            for page_num in range(start - 1, min(end, self.total_pages)):
                writer.add_page(self.reader.pages[page_num])
            
            output_path = output_dir / f"{name}.pdf"
            with open(output_path, 'wb') as f:
                writer.write(f)
            outputs.append(str(output_path))
        
        return outputs
    
    def split_every_n(self, n: int, output_dir: Union[str, Path],
                      prefix: str = "part") -> List[str]:
        """
        Split PDF every N pages.
        
        Args:
            n: Number of pages per split
            output_dir: Output directory
            prefix: Output file prefix
        
        Returns:
            List of output file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        outputs = []
        part = 1
        
        for start in range(0, self.total_pages, n):
            writer = PdfWriter()
            end = min(start + n, self.total_pages)
            
            for page_num in range(start, end):
                writer.add_page(self.reader.pages[page_num])
            
            output_path = output_dir / f"{prefix}_{part:03d}.pdf"
            with open(output_path, 'wb') as f:
                writer.write(f)
            outputs.append(str(output_path))
            part += 1
        
        return outputs
    
    def split_single_pages(self, output_dir: Union[str, Path],
                           prefix: str = "page") -> List[str]:
        """Split PDF into individual pages."""
        return self.split_every_n(1, output_dir, prefix)


class PDFExtractor:
    """Extract content from PDFs."""
    
    def __init__(self, input_file: Union[str, Path]):
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"File not found: {self.input_file}")
        self.reader = PdfReader(str(self.input_file))
    
    def extract_pages(self, page_numbers: List[int],
                      output_file: Union[str, Path]) -> str:
        """
        Extract specific pages to a new PDF.
        
        Args:
            page_numbers: List of page numbers (1-indexed)
            output_file: Output file path
        
        Returns:
            Output file path
        """
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        writer = PdfWriter()
        
        for page_num in page_numbers:
            if 1 <= page_num <= len(self.reader.pages):
                writer.add_page(self.reader.pages[page_num - 1])
        
        with open(output, 'wb') as f:
            writer.write(f)
        
        return str(output)
    
    def get_text(self, page_numbers: Optional[List[int]] = None) -> str:
        """
        Extract text from PDF.
        
        Args:
            page_numbers: Specific pages to extract (1-indexed), None for all
        
        Returns:
            Extracted text
        """
        pages = page_numbers or list(range(1, len(self.reader.pages) + 1))
        text_parts = []
        
        for page_num in pages:
            if 1 <= page_num <= len(self.reader.pages):
                page = self.reader.pages[page_num - 1]
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- Page {page_num} ---\n{text}")
        
        return "\n\n".join(text_parts)


class PDFCompressor:
    """Compress PDF files."""
    
    @staticmethod
    def compress(input_file: Union[str, Path], output_file: Union[str, Path],
                 quality: str = "medium") -> str:
        """
        Compress a PDF file.
        
        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            quality: Compression level (low, medium, high)
        
        Returns:
            Output file path
        """
        input_path = Path(input_file)
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Apply compression based on quality
        for page in writer.pages:
            if quality in ["low", "medium"]:
                page.compress_content_streams()
        
        # Copy metadata
        if reader.metadata:
            writer.add_metadata({
                k: v for k, v in reader.metadata.items() 
                if v is not None
            })
        
        with open(output, 'wb') as f:
            writer.write(f)
        
        return str(output)


class PDFRotator:
    """Rotate PDF pages."""
    
    @staticmethod
    def rotate(input_file: Union[str, Path], output_file: Union[str, Path],
               angle: int, page_numbers: Optional[List[int]] = None) -> str:
        """
        Rotate pages in a PDF.
        
        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            angle: Rotation angle (90, 180, 270)
            page_numbers: Pages to rotate (1-indexed), None for all
        
        Returns:
            Output file path
        """
        input_path = Path(input_file)
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        
        for i, page in enumerate(reader.pages):
            if page_numbers is None or (i + 1) in page_numbers:
                page.rotate(angle)
            writer.add_page(page)
        
        with open(output, 'wb') as f:
            writer.write(f)
        
        return str(output)


class PDFWatermarker:
    """Add watermarks to PDFs."""
    
    @staticmethod
    def add_text_watermark(input_file: Union[str, Path], output_file: Union[str, Path],
                           text: str, opacity: float = 0.3,
                           font_size: int = 50, color: str = "gray") -> str:
        """
        Add text watermark to all pages.
        
        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            text: Watermark text
            opacity: Watermark opacity (0-1)
            font_size: Font size
            color: Text color
        
        Returns:
            Output file path
        """
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        input_path = Path(input_file)
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        
        for page in reader.pages:
            # Get page dimensions
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Create watermark PDF
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            # Set transparency
            can.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacity)
            can.setFont("Helvetica-Bold", font_size)
            
            # Rotate and draw text
            can.saveState()
            can.translate(page_width / 2, page_height / 2)
            can.rotate(45)
            can.drawCentredString(0, 0, text)
            can.restoreState()
            
            can.save()
            packet.seek(0)
            
            # Merge watermark with page
            watermark = PdfReader(packet)
            page.merge_page(watermark.pages[0])
            writer.add_page(page)
        
        with open(output, 'wb') as f:
            writer.write(f)
        
        return str(output)
    
    @staticmethod
    def add_stamp_watermark(input_file: Union[str, Path], output_file: Union[str, Path],
                            stamp_file: Union[str, Path]) -> str:
        """
        Add stamp/watermark from another PDF.
        
        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            stamp_file: Stamp PDF path (single page)
        
        Returns:
            Output file path
        """
        input_path = Path(input_file)
        stamp_path = Path(stamp_file)
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        reader = PdfReader(str(input_path))
        stamp_reader = PdfReader(str(stamp_path))
        writer = PdfWriter()
        
        stamp_page = stamp_reader.pages[0]
        
        for page in reader.pages:
            page.merge_page(stamp_page)
            writer.add_page(page)
        
        with open(output, 'wb') as f:
            writer.write(f)
        
        return str(output)


class PDFEncryptor:
    """Encrypt and decrypt PDFs."""
    
    @staticmethod
    def encrypt(input_file: Union[str, Path], output_file: Union[str, Path],
                password: str, owner_password: Optional[str] = None) -> str:
        """
        Encrypt a PDF with password.
        
        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            password: User password (required to open)
            owner_password: Owner password (optional, for permissions)
        
        Returns:
            Output file path
        """
        input_path = Path(input_file)
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        # Copy metadata
        if reader.metadata:
            writer.add_metadata({
                k: v for k, v in reader.metadata.items() 
                if v is not None
            })
        
        writer.encrypt(
            user_password=password,
            owner_password=owner_password or password,
        )
        
        with open(output, 'wb') as f:
            writer.write(f)
        
        return str(output)
    
    @staticmethod
    def decrypt(input_file: Union[str, Path], output_file: Union[str, Path],
                password: str) -> str:
        """
        Decrypt a PDF.
        
        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            password: Password to decrypt
        
        Returns:
            Output file path
        """
        input_path = Path(input_file)
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        reader = PdfReader(str(input_path))
        
        if reader.is_encrypted:
            if not reader.decrypt(password):
                raise ValueError("Incorrect password")
        
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        with open(output, 'wb') as f:
            writer.write(f)
        
        return str(output)


class PDFInfo:
    """Get PDF information."""
    
    @staticmethod
    def get_info(input_file: Union[str, Path]) -> Dict:
        """
        Get PDF metadata and info.
        
        Args:
            input_file: Input PDF path
        
        Returns:
            Dict with PDF information
        """
        input_path = Path(input_file)
        reader = PdfReader(str(input_path))
        
        info = {
            "filename": input_path.name,
            "pages": len(reader.pages),
            "size": input_path.stat().st_size,
            "encrypted": reader.is_encrypted,
        }
        
        # Metadata
        if reader.metadata:
            info["title"] = reader.metadata.get("/Title", "") or ""
            info["author"] = reader.metadata.get("/Author", "") or ""
            info["subject"] = reader.metadata.get("/Subject", "") or ""
            info["creator"] = reader.metadata.get("/Creator", "") or ""
            info["producer"] = reader.metadata.get("/Producer", "") or ""
            info["creation_date"] = str(reader.metadata.get("/CreationDate", ""))
            info["modification_date"] = str(reader.metadata.get("/ModDate", ""))
        
        # Page info
        if reader.pages:
            first_page = reader.pages[0]
            info["page_width"] = float(first_page.mediabox.width)
            info["page_height"] = float(first_page.mediabox.height)
        
        return info
    
    @staticmethod
    def format_info(info: Dict) -> str:
        """Format info dict as readable string."""
        lines = []
        lines.append(f"File: {info['filename']}")
        lines.append(f"Pages: {info['pages']}")
        lines.append(f"Size: {PDFInfo._format_size(info['size'])}")
        lines.append(f"Encrypted: {'Yes' if info['encrypted'] else 'No'}")
        
        if info.get('title'):
            lines.append(f"Title: {info['title']}")
        if info.get('author'):
            lines.append(f"Author: {info['author']}")
        if info.get('page_width') and info.get('page_height'):
            lines.append(f"Page size: {info['page_width']:.0f} x {info['page_height']:.0f} pts")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
