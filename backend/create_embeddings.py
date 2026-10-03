import json
from sentence_transformers import SentenceTransformer

# Load the Sentence-BERT model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load our processed chunks
with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Extract the text from each chunk
texts = [chunk["text"] for chunk in chunks]

# Convert text into embeddings
embeddings = model.encode(texts)

# Display information
print("Number of chunks:", len(texts))
print("Embedding shape:", embeddings.shape)

# Show the first embedding
print("\nFirst chunk:")
print(texts[0])

print("\nFirst embedding:")
print(embeddings[0])