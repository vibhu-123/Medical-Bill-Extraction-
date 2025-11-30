# {
#  "cells": [
#   {
#    "cell_type": "code",
#    "execution_count": null,
#    "id": "38113fcc",
#    "metadata": {
#     "vscode": {
#      "languageId": "plaintext"
#     }
#    },
#    "outputs": [],
#    "source": [
#     "# ============================================================\n",
#     "# 🔥 INSTALL DEPENDENCIES\n",
#     "# ============================================================\n",
#     "!pip install google-genai pymupdf pillow requests --quiet\n",
#     "\n",
#     "# ============================================================\n",
#     "# 🔥 IMPORTS\n",
#     "# ============================================================\n",
#     "import fitz  # PyMuPDF\n",
#     "import requests\n",
#     "import json\n",
#     "from google.genai import Client\n",
#     "import base64\n",
#     "\n",
#     "# ============================================================\n",
#     "# 🔥 GEMINI CLIENT\n",
#     "# ============================================================\n",
#     "API_KEY = \"AIzaSyC7-S7s0jhUKGE3xSqMTYoH1I807Cdb2HE\"   # <- PUT YOUR KEY\n",
#     "client = Client(api_key=API_KEY)\n",
#     "\n",
#     "# ============================================================\n",
#     "# 🔥 DOWNLOAD FILE FROM URL\n",
#     "# ============================================================\n",
#     "def download_from_url(url):\n",
#     "    r = requests.get(url)\n",
#     "    if r.status_code != 200:\n",
#     "        raise Exception(\"❌ Cannot download file. Check URL or SAS expiry.\")\n",
#     "    \n",
#     "    ext = url.split(\"?\")[0].split(\".\")[-1].lower()\n",
#     "    \n",
#     "    filename = \"downloaded_file.\" + ext\n",
#     "    with open(filename, \"wb\") as f:\n",
#     "        f.write(r.content)\n",
#     "\n",
#     "    return filename\n",
#     "\n",
#     "# ============================================================\n",
#     "# 🔥 EXTRACT TEXT (PDF or IMAGE)\n",
#     "# ============================================================\n",
#     "def extract_text_from_file(filepath):\n",
#     "    # --- PDF ---\n",
#     "    if filepath.endswith(\".pdf\"):\n",
#     "        print(\"📄 PDF detected — extracting pages...\")\n",
#     "        doc = fitz.open(filepath)\n",
#     "        pages = [p.get_text() for p in doc]\n",
#     "        return pages\n",
#     "\n",
#     "    # --- IMAGE ---\n",
#     "    print(\"🖼 Image detected — sending to Gemini Vision...\")\n",
#     "    with open(filepath, \"rb\") as f:\n",
#     "        b64 = base64.b64encode(f.read()).decode()\n",
#     "\n",
#     "    prompt = \"\"\"\n",
#     "    Extract ALL visible text from this medical bill image.\n",
#     "    Return ONLY text. No markdown. No comments.\n",
#     "    \"\"\"\n",
#     "\n",
#     "    response = client.models.generate_content(\n",
#     "        model=\"models/gemini-2.0-flash\",\n",
#     "        contents=[\n",
#     "            {\"type\": \"input_text\", \"text\": prompt},\n",
#     "            {\"type\": \"input_image\", \"image\": b64}\n",
#     "        ]\n",
#     "    )\n",
#     "\n",
#     "    return [response.text]\n",
#     "\n",
#     "# ============================================================\n",
#     "# 🔥 BILL ITEM EXTRACTION (LLM)\n",
#     "# ============================================================\n",
#     "def extract_bill_items(page_texts):\n",
#     "\n",
#     "    prompt = f\"\"\"\n",
#     "    You are an expert medical bill extraction AI.\n",
#     "\n",
#     "    Extract ALL line items strictly in this JSON structure:\n",
#     "\n",
#     "    {{\n",
#     "      \"pagewise_line_items\": [\n",
#     "        {{\n",
#     "          \"page_no\": \"1\",\n",
#     "          \"page_type\": \"Bill Detail | Final Bill | Pharmacy\",\n",
#     "          \"bill_items\": [\n",
#     "            {{\n",
#     "              \"item_name\": \"string\",\n",
#     "              \"item_rate\": 0,\n",
#     "              \"item_quantity\": 0,\n",
#     "              \"item_amount\": 0\n",
#     "            }}\n",
#     "          ]\n",
#     "        }}\n",
#     "      ]\n",
#     "    }}\n",
#     "\n",
#     "    RULES:\n",
#     "    - No markdown.\n",
#     "    - No comments.\n",
#     "    - No extra fields.\n",
#     "    - item_amount = item_rate * item_quantity\n",
#     "    - Use EXACT item names from bill text\n",
#     "    - If a value is missing, put 0 (never hallucinate)\n",
#     "\n",
#     "    BILL TEXT:\n",
#     "    {page_texts}\n",
#     "    \"\"\"\n",
#     "\n",
#     "    response = client.models.generate_content(\n",
#     "        model=\"models/gemini-2.0-flash\",\n",
#     "        contents=prompt\n",
#     "    )\n",
#     "\n",
#     "    raw = response.text.strip()\n",
#     "    raw = raw.replace(\"```json\", \"\").replace(\"```\", \"\")\n",
#     "\n",
#     "    return json.loads(raw)\n",
#     "\n",
#     "# ============================================================\n",
#     "# 🔥 COMPUTE TOTALS\n",
#     "# ============================================================\n",
#     "def compute_totals(data):\n",
#     "    total_items = 0\n",
#     "    total_amount = 0\n",
#     "\n",
#     "    for page in data[\"pagewise_line_items\"]:\n",
#     "        for item in page[\"bill_items\"]:\n",
#     "            total_items += 1\n",
#     "            total_amount += float(item.get(\"item_amount\", 0))\n",
#     "\n",
#     "    data[\"total_item_count\"] = total_items\n",
#     "    data[\"sub_total_amount\"] = total_amount\n",
#     "    data[\"final_total_amount\"] = total_amount\n",
#     "\n",
#     "    return data\n",
#     "  \n",
#     "def format_final_output(data):\n",
#     "  return {\n",
#     "      \"is_success\": True,\n",
#     "      \"data\": data\n",
#     "  }\n",
#     "\n",
#     "# ============================================================\n",
#     "# 🔥 MAIN FUNCTION — TAKES URL LIKE DATATHON SPEC\n",
#     "# ============================================================\n",
#     "def extract_bill_from_url(request_json):\n",
#     "    url = request_json[\"document\"]\n",
#     "\n",
#     "    print(\"📥 Downloading from URL...\")\n",
#     "    filepath = download_from_url(url)\n",
#     "\n",
#     "    print(\"🔍 Extracting text...\")\n",
#     "    pages = extract_text_from_file(filepath)\n",
#     "\n",
#     "    print(\"🤖 Sending to Gemini LLM...\")\n",
#     "    structure = extract_bill_items(pages)\n",
#     "\n",
#     "    print(\"🧮 Computing totals...\")\n",
#     "    return compute_totals(structure)\n",
#     "\n",
#     "# ============================================================\n",
#     "# 🚀 TEST (Using Datathon sample)\n",
#     "# ============================================================\n",
#     "sample_request = {\n",
#     "    \"document\": \"https://hackrx.blob.core.windows.net/assets/datathon-IIT/Sample%20Document%203.pdf?sv=2025-07-05&spr=https&st=2025-11-28T10%3A08%3A55Z&se=2025-11-30T10%3A08%3A00Z&sr=b&sp=r&sig=S7bEYe%2FswaS7BZPZBiEnc6gXfb9YUH22H%2BBn%2FG2Vycc%3D\"\n",
#     "}\n",
#     "\n",
#     "output = extract_bill_from_url(sample_request)\n",
#     "\n",
#     "print(\"\\n==================== FINAL JSON ====================\")\n",
#     "# print(json.dumps(output, indent=2))\n",
#     "output = extract_bill_from_url(sample_request)\n",
#     "final_output = format_final_output(output)\n",
#     "\n",
#     "print(json.dumps(final_output, indent=2))"
#    ]
#   }
#  ],
#  "metadata": {
#   "language_info": {
#    "name": "python"
#   }
#  },
#  "nbformat": 4,
#  "nbformat_minor": 5
# }
%%writefile main.py
import fitz
import requests
import json
from google.genai import Client
import base64

