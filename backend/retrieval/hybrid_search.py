from .vector_search import VectorSearch
from .bm25_search import BM25Search


class HybridSearch:

    def __init__(self):

        # Initialize both retrieval systems
        self.vector_search = VectorSearch()
        self.bm25_search = BM25Search()

    def search(self, query, top_k=3):

        # ========================================================
        # 1. VECTOR SEARCH
        # ========================================================

        vector_results = self.vector_search.search(
            query,
            top_k=10
        )

        # ========================================================
        # 2. BM25 SEARCH
        # ========================================================

        bm25_results = self.bm25_search.search(
            query,
            top_k=10
        )

        # ========================================================
        # 3. COMBINE RESULTS
        # ========================================================

        combined = {}

        # --------------------------------------------------------
        # Add Vector Search results
        # --------------------------------------------------------

        vector_documents = vector_results.get(
            "documents",
            [[]]
        )

        vector_metadatas = vector_results.get(
            "metadatas",
            [[]]
        )

        if vector_documents and vector_documents[0]:

            for rank, document in enumerate(
                vector_documents[0],
                start=1
            ):

                metadata = {}

                if (
                    vector_metadatas
                    and len(vector_metadatas[0]) >= rank
                ):
                    metadata = vector_metadatas[0][rank - 1]

                combined[document] = {
                    "text": document,
                    "document": metadata.get(
                        "document",
                        "unknown"
                    ),
                    "vector_rank": rank,
                    "bm25_rank": None,
                }

        # --------------------------------------------------------
        # Add BM25 results
        # --------------------------------------------------------

        for rank, result in enumerate(
            bm25_results,
            start=1
        ):

            text = result["text"]

            if text not in combined:

                combined[text] = {
                    "text": text,
                    "document": result.get(
                        "document",
                        "unknown"
                    ),
                    "vector_rank": None,
                    "bm25_rank": rank,
                }

            else:

                combined[text]["bm25_rank"] = rank

        # ========================================================
        # 4. WEIGHTED RECIPROCAL RANK FUSION
        # ========================================================

        for item in combined.values():

            score = 0.0

            # Vector search = 70%
            if item["vector_rank"] is not None:

                score += 0.7 * (
                    1 / (
                        60 + item["vector_rank"]
                    )
                )

            # BM25 keyword search = 30%
            if item["bm25_rank"] is not None:

                score += 0.3 * (
                    1 / (
                        60 + item["bm25_rank"]
                    )
                )

            item["hybrid_score"] = score

        # ========================================================
        # 5. SORT BY HYBRID SCORE
        # ========================================================

        results = sorted(
            combined.values(),
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        # ========================================================
        # 6. REMOVE VERY WEAK RESULTS
        # ========================================================

        # If a result appears in neither search system,
        # it should never reach the generator.
        results = [
            item
            for item in results
            if (
                item["vector_rank"] is not None
                or item["bm25_rank"] is not None
            )
        ]

        # ========================================================
        # 7. RETURN TOP RESULTS
        # ========================================================

        return results[:top_k]