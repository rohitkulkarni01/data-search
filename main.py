import os
import sys
import subprocess
import sqlite3
import shutil
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from parser import setup_database, parse_pdf, parse_docx, parse_dxf, parse_step, parse_txt

app = FastAPI(title="Local Document & CAD Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create workspace to save uploaded files
workspace_dir = os.path.abspath("workspace")
os.makedirs(workspace_dir, exist_ok=True)
app.mount("/files", StaticFiles(directory=workspace_dir), name="files")

class SearchResult(BaseModel):
    file_name: str
    file_path: str
    file_type: str
    metadata_type: str
    metadata_value: str
    highlight: str

@app.post("/browser_index")
async def browser_index(
    files: List[UploadFile] = File(...),
    paths: List[str] = Form(...)
):
    setup_database()
    conn = sqlite3.connect("search_index.db")
    cursor = conn.cursor()
    indexed_count = 0
    
    for file, relative_path in zip(files, paths):
        dest_path = os.path.join(workspace_dir, relative_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        ext = dest_path.lower().split('.')[-1]
        parsed_chunks = []
        
        if ext == 'pdf': parsed_chunks = parse_pdf(dest_path)
        elif ext == 'docx': parsed_chunks = parse_docx(dest_path)
        elif ext == 'dxf': parsed_chunks = parse_dxf(dest_path)
        elif ext in ['step', 'stp']: parsed_chunks = parse_step(dest_path)
        elif ext in ['txt', 'csv']: parsed_chunks = parse_txt(dest_path)
        
        # Save relative_path to DB for clean frontend linking
        insert_batch = [
            (file.filename, relative_path, ext, content, m_type, m_val)
            for content, m_type, m_val in parsed_chunks
        ]
        
        if insert_batch:
            cursor.executemany("INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?)", insert_batch)
            indexed_count += len(insert_batch)
            
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Successfully indexed {indexed_count} text blocks from {len(files)} files."}

@app.get("/serve_pdf")
def serve_pdf(path: str = Query(...)):
    abs_path = os.path.abspath(os.path.join(workspace_dir, path))
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(abs_path, media_type='application/pdf')

@app.get("/open_file")
def open_file_native(path: str = Query(...)):
    abs_path = os.path.abspath(os.path.join(workspace_dir, path))
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="File not found on disk.")
    try:
        if sys.platform == "win32": os.startfile(abs_path)
        elif sys.platform == "darwin": subprocess.call(["open", abs_path])
        else: subprocess.call(["xdg-open", abs_path])
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_model=List[SearchResult])
def search_documents(q: str = Query(...)):
    if not os.path.exists("search_index.db"): return []
    
    conn = sqlite3.connect("search_index.db")
    cursor = conn.cursor()
    query = """
    SELECT file_name, file_path, file_type, metadata_type, metadata_value,
           snippet(documents, 3, '<em class="bg-yellow-200 font-bold px-1 rounded">', '</em>', '...', 15) as highlight
    FROM documents WHERE documents MATCH ? ORDER BY rank LIMIT 100
    """
    try:
        cursor.execute(query, (f"{q}*",))
        results = [
            SearchResult(file_name=row[0], file_path=row[1], file_type=row[2], 
                         metadata_type=row[3], metadata_value=row[4], highlight=row[5]) 
            for row in cursor.fetchall()
        ]
    except: results = []
    conn.close()
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)