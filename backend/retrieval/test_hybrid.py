from .hybrid_search import HybridSearch


search_engine = HybridSearch()

question = "What time does hostel attendance close?"

results = search_engine.search(
    question,
    top_k=5
)

print("\n" + "=" * 70)
print("QUESTION:")
print(question)

print("\nHYBRID SEARCH RESULTS:")

for i, result in enumerate(results):

    print(f"\nResult {i + 1}:")
    print("Document:", result["document"])
    print("Hybrid Score:", result["hybrid_score"])
    print("Text:", result["text"])

print("\n" + "=" * 70)