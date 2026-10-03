import json
import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# CREATE / REBUILD VECTOR DATABASE
# ============================================================

def create_vector_db():

    print("\n==========================================")
    print("Creating vector database...")
    print("==========================================")

    # --------------------------------------------------------
    # 1. Load Sentence-BERT
    # --------------------------------------------------------

    print("Loading Sentence-BERT model...")

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    # --------------------------------------------------------
    # 2. Load processed chunks
    # --------------------------------------------------------

    chunks_file = "data/processed/chunks.json"

    with open(
        chunks_file,
        "r",
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)

    if not chunks:

        print("No chunks found.")

        return False

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # --------------------------------------------------------
    # 3. Generate embeddings
    # --------------------------------------------------------

    print(
        f"Generating embeddings for {len(texts)} chunks..."
    )

    embeddings = model.encode(
        texts
    ).tolist()

    # --------------------------------------------------------
    # 4. Connect to ChromaDB
    # --------------------------------------------------------

    client = chromadb.PersistentClient(
        path="data/chroma_db"
    )

    # --------------------------------------------------------
    # 5. Delete old collection
    # --------------------------------------------------------
    # This prevents duplicate chunk IDs when rebuilding.
    # --------------------------------------------------------

    try:

        client.delete_collection(
            name="campusmind"
        )

        print("Old vector collection removed.")

    except Exception:

        print("No previous collection found.")

    # --------------------------------------------------------
    # 6. Create fresh collection
    # --------------------------------------------------------

    collection = client.get_or_create_collection(
        name="campusmind"
    )

    # --------------------------------------------------------
    # 7. Prepare metadata
    # --------------------------------------------------------

    metadatas = [
        {
            "document": chunk["document"]
        }
        for chunk in chunks
    ]

    ids = [
        chunk["chunk_id"]
        for chunk in chunks
    ]

    # --------------------------------------------------------
    # 8. Store vectors
    # --------------------------------------------------------

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    # --------------------------------------------------------
    # 9. Result
    # --------------------------------------------------------

    print("\n==========================================")
    print("VECTOR DATABASE CREATED")
    print("==========================================")

    print(
        "Number of stored documents:",
        collection.count()
    )

    print("==========================================\n")

    return True


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    create_vector_db()