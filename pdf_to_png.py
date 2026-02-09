import fitz  
from pathlib import Path
import sys

pdf_path = "Menu.pdf"   
out_path = "Menu.png"   # output from the pdf



def pdf_to_png(pdf_path, out_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=300)  
    pix.save(out_path)

    print("OK ->", out_path)


if __name__ == "__main__":
    pdf_file = Path("Menu.pdf")
    pdf_to_png(pdf_file, out_path="Menu.png")
