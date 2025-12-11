import pdfplumber
import re
import csv
import unicodedata
import os

pdf_path = "stocks/1 - Portfolio of 503 stocks in S&P 500.pdf"
output_dir = "memo"
output_csv = os.path.join(output_dir, "companies.csv")

os.makedirs(output_dir, exist_ok=True)

all_text = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            page_text = unicodedata.normalize("NFKC", page_text)
            all_text += page_text + "\n"

pattern = r"(?:\d+\)\s*)?([A-Z]{1,5}):\s*([A-Za-z0-9 ,.'\-&]+)"
matches = re.findall(pattern, all_text)

with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=";")
    writer.writerow(["Code", "Company"])
    for code, company in matches:
        company = company.strip()
        company = re.sub(r'^\d+\s*', '', company)
        writer.writerow([code, company])
        print(f"{code}: {company}")
