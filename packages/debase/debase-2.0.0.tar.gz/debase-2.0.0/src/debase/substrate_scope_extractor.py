"""substrate_scope_extractor.py

Single-file, maintainable CLI tool that extracts the *substrate scope* table
from one or two PDFs (manuscript + SI) using Google Gemini (or compatible).

The file mirrors the *section layout* and logging/debug philosophy of
`enzyme_lineage_extractor.py` so that both tools share a consistent developer
experience and can even live in the same package.

Navigate quickly by jumping to the numbered headers:

    # === 1. CONFIG & CONSTANTS ===
    # === 2. DOMAIN MODELS ===
    # === 3. LOGGING HELPERS ===
    # === 4. PDF HELPERS ===
    # === 5. LLM (GEMINI) HELPERS ===
    # === 6. SCOPE EXTRACTION ===
    # === 7. VALIDATION & MERGE ===
    # === 8. PIPELINE ORCHESTRATOR ===
    # === 9. CLI ENTRYPOINT ===
"""

# === 1. CONFIG & CONSTANTS ===
from __future__ import annotations

import os
import re
import json
import time
import logging

# Import universal caption pattern
try:
    from .caption_pattern import get_universal_caption_pattern
except ImportError:
    # Fallback if running as standalone script
    from caption_pattern import get_universal_caption_pattern
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union

MODEL_NAME: str = "gemini-2.5-flash"
MAX_CHARS: int = 150_000           # Max characters sent to LLM
BATCH_SIZE: int = 10               # Batch size when extracting reactions
MAX_RETRIES: int = 4               # LLM retry loop
CACHE_DIR: Path = Path.home() / ".cache" / "substrate_scope"

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# === 2. DOMAIN MODELS ===
@dataclass
class SubstrateProduct:
    """Chemical entity in a substrate scope reaction."""
    name: str
    iupac_name: Optional[str] = None

@dataclass
class Cofactor:
    """Cofactor with optional IUPAC name and role."""
    name: str
    iupac_name: Optional[str] = None
    role: Optional[str] = None

@dataclass
class ReactionConditions:
    """Reaction conditions for substrate scope."""
    temperature: Optional[str] = None
    ph: Optional[str] = None
    substrate_concentration: Optional[str] = None
    buffer: Optional[str] = None
    other_conditions: Optional[str] = None

@dataclass
class ScopeEntry:
    """Single substrate scope reaction data point."""
    enzyme_id: str
    substrates: List[SubstrateProduct] = field(default_factory=list)
    products: List[SubstrateProduct] = field(default_factory=list)
    cofactors: List[Cofactor] = field(default_factory=list)
    
    # Performance metrics
    yield_percent: Optional[float] = None
    ttn: Optional[float] = None
    ee: Optional[float] = None
    
    # Reaction conditions
    conditions: ReactionConditions = field(default_factory=ReactionConditions)
    
    # Metadata
    data_location: Optional[str] = None
    data_source_type: Dict[str, str] = field(default_factory=dict)
    campaign_id: Optional[str] = None
    
    # Lineage information (populated during merge)
    parent_id: Optional[str] = None
    mutations: Optional[str] = None
    generation: Optional[int] = None
    aa_seq: Optional[str] = None
    dna_seq: Optional[str] = None
    confidence: Optional[float] = None
    notes: str = ""

@dataclass
class CompoundMapping:
    """Mapping between compound identifiers and IUPAC names."""
    identifiers: List[str]
    iupac_name: str
    common_names: List[str] = field(default_factory=list)
    compound_type: str = "unknown"
    source_location: Optional[str] = None

def _get_iupac_name(compound) -> str:
    """Get IUPAC name for a compound."""
    if not compound:
        return ''
    
    # If we have an IUPAC name, use it
    if compound.iupac_name:
        return compound.iupac_name
    
    return ''

# === 3. LOGGING HELPERS ===