API_KEY = "PASTE_YOUR_API_KEY_HERE"
client = Client(api_key=API_KEY)

def download_from_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Cannot download file")

    ext = url.split("?")[0].split(".")[-1].lower()
    filename = "downloaded_file." + ext

    with open(filename, "wb") as f:
        f.write(r.content)

    return filename

def extract_text_from_file(filepath):

    if filepath.endswith(".pdf"):
        doc = fitz.open(filepath)
        return [p.get_text() for p in doc]

    with open(filepath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    prompt = "Extract all text from medical bill image."

    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=[
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image": b64}
        ]
    )

    return [response.text]

def extract_bill_items(page_texts):

    prompt = f"""
    Extract bill items in JSON:

    {{
      "pagewise_line_items": [
        {{
          "page_no": "1",
          "page_type": "Bill",
          "bill_items": [
            {{
              "item_name": "string",
              "item_rate": 0,
              "item_quantity": 0,
              "item_amount": 0
            }}
          ]
        }}
      ]
    }}

    TEXT:
    {page_texts}
    """

    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=prompt
    )

    raw = response.text.replace("```json", "").replace("```", "")
    return json.loads(raw)

def compute_totals(data):

    total_items = 0
    total_amount = 0

    for page in data["pagewise_line_items"]:
        for item in page["bill_items"]:
            total_items += 1
            total_amount += float(item.get("item_amount", 0))

    data["total_item_count"] = total_items
    data["sub_total_amount"] = total_amount
    data["final_total_amount"] = total_amount

    return data

def format_final_output(data):
    return {
        "is_success": True,
        "data": data
    }

def extract_bill_from_url(request_json):

    url = request_json["document"]

    filepath = download_from_url(url)
    pages = extract_text_from_file(filepath)
    structure = extract_bill_items(pages)

    return compute_totals(structure)
