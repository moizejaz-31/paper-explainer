#!/usr/bin/env python3
"""
Paper Extraction Utility for the paper-explainer skill.
Extracts structured text, sections, contributions, and future work
from local PDFs, arXiv IDs/URLs, or direct PDF URLs.
"""

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Any


def download_url(url: str, dest_path: str, user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"):
    """Downloads a file from a URL with basic error handling and headers."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": user_agent}
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        with open(dest_path, "wb") as f:
            f.write(response.read())


def normalize_arxiv_url(arxiv_ref: str) -> str:
    """Normalizes an arXiv ID or URL into a direct PDF download URL."""
    arxiv_ref = arxiv_ref.strip()
    if arxiv_ref.endswith(".pdf"):
        return arxiv_ref
    
    match_abs = re.search(r"arxiv\.org/abs/([0-9]+\.[0-9]+(?:v[0-9]+)?)", arxiv_ref, re.IGNORECASE)
    if match_abs:
        return f"https://arxiv.org/pdf/{match_abs.group(1)}.pdf"
    
    match_pdf = re.search(r"arxiv\.org/pdf/([0-9]+\.[0-9]+(?:v[0-9]+)?)", arxiv_ref, re.IGNORECASE)
    if match_pdf:
        return f"https://arxiv.org/pdf/{match_pdf.group(1)}.pdf"

    match_id = re.match(r"^([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?)$", arxiv_ref)
    if match_id:
        return f"https://arxiv.org/pdf/{match_id.group(1)}.pdf"

    if arxiv_ref.startswith("http://") or arxiv_ref.startswith("https://"):
        return arxiv_ref
        
    return f"https://arxiv.org/pdf/{arxiv_ref}.pdf"


def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Extracts text page-by-page using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.stderr.write("Error: pypdf is not installed. Run with `uv run --with pypdf extract_paper.py`\n")
        sys.exit(1)

    reader = PdfReader(pdf_path)
    pages = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({
            "page_number": idx + 1,
            "text": text
        })
    return pages


def find_excerpts(text: str, patterns: List[str], max_chars: int = 2000, max_matches: int = 12) -> List[str]:
    """Finds paragraphs matching given regex patterns."""
    paragraphs = re.split(r"\n\s*\n", text)
    matched = []
    combined_pattern = re.compile("|".join(patterns), re.IGNORECASE)

    for p in paragraphs:
        p_clean = " ".join(p.split())
        if len(p_clean) < 40:
            continue
        if combined_pattern.search(p_clean):
            snippet = p_clean[:max_chars] if len(p_clean) > max_chars else p_clean
            if snippet not in matched:
                matched.append(snippet)
            if len(matched) >= max_matches:
                break
    return matched


def parse_paper_sections(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Parses text into structured sections and finds key paper signals."""
    full_text = "\n\n".join([f"--- Page {p['page_number']} ---\n{p['text']}" for p in pages])
    clean_plain_text = "\n\n".join([p["text"] for p in pages])
    
    # Try extracting title from page 1
    page1_lines = [line.strip() for line in pages[0]["text"].split("\n") if line.strip()]
    title = ""
    for line in page1_lines[:6]:
        if "arxiv" in line.lower() or "conference" in line.lower() or "neurips" in line.lower() or "proceedings" in line.lower() or line.isdigit():
            continue
        if len(line) > 10:
            title = line
            break

    contribution_patterns = [
        r"we summarize our contributions",
        r"our (main|key)?\s*contributions are",
        r"this paper makes the following contributions",
        r"in summary, (our|we)",
        r"the main contributions of this (work|paper)",
        r"we make the following contributions",
        r"our contribution is threefold",
        r"we propose",
    ]

    future_work_patterns = [
        r"future work",
        r"future research",
        r"future direction",
        r"in the future",
        r"we plan to",
        r"we leave (this|it|further) (as|for|to) future",
        r"open question",
        r"promising avenue",
        r"avenue for future",
        r"remains to be investigated",
    ]

    limitation_patterns = [
        r"limitation",
        r"bottleneck",
        r"failure cases?",
        r"drawback",
        r"one constraint",
        r"a key challenge remains",
        r"potential negative",
    ]

    contributions = find_excerpts(clean_plain_text, contribution_patterns)
    future_work = find_excerpts(clean_plain_text, future_work_patterns)
    limitations = find_excerpts(clean_plain_text, limitation_patterns)

    # Heuristic abstract extraction
    abstract_text = ""
    match_abs = re.search(r"(?i)\babstract\b[:\s]*(.+?)(?=\n\s*(?:1\.?\s*)?introduction|\n\s*[I1]\.\s+introduction)", clean_plain_text, re.DOTALL)
    if match_abs:
        abstract_text = " ".join(match_abs.group(1).split())[:2500]
    elif len(pages) > 0:
        abstract_text = " ".join(pages[0]["text"].split()[:350])

    # Extract conclusion / future work block
    conclusion_text = ""
    match_concl = re.search(r"(?i)\b(?:conclusion|conclusions|concluding\s+remarks)\b[:\s]*(.+?)(?=\n\s*(?:references|acknowledgements|appendix)|\Z)", clean_plain_text, re.DOTALL)
    if match_concl:
        conclusion_text = " ".join(match_concl.group(1).split())[:4000]

    return {
        "title": title,
        "abstract": abstract_text,
        "contributions_excerpts": contributions,
        "future_work_excerpts": future_work,
        "limitations_excerpts": limitations,
        "conclusion_section": conclusion_text,
        "total_pages": len(pages),
        "pages_summary": [{"page": p["page_number"], "char_count": len(p["text"])} for p in pages],
        "_full_text_cache": full_text
    }


def main():
    parser = argparse.ArgumentParser(description="Extract paper content for paper-explainer skill")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pdf", type=str, help="Path to local PDF file")
    group.add_argument("--arxiv", type=str, help="arXiv ID or URL")
    group.add_argument("--url", type=str, help="Direct URL to paper PDF")
    group.add_argument("--text", type=str, help="Path to plain text / markdown file of the paper")

    parser.add_argument("--output", type=str, required=True, help="Destination JSON file for extracted content")
    parser.add_argument("--save-pdf", type=str, default=None, help="Optional path to save downloaded PDF")
    parser.add_argument("--save-text", type=str, default=None, help="Optional path to save extracted full text")

    args = parser.parse_args()

    temp_pdf = None
    pdf_path = None

    try:
        if args.arxiv:
            pdf_url = normalize_arxiv_url(args.arxiv)
            sys.stderr.write(f"Downloading arXiv paper from {pdf_url}...\n")
            if args.save_pdf:
                pdf_path = args.save_pdf
            else:
                temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
                pdf_path = temp_file.name
                temp_pdf = pdf_path
                temp_file.close()
            download_url(pdf_url, pdf_path)
            source_info = f"arXiv: {args.arxiv} ({pdf_url})"

        elif args.url:
            sys.stderr.write(f"Downloading paper from URL {args.url}...\n")
            if args.save_pdf:
                pdf_path = args.save_pdf
            else:
                temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
                pdf_path = temp_file.name
                temp_pdf = pdf_path
                temp_file.close()
            download_url(args.url, pdf_path)
            source_info = f"URL: {args.url}"

        elif args.pdf:
            if not os.path.exists(args.pdf):
                sys.stderr.write(f"Error: File '{args.pdf}' not found.\n")
                sys.exit(1)
            pdf_path = args.pdf
            source_info = f"Local PDF: {args.pdf}"

        elif args.text:
            if not os.path.exists(args.text):
                sys.stderr.write(f"Error: File '{args.text}' not found.\n")
                sys.exit(1)
            with open(args.text, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            pages = [{"page_number": 1, "text": content}]
            parsed = parse_paper_sections(pages)
            full_text = parsed.pop("_full_text_cache")
            parsed["source"] = f"Text file: {args.text}"
            
            # Save full text if requested
            text_out = args.save_text or os.path.splitext(args.output)[0] + "_full.txt"
            with open(text_out, "w", encoding="utf-8") as f:
                f.write(full_text)
            parsed["full_text_file"] = text_out

            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)
            print(f"Success! Extracted paper information written to: {args.output}")
            return

        # Process PDF
        pages = extract_text_from_pdf(pdf_path)
        parsed = parse_paper_sections(pages)
        full_text = parsed.pop("_full_text_cache")
        parsed["source"] = source_info

        # Save full text sidecar for detailed inspection
        text_out = args.save_text or os.path.splitext(args.output)[0] + "_full.txt"
        with open(text_out, "w", encoding="utf-8") as f:
            f.write(full_text)
        parsed["full_text_file"] = text_out

        # Write output JSON
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)

        print(f"Success! Extracted paper information written to: {args.output}")
        print(f"Full text written to: {text_out}")

    except Exception as e:
        sys.stderr.write(f"Error during paper extraction: {e}\n")
        sys.exit(1)
    finally:
        if temp_pdf and os.path.exists(temp_pdf) and not args.save_pdf:
            try:
                os.remove(temp_pdf)
            except OSError:
                pass


if __name__ == "__main__":
    main()
