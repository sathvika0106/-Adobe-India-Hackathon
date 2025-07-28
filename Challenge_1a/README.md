  # Adobe Hackathon Challenge 1A –  PDF Processing Solution

  ## 🧾 Objective

  This solution addresses **Challenge 1A** of the Adobe Hackathon. The goal is to process a set of PDF documents and extract a hierarchical **outline** using visual cues (specifically font sizes). The output is a structured JSON file containing:
  - The **document title**
  - A list of headings (H1, H2, H3) with their **text**, **level**, and **page number**

  ---

  ## 🧠 Methodology

  ### 1. **Text Block Extraction**
  Using the `PyMuPDF` (`fitz`) library, the script reads each page of the PDF and captures all text spans, along with their:
  - Font size
  - Font type
  - Bounding box
  - Page number

  These are stored per page to preserve structure.

  ### 2. **Font Size Ranking**
  All unique font sizes from the document are collected and sorted from largest to smallest. Based on the sorted list:
  - The largest size is treated as the **Title**
  - The next three sizes are treated as **H1**, **H2**, and **H3** respectively

  If fewer sizes are present, fallback logic ensures graceful handling.

  ### 3. **Hierarchy Assignment**
  Text spans are then matched to one of the following levels:
  - `Title`: First occurrence of the largest font size
  - `H1`, `H2`, `H3`: Assigned based on size thresholds

  The result is a list of headings with their type and page number.

  ### 4. **Output Format**
  Each PDF results in a `.json` file with the following structure:

  ```json
  {
    "title": "Main Title of the Document",
    "outline": [
      { "level": "H1", "text": "Introduction", "page": 1 },
      { "level": "H2", "text": "Planning Tips", "page": 2 },
      { "level": "H3", "text": "Packing List", "page": 2 }
    ]
  }
  ```
  ---
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
  ## 📦 Prerequisites

  - Docker Desktop installed: https://www.docker.com/products/docker-desktop
  - Git Bash (recommended for Windows users)

  ---

  ## 🛠️ How to Build

  In Git Bash (inside the project folder):

  ```bash
  docker build --platform linux/amd64 -t Challenge_1a .
  ```


  ## 🚀 How to Run

  After building the Docker image, place all your `.pdf` files inside the `input/` folder.

  Then run the extractor:
  - in bash only

  ```bash

  docker run --rm \
    -v "/$PWD/input:/app/input" \
    -v "/$PWD/output:/app/output" \
    --network none Challenge_1a
