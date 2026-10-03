from pathlib import Path
import json
import re


def process_documents():

    # ========================================================
    # LOCATIONS
    # ========================================================

    raw_folder = Path("data/raw")
    upload_folder = Path("backend/uploads")
    output_folder = Path("data/processed")

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    chunks = []

    # ========================================================
    # PROCESS TEXT FILE
    # ========================================================

    def process_file(file):

        print(f"Processing: {file}")

        text = file.read_text(
            encoding="utf-8"
        )

        # Clean spaces and blank lines
        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        # Split into sentences
        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            chunk = {
                "chunk_id": f"C{len(chunks) + 1:03d}",
                "document": file.name,
                "text": sentence
            }

            chunks.append(chunk)

    # ========================================================
    # PROCESS COLLEGE DOCUMENTS
    # ========================================================

    print("\nProcessing documents from data/raw...")

    if raw_folder.exists():

        for file in raw_folder.glob("*.txt"):

            process_file(file)

    # ========================================================
    # PROCESS UPLOADED DOCUMENTS
    # ========================================================

    print("\nProcessing uploaded documents...")

    if upload_folder.exists():

        for file in upload_folder.glob("*.txt"):

            process_file(file)

    # ========================================================
    # SAVE CHUNKS
    # ========================================================

    output_file = (
        output_folder /
        "chunks.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chunks,
            f,
            indent=4,
            ensure_ascii=False
        )

    # ========================================================
    # RESULT
    # ========================================================

    print("\n==========================================")
    print("DOCUMENT PROCESSING COMPLETE")
    print("==========================================")

    print(
        "Total chunks created :",
        len(chunks)
    )

    print(
        "Saved to             :",
        output_file
    )

    return True


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    process_documents()