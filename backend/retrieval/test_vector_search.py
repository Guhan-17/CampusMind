
from .vector_search import VectorSearch
search_engine = VectorSearch()

question = "When should I pay my college fees?"

results = search_engine.search(
    question,
    top_k=3
)

print("\nQUESTION:")
print(question)

print("\nRETRIEVED RESULTS:")

for i, document in enumerate(results["documents"][0]):

    print(f"\nResult {i + 1}:")
    print(document)

    print(
    "Metadata:",
    results["metadatas"][0][i])