# --- Debug dump helper ----------------------------------------------------
def _dump(text: str | bytes, path: Path | str) -> None:
    """Write `text` / `bytes` to `path`, creating parent dirs as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(text, (bytes, bytearray)) else "w"
    with p.open(mode) as fh:
        fh.write(text)

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

log = get_logger(__name__)

# === 4. PDF HELPERS ===
try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "PyMuPDF is required for PDF parsing. Install with `pip install pymupdf`."
    ) from exc

from base64 import b64encode

# Use universal caption pattern
_CAPTION_PREFIX_RE = get_universal_caption_pattern()

def _open_doc(pdf_path: str | Path | bytes):
    if isinstance(pdf_path, (str, Path)):
        return fitz.open(pdf_path)  # type: ignore[arg-type]
    return fitz.open(stream=pdf_path, filetype="pdf")  # type: ignore[arg-type]

def extract_text(pdf_path: str | Path | bytes) -> str:
    """Extract raw text from a PDF file (all blocks)."""
    doc = _open_doc(pdf_path)
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()

def extract_captions(pdf_path: str | Path | bytes, max_chars: int = MAX_CHARS) -> str:
    """Extract figure/table captions using the improved regex."""
    doc = _open_doc(pdf_path)
    captions: list[str] = []
    try:
        for page in doc:
            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                # Get all lines in this block
                block_lines = []
                for line in block.get("lines", []):
                    text_line = "".join(span["text"] for span in line.get("spans", []))
                    block_lines.append(text_line.strip())
                
                # Check if any line starts with a caption prefix
                for i, line in enumerate(block_lines):
                    if _CAPTION_PREFIX_RE.match(line):
                        # Found a caption start - collect lines
                        caption_parts = [line]
                        for j in range(i + 1, len(block_lines)):
                            next_line = block_lines[j]
                            if not next_line:  # Empty line signals end
                                break
                            if _CAPTION_PREFIX_RE.match(next_line):
                                break
                            caption_parts.append(next_line)
                        
                        full_caption = " ".join(caption_parts)
                        captions.append(full_caption)
    finally:
        doc.close()
    
    joined = "\n".join(captions)
    return joined[:max_chars]

def limited_concat(*pdf_paths: str | Path, max_chars: int = MAX_CHARS) -> str:
    """Concatenate **all text** from PDFs, trimmed to `max_chars`."""
    total = 0
    chunks: list[str] = []
    for p in pdf_paths:
        t = extract_text(p)
        if total + len(t) > max_chars:
            t = t[: max_chars - total]
        chunks.append(t)
        total += len(t)
        if total >= max_chars:
            break
    return "\n".join(chunks)

def limited_caption_concat(*pdf_paths: str | Path, max_chars: int = MAX_CHARS) -> str:
    """Concatenate caption text and SI table of contents from PDFs, trimmed to `max_chars`."""
    total = 0
    chunks: list[str] = []
    
    for idx, p in enumerate(pdf_paths):
        # For SI (second PDF), first extract table of contents pages
        if idx == 1:  # SI document
            doc = _open_doc(p)
            try:
                # Extract first few pages which typically contain TOC
                toc_text = []
                for page_num in range(min(5, doc.page_count)):
                    if total >= max_chars:
                        break
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    
                    # Look for TOC indicators
                    if any(indicator in page_text.lower() for indicator in 
                           ['table of contents', 'supporting information', 'contents', 'page']):
                        toc_text.append(f"\n[SI TOC Page {page_num + 1}]\n{page_text}")
                        total += len(page_text)
                
                if toc_text:
                    chunks.extend(toc_text)
            finally:
                doc.close()
        
        # Extract captions
        if total < max_chars:
            t = extract_captions(p)
            if total + len(t) > max_chars:
                t = t[: max_chars - total]
            chunks.append(t)
            total += len(t)
            if total >= max_chars:
                break
    
    return "\n".join(chunks)

def extract_figure_image(pdf_paths: List[Path], figure_ref: str, caption_hint: Optional[str] = None, document_hint: Optional[str] = None) -> Optional[str]:
    """Extract figure as a page region when embedded images aren't available.
    
    Args:
        pdf_paths: List of PDF paths to search
        figure_ref: Figure reference to search for (e.g., "Figure 3" or "Figure 3(a)")
        caption_hint: Optional caption text to help identify the exact figure
        document_hint: Optional hint about which document to search ("manuscript" or "supplementary")
        
    Returns:
        Base64-encoded PNG string or None if not found
    """
    if not pdf_paths:
        return None
    
    # Always extract the base reference, removing sub-letters like (a), (b), c, etc.
    import re
    # If we have a caption hint, we can search by caption regardless of reference type
    if caption_hint:
        base_figure_ref = figure_ref
        log.info("Using caption-based search for '%s'", figure_ref)
    else:
        # Match patterns like "Figure 1", "Figure 1c", "Figure 1(c)", "Fig. 1", etc.
        base_figure_match = re.match(r'((?:Figure|Fig\.?)\s*\d+)', figure_ref, re.IGNORECASE)
        if base_figure_match:
            base_figure_ref = base_figure_match.group(1)
            log.info("Extracting entire figure '%s' from reference '%s'", base_figure_ref, figure_ref)
        else:
            base_figure_ref = figure_ref
    
    # Determine which PDFs to search based on document hint
    if document_hint and len(pdf_paths) > 1:
        if document_hint.lower() == "manuscript":
            # ONLY search in manuscript (first PDF)
            search_paths = [pdf_paths[0]]
            log.info("Searching ONLY in manuscript document for '%s' (hint: %s)", figure_ref, document_hint)
        elif document_hint.lower() == "supplementary":
            # ONLY search in SI (second PDF if available)
            search_paths = [pdf_paths[1]] if len(pdf_paths) > 1 else pdf_paths
            log.info("Searching ONLY in supplementary document for '%s' (hint: %s)", figure_ref, document_hint)
        else:
            # No specific hint, search all PDFs
            search_paths = list(pdf_paths)
    else:
        # No hint or single PDF, search all available
        search_paths = list(pdf_paths)
        
    # Extract reference number BEFORE the loop
    # When we have a caption, just extract the number part from any reference type
    if caption_hint:
        # Extract number from any reference type (Chart 1, Figure 3, Table S2, etc.)
        num_match = re.search(r'\b(\w*\d+\w*)\b', base_figure_ref)
        figure_num = num_match.group(1) if num_match else base_figure_ref
    else:
        # Original logic for figure references
        figure_num = base_figure_ref.replace('Figure ', '').replace('figure ', '').replace('Fig. ', '').replace('fig. ', '').replace('Fig ', '').replace('fig ', '')
    
    for pdf_idx, pdf_path in enumerate(search_paths):
        doc = _open_doc(pdf_path)
        try:
            log.debug("Searching %s (document %d/%d) with %d pages for figure '%s'", 
                     pdf_path.name, pdf_idx + 1, len(search_paths), doc.page_count, figure_num)
                     
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                # Debug: Check if page contains any mention of the figure
                # Note: This is just for debugging - we don't skip pages based on this
                # because pages might reference Figure 3 but display Figure 2
                if figure_num.lower() in page_text.lower():
                    log.debug("Page %d contains mention of figure number '%s' (but may not be the actual figure)", page_num + 1, figure_num)
                
                # Check if this page contains the figure caption
                found = False
                caption_rect = None
                
                # First try to find using caption hint if provided
                if caption_hint and len(caption_hint) > 10:
                    log.debug("Page %d: Searching for caption hint: '%s...'", page_num + 1, caption_hint[:50])
                    # Try to find a unique portion of the caption
                    # Start with longer snippets and work down to shorter ones
                    caption_lengths = [100, 50, 30, 20]
                    
                    for length in caption_lengths:
                        if len(caption_hint) >= length:
                            snippet = caption_hint[:length]
                            # Clean up the snippet to avoid partial words
                            if length < len(caption_hint):
                                # Try to end at a word boundary
                                last_space = snippet.rfind(' ')
                                if last_space > length * 0.6:  # Don't trim too much
                                    snippet = snippet[:last_space]
                            
                            # Clean up common PDF artifacts
                            snippet_cleaned = snippet.replace('\u00AD', '').replace('\u200B', '').strip()
                            page_text_cleaned = page_text.replace('\u00AD', '').replace('\u200B', '')
                            
                            if snippet_cleaned in page_text_cleaned:
                                # Found the caption text! Trust it over figure number matching
                                snippet_pos = page_text_cleaned.find(snippet_cleaned)
                                log.info("Page %d: Found caption snippet '%s...' at position %d", 
                                        page_num + 1, snippet[:30], snippet_pos)
                                if snippet_pos != -1:
                                    # Caption-based search is highly reliable - the AI gave us this specific caption
                                    # Check if there's a figure indicator either before OR within the caption
                                    context_start = max(0, snippet_pos - 200)
                                    context_before = page_text[context_start:snippet_pos].lower()
                                    caption_start = page_text[snippet_pos:snippet_pos + 100].lower()
                                    
                                    # Basic check: is there any figure/fig mention nearby or in the caption itself?
                                    has_figure_indicator = any(indicator in context_before or indicator in caption_start 
                                                             for indicator in ['fig', 'figure', 'scheme', 'chart', 'table'])
                                    
                                    if has_figure_indicator or len(snippet) > 50:  # Long captions are very specific
                                        caption_instances = page.search_for(snippet, quads=False)
                                        if caption_instances:
                                            caption_rect = caption_instances[0]
                                            found = True
                                            log.info("Found figure using CAPTION TEXT: '%s...' on page %d (caption-based search)", 
                                                    snippet[:50], page_num + 1)
                                            break
                                        else:
                                            log.debug("Caption text found but couldn't locate it for extraction")
                                    else:
                                        log.debug("Caption snippet found but no figure indicator nearby, might be body text")
                
                # If not found with hint, look for actual figure captions using regex patterns
                # BUT: If we have a caption hint, we should trust it and not fall back to generic patterns
                if not found and not caption_hint:
                    caption_patterns = [
                        # More flexible patterns to match various formats
                        rf"^Figure\s+{re.escape(figure_num)}[\s\.\:]",  # "Figure 3." or "Figure 3:" or "Figure 3 " at start
                        rf"^Fig\.?\s*{re.escape(figure_num)}[\s\.\:]",  # "Fig. 3." or "Fig 3:" at start
                        rf"Figure\s+{re.escape(figure_num)}[\s\.\:]",  # "Figure 3." anywhere
                        rf"Fig\.?\s*{re.escape(figure_num)}[\s\.\:]",  # "Fig. 3." anywhere
                        rf"^Figure\s+{re.escape(figure_num)}\s+[A-Z]",  # "Figure 3 Substrate scope"
                        rf"^Fig\.?\s*{re.escape(figure_num)}\s+[A-Z]",  # "Fig. 3 Substrate"
                        # Special patterns for edge cases
                        rf"Fig\.\s*{re.escape(figure_num)}\s*\|",  # "Fig. 3 |"
                        # Removed the pattern that matches just "3." - too prone to false matches
                    ]
                    
                    for pattern in caption_patterns:
                        matches = re.search(pattern, page_text, re.MULTILINE | re.IGNORECASE)
                        if matches:
                            # Found actual figure caption, get its position
                            caption_text = matches.group(0)
                            caption_instances = page.search_for(caption_text, quads=False)
                            if caption_instances:
                                caption_rect = caption_instances[0]
                                found = True
                                log.info("Found actual figure caption '%s' on page %d", caption_text, page_num + 1)
                                break
                
                if not found and not caption_hint:
                    # Try a fuzzy search for lines that look like figure captions
                    lines = page_text.split('\n')
                    for i, line in enumerate(lines):
                        line_stripped = line.strip()
                        line_lower = line_stripped.lower()
                        
                        # Check if this looks like a figure caption (starts with fig/figure)
                        # and NOT an inline reference (which would have text before it)
                        # Use regex to match figure number more precisely
                        fig_num_pattern = rf'\b{re.escape(figure_num)}\b'
                        if (line_lower.startswith(('fig.', 'fig ', 'figure')) and 
                            re.search(fig_num_pattern, line_lower) and 
                            len(line_stripped) < 200 and
                            not line_lower.endswith(')')):  # Exclude inline refs like "(Fig. 2)"
                            
                            # Found a potential caption line
                            caption_instances = page.search_for(line_stripped[:50], quads=False)
                            if caption_instances:
                                caption_rect = caption_instances[0]
                                found = True
                                log.info("Found figure via fuzzy search: '%s' on page %d", line_stripped[:50], page_num + 1)
                                break
                
                if not found:
                    # Skip this page if we didn't find the actual figure caption
                    continue
                
                log.info("Found figure caption on page %d at y=%.0f", page_num + 1, caption_rect.y0)
                
                # Extract just the figure with its caption, avoiding excessive white space
                page_rect = page.rect
                
                # Extract the entire page containing the identified location
                fig_top = 0  # Start from top of page
                fig_bottom = page_rect.height  # Full page height
                fig_left = 0  # Full width
                fig_right = page_rect.width
                
                # Extract the entire page
                clip_rect = fitz.Rect(fig_left, fig_top, fig_right, fig_bottom)
                mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
                pix = page.get_pixmap(clip=clip_rect, matrix=mat)
                
                log.info("Extracted entire page: %.0fx%.0f pixels from page %d", 
                         pix.width, pix.height, page_num + 1)
                
                # Convert to PNG
                img_bytes = pix.tobytes("png")
                log.info("Converted to PNG: %dx%d pixels from page %d", 
                         pix.width, pix.height, page_num + 1)
                
                return b64encode(img_bytes).decode()
                
        finally:
            doc.close()
    
    log.warning("Could not find figure caption for '%s'", figure_ref)
    return None

def extract_scheme_image(pdf_paths: List[Path], scheme_ref: str) -> Optional[str]:
    """Extract scheme as a page region, similar to figures.
    
    Args:
        pdf_paths: List of PDF paths to search
        scheme_ref: Scheme reference to search for (e.g., "Scheme 2" or "Scheme S2")
        
    Returns:
        Base64-encoded PNG string or None if not found
    """
    if not pdf_paths:
        return None
    
    for pdf_path in pdf_paths:
        doc = _open_doc(pdf_path)
        try:
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                # Check if this page contains the scheme
                found = False
                scheme_instances = None
                
                # Look for scheme reference with various patterns
                variations = [
                    f"{scheme_ref}.",  # "Scheme 2."
                    f"{scheme_ref}:",  # "Scheme 2:"
                    f"{scheme_ref} ",  # "Scheme 2 "
                    scheme_ref,
                ]
                
                for variation in variations:
                    scheme_instances = page.search_for(variation, quads=False)
                    if scheme_instances:
                        # Check if this is likely a scheme title (not a reference in text)
                        for rect in scheme_instances:
                            # Get text around this location
                            x0, y0, x1, y1 = rect
                            text_around = page.get_textbox(fitz.Rect(x0-50, y0-5, x1+400, y1+20))
                            # Check if it looks like a scheme title
                            if any(keyword in text_around.lower() for keyword in 
                                   ['substrate scope', 'reaction', 'synthesis', 'procedure', 'explored']):
                                found = True
                                scheme_rect = rect
                                break
                        if found:
                            break
                
                if not found:
                    continue
                
                log.info("Found scheme on page %d at y=%.0f", page_num + 1, scheme_rect.y0)
                
                # For schemes, we often want to capture more of the page
                # since they can be large and include multiple reactions
                page_rect = page.rect
                
                # Define the region to extract
                # For schemes, we want to capture everything below the title
                # until we hit significant text (which would be the next section)
                top_margin = max(0, scheme_rect.y1 + 5)  # Start just below the scheme title
                
                # Look for the next major text block that might indicate end of scheme
                # This is a simple heuristic - look for blocks of text below the scheme
                text_blocks = page.get_text("blocks")
                bottom_y = page_rect.height  # Default to full page
                
                for block in text_blocks:
                    block_y = block[1]  # y-coordinate of block
                    block_text = block[4]  # text content
                    # If we find a substantial text block below the scheme title
                    if block_y > scheme_rect.y1 + 50 and len(block_text) > 100:
                        # This might be the next section
                        bottom_y = block_y - 10
                        break
                
                # Create the clip rectangle
                clip_rect = fitz.Rect(0, top_margin, page_rect.width, bottom_y)
                
                # Extract the region as an image
                mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
                pix = page.get_pixmap(clip=clip_rect, matrix=mat)
                
                # Convert to PNG
                img_bytes = pix.tobytes("png")
                log.info("Extracted scheme region: %.0fx%.0f pixels from page %d", 
                         clip_rect.width * 2, clip_rect.height * 2, page_num + 1)
                
                return b64encode(img_bytes).decode()
                
        finally:
            doc.close()
    
    log.warning("Could not find scheme '%s'", scheme_ref)
    return None


def _build_caption_index(pdf_paths: List[Path]) -> Dict[str, Dict[str, Any]]:
    """Build an index of all captions for quick lookup."""
    cap_pattern = get_universal_caption_pattern()
    caption_index = {}
    
    for pdf_idx, pdf_path in enumerate(pdf_paths):
        doc = _open_doc(pdf_path)
        source = "manuscript" if pdf_idx == 0 else "supplementary"
        
        try:
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                for match in cap_pattern.finditer(page_text):
                    caption_text = match.group(0).strip()
                    caption_lower = caption_text.lower()
                    
                    # Store caption info
                    caption_info = {
                        'full_caption': caption_text,
                        'page_text': page_text,
                        'page_num': page_num + 1,
                        'pdf_path': pdf_path,
                        'source': source,
                        'match_start': match.start(),
                        'doc': doc  # Keep doc reference for page extraction
                    }
                    
                    # Create multiple keys for flexible matching
                    # Key 1: Full caption text (first 100 chars)
                    key1 = caption_text[:100].lower().strip()
                    caption_index[key1] = caption_info
                    
                    # Key 2: Simplified reference (e.g., "table 5", "figure s3")
                    ref_match = re.search(r'(table|figure|fig|scheme)\s*s?(\d+[a-z]?)', caption_lower)
                    if ref_match:
                        key2 = f"{ref_match.group(1)} {ref_match.group(2)}"
                        caption_index[key2] = caption_info
                        
                        # Also store with 's' prefix if in SI
                        if source == "supplementary" and 's' not in key2:
                            key3 = f"{ref_match.group(1)} s{ref_match.group(2)}"
                            caption_index[key3] = caption_info
        finally:
            doc.close()
    
    return caption_index

def _extract_text_around_reference(pdf_paths: List[Path], ref: str, context_chars: int = 2000, document_hint: Optional[str] = None) -> str:
    """Extract text around a specific reference using caption index."""
    import re
    
    # Filter PDFs based on document hint BEFORE building caption index
    search_paths = pdf_paths
    if document_hint and len(pdf_paths) > 1:
        if document_hint.lower() == "manuscript":
            # ONLY search in manuscript (first PDF)
            search_paths = [pdf_paths[0]]
            log.info("Text extraction: Searching ONLY in manuscript document for '%s'", ref)
        elif document_hint.lower() == "supplementary":
            # ONLY search in SI (second PDF if available)
            search_paths = [pdf_paths[1]] if len(pdf_paths) > 1 else pdf_paths
            log.info("Text extraction: Searching ONLY in supplementary document for '%s'", ref)
    
    # Build caption index from filtered paths
    # Use a cache key that includes the document hint
    cache_key = f"_caption_index_{document_hint or 'all'}"
    if not hasattr(_extract_text_around_reference, cache_key):
        setattr(_extract_text_around_reference, cache_key, _build_caption_index(search_paths))
    
    caption_index = getattr(_extract_text_around_reference, cache_key)
    ref_lower = ref.lower().strip()
    
    # Try multiple matching strategies
    matches = []
    
    # Strategy 1: Direct key lookup
    if ref_lower in caption_index:
        matches.append(caption_index[ref_lower])
    
    # Strategy 2: Normalized reference lookup
    ref_match = re.match(r'(table|figure|fig|scheme)\s*s?(\d+[a-z]?)', ref_lower, re.I)
    if ref_match:
        ref_type, ref_num = ref_match.groups()
        if ref_type == 'fig':
            ref_type = 'figure'
        
        # Try different key formats
        keys_to_try = [
            f"{ref_type} {ref_num}",
            f"{ref_type} s{ref_num}",
            f"table {ref_num}",
            f"fig {ref_num}",
            f"figure {ref_num}"
        ]
        
        for key in keys_to_try:
            if key in caption_index and caption_index[key] not in matches:
                matches.append(caption_index[key])
    
    # Strategy 3: Fuzzy matching
    if not matches and ref_match:
        for key, info in caption_index.items():
            if ref_num in key and any(t in key for t in ['table', 'figure', 'fig', 'scheme']):
                if info not in matches:
                    matches.append(info)
    
    # No need to filter by document hint here since we already filtered the PDFs
    
    # Extract text from matches
    extracted_sections = []
    for match in matches:
        page_text = match['page_text']
        caption_start = match['match_start']
        
        # Extract context around the caption
        start = max(0, caption_start - context_chars // 2)
        end = min(len(page_text), caption_start + context_chars)
        
        section = page_text[start:end]
        source_label = f"{match['source'].upper()} page {match['page_num']}"
        extracted_sections.append(f"\n[From {source_label}]\n{section}")
    
    if not extracted_sections:
        log.warning(f"No matches found for reference '{ref}'")
        # Fallback to old approach
        for pdf_path in pdf_paths:
            doc = _open_doc(pdf_path)
            try:
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    
                    if ref_lower in page_text.lower():
                        pos = page_text.lower().find(ref_lower)
                        start = max(0, pos - context_chars // 2)
                        end = min(len(page_text), pos + context_chars)
                        extracted_sections.append(page_text[start:end])
                        break
            finally:
                doc.close()
    
    return "\n\n".join(extracted_sections)

def _extract_sections_by_title(pdf_paths: List[Path], section_titles: List[str], max_chars_per_section: int = 10000) -> str:
    """Extract sections by their titles from PDFs."""
    import re
    extracted_sections = []
    
    for pdf_path in pdf_paths:
        doc = _open_doc(pdf_path)
        try:
            # Build full text with page markers
            pages_text = []
            for i, page in enumerate(doc):
                page_text = page.get_text()
                pages_text.append(f"\n[PAGE {i+1}]\n{page_text}")
            full_text = "".join(pages_text)
            
            for title in section_titles:
                # Find section start
                title_pattern = re.escape(title)
                match = re.search(rf'{title_pattern}', full_text, re.IGNORECASE)
                
                if match:
                    start_pos = match.start()
                    
                    # Find the page number
                    page_match = re.search(r'\[PAGE (\d+)\]', full_text[:start_pos][::-1])
                    page_num = "unknown"
                    if page_match:
                        page_num = page_match.group(1)[::-1]
                    
                    # Try to find the next section header
                    next_section_patterns = [
                        r'\n[A-Z][A-Za-z\s]+:\s*\n',  # "Section Title:\n"
                        r'\n\d+\.\s+[A-Z]',  # "1. Next Section"
                        r'\n[A-Z]{2,}[A-Z\s]*\n',  # "SECTION HEADER\n"
                        r'\nReferences\s*\n',
                        r'\nAcknowledg',
                        r'\n\[PAGE \d+\]',  # Next page
                    ]
                    
                    end_pos = len(full_text)
                    for pattern in next_section_patterns:
                        next_match = re.search(pattern, full_text[start_pos + 100:], re.IGNORECASE)
                        if next_match:
                            end_pos = min(end_pos, start_pos + 100 + next_match.start())
                    
                    # Extract section with size limit
                    section_text = full_text[start_pos:min(start_pos + max_chars_per_section, end_pos)]
                    
                    # Clean up page markers
                    section_text = re.sub(r'\[PAGE \d+\]', '', section_text)
                    
                    extracted_sections.append(
                        f"\n=== Section: '{title}' from {pdf_path.name} (starting page {page_num}) ===\n{section_text}"
                    )
                    log.info("Extracted section '%s' (%d chars) from %s", 
                            title, len(section_text), pdf_path.name)
        finally:
            doc.close()
    
    return "\n".join(extracted_sections)

def _extract_text_from_page(pdf_paths: List[Path], page_num: Union[str, int]) -> str:
    """Extract text from a specific page number in the PDFs."""
    # Convert page number to int and handle S-prefix
    page_str = str(page_num).strip().upper()
    if page_str.startswith('S'):
        # Supplementary page - look in the SI PDF (second PDF)
        actual_page = int(page_str[1:]) - 1  # 0-indexed
        pdf_index = 1 if len(pdf_paths) > 1 else 0
    else:
        # Regular page - look in the main PDF
        actual_page = int(page_str) - 1  # 0-indexed
        pdf_index = 0
    
    if pdf_index >= len(pdf_paths):
        log.warning("Page %s requested but not enough PDFs provided", page_str)
        return ""
    
    try:
        doc = _open_doc(pdf_paths[pdf_index])
        if 0 <= actual_page < len(doc):
            page = doc[actual_page]
            page_text = page.get_text()
            doc.close()
            log.info("Extracted %d chars from page %s of %s", 
                     len(page_text), page_str, pdf_paths[pdf_index].name)
            return page_text
        else:
            log.warning("Page %s (index %d) out of range for %s (has %d pages)", 
                       page_str, actual_page, pdf_paths[pdf_index].name, len(doc))
            doc.close()
            return ""
    except Exception as e:
        log.error("Failed to extract page %s: %s", page_str, e)
        return ""

def _extract_text_from_pages(pdf_paths: List[Path], page_nums: List[Union[str, int]], max_pages: int = 10) -> str:
    """Extract text from multiple page numbers."""
    all_text = []
    pages_extracted = 0
    
    for page_num in page_nums[:max_pages]:
        page_text = _extract_text_from_page(pdf_paths, page_num)
        if page_text:
            all_text.append(f"\n[PAGE {page_num}]\n{page_text}")
            pages_extracted += 1
    
    if pages_extracted == 0:
        log.warning("No pages extracted from requested pages: %s", page_nums[:5])
    else:
        log.info("Extracted text from %d pages", pages_extracted)
    return "\n".join(all_text)

# === 5. LLM (GEMINI) HELPERS === ---------------------------------------------
from typing import Tuple

_BACKOFF_BASE = 2.0  # exponential back-off base (seconds)

# -- 5.1  Import whichever SDK is installed -----------------------------------

def _import_gemini_sdk() -> Tuple[str, Any]:
    """Return (flavor, module) where flavor in {"new", "legacy"}."""
    try:
        import google.generativeai as genai  # official SDK >= 1.0
        return "new", genai
    except ImportError:
        try:
            import google_generativeai as genai  # legacy prerelease name
            return "legacy", genai
        except ImportError as exc:
            raise ImportError(
                "Neither 'google-generativeai' (>=1.0) nor 'google_generativeai'\n"
                "is installed.  Run:  pip install --upgrade google-generativeai"
            ) from exc

_SDK_FLAVOR, _genai = _import_gemini_sdk()

# -- 5.2  Model factory --------------------------------------------------------

def get_model():
    """Configure API key and return a `GenerativeModel` instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Set the GEMINI_API_KEY environment variable.")
    _genai.configure(api_key=api_key)
    # Positional constructor arg works for both SDK flavors
    return _genai.GenerativeModel(MODEL_NAME)

