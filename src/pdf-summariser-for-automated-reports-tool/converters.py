"""
Converters: Image <-> PDF conversions.
"""

import os
from pathlib import Path
from typing import List, Optional, Union, Tuple

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow not installed. Install with: pip install Pillow")

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    raise ImportError("pypdf not installed. Install with: pip install pypdf")


# Standard page sizes (in points, 72 points = 1 inch)
PAGE_SIZES = {
    "letter": (612, 792),
    "a4": (595, 842),
    "a3": (842, 1191),
    "a5": (420, 595),
    "legal": (612, 1008),
}


class ImageToPDF:
    """Convert images to PDF."""
    
    @staticmethod
    def convert(input_files: List[Union[str, Path]], output_file: Union[str, Path],
                page_size: Optional[str] = None, fit: bool = True,
                quality: int = 95) -> str:
        """
        Convert images to a single PDF.
        
        Args:
            input_files: List of image file paths
            output_file: Output PDF path
            page_size: Page size (letter, a4, a3, a5, legal) or None for image size
            fit: Fit image to page (maintain aspect ratio)
            quality: JPEG quality (1-100)
        
        Returns:
            Output file path
        """
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        images = []
        
        for img_file in input_files:
            img_path = Path(img_file)
            if not img_path.exists():
                raise FileNotFoundError(f"Image not found: {img_path}")
            
            img = Image.open(img_path)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if 'A' in img.mode:
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            images.append(img)
        
        if not images:
            raise ValueError("No images provided")
        
        # Determine target size
        if page_size and page_size.lower() in PAGE_SIZES:
            target_size = PAGE_SIZES[page_size.lower()]
        else:
            target_size = None
        
        # Process images
        processed_images = []
        for img in images:
            if target_size and fit:
                # Fit image to page while maintaining aspect ratio
                img = ImageToPDF._fit_to_page(img, target_size)
            elif target_size:
                # Resize to exact page size (may distort)
                img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            processed_images.append(img)
        
        # Save as PDF
        processed_images[0].save(
            str(output),
            "PDF",
            save_all=True,
            append_images=processed_images[1:],
            quality=quality
        )
        
        return str(output)
    
    @staticmethod
    def _fit_to_page(img: Image.Image, page_size: Tuple[int, int]) -> Image.Image:
        """Fit image to page while maintaining aspect ratio."""
        page_width, page_height = page_size
        img_width, img_height = img.size
        
        # Calculate scaling factor
        scale_w = page_width / img_width
        scale_h = page_height / img_height
        scale = min(scale_w, scale_h)
        
        # Calculate new size
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Resize
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create white page and center image
        page = Image.new('RGB', (page_width, page_height), (255, 255, 255))
        offset_x = (page_width - new_width) // 2
        offset_y = (page_height - new_height) // 2
        page.paste(img, (offset_x, offset_y))
        
        return page
    
    @staticmethod
    def supported_formats() -> List[str]:
        """List supported image formats."""
        return ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.webp']


class PDFToImage:
    """Convert PDF pages to images."""
    
    @staticmethod
    def convert(input_file: Union[str, Path], output_dir: Union[str, Path],
                format: str = "png", dpi: int = 200,
                page_numbers: Optional[List[int]] = None) -> List[str]:
        """
        Convert PDF pages to images.
        
        Args:
            input_file: Input PDF path
            output_dir: Output directory
            format: Output format (png, jpg, jpeg, bmp, tiff)
            dpi: Resolution in DPI
            page_numbers: Specific pages to convert (1-indexed), None for all
        
        Returns:
            List of output file paths
        """
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError("pdf2image not installed. Install with: pip install pdf2image")
        
        input_path = Path(input_file)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        
        # Convert
        images = convert_from_path(
            str(input_path),
            dpi=dpi,
            first_page=page_numbers[0] if page_numbers else None,
            last_page=page_numbers[-1] if page_numbers else None,
        )
        
        outputs = []
        for i, img in enumerate(images):
            page_num = page_numbers[i] if page_numbers else i + 1
            output_path = output_dir / f"page_{page_num:04d}.{format.lower()}"
            img.save(str(output_path), format.upper())
            outputs.append(str(output_path))
        
        return outputs
