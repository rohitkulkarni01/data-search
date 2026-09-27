Universal Document & CAD Search Engine
A lightweight, local search engine designed to instantly locate text and metadata across standard documents and complex engineering CAD files. It extracts contextual data (like X/Y coordinates from DXFs and page numbers from PDFs) and allows you to open the exact location of your search result in one click.

Features
Multi-Format Support: Searches inside .pdf, .docx, .txt, .csv, .dxf (2D CAD), and .step (3D CAD).

Smart Context Extraction: Returns the exact page number for PDFs, paragraph number for Word docs, X/Y spatial coordinates for 2D CAD, and assembly names for 3D CAD.

Blazing Fast Search: Uses an embedded SQLite FTS5 database with inverted indexing for millisecond response times.

Keyword Highlighting: Automatically extracts surrounding text and highlights the exact keyword match in the UI.

Smart File Opener: Clicking a PDF opens it directly in the browser to the exact page. Clicking a CAD or Word file commands your OS to open it in your native desktop application (e.g., AutoCAD, MS Word).

Search History: Automatically saves your recent searches locally for quick access.

Tech Stack
Backend: Python, FastAPI, Uvicorn

Database: SQLite (FTS5 Extension)

Frontend: HTML5, Vanilla JavaScript, Tailwind CSS

Parsers: pymupdf (PDF), python-docx (Word), ezdxf (2D CAD), re (3D STEP ASCII)

Project Structure
Plaintext
document_search_poc/
├── main.py              # FastAPI server and OS routing logic
├── parser.py            # File parsing and SQLite FTS5 database setup
├── index.html           # Tailwind CSS frontend UI
├── requirements.txt     # Python dependencies
├── generate_data.py     # (Optional) Script to generate sample CAD/Doc data
└── workspace/           # (Auto-generated) Stores indexed files
Installation & Setup
Install Python: Ensure you have Python 3.8 or higher installed on your system.

Set up a Virtual Environment (Optional but recommended):

Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:
Create a requirements.txt file (or install directly) with the following packages:

Bash
pip install fastapi uvicorn ezdxf pymupdf python-docx python-multipart
Usage
Start the Backend Server:
Open your terminal in the project directory and run:

Bash
python main.py
The server will start running on [http://127.0.0.1:8000](http://127.0.0.1:8000).

Open the Frontend:
Double-click the index.html file to open it in your standard web browser (Chrome, Edge, Safari, etc.).

Index Your Files:

Click the Select Folder to Index button in the top right corner.

Select a folder on your computer containing your documents and CAD files.

The system will copy them to a local workspace, parse them, and build the search index. Wait for the "Indexing Complete" popup.

Search:

Type a keyword (e.g., "HVAC", "Titanium", "Architecture") and hit Search.

Review the highlighted snippets and metadata.

Click Open Location to launch the file and jump straight to your data.
