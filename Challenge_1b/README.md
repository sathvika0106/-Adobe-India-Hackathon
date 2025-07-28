# Adobe Hackathon Challenge 1B – Multi-Collection PDF Analysis

## 🚀 Overview

This solution addresses Challenge 1B of the Adobe Hackathon, where the goal is to analyze a set of travel-related PDF documents and extract relevant content based on a **persona** and a **task**.

Example:
> **Persona**: Travel Planner  
> **Job to be done**: Plan a trip of 4 days for a group of 10 college friends.

The output is a ranked list of meaningful sections and refined text snippets from the documents to help the persona accomplish their task effectively.

---

## 🧠 Approach Explanation

### 1. **Text Extraction from PDFs**
We use the `PyMuPDF` (`fitz`) library to read and extract text from each page of the PDF. Each block of text is read and sorted top-to-bottom to preserve readability and flow.

### 2. **Section Detection**
A function `is_heading()` is used to identify meaningful section titles:
- The title must be between 3 to 20 words.
- Pure symbols or short fragments are ignored.
- The title must be in **Title Case** or **ALL CAPS**.

This helps eliminate irrelevant matches like "fees." or empty headings.

### 3. **Contextual Text Extraction**
For each identified heading, the script extracts a 15-line context block from the same page (starting at the heading's position). If no heading match is found again, a fallback of the first 1000 characters of the page is used.

### 4. **Semantic Ranking**
Each `(section title + context)` block is converted into an embedding using the `all-MiniLM-L6-v2` model from `sentence-transformers`.

The persona + task are also embedded, and cosine similarity is used to rank the relevance of each section. Additionally, a boost is applied if the content contains relevant travel keywords like:
`["packing", "cuisine", "tips", "restaurants", "coastal", "activities", "guide", "local", etc.]`.

### 5. **Output Format**
The final output JSON includes:
- Metadata (persona, task, time, input files)
- Ranked `extracted_sections` with titles and page numbers
- Corresponding `refined_text` blocks under `subsection_analysis`

---

## 🐳 Dockerfile

Below is the Dockerfile used to containerize the script:

```dockerfile
# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Install required Python libraries
RUN pip install --no-cache-dir \
    PyMuPDF \
    sentence-transformers \
    scikit-learn

# Default command
CMD ["python", "main.py"]
```
## Folder Structure
```graphql

project_folder/
├── input/              # All PDFs go here
│   └── sample1.pdf
├── output/             # Output JSON will be saved here
├── main.py             # Your processing script
├── Dockerfile          # As shown above

```

---

## 🛠️ How to Build

In Git Bash (inside the project folder):

```bash
docker build -t Challenge-1b .

```


## 🚀 How to Run

After building the Docker image, place all your `.pdf` files inside the `input/` folder.

Then run the extractor:
- in bash only

```bash

docker run --rm \
  -v "/$PWD/input:/app/input" \
  -v "/$PWD/output:/app/output" \
  --network none Challenge-1b
```