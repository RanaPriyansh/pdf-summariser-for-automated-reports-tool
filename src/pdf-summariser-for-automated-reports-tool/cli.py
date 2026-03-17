"""
Command-line interface for pdfkit.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Optional

from .core import (
    PDFMerger, PDFSplitter, PDFExtractor, PDFCompressor,
    PDFRotator, PDFWatermarker, PDFEncryptor, PDFInfo
)
from .converters import ImageToPDF, PDFToImage


def main():
    parser = argparse.ArgumentParser(
        prog="pdfkit",
        description="📄 pdfkit — Free PDF Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdfkit merge a.pdf b.pdf -o combined.pdf
  pdfkit split input.pdf --pages 1-5,8,10-12 -o parts/
  pdfkit extract input.pdf --pages 3,5,7 -o extracted.pdf
  pdfkit compress input.pdf -o smaller.pdf
  pdfkit rotate input.pdf --angle 90 -o rotated.pdf
  pdfkit text input.pdf
  pdfkit img2pdf *.jpg -o photos.pdf
  pdfkit watermark input.pdf --text "DRAFT" -o marked.pdf
  pdfkit encrypt input.pdf --password secret -o protected.pdf
  pdfkit info input.pdf
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # === MERGE ===
    merge_parser = subparsers.add_parser("merge", help="Merge multiple PDFs")
    merge_parser.add_argument("files", nargs="+", help="PDF files to merge")
    merge_parser.add_argument("-o", "--output", required=True, help="Output file")
    merge_parser.add_argument("--bookmark", action="store_true", help="Add bookmarks")
    
    # === SPLIT ===
    split_parser = subparsers.add_parser("split", help="Split PDF into parts")
    split_parser.add_argument("input", help="Input PDF file")
    split_parser.add_argument("-o", "--output", required=True, help="Output directory")
    split_parser.add_argument("--pages", help="Page ranges (e.g., 1-5,8,10-12)")
    split_parser.add_argument("--every", type=int, help="Split every N pages")
    split_parser.add_argument("--single", action="store_true", help="Split into single pages")
    split_parser.add_argument("--prefix", default="part", help="Output file prefix")
    
    # === EXTRACT ===
    extract_parser = subparsers.add_parser("extract", help="Extract pages")
    extract_parser.add_argument("input", help="Input PDF file")
    extract_parser.add_argument("-o", "--output", required=True, help="Output file")
    extract_parser.add_argument("--pages", required=True, help="Pages to extract (e.g., 1,3,5-8)")
    
    # === COMPRESS ===
    compress_parser = subparsers.add_parser("compress", help="Compress PDF")
    compress_parser.add_argument("input", help="Input PDF file")
    compress_parser.add_argument("-o", "--output", required=True, help="Output file")
    compress_parser.add_argument("--quality", choices=["low", "medium", "high"], 
                                default="medium", help="Compression quality")
    
    # === ROTATE ===
    rotate_parser = subparsers.add_parser("rotate", help="Rotate pages")
    rotate_parser.add_argument("input", help="Input PDF file")
    rotate_parser.add_argument("-o", "--output", required=True, help="Output file")
    rotate_parser.add_argument("--angle", type=int, choices=[90, 180, 270], required=True)
    rotate_parser.add_argument("--pages", help="Pages to rotate (e.g., 1,3,5), default: all")
    
    # === TEXT ===
    text_parser = subparsers.add_parser("text", help="Extract text from PDF")
    text_parser.add_argument("input", help="Input PDF file")
    text_parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    text_parser.add_argument("--pages", help="Pages to extract (e.g., 1-5)")
    
    # === IMG2PDF ===
    img2pdf_parser = subparsers.add_parser("img2pdf", help="Convert images to PDF")
    img2pdf_parser.add_argument("images", nargs="+", help="Image files")
    img2pdf_parser.add_argument("-o", "--output", required=True, help="Output PDF")
    img2pdf_parser.add_argument("--page-size", choices=["letter", "a4", "a3", "a5", "legal"],
                               help="Page size")
    img2pdf_parser.add_argument("--no-fit", action="store_true", help="Don't fit to page")
    
    # === PDF2IMG ===
    pdf2img_parser = subparsers.add_parser("pdf2img", help="Convert PDF to images")
    pdf2img_parser.add_argument("input", help="Input PDF file")
    pdf2img_parser.add_argument("-o", "--output", required=True, help="Output directory")
    pdf2img_parser.add_argument("--format", default="png", choices=["png", "jpg", "jpeg", "bmp", "tiff"])
    pdf2img_parser.add_argument("--dpi", type=int, default=200, help="Resolution (default: 200)")
    pdf2img_parser.add_argument("--pages", help="Pages to convert (e.g., 1-5)")
    
    # === WATERMARK ===
    watermark_parser = subparsers.add_parser("watermark", help="Add watermark")
    watermark_parser.add_argument("input", help="Input PDF file")
    watermark_parser.add_argument("-o", "--output", required=True, help="Output file")
    watermark_parser.add_argument("--text", help="Watermark text")
    watermark_parser.add_argument("--stamp", help="Stamp PDF file")
    watermark_parser.add_argument("--opacity", type=float, default=0.3, help="Opacity (0-1)")
    
    # === ENCRYPT ===
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt PDF")
    encrypt_parser.add_argument("input", help="Input PDF file")
    encrypt_parser.add_argument("-o", "--output", required=True, help="Output file")
    encrypt_parser.add_argument("--password", required=True, help="Password")
    
    # === DECRYPT ===
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt PDF")
    decrypt_parser.add_argument("input", help="Input PDF file")
    decrypt_parser.add_argument("-o", "--output", required=True, help="Output file")
    decrypt_parser.add_argument("--password", required=True, help="Password")
    
    # === INFO ===
    info_parser = subparsers.add_parser("info", help="Show PDF information")
    info_parser.add_argument("input", help="Input PDF file")
    info_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Version
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "merge":
            cmd_merge(args)
        elif args.command == "split":
            cmd_split(args)
        elif args.command == "extract":
            cmd_extract(args)
        elif args.command == "compress":
            cmd_compress(args)
        elif args.command == "rotate":
            cmd_rotate(args)
        elif args.command == "text":
            cmd_text(args)
        elif args.command == "img2pdf":
            cmd_img2pdf(args)
        elif args.command == "pdf2img":
            cmd_pdf2img(args)
        elif args.command == "watermark":
            cmd_watermark(args)
        elif args.command == "encrypt":
            cmd_encrypt(args)
        elif args.command == "decrypt":
            cmd_decrypt(args)
        elif args.command == "info":
            cmd_info(args)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def parse_page_ranges(pages_str: str) -> List[int]:
    """Parse page range string like '1-5,8,10-12' into list of page numbers."""
    pages = []
    for part in pages_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))
    return sorted(set(pages))


def cmd_merge(args):
    output = PDFMerger.merge(args.files, args.output, add_bookmarks=args.bookmark)
    print(f"Merged {len(args.files)} files -> {output}", file=sys.stderr)


def cmd_split(args):
    splitter = PDFSplitter(args.input)
    
    if args.pages:
        # Parse page ranges and split
        ranges = {}
        for i, part in enumerate(args.pages.split(',')):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                ranges[f"{args.prefix}_{i+1}"] = (start, end)
            else:
                p = int(part)
                ranges[f"{args.prefix}_{i+1}"] = (p, p)
        outputs = splitter.split_by_ranges(ranges, args.output)
    elif args.every:
        outputs = splitter.split_every_n(args.every, args.output, args.prefix)
    elif args.single:
        outputs = splitter.split_single_pages(args.output, args.prefix)
    else:
        print("ERROR: Specify --pages, --every, or --single", file=sys.stderr)
        sys.exit(1)
    
    print(f"Split into {len(outputs)} files -> {args.output}/", file=sys.stderr)


def cmd_extract(args):
    pages = parse_page_ranges(args.pages)
    extractor = PDFExtractor(args.input)
    output = extractor.extract_pages(pages, args.output)
    print(f"Extracted {len(pages)} pages -> {output}", file=sys.stderr)


def cmd_compress(args):
    output = PDFCompressor.compress(args.input, args.output, quality=args.quality)
    
    # Show compression results
    input_size = Path(args.input).stat().st_size
    output_size = Path(args.output).stat().st_size
    reduction = (1 - output_size / input_size) * 100
    
    print(f"Compressed: {_format_size(input_size)} -> {_format_size(output_size)} "
          f"({reduction:.1f}% reduction)", file=sys.stderr)


def cmd_rotate(args):
    pages = parse_page_ranges(args.pages) if args.pages else None
    output = PDFRotator.rotate(args.input, args.output, args.angle, pages)
    print(f"Rotated {args.angle}° -> {output}", file=sys.stderr)


def cmd_text(args):
    pages = parse_page_ranges(args.pages) if args.pages else None
    extractor = PDFExtractor(args.input)
    text = extractor.get_text(pages)
    
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(text)


def cmd_img2pdf(args):
    output = ImageToPDF.convert(
        args.images, args.output,
        page_size=args.page_size,
        fit=not args.no_fit
    )
    print(f"Converted {len(args.images)} images -> {output}", file=sys.stderr)


def cmd_pdf2img(args):
    pages = parse_page_ranges(args.pages) if args.pages else None
    outputs = PDFToImage.convert(
        args.input, args.output,
        format=args.format,
        dpi=args.dpi,
        page_numbers=pages
    )
    print(f"Converted {len(outputs)} pages -> {args.output}/", file=sys.stderr)


def cmd_watermark(args):
    if args.text:
        output = PDFWatermarker.add_text_watermark(
            args.input, args.output,
            text=args.text,
            opacity=args.opacity
        )
    elif args.stamp:
        output = PDFWatermarker.add_stamp_watermark(
            args.input, args.output,
            args.stamp
        )
    else:
        print("ERROR: Specify --text or --stamp", file=sys.stderr)
        sys.exit(1)
    
    print(f"Watermarked -> {output}", file=sys.stderr)


def cmd_encrypt(args):
    output = PDFEncryptor.encrypt(args.input, args.output, args.password)
    print(f"Encrypted -> {output}", file=sys.stderr)


def cmd_decrypt(args):
    output = PDFEncryptor.decrypt(args.input, args.output, args.password)
    print(f"Decrypted -> {output}", file=sys.stderr)


def cmd_info(args):
    info = PDFInfo.get_info(args.input)
    
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print(PDFInfo.format_info(info))


def _format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


if __name__ == "__main__":
    main()
