import fitz
import json
import os
import re
import time
from collections import defaultdict

# --- Final Parser for Submission ---

def clean_text(text):
    """A robust cleaner for heading and title text."""
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove trailing noise from tables of contents
    text = re.sub(r'\s*\.{3,}\s*\d+$', '', text)
    # Handle common ligatures
    return text.replace('ﬀ', 'ff').replace('ﬁ', 'fi').replace('ﬂ', 'fl')

def get_body_font_size(doc):
    """Finds the most common font size to reliably identify body text."""
    if not doc or doc.page_count == 0: return 10.0
    font_counts = defaultdict(int)
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font_counts[round(span["size"])] += 1
    if not font_counts: return 10.0
    # Use the mode (most common) as the body size
    return float(max(font_counts, key=font_counts.get))

def extract_title(doc, body_size):
    """A scoring-based engine to find the most likely title on the first page."""
    title_candidate, max_score = "Untitled Document", 0
    page = doc[0]
    
    # Search the top 35% of the page
    search_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height * 0.35)
    blocks = page.get_text("dict", clip=search_rect)["blocks"]

    for block in blocks:
        if not block.get("lines") or not block['lines'][0]['spans']: continue
        
        line_text = " ".join(s['text'] for s in block['lines'][0]['spans'])
        cleaned_text = clean_text(line_text)
        if len(cleaned_text) < 4 or len(cleaned_text) > 150: continue

        span = block['lines'][0]['spans'][0]
        font_size = span['size']
        
        if font_size < body_size * 1.5: continue
            
        center_pos = (block['bbox'][0] + block['bbox'][2]) / 2
        page_center = page.rect.width / 2
        # Calculate centrality score (0 to 1, where 1 is perfect center)
        center_proximity = max(0, 1 - (abs(center_pos - page_center) / (page_center * 0.8)))
        
        # Score is a combination of size and being centered
        score = font_size * (1 + center_proximity)
        
        if score > max_score:
            max_score = score
            title_candidate = cleaned_text
            
    return title_candidate

def extract_structure(pdf_path):
    """Final version using a perfected dual-strategy parser."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {"title": f"Error: {e}", "outline": []}

    if doc.page_count == 0: return {"title": "Empty Document", "outline": []}

    body_size = get_body_font_size(doc)
    title = extract_title(doc, body_size)
    
    patterns = {
        "H1": re.compile(r'^(?:CHAPTER\s\d+|APPENDIX\s[A-Z]|\d+)\.?\s', re.IGNORECASE),
        "H2": re.compile(r'^\d+\.\d+\.?\s'),
        "H3": re.compile(r'^(?:\d+\.\d+\.\d+\.?|\([a-z]\)|[a-z]\))\s')
    }

    outline_candidates = []

    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("blocks", sort=True)
        for y0, x0, y1, x1, text, _, __ in blocks:
            cleaned_text = clean_text(text)
            if len(cleaned_text) < 3 or len(cleaned_text.split()) > 20 or cleaned_text.lower() == title.lower():
                continue

            # 1. Pattern-based detection for structured headings
            level_found = None
            for level, pattern in patterns.items():
                if pattern.match(cleaned_text):
                    level_found = level
                    break
            if level_found:
                outline_candidates.append({"text": cleaned_text, "page": page_num, "y": y0, "level": level_found})
                continue

            # 2. Style-based detection for non-structured headings
            dict_block = page.get_text("dict", clip=(y0, x0, y1, x1))["blocks"]
            if not dict_block or not dict_block[0]['lines'][0]['spans']: continue
            
            span = dict_block[0]['lines'][0]['spans'][0]
            if "bold" in span['font'].lower() and span['size'] > body_size * 1.1:
                outline_candidates.append({"text": cleaned_text, "page": page_num, "y": y0, "level": "H2"})

    # Deduplicate and finalize the outline
    final_outline, seen = [], set()
    outline_candidates.sort(key=lambda x: (x['page'], x['y']))
    for cand in outline_candidates:
        entry_key = (cand['text'], cand['page'])
        if entry_key not in seen:
            final_outline.append({"level": cand['level'], "text": cand['text'], "page": cand['page']})
            seen.add(entry_key)
            
    doc.close()
    return {"title": title, "outline": final_outline}

def main():
    # This main function is configured for the Docker submission environment
    parser = argparse.ArgumentParser(description="Adobe Hackathon Round 1A Submission")
    parser.add_argument('--input_dir', type=str, default='/app/input', help="Input directory for PDFs")
    parser.add_argument('--output_dir', type=str, default='/app/output', help="Output directory for JSONs")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    for fname in os.listdir(args.input_dir):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(args.input_dir, fname)
            print(f"Processing: {fname}")
            
            struct = extract_structure(path)

            base_name = os.path.splitext(fname)[0]
            out_path = os.path.join(args.output_dir, base_name + ".json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(struct, f, indent=4)

if __name__ == "__main__":
    import argparse
    main()