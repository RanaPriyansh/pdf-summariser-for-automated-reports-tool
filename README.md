# PDF summariser for automated reports

**Stop paying for Adobe Acrobat, SmallPDF, and iLovePDF.**

pdfkit is a 100% free, offline CLI tool for:
- **Merge** multiple PDFs into one
- **Split** PDFs by page ranges
- **Extract** specific pages
- **Compress** PDF file sizes
- **Rotate** pages
- **Extract text** from PDFs
- **Images → PDF** conversion
- **PDF → Images** conversion
- **Watermark** PDFs
- **Encrypt/Decrypt** with passwords
- **Metadata** viewing/editing

Everything runs **locally**. No uploads. No limits. No watermarks on your watermarks.

## Why?

| Service | Free Tier | pdfkit |
|---------|-----------|--------|
| SmallPDF | 2 tasks/day | Unlimited forever |
| iLovePDF | Limited, ads | No ads, no limits |
| Adobe Acrobat | $23/month | $0 forever |
| ILovePDF API | 250 files/month | Unlimited forever |
| PDF24 | Desktop only | CLI + Python API |

## Quick Start

```bash
pip install pdfkit

# PDF summariser for automated reports
pdfkit merge file1.pdf file2.pdf -o combined.pdf

# PDF summariser for automated reports
pdfkit split input.pdf --pages 1-5,8,10-12 -o output/

# PDF summariser for automated reports
pdfkit extract input.pdf --pages 3,5,7 -o extracted.pdf

# PDF summariser for automated reports
pdfkit compress input.pdf -o compressed.pdf --quality medium

# PDF summariser for automated reports
pdfkit rotate input.pdf --angle 90 --pages all -o rotated.pdf

# PDF summariser for automated reports
pdfkit text input.pdf

# PDF summariser for automated reports
pdfkit img2pdf *.jpg -o photos.pdf

# PDF summariser for automated reports
pdfkit pdf2img input.pdf -o output/ --format png

# PDF summariser for automated reports
pdfkit watermark input.pdf --text "DRAFT" -o watermarked.pdf

# PDF summariser for automated reports
pdfkit encrypt input.pdf --password secret123 -o protected.pdf

# PDF summariser for automated reports
pdfkit info input.pdf
```

## Features

- **100% offline** — No data ever leaves your machine
- **No limits** — Process as many files as you want
- **No watermarks** — Unlike "free" online tools
- **Fast** — Pure Python, no cloud roundtrips
- **Scriptable** — Perfect for automation and agents
- **Cross-platform** — Linux, macOS, Windows

## Commands

### merge — Combine multiple PDFs

```bash
pdfkit merge a.pdf b.pdf c.pdf -o combined.pdf
pdfkit merge *.pdf -o all-in-one.pdf --bookmark
```

### split — Split PDF into parts

```bash
# PDF summariser for automated reports
pdfkit split input.pdf --pages 1-5,6-10 -o parts/

# PDF summariser for automated reports
pdfkit split input.pdf --every 2 -o chunks/

# PDF summariser for automated reports
pdfkit split input.pdf --single -o pages/
```

### extract — Extract specific pages

```bash
pdfkit extract input.pdf --pages 1,3,5-8 -o extracted.pdf
```

### compress — Reduce file size

```bash
pdfkit compress input.pdf -o smaller.pdf
pdfkit compress input.pdf -o small.pdf --quality low    # Aggressive
pdfkit compress input.pdf -o small.pdf --quality high   # Minimal
```

### rotate — Rotate pages

```bash
pdfkit rotate input.pdf --angle 90 -o rotated.pdf
pdfkit rotate input.pdf --angle 180 --pages 1,3,5 -o partial.pdf
```

### text — Extract text content

```bash
pdfkit text input.pdf                    # Print to stdout
pdfkit text input.pdf -o text.txt        # Save to file
pdfkit text input.pdf --pages 1-5        # Specific pages
```

### img2pdf — Convert images to PDF

```bash
pdfkit img2pdf photo1.jpg photo2.png -o photos.pdf
pdfkit img2pdf scans/*.png -o document.pdf --page-size a4
```

### pdf2img — Convert PDF to images

```bash
pdfkit pdf2img input.pdf -o output/
pdfkit pdf2img input.pdf -o output/ --format jpg --dpi 300
```

### watermark — Add watermark

```bash
pdfkit watermark input.pdf --text "CONFIDENTIAL" -o marked.pdf
pdfkit watermark input.pdf --stamp watermark.pdf -o marked.pdf
pdfkit watermark input.pdf --text "DRAFT" --opacity 0.3 -o marked.pdf
```

### encrypt/decrypt — Password protection

```bash
pdfkit encrypt input.pdf --password secret -o protected.pdf
pdfkit decrypt protected.pdf --password secret -o unlocked.pdf
```

### info — View PDF metadata

```bash
pdfkit info input.pdf
# PDF summariser for automated reports
# PDF summariser for automated reports
# PDF summariser for automated reports
# PDF summariser for automated reports
# PDF summariser for automated reports
# PDF summariser for automated reports
```

## Python API

```python
from pdfkit import PDFMerger, PDFSplitter, PDFExtractor

# PDF summariser for automated reports
merger = PDFMerger()
merger.merge(["a.pdf", "b.pdf"], "combined.pdf")

# PDF summariser for automated reports
splitter = PDFSplitter("input.pdf")
splitter.split_by_ranges({"part1": (1, 5), "part2": (6, 10)}, "output/")

# PDF summariser for automated reports
extractor = PDFExtractor("input.pdf")
text = extractor.get_text()
print(text)
```

## Use Cases

### For Developers
- Automate document processing in CI/CD
- Batch process reports
- Generate documentation PDFs

### For AI Agents
- Extract text from PDFs for LLM processing
- Split large PDFs for context windows
- Compress PDFs before sharing

### For Everyone
- Merge scanned pages into one document
- Add watermarks to contracts
- Protect sensitive documents with passwords
- Convert images to PDF for submissions

## System Requirements

- Python 3.8+
- ~10MB disk space
- No external dependencies (pure Python with pypdf)

## Contributing

We need help with:
- [ ] GUI version
- [ ] Batch mode improvements
- [ ] More compression options
- [ ] OCR integration
- [ ] Form filling

## License

MIT — Free forever. No catch.

---

**Built because PDF manipulation shouldn't cost money.**
