import chromadb
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to existing database
client = chromadb.PersistentClient(path="data/chroma_db")

collection = client.get_collection("campusmind")

# Student question
question = "When should I pay my college fees?"

# Convert question into an embedding
query_embedding = model.encode([question]).tolist()

# Search ChromaDB
results = collection.query(
    query_embeddings=query_embedding,
    n_results=3
)

# Display results
print("\nStudent Question:")
print(question)

print("\nMost Relevant Information:\n")

for i, document in enumerate(results["documents"][0]):
    print(f"Result {i + 1}:")
    print(document)
    print("Source:", results["metadatas"][0][i]["document"])
    print()
    