# === 5.3  Unified call helper ----------------------------------------------

def _extract_text(resp) -> str:
    """
    Pull the *first* textual part out of a GenerativeAI response, handling both
    the old prerelease SDK and the >=1.0 SDK. Also tracks token usage.

    Returns an empty string if no textual content is found.
    """
    # Track token usage if available
    try:
        if hasattr(resp, 'usage_metadata'):
            input_tokens = getattr(resp.usage_metadata, 'prompt_token_count', 0)
            output_tokens = getattr(resp.usage_metadata, 'candidates_token_count', 0)
            if input_tokens or output_tokens:
                # Import wrapper token tracking
                try:
                    from .wrapper import add_token_usage
                    add_token_usage('substrate_scope_extractor', input_tokens, output_tokens)
                except ImportError:
                    pass  # wrapper not available
    except Exception:
        pass  # token tracking is best-effort

    # 1) Legacy SDK (<= 0.4) - still has nice `.text`
    if getattr(resp, "text", None):
        return resp.text

    # 2) >= 1.0 SDK
    if getattr(resp, "candidates", None):
        cand = resp.candidates[0]

        # 2a) Some beta builds still expose `.text`
        if getattr(cand, "text", None):
            return cand.text

        # 2b) Official path: candidate.content.parts[*].text
        if getattr(cand, "content", None):
            parts = [
                part.text                     # Part objects have .text
                for part in cand.content.parts
                if getattr(part, "text", None)
            ]
            if parts:
                return "".join(parts)

    # 3) As a last resort fall back to str()
    return str(resp)

def generate_json_with_retry(
    model,
    prompt: str,
    schema_hint: str | None = None,
    *,
    max_retries: int = MAX_RETRIES,
    debug_dir: str | Path | None = None,
    tag: str = 'gemini',
):
    """
    Call Gemini with retries & exponential back-off, returning parsed JSON.

    Also strips Markdown fences that the model may wrap around its JSON.
    """
    # Log prompt details
    log.info("=== GEMINI API CALL: %s ===", tag.upper())
    log.info("Prompt length: %d characters", len(prompt))
    log.info("First 500 chars of prompt:\n%s\n...(truncated)", prompt[:500])
    
    # Save full prompt to debug directory if provided
    if debug_dir:
        debug_path = Path(debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)
        prompt_file = debug_path / f"{tag}_prompt_{int(time.time())}.txt"
        with open(prompt_file, 'w') as f:
            f.write(f"=== PROMPT FOR {tag.upper()} ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Length: {len(prompt)} characters\n")
            f.write("="*80 + "\n\n")
            f.write(prompt)
        log.info("Full prompt saved to: %s", prompt_file)
    
    fence_re = re.compile(r"```json|```", re.I)
    for attempt in range(1, max_retries + 1):
        try:
            log.info("Calling Gemini API (attempt %d/%d)...", attempt, max_retries)
            resp = model.generate_content(prompt)
            raw = _extract_text(resp).strip()
            
            # Log response
            log.info("Gemini response length: %d characters", len(raw))
            log.info("First 500 chars of response:\n%s\n...(truncated)", raw[:500])
            
            # Save full response to debug directory
            if debug_dir:
                response_file = debug_path / f"{tag}_response_{int(time.time())}.txt"
                with open(response_file, 'w') as f:
                    f.write(f"=== RESPONSE FOR {tag.upper()} ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(raw)} characters\n")
                    f.write("="*80 + "\n\n")
                    f.write(raw)
                log.info("Full response saved to: %s", response_file)

            # Remove common Markdown fences
            if raw.startswith("```"):
                raw = fence_re.sub("", raw).strip()
            
            # Try to find JSON in the response
            # First, try to parse as-is
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                # If that fails, look for JSON array or object
                # Find the first '[' or '{' and the matching closing bracket
                json_start = -1
                json_end = -1
                bracket_stack = []
                in_string = False
                escape_next = False
                
                for i, char in enumerate(raw):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                        
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if in_string:
                        continue
                    
                    if char in '[{':
                        if json_start == -1:
                            json_start = i
                        bracket_stack.append(char)
                    elif char in ']}':
                        if bracket_stack:
                            opening = bracket_stack.pop()
                            if (opening == '[' and char == ']') or (opening == '{' and char == '}'):
                                if not bracket_stack:  # Found complete JSON
                                    json_end = i + 1
                                    break
                
                if json_start >= 0 and json_end > json_start:
                    # Extract the JSON portion
                    json_str = raw[json_start:json_end]
                    parsed = json.loads(json_str)
                else:
                    # Look for simple [] in the response
                    if '[]' in raw:
                        parsed = []
                    else:
                        # No JSON structure found, re-raise the original error
                        raise json.JSONDecodeError("No JSON structure found in response", raw, 0)
            log.info("Successfully parsed JSON response")
            return parsed
        except Exception as exc:                                 # broad except OK here
            log.warning(
                "Gemini call failed (attempt %d/%d): %s",
                attempt, max_retries, exc,
            )
            if attempt == max_retries:
                raise
            time.sleep(_BACKOFF_BASE ** attempt)
