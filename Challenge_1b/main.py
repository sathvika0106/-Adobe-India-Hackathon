# import os
# import json
# import fitz  # PyMuPDF
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# from datetime import datetime

# def extract_text_by_page(pdf_path):
#     doc = fitz.open(pdf_path)
#     pages = []
#     for i, page in enumerate(doc):
#         text = page.get_text("blocks")
#         text.sort(key=lambda block: (-block[3] + block[1]))  # sort top-to-bottom
#         page_text = "\n".join(block[4] for block in text if block[4].strip())
#         pages.append(page_text)
#     return pages

# def get_document_sections(pages):
#     sections = []
#     for i, text in enumerate(pages):
#         paragraphs = text.split("\n")
#         for para in paragraphs:
#             if len(para.split()) < 15:  # possible heading
#                 sections.append({
#                     "section_title": para.strip(),
#                     "page_number": i + 1,
#                     "refined_text": None
#                 })
#     return sections

# def extract_section_contexts(pages, sections):
#     results = []
#     for section in sections:
#         page_text = pages[section["page_number"] - 1]
#         idx = page_text.find(section["section_title"])
#         context = page_text[idx:idx+1000] if idx != -1 else page_text[:1000]
#         results.append({**section, "refined_text": context})
#     return results

# def rank_sections(sections, query, model):
#     texts = [s["section_title"] + " " + (s["refined_text"] or "") for s in sections]
#     embeddings = model.encode(texts)
#     query_emb = model.encode([query])
#     similarities = cosine_similarity(query_emb, embeddings)[0]
#     ranked = sorted(zip(sections, similarities), key=lambda x: -x[1])
#     return [dict(item[0], importance_rank=i+1) for i, item in enumerate(ranked[:5])]

# def process_documents(input_dir, persona, task):
#     model = SentenceTransformer('all-MiniLM-L6-v2')

#     all_sections = []
#     metadata_files = []
#     for filename in os.listdir(input_dir):
#         if filename.endswith(".pdf"):
#             filepath = os.path.join(input_dir, filename)
#             pages = extract_text_by_page(filepath)
#             sections = get_document_sections(pages)
#             sections = extract_section_contexts(pages, sections)
#             for s in sections:
#                 s["document"] = filename
#             all_sections.extend(sections)
#             metadata_files.append(filename)

#     query = f"{persona} - {task}"
#     ranked_sections = rank_sections(all_sections, query, model)

#     output = {
#         "metadata": {
#             "input_documents": metadata_files,
#             "persona": persona,
#             "job_to_be_done": task,
#             "processing_timestamp": datetime.now().isoformat()
#         },
#         "extracted_sections": [
#             {
#                 "document": sec["document"],
#                 "section_title": sec["section_title"],
#                 "importance_rank": sec["importance_rank"],
#                 "page_number": sec["page_number"]
#             }
#             for sec in ranked_sections
#         ],
#         "subsection_analysis": [
#             {
#                 "document": sec["document"],
#                 "refined_text": sec["refined_text"],
#                 "page_number": sec["page_number"]
#             }
#             for sec in ranked_sections
#         ]
#     }
#     return output

# if __name__ == "__main__":
#     input_dir = "./input"
#     output_dir = "./output"
#     output_path = os.path.join(output_dir, "travel_planner.json")

#     persona = "Travel Planner"
#     task = "Plan a trip of 4 days for a group of 10 college friends."

#     result = process_documents(input_dir, persona, task)

#     os.makedirs(output_dir, exist_ok=True)
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(result, f, indent=4, ensure_ascii=False)

#     print(f"Output written to {output_path}")
import os
import json
import fitz  # PyMuPDF
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime


def extract_text_by_page(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        text = page.get_text("blocks")
        text.sort(key=lambda block: (-block[3] + block[1]))  # top to bottom
        page_text = "\n".join(block[4] for block in text if block[4].strip())
        pages.append(page_text)
    return pages


def is_heading(text):
    text = text.strip()
    if not text or len(text.split()) < 3 or len(text.split()) > 20:
        return False
    if re.fullmatch(r"[^\w\s]+", text):  # only symbols
        return False
    if text.isupper() or text.istitle():
        return True
    return False


def get_document_sections(pages):
    sections = []
    for i, page in enumerate(pages):
        lines = page.split('\n')
        for line in lines:
            if is_heading(line):
                sections.append({
                    "section_title": line.strip(),
                    "page_number": i + 1,
                    "refined_text": None
                })
    return sections


def extract_section_contexts(pages, sections):
    results = []
    for section in sections:
        page_text = pages[section["page_number"] - 1]
        para = ""
        lines = page_text.split('\n')
        found = False
        for idx, line in enumerate(lines):
            if section["section_title"] in line:
                found = True
                para = "\n".join(lines[idx:idx + 15])
                break
        if not found:
            para = page_text[:1000]
        results.append({**section, "refined_text": para})
    return results


def rank_sections(sections, query, model):
    if not sections:
        return []

    boost_keywords = [
        "packing", "cuisine", "food", "activities", "things to do",
        "entertainment", "nightlife", "tips", "tricks", "guide",
        "plan", "water sports", "coastal", "restaurants", "cities",
        "checklist", "hotel", "transport", "local"
    ]

    texts = []
    boosts = []

    for s in sections:
        full = s["section_title"] + " " + (s["refined_text"] or "")
        texts.append(full)

        if any(kw in full.lower() for kw in boost_keywords):
            boosts.append(0.1)
        else:
            boosts.append(0.0)

    embeddings = model.encode(texts)
    query_emb = model.encode([query])
    sims = cosine_similarity(query_emb, embeddings)[0]
    sims = [s + b for s, b in zip(sims, boosts)]

    ranked = sorted(zip(sections, sims), key=lambda x: -x[1])
    
    # ✅ RETURN ALL MATCHES
    return [dict(sec[0], importance_rank=i + 1) for i, sec in enumerate(ranked)]


def process_documents(input_dir, persona, task):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    all_sections = []
    metadata_files = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(input_dir, filename)
            pages = extract_text_by_page(filepath)
            sections = get_document_sections(pages)
            sections = extract_section_contexts(pages, sections)
            for s in sections:
                s["document"] = filename
            all_sections.extend(sections)
            metadata_files.append(filename)

    query = f"{persona} - {task}"
    ranked_sections = rank_sections(all_sections, query, model)

    output = {
        "metadata": {
            "input_documents": metadata_files,
            "persona": persona,
            "job_to_be_done": task,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [
            {
                "document": s["document"],
                "section_title": s["section_title"],
                "importance_rank": s["importance_rank"],
                "page_number": s["page_number"]
            }
            for s in ranked_sections
        ],
        "subsection_analysis": [
            {
                "document": s["document"],
                "refined_text": s["refined_text"].replace("\n", " ").strip(),
                "page_number": s["page_number"]
            }
            for s in ranked_sections
        ]
    }

    return output


if __name__ == "__main__":
    input_dir = "./input"
    output_dir = "./output"
    output_path = os.path.join(output_dir, "travel_planner.json")

    persona = "Travel Planner"
    task = "Plan a trip of 4 days for a group of 10 college friends."

    os.makedirs(output_dir, exist_ok=True)
    result = process_documents(input_dir, persona, task)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"✅ Output written to {output_path}")

