import chromadb
from sentence_transformers import SentenceTransformer


class VectorSearch:

    def __init__(self):

        # ========================================================
        # LOAD SENTENCE-BERT MODEL
        # ========================================================

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        # ========================================================
        # CONNECT TO CHROMADB
        # ========================================================

        self.client = chromadb.PersistentClient(
            path="data/chroma_db"
        )

        self.collection = self.client.get_collection(
            name="campusmind"
        )

    # ============================================================
    # VECTOR SEARCH
    # ============================================================

    def search(
        self,
        query,
        top_k=10
    ):

        # --------------------------------------------------------
        # Convert question into embedding
        # --------------------------------------------------------

        query_embedding = self.model.encode(
            [query]
        ).tolist()

        # --------------------------------------------------------
        # Search ChromaDB
        # --------------------------------------------------------

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        return results