# -------------------------------------------------------------------- end 5 ---

# === 6. SCOPE EXTRACTION ===
"""
Substrate scope extraction with compound mapping, enzyme-substrate pairing,
and individual reaction extraction.
"""

# ---- 6.1  Prompt templates -------------------------------------------------

_SCOPE_LOC_PROMPT = """
You are an expert reader of biocatalysis manuscripts.
Analyze this paper and identify all locations containing substrate scope data.

Your task is to:
1. Identify all locations (tables, figures, text) containing substrate scope reaction data
2. Distinguish substrate scope studies from model reactions used for evolution
3. Determine which enzyme variants were tested in substrate scope studies
4. Note if multiple substrates are tested with the same enzyme variant

Return your analysis as JSON array (max {max_results} locations):
[
  {{
    "location": "e.g., SI Table 4, Figure 3, etc.",
    "type": "table/figure/text",
    "confidence": 0-100,
    "reason": "why this contains substrate scope",
    "enzyme_variants_tested": ["list", "of", "enzyme", "variants"],
    "number_of_substrates": "approximate number"
  }}
]
""".strip()



_SUBSTRATE_SCOPE_PROMPT = """
Extract ALL substrate scope data from the primary sources in one complete extraction.
{extraction_hints}

For EACH reaction, extract:
1. Enzyme variant ID
2. Substrate identifiers - ONLY if explicitly shown in the reaction
3. Product identifiers - The compound IDs associated with the reaction results
4. Performance metrics (yield%, ee%, dr, TTN)
5. Reaction conditions (temperature, pH, buffer, substrate concentrations - NOT dithionite/reducing agents)
6. Data location (which figure/table this comes from)

CRITICAL - IDENTIFYING SUBSTRATES VS PRODUCTS:
- If no specific substrate ID is shown, use null for substrate_ids
- Extract values EXACTLY as written in the primary source - NO CHANGES WHATSOEVER
- DO NOT round, estimate, convert, or modify any numbers
- If the text shows "trace", report exactly "trace" in notes, yield_percent=null
- If the text shows "n.d.", report exactly "n.d." in notes, yield_percent=null
- If the text shows "80:20 er", calculate ee as 60.0 (|80-20|)
- If the text shows "91% ee", report ee_percent as 91.0
- If no value is shown, return null, not 0 or empty string
- Extract ALL reactions from ALL identified locations
- Use compound identifiers EXACTLY as shown (not IUPAC names)
- Extract reaction conditions EXACTLY as written - NO PARAPHRASING
- IMPORTANT: Substrate concentration refers to the concentration of the actual chemical substrates being transformed in the reaction, NOT reducing agents (e.g., dithionite, NADH) or other additives

IMPORTANT: 
- Substrate IDs must be EXPLICITLY visible in the source - DO NOT INFER FROM PATTERNS
- Product IDs should be extracted as labeled in the scheme/figure
- If only product ID is shown with yields/ee data, substrate_ids should be null

Return as JSON:
{{
  "substrate_scope_data": [
    {{
      "enzyme_id": "enzyme variant name",
      "substrate_ids": null or ["list of EXPLICITLY shown substrate identifiers"],
      "product_ids": ["list of product identifiers"],
      "yield_percent": null or number,
      "ee_percent": null or number,
      "dr": "ratio if reported",
      "ttn": null or number,
      "reaction_conditions": {{
        "temperature": "",
        "ph": "",
        "buffer": "",
        "substrate_concentration": "concentration of actual substrates/reagents, NOT reducing agents like dithionite",
        "other_conditions": "including enzyme loading, reducing agents (e.g., dithionite), time, etc."
      }},
      "data_location": "specific figure/table",
      "notes": "any special notes (e.g., 'no product detected')"
    }}
  ],
  "compound_ids_found": ["list of all unique compound identifiers found in the substrate scope data"]
}}
""".strip()

_IUPAC_MAPPING_PROMPT = """
You are an expert chemist analyzing a supporting information document to map compound identifiers to their IUPAC names.

COMPOUND IDS TO MAP: {compound_ids}

Your task is to:
1. Search through the ENTIRE document for these specific compound identifiers
2. Find their corresponding IUPAC names, which may be in:
   - Experimental sections
   - Compound characterization sections
   - NMR data sections
   - Synthetic procedures
   - Tables of compounds
   - Any other location in the document

3. For each compound, extract:
   - The exact identifier (e.g., "3a", "4b", "S1")
   - The IUPAC systematic name
   - Any common/trivial names mentioned
   - The compound type (substrate/product/intermediate)

IMPORTANT:
- Search the ENTIRE document thoroughly
- IUPAC names may be far from where the identifier first appears
- Look for patterns like "Compound 3a:", "Preparation of 3a", "(3a)" followed by chemical names
- Some compounds may have both systematic and common names
- Only return compounds you find with high confidence

Return as JSON:
{{
  "compound_mappings": [
    {{
      "identifier": "exact compound ID",
      "iupac_name": "IUPAC systematic name",
      "common_names": ["list of common/trivial names"],
      "compound_type": "substrate/product/intermediate/other",
      "confidence": 0.8-1.0
    }}
  ]
}}
""".strip()


# ---- 6.2  Helper functions -------------------------------------------------


def extract_iupac_mappings_from_pdfs(
    pdf_paths: List[Path],
    compound_ids: List[str],
    model,
    debug_dir: Optional[Path] = None,
) -> Dict[str, Dict[str, Any]]:
    """Extract IUPAC name mappings for compound IDs from manuscript and SI PDFs using multimodal API."""
    log = logging.getLogger(__name__)
    
    if not pdf_paths:
        log.warning("No PDFs provided for IUPAC mapping")
        return {}
    
    log.info("Extracting IUPAC mappings for %d compound IDs using multimodal API", len(compound_ids))
    
    # Format the prompt
    prompt = _IUPAC_MAPPING_PROMPT.format(
        compound_ids=", ".join(sorted(compound_ids))
    )
    
    # Prepare multimodal content with PDFs
    content_parts = [prompt]
    
    # Add PDFs to the multimodal request
    for pdf_path in pdf_paths:
        if pdf_path and pdf_path.exists():
            doc_type = "Manuscript" if "si" not in str(pdf_path).lower() else "Supporting Information"
            log.info(f"Adding {doc_type} PDF to multimodal request")
            
            try:
                pdf_bytes = pdf_path.read_bytes()
                # Create a blob dict for the PDF content
                pdf_blob = {
                    "mime_type": "application/pdf",
                    "data": pdf_bytes
                }
                content_parts.append(f"\n\n[{doc_type} PDF]")
                content_parts.append(pdf_blob)
            except Exception as e:
                log.warning(f"Failed to read PDF {pdf_path}: {e}")
    
    # Call multimodal API
    try:
        log.info("=== GEMINI MULTIMODAL API CALL: IUPAC_MAPPINGS ===")
        log.info("Prompt length: %d characters", len(prompt))
        log.info("Number of PDFs: %d", len(pdf_paths))
        log.info("Compounds to find: %s", ", ".join(sorted(compound_ids)))
        
        # Save debug info
        if debug_dir:
            debug_path = Path(debug_dir)
            prompt_file = debug_path / f"iupac_mappings_prompt_{int(time.time())}.txt"
            with open(prompt_file, 'w') as f:
                f.write("=== PROMPT FOR IUPAC_MAPPINGS ===\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Number of compound IDs: {len(compound_ids)}\n")
                f.write(f"Number of PDFs: {len(pdf_paths)}\n")
                f.write("="*80 + "\n\n")
                f.write(prompt)
            log.info("Full prompt saved to: %s", prompt_file)
        
        # Make multimodal API call
        response = model.generate_content(content_parts)
        raw_text = _extract_text(response).strip()
        
        # Log response
        log.info("Gemini multimodal response length: %d characters", len(raw_text))
        
        if debug_dir:
            response_file = debug_path / f"iupac_mappings_response_{int(time.time())}.txt"
            with open(response_file, 'w') as f:
                f.write("=== RESPONSE FOR IUPAC_MAPPINGS ===\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Length: {len(raw_text)} characters\n")
                f.write("="*80 + "\n\n")
                f.write(raw_text)
            log.info("Full response saved to: %s", response_file)
        
        # Parse JSON
        data = json.loads(_extract_json(raw_text))
        
        # Parse the response
        mappings = {}
        compound_mappings = data.get("compound_mappings", []) if isinstance(data, dict) else []
        
        for mapping in compound_mappings:
            identifier = mapping.get("identifier", "").lower().strip()
            if identifier and identifier in [cid.lower().strip() for cid in compound_ids]:
                mappings[identifier] = {
                    "iupac_name": mapping.get("iupac_name", ""),
                    "common_names": mapping.get("common_names", []),
                    "compound_type": mapping.get("compound_type", "unknown"),
                    "confidence": mapping.get("confidence", 0.8)
                }
                log.info("Found IUPAC name for '%s': %s", 
                        identifier, mappings[identifier]["iupac_name"][:50] + "..." 
                        if len(mappings[identifier]["iupac_name"]) > 50 
                        else mappings[identifier]["iupac_name"])
        
        log.info("Successfully extracted %d IUPAC mappings", len(mappings))
        return mappings
        
    except Exception as exc:
        log.error("Failed to extract IUPAC mappings: %s", exc)
        return {}


def identify_scope_locations_for_campaign(
    text: str,
    model,
    campaign_id: str,
    enzyme_ids: List[str],
    *,
    max_results: int = 5,
    debug_dir: str | Path | None = None,
) -> List[dict]:
    """Ask Gemini where substrate scope data is located for a specific campaign."""
    
    # Simple model reaction context
    model_reactions_context = """
IMPORTANT: Substrate scope reactions are those that test DIFFERENT substrates than the model reactions used for evolution.
Model reactions are used to evolve/optimize enzymes. Substrate scope reactions test evolved enzymes on different substrates.
"""
    
    # Create campaign-specific prompt for location identification
    campaign_prompt = f"""
You are an expert reader of biocatalysis manuscripts.
Analyze this paper and identify all locations containing substrate scope data for the specific campaign: "{campaign_id}".

CAMPAIGN CONTEXT:
- Campaign ID: {campaign_id}
- Target enzymes: {', '.join(enzyme_ids)}

{model_reactions_context}

Your task is to:
1. Identify locations (tables, figures, text) containing substrate scope reaction data specifically for this campaign
2. Focus only on substrate scope studies involving the enzymes: {', '.join(enzyme_ids)}
3. CRITICAL: Distinguish substrate scope studies from model reactions used for evolution
   - Model reactions are those used to evolve/optimize the enzymes
   - Substrate scope reactions test the evolved enzymes on DIFFERENT substrates
4. Note that not all campaigns have substrate scope data - it's okay to return empty results if no substrate scope data exists for this campaign
5. Determine which enzyme variants from this campaign were tested in substrate scope studies

IMPORTANT FIGURE REFERENCE RULES:
- For figures, ALWAYS return the main figure number only (e.g., "Figure 2", NOT "Figure 2a" or "Figure 2(a)")
- Include the figure caption if available to help with identification
- The extraction system will handle retrieving the entire figure including all sub-panels

Return your analysis as JSON array (max {max_results} locations, or empty array if no substrate scope data for this campaign):
[
  {{
    "location": "Main figure/table reference (e.g., 'Figure 2', 'Table S1', NOT 'Figure 2a')",
    "type": "table|figure|text",
    "confidence": 0.0-1.0,
    "enzyme_variants": ["list of enzyme IDs found"],
    "substrates_tested": ["list of substrates if identifiable"],
    "campaign_match": true/false,
    "is_substrate_scope": true/false,
    "model_reaction_excluded": "reason why this is not a model reaction",
    "caption": "Include the figure/table caption if available",
    "document": "manuscript|supplementary - specify whether this location is in the main manuscript or supplementary information"
  }}
]

Important: Only return locations that contain TRUE substrate scope data (not model reactions) for the specified campaign and enzymes. If no substrate scope data exists for this campaign, return an empty array.
"""
    
    prompt = campaign_prompt + "\n\nTEXT:\n" + text[:15_000]
    locs: List[dict] = []
    try:
        locs = generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag=f"scope_locate_{campaign_id}",
        )
    except Exception as exc:  # pragma: no cover
        log.warning("identify_scope_locations_for_campaign(%s): %s", campaign_id, exc)
    return locs if isinstance(locs, list) else []



