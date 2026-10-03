from pathlib import Path

# Location of our documents
data_folder = Path("data/raw")

# Find all text files
files = data_folder.glob("*.txt")

# Read each document
for file in files:
    print("\n==============================")
    print("DOCUMENT:", file.name)
    print("==============================")

    text = file.read_text(encoding="utf-8")

    print(text)