import os
import json
import fitz  # PyMuPDF

def extract_outline(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ Failed to open {pdf_path}: {e}")
        return {"title": "", "outline": []}

    font_sizes = []
    blocks_by_page = {}

    for page_num, page in enumerate(doc, 1):
        try:
            blocks = page.get_text("dict")["blocks"]
        except Exception as e:
            print(f"⚠️ Could not extract text from page {page_num}: {e}")
            continue

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text or len(text) < 3:
                        continue
                    font_sizes.append(span["size"])
                    blocks_by_page.setdefault(page_num, []).append({
                        "text": text,
                        "size": span["size"],
                        "font": span["font"],
                        "page": page_num,
                        "bbox": span["bbox"]
                    })

    size_thresholds = sorted(list(set(font_sizes)), reverse=True)

    # ❗ No text found
    if not size_thresholds:
        print(f"⚠️ No extractable text found in: {pdf_path}")
        return {"title": "", "outline": []}

    # Font size thresholds
    title_size = size_thresholds[0]
    h1_size = size_thresholds[1] if len(size_thresholds) > 1 else title_size
    h2_size = size_thresholds[2] if len(size_thresholds) > 2 else h1_size
    h3_size = size_thresholds[3] if len(size_thresholds) > 3 else h2_size

    title = ""
    outline = []

    for page, blocks in blocks_by_page.items():
        for b in blocks:
            text = b["text"]
            size = b["size"]

            if size == title_size and title == "":
                title = text
            elif size == h1_size:
                outline.append({"level": "H1", "text": text, "page": page})
            elif size == h2_size:
                outline.append({"level": "H2", "text": text, "page": page})
            elif size == h3_size:
                outline.append({"level": "H3", "text": text, "page": page})

    return {"title": title, "outline": outline}

def process_all_pdfs(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]
    if not files:
        print(f"⚠️ No PDF files found in {input_dir}")
        return

    for file in files:
        input_path = os.path.join(input_dir, file)
        output_path = os.path.join(output_dir, file.replace(".pdf", ".json"))
        print(f"📄 Processing: {file}")

        try:
            result = extract_outline(input_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Done: {file} → {output_path}")
        except Exception as e:
            print(f"❌ Error processing {file}: {e}")

if __name__ == "__main__":
    process_all_pdfs("/app/input", "/app/output")