def _extract_json(text: str) -> str:
    """Extract JSON content from raw LLM response text."""
    # Remove common markdown code block markers
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    
    if text.endswith('```'):
        text = text[:-3]
    
    # Find JSON structure
    text = text.strip()
    
    # Look for JSON object or array
    json_start = -1
    json_end = -1
    
    for i, char in enumerate(text):
        if char in '[{' and json_start == -1:
            json_start = i
            break
    
    if json_start >= 0:
        # Find the matching closing bracket
        bracket_stack = []
        in_string = False
        escape_next = False
        
        for i in range(json_start, len(text)):
            char = text[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if in_string:
                continue
            
            if char in '[{':
                bracket_stack.append(char)
            elif char in ']}':
                if bracket_stack:
                    opening = bracket_stack.pop()
                    if (opening == '[' and char == ']') or (opening == '{' and char == '}'):
                        if not bracket_stack:  # Found complete JSON
                            json_end = i + 1
                            break
        
        if json_end > json_start:
            return text[json_start:json_end]
    
    # If no JSON found, return the original text
    return text





def convert_pdf_to_images(pdf_path: Path, max_pages: int = 50) -> List[str]:
    """Convert PDF pages to base64-encoded PNG images.
    
    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum number of pages to convert (default 50)
        
    Returns:
        List of base64-encoded PNG strings, one per page
    """
    import base64
    from io import BytesIO
    
    doc = _open_doc(pdf_path)
    images = []
    
    try:
        page_count = min(doc.page_count, max_pages)
        log.info("Converting %d pages from %s to PNG images", page_count, pdf_path.name)
        
        for page_num in range(page_count):
            page = doc[page_num]
            # Render at 150 DPI for reasonable quality/size tradeoff
            pix = page.get_pixmap(dpi=150)
            
            # Convert to PNG
            img_data = pix.tobytes(output="png")
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            images.append(img_base64)
            
        log.info("Successfully converted %d pages to PNG", len(images))
    finally:
        doc.close()
    
    return images

def extract_substrate_scope_entries_for_campaign(
    text: str,
    model,
    locations: List[dict],
    campaign_id: str,
    enzyme_ids: List[str],
    *,
    pdf_paths: List[Path] = None,
    debug_dir: str | Path | None = None,
) -> List[dict]:
    """Extract substrate scope data specifically for a campaign."""
    
    extraction_hints = ""
    all_refs = []
    
    if locations:
        # Sort locations by confidence and use only the PRIMARY (most confident) location
        sorted_locations = sorted(locations, key=lambda x: x.get('confidence', 0), reverse=True)
        primary_location = sorted_locations[0] if sorted_locations else None
        
        if primary_location:
            primary_ref = primary_location.get('location', '')
            all_refs = [primary_ref]  # Only extract from primary location
            
            extraction_hints = f"\nPRIMARY substrate scope location for campaign {campaign_id}: {primary_ref}"
            extraction_hints += f"\nLocation confidence: {primary_location.get('confidence', 0)}%"
            extraction_hints += f"\nLocation type: {primary_location.get('type', 'unknown')}"
        
        # Focus on campaign-specific enzyme variants
        extraction_hints += f"\nTarget enzymes for this campaign: {', '.join(enzyme_ids)}"
    
    # Extract text from ONLY the primary location
    extraction_texts = []
    figure_images = {}
    
    # Create a mapping of location strings to their full location data
    location_map = {loc.get('location', ''): loc for loc in locations}
    
    # Check document type and load appropriate PDF
    use_full_pdf = False
    pdf_data = None
    pdf_type = ""
    primary_document = ""
    
    if primary_location:
        primary_document = primary_location.get('document', '').lower()
        if primary_document == 'manuscript' and pdf_paths and len(pdf_paths) > 0:
            log.info("Campaign %s - Primary substrate scope location is in manuscript - will send full manuscript as PDF", campaign_id)
            pdf_type = "manuscript"
            manuscript_path = pdf_paths[0]  # First PDF is manuscript
            try:
                with open(manuscript_path, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()
                log.info("Campaign %s - Successfully loaded manuscript PDF (%d bytes)", campaign_id, len(pdf_data))
                use_full_pdf = True
            except Exception as e:
                log.warning("Campaign %s - Failed to load manuscript PDF: %s", campaign_id, e)
        elif primary_document in ['supplementary', 'si'] and pdf_paths and len(pdf_paths) > 1:
            log.info("Campaign %s - Primary substrate scope location is in supplementary information - will send full SI as PDF", campaign_id)
            pdf_type = "supplementary"
            si_path = pdf_paths[1]  # Second PDF is SI
            try:
                with open(si_path, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()
                log.info("Campaign %s - Successfully loaded SI PDF (%d bytes)", campaign_id, len(pdf_data))
                use_full_pdf = True
            except Exception as e:
                log.warning("Campaign %s - Failed to load SI PDF: %s", campaign_id, e)
    
    # If not using full PDF, extract text normally
    if not use_full_pdf:
        for ref in all_refs:
            if ref and pdf_paths:
                # Get document hint for this reference
                document_hint = location_map.get(ref, {}).get('document', '')
                ref_text = _extract_text_around_reference(pdf_paths, ref, context_chars=5000, document_hint=document_hint)
                if ref_text:
                    extraction_texts.append(f"\n=== Data from {ref} ===\n{ref_text}")
                
                # Extract figure images for this reference (crop page around figure)
                try:
                    # Get caption hint if available
                    caption_hint = location_map.get(ref, {}).get('caption', '')
                    
                    # If we have a good caption, try to extract based on caption pattern
                    if caption_hint and len(caption_hint) > 20:
                        # Extract the figure reference from the caption itself
                        import re
                        caption_fig_match = re.match(r'((?:Figure|Fig\.?)\s*\d+[a-zA-Z]?)', caption_hint, re.IGNORECASE)
                        if caption_fig_match:
                            # Use the figure reference from the caption for more accurate matching
                            fig_ref_from_caption = caption_fig_match.group(1)
                            log.info("Campaign %s - using figure reference from caption: '%s' (original: '%s')", 
                                    campaign_id, fig_ref_from_caption, ref)
                            fig_base64 = extract_figure_image(pdf_paths, fig_ref_from_caption, caption_hint=caption_hint, document_hint=document_hint)
                        else:
                            # Fallback to original reference
                            fig_base64 = extract_figure_image(pdf_paths, ref, caption_hint=caption_hint, document_hint=document_hint)
                    else:
                        # No caption hint, use original reference
                        fig_base64 = extract_figure_image(pdf_paths, ref, caption_hint=caption_hint, document_hint=document_hint)
                    
                    if fig_base64:
                        figure_images[ref] = fig_base64
                        log.info("Campaign %s - extracted cropped figure image for %s", campaign_id, ref)
                        
                        # Save the figure image to debug folder
                        if debug_dir:
                            debug_path = Path(debug_dir)
                            debug_path.mkdir(parents=True, exist_ok=True)
                            # Clean ref for filename
                            safe_ref = re.sub(r'[^\w\s-]', '', ref).strip().replace(' ', '_')
                            image_file = debug_path / f"figure_{safe_ref}_{campaign_id}.png"
                            
                            # Decode and save the image
                            import base64
                            with open(image_file, 'wb') as f:
                                f.write(base64.b64decode(fig_base64))
                            log.info("Campaign %s - saved figure image to %s", campaign_id, image_file)
                except Exception as e:
                    log.warning("Campaign %s - failed to extract figure for %s: %s", campaign_id, ref, e)
    
    if not extraction_texts:
        extraction_texts = [text[:50_000]]
    
    extraction_text = "\n\n".join(extraction_texts)
    
    # Model reaction context
    model_reactions_context = "NOTE: Exclude model reactions used for evolution. Only include tests on DIFFERENT substrates."
    
    # Create campaign-specific prompt
    campaign_prompt = f"""
You are an expert reader of biocatalysis manuscripts.
Extract ALL substrate scope reaction data specifically for campaign: "{campaign_id}".

CAMPAIGN CONTEXT:
- Campaign ID: {campaign_id}
- Target enzymes: {', '.join(enzyme_ids)}

{model_reactions_context}

KEY INSTRUCTIONS:
1. Extract ONLY substrate scope data for enzymes: {', '.join(enzyme_ids)}
2. EXCLUDE model reactions used for evolution - only include tests on DIFFERENT substrates
3. Extract ALL metrics: yield%, ee%, TTN, dr, conversion, temperature, pH, etc.
4. If no substrate scope exists for this campaign, return empty array

DATA ACCURACY:
- Match each product ID with its specific yield/ee/TTN values
- Return null for unclear values rather than guessing

⚠️ CRITICAL - SUBSTRATE vs PRODUCT IDs: ⚠️
In substrate scope tables, compound IDs (4, 5, 6, etc.) shown with yields are PRODUCT IDs!
- Yields refer to products formed, not substrates consumed
- Use substrate_ids: null unless substrate IDs are explicitly shown
- Example: "Compound 4: 85% yield" → product_ids: ["4"], substrate_ids: null
- Only if you see "A → 4" would you use substrate_ids: ["A"], product_ids: ["4"]


{extraction_hints}

Return your analysis as JSON in this format:
{{
  "substrate_scope_data": [
    {{
      "enzyme_id": "enzyme identifier",
      "substrate_ids": null,  // Use null if no substrate ID is shown, DO NOT put product IDs here!
      "product_ids": ["4"],   // The compound ID shown with yield data (e.g., "4: 85% yield")
      "substrate_names": [],  // ONLY populate if exact names are written in PDF, otherwise leave empty
      "product_names": [],   // ONLY populate if exact names are written in PDF, otherwise leave empty
      "yield_percent": number or null,
      "ee": number or null,
      "ttn": number or null,
      "temperature": "temperature" or null,
      "ph": "pH" or null,
      "buffer": "buffer" or null,
      "substrate_concentration": "concentration" or null,
      "data_location": "where this data was found",
      "campaign_id": "{campaign_id}",
      "is_substrate_scope": true,
      "model_reaction_excluded": "reason why this is not a model reaction"
    }}
  ]
}}

CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY valid JSON - no markdown, no comments, no explanations
- Start directly with {{ and end with }}
- NO text before or after the JSON
- If no substrate scope data exists for this campaign, return exactly: {{"substrate_scope_data": []}}
- Every number field should be a number (not a string) or null
- Temperature should be a string with units (e.g., "25 °C") or null
"""
    
    try:
        # Use multimodal extraction if we have figure images OR full PDF
        if figure_images or pdf_data:
            if pdf_data:
                log.info("Campaign %s - using multimodal extraction with FULL %s PDF", campaign_id, pdf_type.upper())
            elif figure_images:
                log.info("Campaign %s - using multimodal extraction with %d figure images", campaign_id, len(figure_images))
            
            # Prepare multimodal content
            import PIL.Image
            import io
            import base64
            
            # Modify prompt if using full PDF
            if pdf_data:
                modified_prompt = campaign_prompt.replace(
                    "TEXT:\n",
                    f"FULL {pdf_type.upper()} PDF:\nThe attached PDF contains the complete {pdf_type}. Please analyze it to find substrate scope data.\n\n"
                )
                content_parts = [
                    modified_prompt,
                    {
                        "mime_type": "application/pdf",
                        "data": pdf_data
                    }
                ]
            else:
                content_parts = [campaign_prompt + "\n\nTEXT:\n" + extraction_text]
            
            # Add figure images if available (and not using PDF)
            if figure_images and not pdf_data:
                for fig_ref, fig_base64 in figure_images.items():
                    try:
                        # Convert base64 to PIL Image
                        img_bytes = base64.b64decode(fig_base64)
                        image = PIL.Image.open(io.BytesIO(img_bytes))
                        content_parts.append(f"\n[Figure: {fig_ref}]")
                        content_parts.append(image)
                        log.info("Campaign %s - added figure %s to multimodal prompt", campaign_id, fig_ref)
                    except Exception as e:
                        log.warning("Campaign %s - failed to add figure %s: %s", campaign_id, fig_ref, e)
            
            # Save debug info
            if debug_dir:
                debug_path = Path(debug_dir)
                debug_path.mkdir(parents=True, exist_ok=True)
                prompt_file = debug_path / f"substrate_scope_{campaign_id}_multimodal_prompt.txt"
                
                prompt_info = f"=== CAMPAIGN {campaign_id} MULTIMODAL PROMPT ===\n"
                prompt_info += f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                if pdf_data:
                    prompt_info += f"Mode: FULL {pdf_type.upper()} PDF\n"
                    prompt_info += f"{pdf_type.capitalize()} PDF size: {len(pdf_data)} bytes\n"
                    prompt_info += f"Primary location document: {primary_document}\n"
                else:
                    prompt_info += f"Mode: FIGURE EXTRACTION\n"
                    prompt_info += f"Text length: {len(extraction_text)} characters\n"
                    prompt_info += f"Figure images included: {len(figure_images)}\n"
                    for fig_ref in figure_images.keys():
                        prompt_info += f"  - {fig_ref}\n"
                
                prompt_info += "="*80 + "\n\n"
                
                if pdf_data:
                    prompt_info += modified_prompt
                else:
                    prompt_info += campaign_prompt + "\n\nTEXT:\n" + extraction_text
                
                with open(prompt_file, 'w') as f:
                    f.write(prompt_info)
                log.info("Campaign %s - prompt saved to: %s", campaign_id, prompt_file)
            
            # Call multimodal API
            response = model.generate_content(content_parts)
            raw_text = response.text.strip()
            
            # Save response
            if debug_dir:
                response_file = debug_path / f"substrate_scope_{campaign_id}_multimodal_response.txt"
                with open(response_file, 'w') as f:
                    f.write(f"=== CAMPAIGN {campaign_id} MULTIMODAL RESPONSE ===\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(raw_text)} characters\n")
                    f.write("="*80 + "\n\n")
                    f.write(raw_text)
                log.info("Campaign %s - response saved to: %s", campaign_id, response_file)
            
            # Parse JSON
            import json
            data = json.loads(raw_text.strip('```json').strip('```').strip())
        else:
            log.info("Campaign %s - using text-only extraction", campaign_id)
            data = generate_json_with_retry(
                model,
                campaign_prompt + "\n\nTEXT:\n" + extraction_text,
                debug_dir=debug_dir,
                tag=f"substrate_scope_{campaign_id}",
            )
        
        scope_data = data.get("substrate_scope_data", [])
        
        # Add campaign_id to each entry if not present
        for entry in scope_data:
            if "campaign_id" not in entry:
                entry["campaign_id"] = campaign_id
        
        log.info("Campaign %s - extracted %d substrate scope entries", campaign_id, len(scope_data))
        return scope_data
        
    except Exception as exc:
        log.error("Failed to extract substrate scope data for campaign %s: %s", campaign_id, exc)
        return []


def _extract_single_reaction(
    text: str,
    model,
    enzyme_id: str,
    substrate_name: str,
    data_location: str,
    context_pairs: List[Tuple[str, str, str]] = None,
    *,
    pdf_paths: List[Path] = None,
    debug_dir: str | Path | None = None,
) -> Optional[dict]:
    """Extract data for a single enzyme-substrate pair."""
    # Build context
    context_info = ""
    if context_pairs:
        context_info = "\nCONTEXT - NEIGHBORING ENTRIES:\n"
        for ctx_enzyme, ctx_substrate, _ in context_pairs[:4]:
            if ctx_enzyme == enzyme_id and ctx_substrate != substrate_name:
                context_info += f"- {ctx_substrate} (same enzyme, different substrate)\n"
    
    # Extract focused text for this specific reaction
    if data_location and pdf_paths:
        # Extract text around the data location and reaction conditions
        extraction_text = _extract_text_around_reference(pdf_paths, data_location, context_chars=2000)
        
        # Also extract reaction conditions section if available
        conditions_sections = ["General procedure", "Reaction conditions", "Standard conditions"]
        conditions_text = _extract_sections_by_title(pdf_paths, conditions_sections, max_chars_per_section=2000)
        
        if conditions_text:
            extraction_text += "\n\n=== REACTION CONDITIONS ===\n" + conditions_text
    else:
        extraction_text = text[:20_000]
    
    prompt = _SINGLE_REACTION_PROMPT.format(
        enzyme_id=enzyme_id,
        substrate_name=substrate_name,
        data_location=data_location,
        context_info=context_info
    )
    prompt += "\n\nTEXT:\n" + extraction_text
    
    try:
        return generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag=f"reaction_{enzyme_id[:10]}_{substrate_name[:10]}",
        )
    except Exception as exc:
        log.error("Failed to extract reaction %s-%s: %s", enzyme_id, substrate_name, exc)
        return None

def _parse_scope_entries(data: List[dict], compound_mappings: Dict[str, CompoundMapping], campaign_id: Optional[str] = None) -> List[ScopeEntry]:
    """Convert raw JSON to ScopeEntry objects with IUPAC enhancement."""
    entries: List[ScopeEntry] = []
    
    for item in data:
        try:
            # Parse substrate IDs
            substrates = []
            substrate_ids = item.get("substrate_ids")
            
            # Handle null substrate_ids
            if substrate_ids is None:
                # Leave substrates empty if substrate_ids is explicitly null
                pass
            else:
                # Also handle old format
                if not substrate_ids and item.get("substrates"):
                    substrates_data = item.get("substrates") or []
                    for s in substrates_data:
                        if isinstance(s, dict):
                            substrate_ids.append(s.get("identifier") or s.get("name", ""))
                        else:
                            substrate_ids.append(str(s))
                
                for sid in substrate_ids:
                    # Look up IUPAC name
                    iupac_name = None
                    mapping = compound_mappings.get(str(sid).lower())
                    if mapping:
                        iupac_name = mapping.iupac_name
                    
                    substrates.append(SubstrateProduct(name=str(sid), iupac_name=iupac_name))
            
            # Parse product IDs
            products = []
            product_ids = item.get("product_ids") or []
            # Also handle old format
            if not product_ids and item.get("products"):
                products_data = item.get("products") or []
                for p in products_data:
                    if isinstance(p, dict):
                        product_ids.append(p.get("identifier") or p.get("name", ""))
                    else:
                        product_ids.append(str(p))
            
            for pid in product_ids:
                # Look up IUPAC name
                iupac_name = None
                mapping = compound_mappings.get(str(pid).lower())
                if mapping:
                    iupac_name = mapping.iupac_name
                
                products.append(SubstrateProduct(name=str(pid), iupac_name=iupac_name))
            
            # Parse cofactors
            cofactors = []
            cofactors_data = item.get("cofactors") or []
            for c in cofactors_data:
                if isinstance(c, dict):
                    cofactors.append(Cofactor(
                        name=c.get("name", ""),
                        iupac_name=c.get("iupac_name"),
                        role=c.get("role")
                    ))
            
            # Parse conditions
            cond_data = item.get("reaction_conditions", {})
            conditions = ReactionConditions(
                temperature=cond_data.get("temperature"),
                ph=cond_data.get("ph"),
                substrate_concentration=cond_data.get("substrate_concentration"),
                buffer=cond_data.get("buffer"),
                other_conditions=cond_data.get("other_conditions")
            )
            
            # Parse numeric values
            def parse_numeric(val):
                if not val or val in ["", "n.d.", "N/A", None]:
                    return None
                try:
                    # Extract numeric part
                    match = re.search(r'(\d+\.?\d*)', str(val))
                    return float(match.group(1)) if match else None
                except:
                    return None
            
            # Parse ee - handle both percentage and ratio formats
            ee_value = item.get("ee_percent")
            if ee_value is None and item.get("ee"):
                # Try to extract from ratio format like "80:20 er"
                ee_str = str(item.get("ee"))
                match = re.search(r'(\d+):(\d+)', ee_str)
                if match:
                    major = float(match.group(1))
                    minor = float(match.group(2))
                    # Convert ratio to ee%
                    ee_value = abs(major - minor)
            
            entry = ScopeEntry(
                enzyme_id=item.get("enzyme_id", ""),
                substrates=substrates,
                products=products,
                cofactors=cofactors,
                yield_percent=parse_numeric(item.get("yield_percent")),
                ttn=parse_numeric(item.get("ttn")),
                ee=parse_numeric(ee_value),
                conditions=conditions,
                data_location=item.get("data_location", ""),
                data_source_type={"all": "text/figure"},
                campaign_id=campaign_id or item.get("campaign_id", ""),
                notes=item.get("notes", "")
            )
            
            entries.append(entry)
            
        except Exception as exc:  # pragma: no cover
            log.debug("Skipping malformed scope entry %s: %s", item, exc)
    
    return entries

# ---- 6.3  Public API -------------------------------------------------------

def get_substrate_scope(
    caption_text: str,
    full_text: str,
    model,
    *,
    pdf_paths: Optional[List[Path]] = None,
    debug_dir: str | Path | None = None,
) -> List[ScopeEntry]:
    """
    High-level wrapper used by the pipeline.

    1. Use captions to identify substrate scope locations
    2. Identify sections containing IUPAC names
    3. Extract compound mappings from identified sections
    4. Identify enzyme-substrate pairs
    5. Extract individual reactions with context
    """
    # Step 1: Find locations using captions
    # For backward compatibility, use campaign-specific function with generic parameters
    locations = identify_scope_locations_for_campaign(
        caption_text, model, "general", ["all"], debug_dir=debug_dir
    )
    if locations:
        location_summary = []
        for loc in locations[:3]:
            location_summary.append(
                f"{loc.get('location', 'Unknown')} ({loc.get('type', 'unknown')}, "
                f"confidence: {loc.get('confidence', 0)})"
            )
        log.info("Identified %d substrate scope locations: %s", 
                 len(locations), ", ".join(location_summary))
    else:
        log.warning("No substrate scope locations identified")
        return []
    
    # Step 2: Extract all substrate scope data first
    # (This gets us the compound IDs we need to map)
    time.sleep(2)  # Rate limiting
    log.info("Extracting all substrate scope data from all identified sources...")
    
    # Extract images for all figure and scheme locations
    figure_images = {}
    for loc in locations:
        location_str = loc.get('location', '')
        location_type = loc.get('type', 'unknown')
        
        # Extract if it's a figure, scheme, or contains those keywords
        should_extract = False
        if pdf_paths:
            if location_type in ['figure', 'scheme']:
                should_extract = True
            elif any(keyword in location_str.lower() for keyword in ['figure', 'fig', 'scheme']):
                should_extract = True
        
        if should_extract:
            figure_ref = location_str
            confidence = loc.get('confidence', 0)
            caption_hint = loc.get('caption', '')
            log.info("Extracting image for %s (confidence: %d%%, type: %s)", figure_ref, confidence, location_type)
            
            # Use appropriate extraction function based on type
            if 'scheme' in location_str.lower() or location_type == 'scheme':
                figure_image = extract_scheme_image(pdf_paths, figure_ref)
            else:
                document_hint = loc.get('document', '')
                figure_image = extract_figure_image(pdf_paths, figure_ref, caption_hint=caption_hint, document_hint=document_hint)
                
            if figure_image:
                log.info("Successfully extracted %s image for %s (%d bytes)", 
                         location_type, figure_ref, len(figure_image))
                figure_images[figure_ref] = figure_image
                
                # Save figure image if debug_dir is enabled
                if debug_dir:
                    import base64
                    debug_path = Path(debug_dir)
                    image_path = debug_path / f"{location_type}_image_{figure_ref.replace(' ', '_')}.png"
                    with open(image_path, 'wb') as f:
                        f.write(base64.b64decode(figure_image))
                    log.info("Saved %s image to %s", location_type, image_path)
            else:
                log.warning("Failed to extract %s image for %s", location_type, figure_ref)
    
    # Extract all substrate scope data in one call
    # Note: This function is now deprecated in favor of campaign-specific extraction
    # For backward compatibility, we'll use a generic campaign approach
    raw_entries = extract_substrate_scope_entries_for_campaign(
        full_text, model, locations,
        campaign_id="general",
        enzyme_ids=["all"],
        pdf_paths=pdf_paths,
        debug_dir=debug_dir
    )
    
    if not raw_entries:
        log.warning("No substrate scope data found")
        return []
    
    # Step 3: Collect all compound IDs from substrate scope data
    log.info("Collecting compound IDs from substrate scope data...")
    
    all_compound_ids = set()
    for entry in raw_entries:
        substrate_ids = entry.get('substrate_ids') or []
        for sid in substrate_ids:
            all_compound_ids.add(str(sid))
        product_ids = entry.get('product_ids') or []
        for pid in product_ids:
            all_compound_ids.add(str(pid))
        # Also check if compound_ids_found was returned
        compound_ids_found = entry.get('compound_ids_found', [])
        for cid in compound_ids_found:
            all_compound_ids.add(str(cid))
    
    log.info("Found %d unique compound IDs to map: %s", len(all_compound_ids), sorted(all_compound_ids))
    
    # Step 4: Extract IUPAC mappings from PDFs
    log.info("Extracting IUPAC name mappings from PDFs...")
    
    compound_mappings = {}
    if pdf_paths:
        iupac_mappings = extract_iupac_mappings_from_pdfs(
            pdf_paths,
            list(all_compound_ids),
            model,
            debug_dir=debug_dir
        )
        
        # Convert to CompoundMapping objects
        for cid, mapping_data in iupac_mappings.items():
            compound_mappings[cid] = CompoundMapping(
                identifiers=[cid],
                iupac_name=mapping_data.get("iupac_name", ""),
                common_names=mapping_data.get("common_names", []),
                compound_type=mapping_data.get("compound_type", "unknown")
            )
    else:
        log.warning("No SI PDF found for IUPAC mapping")
    
    # Step 5: Parse all entries with compound mappings
    entries = _parse_scope_entries(raw_entries, compound_mappings)
    log.info("Successfully parsed %d substrate scope entries", len(entries))
    
    return entries


def get_substrate_scope_for_campaign(
    caption_text: str,
    full_text: str,
    model,
    *,
    campaign_id: str,
    enzyme_ids: List[str],
    pdf_paths: Optional[List[Path]] = None,
    debug_dir: str | Path | None = None,
) -> List[ScopeEntry]:
    """
    Campaign-specific substrate scope extraction.
    
    Like get_substrate_scope but focuses on a specific campaign and its enzymes.
    Tells Gemini about the specific campaign and that it's okay to return null if
    no substrate scope data exists for this campaign.
    """
    log.info("Starting campaign-specific substrate scope extraction for: %s", campaign_id)
    log.info("Target enzymes: %s", enzyme_ids)
    
    # Step 1: Find locations using captions with campaign context
    locations = identify_scope_locations_for_campaign(
        caption_text, model, campaign_id, enzyme_ids, debug_dir=debug_dir
    )
    
    if not locations:
        log.info("No substrate scope locations identified for campaign %s", campaign_id)
        return []
    
    location_summary = []
    for loc in locations[:3]:
        location_summary.append(
            f"{loc.get('location', 'Unknown')} ({loc.get('type', 'unknown')}, "
            f"confidence: {loc.get('confidence', 0)})"
        )
    log.info("Campaign %s - identified %d substrate scope locations: %s", 
             campaign_id, len(locations), ", ".join(location_summary))
    
    
    # Step 3: Extract raw entries with campaign context
    raw_entries = extract_substrate_scope_entries_for_campaign(
        full_text, model, locations, campaign_id, enzyme_ids, 
        pdf_paths=pdf_paths, debug_dir=debug_dir
    )
    
    if not raw_entries:
        log.info("No substrate scope entries extracted for campaign %s", campaign_id)
        return []
        
    log.info("Campaign %s - extracted %d raw substrate scope entries", campaign_id, len(raw_entries))
    
    # Step 4: Collect all compound IDs from raw entries
    all_compound_ids = set()
    for entry in raw_entries:
        substrate_ids = entry.get("substrate_ids", []) or []
        product_ids = entry.get("product_ids", []) or []
        for sid in substrate_ids:
            all_compound_ids.add(str(sid))
        for pid in product_ids:
            all_compound_ids.add(str(pid))
        # Also check if compound_ids_found was returned
        compound_ids_found = entry.get('compound_ids_found', [])
        for cid in compound_ids_found:
            all_compound_ids.add(str(cid))
    
    log.info("Campaign %s - found %d unique compound IDs to map", campaign_id, len(all_compound_ids))
    
    # Step 5: Extract IUPAC mappings from SI PDF
    log.info("Campaign %s - extracting IUPAC name mappings from SI PDF...", campaign_id)
    
    # Find SI PDF
    si_pdf_path = None
    if pdf_paths:
        for pdf_path in pdf_paths:
            if "si" in str(pdf_path).lower() or "supplement" in str(pdf_path).lower():
                si_pdf_path = pdf_path
                break
    
    compound_mappings = {}
    if si_pdf_path:
        iupac_mappings = extract_iupac_mappings_from_pdfs(
            [si_pdf_path],
            list(all_compound_ids),
            model,
            debug_dir=debug_dir
        )
        
        # Convert to CompoundMapping objects
        for cid, mapping_data in iupac_mappings.items():
            compound_mappings[cid] = CompoundMapping(
                identifiers=[cid],
                iupac_name=mapping_data.get("iupac_name", ""),
                common_names=mapping_data.get("common_names", []),
                compound_type=mapping_data.get("compound_type", "unknown")
            )
    else:
        log.warning("Campaign %s - no SI PDF found for IUPAC mapping", campaign_id)
    
    # Step 5: Parse all entries with compound mappings
    entries = _parse_scope_entries(raw_entries, compound_mappings, campaign_id)
    log.info("Campaign %s - successfully parsed %d substrate scope entries", campaign_id, len(entries))
    
    return entries

# === 7. VALIDATION & MERGE ===
"""Validation, duplicate detection, and merging with lineage data."""

def validate_scope_entries(entries: List[ScopeEntry]) -> List[str]:
    """Validate for suspicious patterns like duplicate values."""
    warnings = []
    
    # Track values
    ttn_values: Dict[float, List[str]] = {}
    yield_values: Dict[float, List[str]] = {}
    ee_values: Dict[float, List[str]] = {}
    
    for entry in entries:
        substrate_name = entry.substrates[0].name if entry.substrates else "Unknown"
        key = f"{entry.enzyme_id}-{substrate_name}"
        
        if entry.ttn is not None:
            if entry.ttn not in ttn_values:
                ttn_values[entry.ttn] = []
            ttn_values[entry.ttn].append(key)
        
        if entry.yield_percent is not None:
            if entry.yield_percent not in yield_values:
                yield_values[entry.yield_percent] = []
            yield_values[entry.yield_percent].append(key)
        
        if entry.ee is not None:
            if entry.ee not in ee_values:
                ee_values[entry.ee] = []
            ee_values[entry.ee].append(key)
    
    # Check for suspicious duplicates
    for value, items in ttn_values.items():
        if len(items) > 1:
            warnings.append(f"Multiple entries have TTN={value}: {', '.join(items[:3])}")
    
    for value, items in yield_values.items():
        if len(items) > 1:
            warnings.append(f"Multiple entries have yield={value}%: {', '.join(items[:3])}")
    
    for value, items in ee_values.items():
        if len(items) > 1:
            warnings.append(f"Multiple entries have ee={value}%: {', '.join(items[:3])}")
    
    if warnings:
        log.warning("Validation warnings found - possible extraction errors")
        for warning in warnings:
            log.warning("  %s", warning)
    
    return warnings

def _match_enzymes_with_gemini(
    scope_enzymes: List[str],
    lineage_enzymes: List[str],
    model,
    debug_dir: Optional[Path] = None
) -> Dict[str, str]:
    """Use Gemini to match enzyme names between substrate scope and lineage data."""
    
    prompt = """You are an expert at matching enzyme variant names that may have Unicode or formatting differences.

ENZYME NAMES FROM SUBSTRATE SCOPE DATA:
""" + "\n".join(f"- {e}" for e in sorted(set(scope_enzymes))) + """

ENZYME NAMES FROM LINEAGE DATA:
""" + "\n".join(f"- {e}" for e in sorted(set(lineage_enzymes))) + """

TASK:
Match each substrate scope enzyme name to its corresponding lineage enzyme name.
These are the SAME enzymes but may have different formatting:
- Unicode vs ASCII characters (e.g., "ʟ" vs "L", "ᴅ" vs "D")
- Different capitalization
- Minor formatting differences

IMPORTANT:
- Only match enzymes that are clearly the same variant
- Look for matching generation numbers (G0, G1, G2, etc.)
- Consider the pattern: [L/D]-ApPgb-αEsA-G[number]
- If no clear match exists, return null for that enzyme

Return as JSON:
{{
  "enzyme_matches": {{
    "substrate_scope_enzyme_name": "matching_lineage_enzyme_name_or_null"
  }}
}}
"""

    try:
        response = generate_json_with_retry(
            model,
            prompt,
            debug_dir=debug_dir,
            tag="enzyme_matching"
        )
        
        matches = response.get("enzyme_matches", {})
        log.info("Gemini matched %d enzyme names", len([v for v in matches.values() if v]))
        return matches
        
    except Exception as exc:
        log.error("Failed to match enzymes with Gemini: %s", exc)
        return {}

def merge_with_lineage(
    entries: List[ScopeEntry],
    lineage_csv: Optional[Path],
    model=None
) -> List[ScopeEntry]:
    """Merge substrate scope entries with enzyme lineage data using Gemini for matching."""
    if not lineage_csv or not lineage_csv.exists():
        return entries
    
    try:
        import pandas as pd
        lineage_df = pd.read_csv(lineage_csv)
        log.info("Loading lineage data from %s (%d enzymes)", lineage_csv, len(lineage_df))
        
        # Get unique enzyme names from both sources
        scope_enzymes = list(set(entry.enzyme_id for entry in entries if entry.enzyme_id))
        lineage_enzymes = list(lineage_df['enzyme_id'].dropna().unique())
        
        log.info("Found %d unique enzymes in substrate scope data", len(scope_enzymes))
        log.info("Found %d unique enzymes in lineage data", len(lineage_enzymes))
        
        # Use Gemini to match enzyme names if model is provided
        if model and scope_enzymes and lineage_enzymes:
            log.info("Using Gemini to match enzyme names between datasets...")
            enzyme_matches = _match_enzymes_with_gemini(
                scope_enzymes, 
                lineage_enzymes, 
                model,
                debug_dir=Path("examples/amino_esters_test/substrate_scope_debug_v4") if Path("examples/amino_esters_test/substrate_scope_debug_v4").exists() else None
            )
        else:
            # Fallback to simple case-insensitive matching
            log.info("Using simple case-insensitive matching (no model provided)")
            enzyme_matches = {}
            for scope_enzyme in scope_enzymes:
                for lineage_enzyme in lineage_enzymes:
                    if scope_enzyme.lower() == lineage_enzyme.lower():
                        enzyme_matches[scope_enzyme] = lineage_enzyme
                        break
        
        # Create lookup map with matched names
        lineage_map = {}
        for _, row in lineage_df.iterrows():
            enzyme_id = str(row.get('enzyme_id', ''))
            lineage_map[enzyme_id] = {
                'parent_id': row.get('parent_enzyme_id', ''),  # Note: might be 'parent_enzyme_id' not 'parent_id'
                'mutations': row.get('mutations', ''),
                'generation': row.get('generation'),
                'aa_seq': row.get('protein_sequence', '') or row.get('aa_seq', ''),  # Try both column names
                'dna_seq': row.get('dna_seq', ''),
                'confidence': row.get('seq_confidence', '') or row.get('confidence', '')
            }
        
        # Merge using matched names
        merged_count = 0
        for entry in entries:
            if entry.enzyme_id in enzyme_matches:
                matched_name = enzyme_matches[entry.enzyme_id]
                if matched_name and matched_name in lineage_map:
                    data = lineage_map[matched_name]
                    entry.parent_id = data['parent_id']
                    entry.mutations = data['mutations']
                    # Skip generation - to be filled by lineage_format
                    # entry.generation = data['generation']
                    entry.aa_seq = data['aa_seq']
                    entry.dna_seq = data['dna_seq']
                    entry.confidence = data['confidence']
                    merged_count += 1
                    log.debug("Merged %s -> %s", entry.enzyme_id, matched_name)
        
        log.info("Merged lineage data for %d/%d entries", merged_count, len(entries))
        
    except Exception as exc:
        log.error("Failed to merge with lineage: %s", exc)
    
    return entries

# === 8. PIPELINE ORCHESTRATOR ===
"""High-level function that ties everything together."""

import pandas as pd

def _entries_to_dataframe(entries: List[ScopeEntry]) -> pd.DataFrame:
    """Convert ScopeEntry objects to tidy DataFrame."""
    rows = []
    
    for entry in entries:
        row = {
            'enzyme_id': entry.enzyme_id,
            'parent_enzyme_id': entry.parent_id or '',
            'mutations': entry.mutations or '',
            'generation': '',  # Empty generation - to be filled by lineage_format
            'campaign_id': entry.campaign_id or '',
            'protein_sequence': entry.aa_seq or '',
            'nucleotide_sequence': entry.dna_seq or '',
            'sequence_confidence': str(entry.confidence) if entry.confidence is not None else '',
            'flag': '',
            
            'substrate_list': '; '.join(s.name for s in entry.substrates if s.name),
            'substrate_iupac_list': '; '.join(_get_iupac_name(s) for s in entry.substrates),
            'product_list': '; '.join(p.name for p in entry.products if p.name),
            'product_iupac_list': '; '.join(_get_iupac_name(p) for p in entry.products),
            
            'cofactor_list': '; '.join(c.name for c in entry.cofactors if c.name),
            'cofactor_iupac_list': '; '.join(c.iupac_name or '' for c in entry.cofactors),
            'cofactor_roles': '; '.join(c.role or '' for c in entry.cofactors),
            
            'yield': str(entry.yield_percent) if entry.yield_percent is not None else '',
            'ttn': str(entry.ttn) if entry.ttn is not None else '',
            'ee': str(entry.ee) if entry.ee is not None else '',
            
            'reaction_temperature': entry.conditions.temperature or '',
            'reaction_ph': entry.conditions.ph or '',
            'reaction_substrate_concentration': entry.conditions.substrate_concentration or '',
            'reaction_buffer': entry.conditions.buffer or '',
            'reaction_other_conditions': entry.conditions.other_conditions or '',
            
            'data_location': entry.data_location or ''
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Define column order
    column_order = [
        'enzyme_id', 'parent_enzyme_id', 'mutations', 'generation', 'campaign_id',
        'protein_sequence', 'nucleotide_sequence', 'sequence_confidence', 'flag',
        'substrate_list', 'substrate_iupac_list', 
        'product_list', 'product_iupac_list',
        'cofactor_list', 'cofactor_iupac_list', 'cofactor_roles',
        'yield', 'ttn', 'ee',
        'reaction_temperature', 'reaction_ph', 'reaction_substrate_concentration',
        'reaction_buffer', 'reaction_other_conditions',
        'data_location'
    ]
    
    # Ensure all columns exist
    for col in column_order:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder
    df = df[column_order]
    
    return df

def run_pipeline(
    manuscript: Union[str, Path],
    si: Optional[Union[str, Path]] = None,
    output_csv: Optional[Union[str, Path]] = None,
    *,
    lineage_csv: Optional[Union[str, Path]] = None,
    debug_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Execute the end-to-end substrate scope extraction pipeline.

    Parameters
    ----------
    manuscript : str | Path
        Path to the main PDF file.
    si : str | Path | None, optional
        Path to the Supplementary Information PDF, if available.
    output_csv : str | Path | None, optional
        If provided, the substrate scope table will be written here.
    lineage_csv : str | Path | None, optional
        Path to enzyme lineage CSV for sequence merging.

    Returns
    -------
    pandas.DataFrame
        One row per substrate-enzyme combination with all data.
    """
    t0 = time.perf_counter()
    manuscript = Path(manuscript)
    si_path = Path(si) if si else None

    # 1. Prepare raw text ------------------------------------------------------
    pdf_paths = [p for p in (manuscript, si_path) if p]
    caption_text = limited_caption_concat(*pdf_paths)
    full_text = limited_concat(*pdf_paths)
    
    log.info("Loaded %d chars of captions and %d chars of full text", 
             len(caption_text), len(full_text))

    # 2. Connect to Gemini -----------------------------------------------------
    model = get_model()

    # 3. Check for campaign-based extraction -----------------------------------
    all_entries = []
    
    if lineage_csv:
        import pandas as pd
        lineage_df = pd.read_csv(lineage_csv)
        
        # Check if we have campaign_id column - if so, process each campaign separately
        if 'campaign_id' in lineage_df.columns:
            campaigns = lineage_df['campaign_id'].unique()
            log.info("Detected %d campaigns in lineage data - processing each separately", len(campaigns))
            log.info("Campaigns: %s", campaigns.tolist())
            
            # Simple campaign context for model reaction awareness
            campaigns_context_text = f"All campaigns: {campaigns.tolist()}"
            identify_scope_locations_for_campaign._all_campaigns_context = campaigns_context_text
            extract_substrate_scope_entries_for_campaign._all_campaigns_context = campaigns_context_text
            
            for campaign_id in campaigns:
                log.info("\n" + "="*60)
                log.info("Processing campaign: %s", campaign_id)
                log.info("="*60)
                
                # Get enzymes for this campaign
                campaign_enzymes = lineage_df[lineage_df['campaign_id'] == campaign_id]
                if 'enzyme_id' in campaign_enzymes.columns:
                    enzyme_ids = campaign_enzymes['enzyme_id'].tolist()
                elif 'enzyme' in campaign_enzymes.columns:
                    enzyme_ids = campaign_enzymes['enzyme'].tolist()
                elif 'variant_id' in campaign_enzymes.columns:
                    enzyme_ids = campaign_enzymes['variant_id'].tolist()
                else:
                    raise ValueError("No enzyme ID column found in lineage data")
                
                log.info("Campaign %s has %d enzymes: %s", campaign_id, len(enzyme_ids), enzyme_ids)
                
                # Create campaign-specific debug dir
                campaign_debug_dir = Path(debug_dir) / campaign_id if debug_dir else None
                
                # Extract substrate scope for this campaign
                campaign_entries = get_substrate_scope_for_campaign(
                    caption_text, full_text, model, 
                    campaign_id=campaign_id,
                    enzyme_ids=enzyme_ids,
                    pdf_paths=pdf_paths, 
                    debug_dir=campaign_debug_dir
                )
                
                if campaign_entries:
                    log.info("Extracted %d substrate scope entries for campaign %s", len(campaign_entries), campaign_id)
                    all_entries.extend(campaign_entries)
                else:
                    log.info("No substrate scope data found for campaign %s", campaign_id)
        else:
            # Original single extraction
            entries = get_substrate_scope(caption_text, full_text, model, pdf_paths=pdf_paths, debug_dir=debug_dir)
            all_entries = entries
    else:
        # No lineage data - single extraction
        entries = get_substrate_scope(caption_text, full_text, model, pdf_paths=pdf_paths, debug_dir=debug_dir)
        all_entries = entries

    if not all_entries:
        log.warning("No substrate scope data extracted from any campaign")
        all_entries = []  # Allow empty results

    # 4. Merge with lineage if available ---------------------------------------
    if lineage_csv and all_entries:
        all_entries = merge_with_lineage(all_entries, Path(lineage_csv), model)

    # 5. Validate entries ------------------------------------------------------
    warnings = validate_scope_entries(all_entries)
    if warnings:
        log.warning("Found %d validation warnings", len(warnings))

    # 6. Convert to DataFrame --------------------------------------------------
    df_final = _entries_to_dataframe(all_entries)

    # 7. Write CSV if requested ------------------------------------------------
    if output_csv:
        output_path = Path(output_csv)
        df_final.to_csv(output_path, index=False)
        log.info(
            "Saved substrate scope CSV -> %s (%.1f kB)",
            output_path,
            output_path.stat().st_size / 1024,
        )

    log.info(
        "Pipeline finished in %.2f s (entries: %d)",
        time.perf_counter() - t0,
        len(df_final),
    )
    return df_final

# === 9. CLI ENTRYPOINT ===
"""Simple argparse wrapper matching enzyme_lineage_extractor.py style."""

import argparse

# -- 9.1  Argument parser ----------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="substrate_scope_extractor",
        description="Extract substrate scope data from PDFs using Google Gemini",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--manuscript", required=True, help="Path to main manuscript PDF")
    p.add_argument("--si", help="Path to Supplementary Information PDF")
    p.add_argument("-o", "--output", help="CSV file for extracted data")
    p.add_argument("--lineage-csv", help="Path to enzyme lineage CSV for merging")
    p.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity; repeat (-vv) for DEBUG logging",
    )
    p.add_argument(
        "--debug-dir",
        metavar="DIR",
        help="Write ALL intermediate artefacts (prompts, raw Gemini replies) to DIR",
    )
    return p

# -- 9.2  main() -------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    # Configure logging early so everything respects the chosen level.
    level = logging.DEBUG if args.verbose >= 2 else logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    run_pipeline(
        manuscript=args.manuscript,
        si=args.si,
        output_csv=args.output,
        lineage_csv=args.lineage_csv,
        debug_dir=args.debug_dir,
    )

if __name__ == "__main__":
    main()

# -------------------------------------------------------------------- end 9 ---
