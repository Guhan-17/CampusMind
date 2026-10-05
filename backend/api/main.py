from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Depends,
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
)

from pathlib import Path
from datetime import datetime
import shutil

from backend.retrieval.bm25_search import BM25Search
from backend.generation.rag_generator import RAGGenerator

from backend.auth import (
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    create_access_token,
    verify_token,
)

from backend.process_documents import process_documents


# ============================================================
# CAMPUSMIND API
# ============================================================

app = FastAPI(
    title="CampusMind API",
    description="AI-powered college information assistant",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = Path("backend/uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# RAG SYSTEM
# ============================================================

# Render Free-friendly retrieval
# Uses BM25 instead of SentenceTransformer + PyTorch.

retriever = BM25Search()
generator = RAGGenerator()


# ============================================================
# AUTHENTICATION
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/admin/login"
)


def get_current_admin(
    token: str = Depends(oauth2_scheme)
):
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required.",
        )

    if payload.get("sub") != ADMIN_USERNAME:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin account.",
        )

    return payload


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "CampusMind API is running",
        "status": "online",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.post("/admin/login")
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    if (
        form_data.username != ADMIN_USERNAME
        or form_data.password != ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin username or password.",
        )

    token = create_access_token(
        form_data.username
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
async def ask_question(data: dict):

    question = data.get(
        "question",
        ""
    ).strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:

        results = retriever.search(
            question,
            top_k=3,
        )

        if not results:
            return {
                "answer": (
                    "Sorry, I could not find relevant "
                    "information in the college documents."
                )
            }

        prompt = generator.build_prompt(
            question,
            results,
        )

        answer = generator.generate_answer(
            prompt
        )

        return {
            "answer": answer,
        }

    except Exception as e:

        print("ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="CampusMind could not process the question.",
        )


# ============================================================
# REBUILD KNOWLEDGE BASE
# ============================================================

def rebuild_knowledge_base():

    print("\n==========================================")
    print("REBUILDING CAMPUSMIND KNOWLEDGE BASE")
    print("==========================================")

    # --------------------------------------------------------
    # 1. Process documents
    # --------------------------------------------------------

    print("\n[1/2] Processing documents...")

    process_documents()

    # --------------------------------------------------------
    # 2. Reload BM25 retriever
    # --------------------------------------------------------

    global retriever

    print("\n[2/2] Reloading BM25 retriever...")

    retriever = BM25Search()

    print("\n==========================================")
    print("KNOWLEDGE BASE UPDATED SUCCESSFULLY")
    print("==========================================\n")


# ============================================================
# ADMIN UPLOAD DOCUMENT
# ============================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    admin=Depends(get_current_admin),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    # --------------------------------------------------------
    # Allowed file types
    # --------------------------------------------------------

    allowed_extensions = [
        ".pdf",
        ".txt",
    ]

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are allowed.",
        )

    # --------------------------------------------------------
    # Security: clean filename
    # --------------------------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    file_path = UPLOAD_DIR / safe_filename

    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    try:

        with file_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

    except Exception as e:

        print(
            "UPLOAD ERROR:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Could not save the uploaded document.",
        )

    # --------------------------------------------------------
    # Automatically rebuild knowledge base
    # --------------------------------------------------------

    try:

        rebuild_knowledge_base()

    except Exception as e:

        print(
            "KNOWLEDGE BASE ERROR:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Document uploaded, but the knowledge "
                "base could not be updated."
            ),
        )

    return {
        "message": (
            "Document uploaded and added "
            "to CampusMind successfully."
        ),
        "filename": safe_filename,
        "uploaded_by": admin.get("sub"),
        "status": "processed",
    }


# ============================================================
# LIST UPLOADED DOCUMENTS
# ============================================================

@app.get("/admin/documents")
async def get_documents(
    admin=Depends(get_current_admin),
):

    documents = []

    for file in UPLOAD_DIR.iterdir():

        if not file.is_file():
            continue

        if file.suffix.lower() not in [
            ".txt",
            ".pdf",
        ]:
            continue

        stat = file.stat()

        documents.append({
            "filename": file.name,
            "size": stat.st_size,
            "uploaded_at": datetime.fromtimestamp(
                stat.st_mtime
            ).isoformat(),
        })

    # Newest first
    documents.sort(
        key=lambda x: x["uploaded_at"],
        reverse=True,
    )

    return {
        "documents": documents,
        "count": len(documents),
    }


# ============================================================
# DELETE DOCUMENT
# ============================================================

@app.delete("/admin/documents/{filename}")
async def delete_document(
    filename: str,
    admin=Depends(get_current_admin),
):

    # --------------------------------------------------------
    # Security check
    # --------------------------------------------------------

    safe_filename = Path(
        filename
    ).name

    if safe_filename != filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    file_path = UPLOAD_DIR / safe_filename

    # --------------------------------------------------------
    # Check file exists
    # --------------------------------------------------------

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if not file_path.is_file():

        raise HTTPException(
            status_code=400,
            detail="Invalid document.",
        )

    # --------------------------------------------------------
    # Delete document
    # --------------------------------------------------------

    try:

        file_path.unlink()

        print(
            f"Deleted document: {safe_filename}"
        )

    except Exception as e:

        print(
            "DELETE ERROR:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Could not delete document.",
        )

    # --------------------------------------------------------
    # Rebuild knowledge base
    # --------------------------------------------------------

    try:

        rebuild_knowledge_base()

    except Exception as e:

        print(
            "REBUILD ERROR:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Document deleted, but the knowledge "
                "base could not be rebuilt."
            ),
        )

    return {
        "message": "Document deleted successfully.",
        "filename": safe_filename,
        "deleted_by": admin.get("sub"),
        "knowledge_base": "updated",
    }


# ============================================================
# MANUAL REBUILD
# ============================================================

@app.post("/admin/rebuild")
async def manual_rebuild(
    admin=Depends(get_current_admin),
):

    try:

        rebuild_knowledge_base()

        return {
            "message": "Knowledge base rebuilt successfully.",
            "rebuilt_by": admin.get("sub"),
            "status": "success",
        }

    except Exception as e:

        print(
            "MANUAL REBUILD ERROR:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Knowledge base rebuild failed.",
        )