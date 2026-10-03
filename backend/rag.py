import chromadb
from sentence_transformers import SentenceTransformer

# 1. Load Sentence-BERT
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Connect to ChromaDB
client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_collection("campusmind")

# 3. Student question
question = "When should I pay my college fees?"

# 4. Convert question into embedding
query_embedding = model.encode([question]).tolist()

# 5. Retrieve relevant information
results = collection.query(
    query_embeddings=query_embedding,
    n_results=3
)

# 6. Combine retrieved chunks as context
context = "\n".join(results["documents"][0])

# 7. Display the retrieved context
print("\nQUESTION:")
print(question)

print("\nRETRIEVED CONTEXT:")
print(context)

print("\n--- RAG CONTEXT READY ---")