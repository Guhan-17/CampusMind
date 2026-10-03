import json

from backend.retrieval.hybrid_search import HybridSearch


# Load evaluation questions
with open(
    "evaluation/test_questions.json",
    "r",
    encoding="utf-8"
) as file:
    test_questions = json.load(file)


# Initialize hybrid search
search_engine = HybridSearch()

total_questions = len(test_questions)
correct = 0


print("\n" + "=" * 60)
print("CampusMind Retrieval Evaluation")
print("=" * 60)


for index, item in enumerate(test_questions, start=1):

    question = item["question"]
    expected_document = item["expected_document"]

    print(f"\nQuestion {index}:")
    print(question)

    results = search_engine.search(
        question,
        top_k=3
    )

    retrieved_documents = [
        result["document"]
        for result in results
    ]

    print("Retrieved:")
    print(retrieved_documents)

    print("Expected:")
    print(expected_document)

    if expected_document in retrieved_documents:
        print("Result: PASS")
        correct += 1
    else:
        print("Result: FAIL")


accuracy = (correct / total_questions) * 100


print("\n" + "=" * 60)
print("Evaluation Summary")
print("=" * 60)

print(f"Total Questions : {total_questions}")
print(f"Correct         : {correct}")
print(f"Incorrect       : {total_questions - correct}")
print(f"Accuracy        : {accuracy:.2f}%")

print("=" * 60)