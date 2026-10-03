import json

from backend.retrieval.hybrid_search import HybridSearch
from backend.generation.rag_generator import RAGGenerator


# --------------------------------------------------
# Load test questions
# --------------------------------------------------

with open(
    "evaluation/test_questions.json",
    "r",
    encoding="utf-8"
) as file:
    test_questions = json.load(file)


# --------------------------------------------------
# Initialize components
# --------------------------------------------------

search_engine = HybridSearch()
rag_generator = RAGGenerator()


print("\n" + "=" * 70)
print("CampusMind RAG Evaluation")
print("=" * 70)


# --------------------------------------------------
# Run evaluation
# --------------------------------------------------

for index, item in enumerate(test_questions, start=1):

    question = item["question"]

    print(f"\nQuestion {index}")
    print("-" * 70)
    print(question)

    # 1. Retrieve relevant documents
    results = search_engine.search(
        question,
        top_k=3
    )

    # 2. Build RAG prompt
    prompt = rag_generator.build_prompt(
        question,
        results
    )

    # 3. Generate answer using Ollama
    answer = rag_generator.generate_answer(
        prompt
    )

    print("\nGenerated Answer:")
    print(answer.strip())


print("\n" + "=" * 70)
print("RAG Evaluation Complete")
print("=" * 70)