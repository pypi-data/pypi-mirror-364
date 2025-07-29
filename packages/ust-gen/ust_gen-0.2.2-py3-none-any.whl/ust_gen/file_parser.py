import PyPDF2
import pandas as pd

def parse_pdf(filepath: str) -> str:
    text = ""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def parse_excel(filepath: str) -> str:
    df_dict = pd.read_excel(filepath, sheet_name=None)
    all_text = ""
    for sheet, df in df_dict.items():
        all_text += df.to_string(index=False) + "\n"
    return all_text
