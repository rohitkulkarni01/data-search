import os
import sqlite3
import re
import pymupdf
import docx
import ezdxf

def setup_database():
    conn = sqlite3.connect("search_index.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS documents")
    cursor.execute("""
    CREATE VIRTUAL TABLE documents USING fts5(
        file_name, file_path, file_type, content, metadata_type, metadata_value
    )
    """)
    conn.commit()
    conn.close()

def parse_pdf(file_path):
    docs = []
    try:
        doc = pymupdf.open(file_path)
        for page_num in range(len(doc)):
            text = doc.load_page(page_num).get_text("text").strip()
            if text: docs.append((text, "page", str(page_num + 1)))
    except Exception: pass
    return docs

def parse_docx(file_path):
    docs = []
    try:
        doc = docx.Document(file_path)
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if text: docs.append((text, "paragraph", str(i + 1)))
    except Exception: pass
    return docs

def parse_dxf(file_path):
    docs = []
    try:
        msp = ezdxf.readfile(file_path).modelspace()
        for entity in msp.query('TEXT MTEXT'):
            text = entity.dxf.text.strip() if entity.dxftype() == 'TEXT' else entity.text.strip()
            if text:
                coords = f"X: {entity.dxf.insert.x:.2f}, Y: {entity.dxf.insert.y:.2f}"
                docs.append((text, "coordinates", coords))
    except Exception: pass
    return docs

def parse_step(file_path):
    docs = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            matches = re.findall(r"PRODUCT\('([^']+)','([^']*)'", content)
            for i, match in enumerate(matches):
                part_name = match[0].strip()
                description = match[1].strip()
                if part_name:
                    text = f"3D Part: {part_name}" + (f" ({description})" if description else "")
                    docs.append((text, "3D Component", f"Assembly Item #{i+1}"))
    except Exception: pass
    return docs

def parse_txt(file_path):
    docs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if line.strip(): docs.append((line.strip(), "line", str(i + 1)))
    except Exception: pass
    return docs