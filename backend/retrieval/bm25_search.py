import json
import re
from rank_bm25 import BM25Okapi


class BM25Search:

    def __init__(self):

        # Load processed chunks
        with open(
            "data/processed/chunks.json",
            "r",
            encoding="utf-8"
        ) as file:

            self.chunks = json.load(file)

        # Get text from every chunk
        self.documents = [
            chunk["text"]
            for chunk in self.chunks
        ]

        # Tokenize documents
        self.tokenized_documents = [
            self.tokenize(text)
            for text in self.documents
        ]

        # Create BM25 index
        self.bm25 = BM25Okapi(
            self.tokenized_documents
        )

    def tokenize(self, text):

        return re.findall(
            r"\b\w+\b",
            text.lower()
        )

    def search(self, query, top_k=3):

        # Convert query into tokens
        query_tokens = self.tokenize(query)

        # Calculate BM25 relevance scores
        scores = self.bm25.get_scores(
            query_tokens
        )

        # Sort results by highest score
        ranked_indexes = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []

        for index in ranked_indexes:

            results.append({
                "chunk_id": self.chunks[index]["chunk_id"],
                "document": self.chunks[index]["document"],
                "text": self.chunks[index]["text"],
                "score": float(scores[index])
            })

        return results