#!/usr/bin/env python3
"""
EPUB Thumbnail Extractor

Extracts cover images from EPUB files and saves them as PNG thumbnails.
Usage: python extract_epub_thumbnail.py <epub_file_path>
"""

import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
import io
import os, sys


def find_cover_image_in_opf(opf_content: str, opf_dir: Path) -> str | None:
    """Parse OPF file to find cover image path."""
    try:
        root = ET.fromstring(opf_content)

        # Define namespaces commonly used in EPUB OPF files
        namespaces = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }

        # Method 1: Look for meta tag with name="cover"
        for meta in root.findall('.//opf:meta[@name="cover"]', namespaces):
            cover_id = meta.get('content')
            if cover_id:
                # Find the item with this ID
                item = root.find(f'.//opf:item[@id="{cover_id}"]', namespaces)
                if item is not None:
                    href = item.get('href')
                    if href:
                        return str(opf_dir / href)

        # Method 2: Look for item with properties="cover-image"
        for item in root.findall('.//opf:item[@properties="cover-image"]', namespaces):
            href = item.get('href')
            if href:
                return str(opf_dir / href)

        # Method 3: Look for items with common cover image names
        for item in root.findall('.//opf:item', namespaces):
            href = item.get('href', '').lower()
            media_type = item.get('media-type', '')
            if ('cover' in href or 'cover' in item.get('id', '').lower()) and 'image' in media_type:
                return str(opf_dir / item.get('href'))

        # Method 4: First image in manifest
        item = root.find('.//opf:item[starts-with(@media-type, "image/")]', namespaces)
        if item is not None:
            href = item.get('href')
            if href:
                return str(opf_dir / href)

    except ET.ParseError as e:
        print(f"Warning: Could not parse OPF file: {e}")

    return None


def extract_cover_from_epub(epub_path: Path) -> Image.Image | None:
    """Extract cover image from EPUB file."""
    try:
        with zipfile.ZipFile(epub_path, 'r') as epub_zip:
            # First, find the OPF file location from container.xml
            container_xml = epub_zip.read('META-INF/container.xml').decode('utf-8')
            container_root = ET.fromstring(container_xml)

            # Find the OPF file path
            rootfile = container_root.find('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile')
            if rootfile is None:
                print("Error: Could not find rootfile in container.xml")
                return None

            opf_path = rootfile.get('full-path')
            if not opf_path:
                print("Error: OPF path not found in container.xml")
                return None

            # Read and parse the OPF file
            opf_content = epub_zip.read(opf_path).decode('utf-8')
            opf_dir = Path(opf_path).parent

            # Find cover image path
            cover_path = find_cover_image_in_opf(opf_content, opf_dir)

            if not cover_path:
                print("Warning: Could not find cover image in OPF manifest, trying common locations...")
                # Try common cover image locations
                common_paths = [
                    'cover.jpg', 'cover.jpeg', 'cover.png',
                    'images/cover.jpg', 'images/cover.jpeg', 'images/cover.png',
                    'OEBPS/cover.jpg', 'OEBPS/cover.jpeg', 'OEBPS/cover.png',
                    'OEBPS/images/cover.jpg', 'OEBPS/images/cover.jpeg', 'OEBPS/images/cover.png'
                ]

                for path in common_paths:
                    try:
                        image_data = epub_zip.read(path)
                        return Image.open(io.BytesIO(image_data))
                    except KeyError:
                        continue

                print("Error: Could not find cover image in EPUB")
                return None

            # Normalize path separators
            cover_path = cover_path.replace('\\', '/')

            # Read the cover image
            try:
                image_data = epub_zip.read(cover_path)
                return Image.open(io.BytesIO(image_data))
            except KeyError:
                print(f"Error: Cover image not found at path: {cover_path}")
                return None

    except zipfile.BadZipFile:
        print(f"Error: {epub_path} is not a valid EPUB/ZIP file")
        return None
    except Exception as e:
        print(f"Error extracting cover: {e}")
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_epub_thumbnail.py <epub_file_path>")
        sys.exit(1)

    epub_path = Path(sys.argv[1])

    if not epub_path.exists():
        print(f"Error: File not found: {epub_path}")
        sys.exit(1)

    if not epub_path.suffix.lower() == '.epub':
        print(f"Error: File must be an EPUB file: {epub_path}")
        sys.exit(1)

    print(f"Processing: {epub_path}")

    # Extract cover image
    cover_image = extract_cover_from_epub(epub_path)

    if cover_image is None:
        print("Failed to extract cover image")
        sys.exit(1)

    # Create thumb directory
    thumb_dir = epub_path.parent / 'thumb'
    thumb_dir.mkdir(exist_ok=True)

    # Save thumbnail with .epub.png extension
    thumbnail_path = thumb_dir / f"{epub_path.name}.png"
    if os.path.exists(thumbnail_path):
        print(f"Thumbnail already exists:  skipping:  {thumbnail_path}")
        sys.exit(0)

    # Convert to RGB if necessary (for CMYK or other color modes)
    if cover_image.mode not in ('RGB', 'RGBA'):
        cover_image = cover_image.convert('RGB')

    # Resize to standard thumbnail size (122x150)
    thumbnail_size = (122, 150)
    cover_image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)

    # Save as PNG
    cover_image.save(thumbnail_path, 'PNG')

    print(f"Thumbnail saved to: {thumbnail_path}")
    print(f"Image size: {cover_image.size[0]}x{cover_image.size[1]}")


if __name__ == '__main__':
    main()
