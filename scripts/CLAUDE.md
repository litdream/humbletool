# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains tools for working with books purchased from HumbleBundle. The primary tool is an EPUB thumbnail extractor that reads EPUB book files and generates PNG thumbnails.

## Project Structure

- `scripts/` - Contains Python utilities for processing EPUB files
- Project uses Python 3.13 as specified in `.python-version`
- Package management via `pyproject.toml`

## Python Environment

The project requires Python 3.13+. Dependencies are managed via `pyproject.toml`:
- `pillow>=10.0.0` - For image processing and format conversion

### Setup

```bash
# Install dependencies (using pip, uv, or your preferred package manager)
pip install -e .
# or
uv pip install -e .
```

## EPUB Thumbnail Extractor

Script: `extract_epub_thumbnail.py`

### Usage

```bash
python extract_epub_thumbnail.py <epub_file_path>
```

### Behavior

- Accepts an EPUB file path as the first argument
- Extracts cover image from the EPUB using multiple detection methods:
  1. OPF metadata with `name="cover"`
  2. OPF item with `properties="cover-image"`
  3. Items with "cover" in the filename or ID
  4. First image in the manifest
  5. Common cover image locations as fallback
- Saves PNG thumbnail in a `thumb/` subdirectory alongside the EPUB file
- Thumbnail filename format: `<original_epub_name>.epub.png`
- Example: `/opt/humblebundle/ml-ai-eng/tinymlcookbook.epub` → `/opt/humblebundle/ml-ai-eng/thumb/tinymlcookbook.epub.png`
- Automatically converts images to RGB mode for consistent PNG output
