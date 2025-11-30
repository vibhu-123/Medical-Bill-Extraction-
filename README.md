# Medical-Bill-Extraction-
Medical Bill Extraction &amp; Summarization Solution

README: |
  # Bajaj Health Datathon – AI Bill Extraction Pipeline (URL-Based)

  This repository contains my complete solution for the Bajaj Health Datathon IIT.
  The system extracts structured medical bill data (line items, totals, page structure)
  directly from **PDF or Image URLs**, matching the Datathon's exact request/response format.

  ======================================================================
  PROBLEM SUMMARY
  ======================================================================

  You must build a pipeline that takes a document URL and extracts:

    - All bill line items
    - item_name
    - item_rate
    - item_quantity
    - item_amount
    - page_number
    - page_type
    - sub_total_amount
    - final_total_amount
    - total_item_count

  And the output must match the EXACT JSON schema:

    {
      "is_success": true,
      "data": {
        "pagewise_line_items": [...],
        "total_item_count": 12,
        "sub_total_amount": 15390,
        "final_total_amount": 15390
      }
    }

  ======================================================================
  INPUT FORMAT (REQUIRED BY DATATHON)
  ======================================================================

  The pipeline accepts input strictly in this JSON format:

    {
      "document": "https://example.com/sample.pdf"
    }

  ======================================================================
  SOLUTION ARCHITECTURE (PIPELINE)
  ======================================================================

  Step-by-step flow:

      Input: Document URL
            ↓
      Download File (PDF/Image)
            ↓
      Text Extraction
          - PDF → PyMuPDF (text layer)
          - Image → Gemini OCR
            ↓
      Gemini 2.0 Flash (Structured Extraction)
          - Extract line items from plain text
          - Produce structured JSON
            ↓
      JSON Cleaning (remove markdown/code fences)
            ↓
      Totals Computed in Python (safe, no hallucination)
            ↓
      Final Response in Datathon Format

  ======================================================================
  KEY COMPONENTS
  ======================================================================

  1. URL DOWNLOAD SYSTEM
     - Supports cloud-hosted PDFs and PNG/JPG images
     - SAS-URLs supported

  2. TEXT EXTRACTION
     - PyMuPDF for machine PDFs (most hospital bills)
     - Gemini OCR for images

  3. GEMINI 2.0 FLASH STRUCTURED EXTRACTION
     - Custom prompt ensures:
       - Strict JSON output
       - No markdown
       - No comments
       - No hallucinated fields
       - Exact item_name from bill

  4. JSON SANITIZATION
     - Removes ```json ... ``` artifacts
     - Parses safely

  5. TOTAL COMPUTATION (SAFETY LAYER)
     - sub_total_amount = sum(item_amount per item)
     - final_total_amount = sum(item_amount)
     - Protects against LLM errors

  ======================================================================
  PROJECT STRUCTURE (RAW TEXT)
  ======================================================================

    bill-extractor/
      ├── README.md
      ├── extractor.ipynb              # Main Colab notebook
      ├── src/
      │     ├── extractor.py
      │     ├── ocr.py
      │     ├── parser.py
      │     └── totals.py
      ├── sample_requests/
      │     └── request.json
      ├── sample_outputs/
      │     └── output.json
      └── requirements.txt

  ======================================================================
  INSTALLATION (COLAB OR LOCAL)
  ======================================================================

  pip install google-genai pymupdf pillow requests

  ======================================================================
  SAMPLE REQUEST (URL-BASED)
  ======================================================================

    {
      "document":
      "https://hackrx.blob.core.windows.net/assets/datathonIIT/sample_3.png?sv=..."
    }

  ======================================================================
  SAMPLE RESPONSE (MATCHES DATATHON FORMAT)
  ======================================================================

    {
      "is_success": true,
      "data": {
        "pagewise_line_items": [
          {
            "page_no": "1",
            "page_type": "Bill Detail",
            "bill_items": [
              {
                "item_name": "Consultation",
                "item_rate": 1000.0,
                "item_quantity": 4.0,
                "item_amount": 4000.0
              }
            ]
          }
        ],
        "total_item_count": 12,
        "sub_total_amount": 15390.0,
        "final_total_amount": 15390.0
      }
    }

  ======================================================================
  EXECUTION IN GOOGLE COLAB
  ======================================================================

  1. Open the extractor.ipynb file
  2. Insert your Gemini API Key
  3. Run all cells
  4. Call extract_bill_from_url({ "document": "<URL>" })
  5. Receive final JSON output

  ======================================================================
  LIMITATIONS
  ======================================================================

    • OCR required for badly scanned PDFs (supported)
    • Handwriting not supported
    • Complex pharmacy tabular layouts may need model tuning
    • JSON may contain trailing artifacts (cleaned automatically)

  ======================================================================
  FUTURE IMPROVEMENTS
  ======================================================================

    • Convert into FastAPI deployment
    • Add discount/tax inference layer
    • Auto-detect pharmacy vs bill vs summary pages
    • Add table reconstruction for broken PDFs

  ======================================================================
  CONTACT
  ======================================================================

    Name: Vaibhav Kumar
    Email: 12212217@nitkkr.ac.in
