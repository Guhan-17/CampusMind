from .rag_generator import RAGGenerator
from backend.retrieval.hybrid_search import HybridSearch


question = "When should I pay my college fees?"

# 1. Hybrid search
search_engine = HybridSearch()

results = search_engine.search(
    question,
    top_k=3
)

# 2. Create RAG generator
rag = RAGGenerator()

# 3. Build prompt using retrieved context
prompt = rag.build_prompt(
    question,
    results
)

# 4. Send prompt to Ollama
answer = rag.generate_answer(prompt)

print("\n==============================")
print("QUESTION")
print("==============================")
print(question)

print("\n==============================")
print("FINAL ANSWER")
print("==============================")
print(answer)