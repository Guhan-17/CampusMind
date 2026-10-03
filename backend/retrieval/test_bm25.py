from .bm25_search import BM25Search


search_engine = BM25Search()

question = "When should I pay my college fees?"

results = search_engine.search(
    question,
    top_k=3
)

print("\nQUESTION:")
print(question)

print("\nBM25 RESULTS:")

for i, result in enumerate(results):

    print(f"\nResult {i + 1}:")
    print("Document:", result["document"])
    print("Score:", result["score"])
    print("Text:", result["text"])