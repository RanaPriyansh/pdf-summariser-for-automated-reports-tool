"""
Tests for pdfkit.
"""

import pytest
import tempfile
from pathlib import Path

# Create test PDFs
def create_test_pdf(path: str, pages: int = 3):
    """Create a simple test PDF."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    c = canvas.Canvas(path, pagesize=letter)
    
    for i in range(pages):
        c.drawString(100, 700, f"Page {i + 1}")
        c.drawString(100, 680, f"Test content for page {i + 1}")
        c.showPage()
    
    c.save()
    return path


class TestPDFMerger:
    """Test PDF merging."""
    
    def test_merge_basic(self):
        from pdfkit import PDFMerger
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test PDFs
            pdf1 = create_test_pdf(f"{tmpdir}/a.pdf", 2)
            pdf2 = create_test_pdf(f"{tmpdir}/b.pdf", 3)
            
            output = f"{tmpdir}/merged.pdf"
            result = PDFMerger.merge([pdf1, pdf2], output)
            
            assert Path(result).exists()
            assert Path(result).stat().st_size > 0
    
    def test_merge_single(self):
        from pdfkit import PDFMerger
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf1 = create_test_pdf(f"{tmpdir}/single.pdf", 1)
            output = f"{tmpdir}/merged.pdf"
            
            result = PDFMerger.merge([pdf1], output)
            assert Path(result).exists()


class TestPDFSplitter:
    """Test PDF splitting."""
    
    def test_split_by_ranges(self):
        from pdfkit import PDFSplitter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 5)
            output_dir = f"{tmpdir}/output"
            
            splitter = PDFSplitter(pdf)
            outputs = splitter.split_by_ranges(
                {"part1": (1, 2), "part2": (3, 5)},
                output_dir
            )
            
            assert len(outputs) == 2
            assert all(Path(p).exists() for p in outputs)
    
    def test_split_every_n(self):
        from pdfkit import PDFSplitter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 6)
            
            splitter = PDFSplitter(pdf)
            outputs = splitter.split_every_n(2, f"{tmpdir}/output")
            
            assert len(outputs) == 3  # 6 pages / 2 = 3 files
    
    def test_split_single_pages(self):
        from pdfkit import PDFSplitter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 3)
            
            splitter = PDFSplitter(pdf)
            outputs = splitter.split_single_pages(f"{tmpdir}/output")
            
            assert len(outputs) == 3


class TestPDFExtractor:
    """Test PDF extraction."""
    
    def test_extract_pages(self):
        from pdfkit import PDFExtractor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 5)
            output = f"{tmpdir}/extracted.pdf"
            
            extractor = PDFExtractor(pdf)
            result = extractor.extract_pages([1, 3, 5], output)
            
            assert Path(result).exists()
    
    def test_get_text(self):
        from pdfkit import PDFExtractor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 2)
            
            extractor = PDFExtractor(pdf)
            text = extractor.get_text()
            
            assert "Page 1" in text
            assert "Page 2" in text


class TestPDFCompressor:
    """Test PDF compression."""
    
    def test_compress(self):
        from pdfkit import PDFCompressor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 5)
            output = f"{tmpdir}/compressed.pdf"
            
            result = PDFCompressor.compress(pdf, output)
            
            assert Path(result).exists()


class TestPDFRotator:
    """Test PDF rotation."""
    
    def test_rotate_all(self):
        from pdfkit import PDFRotator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 3)
            output = f"{tmpdir}/rotated.pdf"
            
            result = PDFRotator.rotate(pdf, output, 90)
            
            assert Path(result).exists()
    
    def test_rotate_specific_pages(self):
        from pdfkit import PDFRotator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 3)
            output = f"{tmpdir}/rotated.pdf"
            
            result = PDFRotator.rotate(pdf, output, 180, page_numbers=[1, 3])
            
            assert Path(result).exists()


class TestPDFInfo:
    """Test PDF info."""
    
    def test_get_info(self):
        from pdfkit import PDFInfo
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 3)
            
            info = PDFInfo.get_info(pdf)
            
            assert info["pages"] == 3
            assert "size" in info
            assert "encrypted" in info
    
    def test_format_info(self):
        from pdfkit import PDFInfo
        
        info = {
            "filename": "test.pdf",
            "pages": 5,
            "size": 1024 * 1024,
            "encrypted": False,
        }
        
        formatted = PDFInfo.format_info(info)
        
        assert "test.pdf" in formatted
        assert "5" in formatted


class TestPDFEncryptor:
    """Test PDF encryption."""
    
    def test_encrypt_decrypt(self):
        from pdfkit import PDFEncryptor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = create_test_pdf(f"{tmpdir}/input.pdf", 2)
            encrypted = f"{tmpdir}/encrypted.pdf"
            decrypted = f"{tmpdir}/decrypted.pdf"
            
            # Encrypt
            PDFEncryptor.encrypt(pdf, encrypted, "password123")
            assert Path(encrypted).exists()
            
            # Decrypt
            PDFEncryptor.decrypt(encrypted, decrypted, "password123")
            assert Path(decrypted).exists()


class TestImageToPDF:
    """Test image to PDF conversion."""
    
    def test_convert(self):
        from pdfkit import ImageToPDF
        from PIL import Image
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test images
            img1 = Image.new('RGB', (100, 100), color='red')
            img2 = Image.new('RGB', (100, 100), color='blue')
            
            img1.save(f"{tmpdir}/img1.png")
            img2.save(f"{tmpdir}/img2.png")
            
            output = f"{tmpdir}/output.pdf"
            result = ImageToPDF.convert(
                [f"{tmpdir}/img1.png", f"{tmpdir}/img2.png"],
                output
            )
            
            assert Path(result).exists()


class TestCLI:
    """Test CLI commands."""
    
    def test_version(self):
        import subprocess
        result = subprocess.run(["pdfkit", "--version"], capture_output=True, text=True)
        assert "1.0.0" in result.stdout
    
    def test_help(self):
        import subprocess
        result = subprocess.run(["pdfkit", "--help"], capture_output=True, text=True)
        assert "merge" in result.stdout
        assert "split" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
