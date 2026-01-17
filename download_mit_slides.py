#!/usr/bin/env python3
"""
MIT OCW Blockchain and Money Course - Lecture Slides Downloader

This script downloads all lecture slides (PDFs) from the MIT OpenCourseWare
"Blockchain and Money" course (15.S12, Fall 2018).

Course page: https://ocw.mit.edu/courses/15-s12-blockchain-and-money-fall-2018/pages/lecture-slides/

Usage:
    python download_mit_slides.py [--output-dir OUTPUT_DIR]

Requirements:
    pip install requests beautifulsoup4
"""

import os
import re
import time
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path


# Base URLs
BASE_URL = "https://ocw.mit.edu"
COURSE_URL = "https://ocw.mit.edu/courses/15-s12-blockchain-and-money-fall-2018"
LECTURE_SLIDES_URL = f"{COURSE_URL}/pages/lecture-slides/"

# Request headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def get_lecture_slide_links(session: requests.Session) -> list[dict]:
    """
    Parse the lecture slides page and extract all PDF resource links.
    
    Returns:
        List of dictionaries with 'title' and 'resource_url' keys.
    """
    print(f"Fetching lecture slides page: {LECTURE_SLIDES_URL}")
    response = session.get(LECTURE_SLIDES_URL, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all links that point to course resources (PDFs)
    slides = []
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        
        # Match resource page URLs (e.g., /courses/15-s12-.../resources/mit15_s12f18_ses1/)
        if "/resources/mit15_s12f18_ses" in href and "(PDF" in text:
            # Clean up the title
            title = text.replace("(PDF)", "").strip()
            title = re.sub(r"\s*-\s*[\d.]+MB\s*", "", title).strip()
            title = re.sub(r"\s*-\s*\d+MB\s*", "", title).strip()
            
            # Normalize URL
            if href.startswith("/"):
                resource_url = urljoin(BASE_URL, href)
            else:
                resource_url = href
            
            slides.append({
                "title": title,
                "resource_url": resource_url
            })
    
    print(f"Found {len(slides)} lecture slides")
    return slides


def get_pdf_download_url(session: requests.Session, resource_url: str) -> str | None:
    """
    Visit a resource page and extract the direct PDF download URL.
    
    Args:
        session: The requests session.
        resource_url: URL of the resource page.
        
    Returns:
        Direct PDF download URL, or None if not found.
    """
    response = session.get(resource_url, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Look for direct PDF links
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if href.endswith(".pdf"):
            if href.startswith("/"):
                return urljoin(BASE_URL, href)
            return href
    
    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a filename.
    """
    # Replace invalid characters with underscores
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    # Remove multiple spaces/underscores
    filename = re.sub(r"[_\s]+", "_", filename)
    return filename.strip("_")


def download_pdf(session: requests.Session, pdf_url: str, output_path: Path, title: str) -> bool:
    """
    Download a PDF file.
    
    Args:
        session: The requests session.
        pdf_url: Direct URL of the PDF file.
        output_path: Path where the PDF will be saved.
        title: Title of the lecture for display purposes.
        
    Returns:
        True if download was successful, False otherwise.
    """
    try:
        print(f"  Downloading: {title}")
        response = session.get(pdf_url, headers=HEADERS, stream=True)
        response.raise_for_status()
        
        # Get file size if available
        total_size = int(response.headers.get("content-length", 0))
        
        with open(output_path, "wb") as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  Progress: {percent:.1f}%", end="", flush=True)
        
        if total_size > 0:
            print()  # New line after progress
        
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  Saved: {output_path.name} ({file_size_mb:.2f} MB)")
        return True
        
    except Exception as e:
        print(f"  Error downloading {title}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download MIT OCW Blockchain and Money lecture slides"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="slides",
        help="Output directory for downloaded PDFs (default: slides)"
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=1.0,
        help="Delay between downloads in seconds (default: 1.0)"
    )
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir.absolute()}")
    
    # Create a session for connection reuse
    session = requests.Session()
    
    # Get all lecture slide links
    slides = get_lecture_slide_links(session)
    
    if not slides:
        print("No lecture slides found!")
        return
    
    # Download each PDF
    print("\nStarting downloads...")
    print("-" * 60)
    
    successful = 0
    failed = 0
    
    for i, slide in enumerate(slides, 1):
        print(f"\n[{i}/{len(slides)}] {slide['title']}")
        
        # Get the direct PDF URL
        pdf_url = get_pdf_download_url(session, slide["resource_url"])
        
        if not pdf_url:
            print(f"  Could not find PDF URL for: {slide['title']}")
            failed += 1
            continue
        
        # Generate output filename
        # Use a numbered prefix to maintain order
        safe_title = sanitize_filename(slide["title"])
        filename = f"{i:02d}_{safe_title}.pdf"
        output_path = output_dir / filename
        
        # Skip if already downloaded
        if output_path.exists():
            print(f"  Already exists: {output_path.name}")
            successful += 1
            continue
        
        # Download the PDF
        if download_pdf(session, pdf_url, output_path, slide["title"]):
            successful += 1
        else:
            failed += 1
        
        # Delay between downloads to be polite to the server
        if i < len(slides):
            time.sleep(args.delay)
    
    # Summary
    print("\n" + "=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Total slides: {len(slides)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Output directory: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
