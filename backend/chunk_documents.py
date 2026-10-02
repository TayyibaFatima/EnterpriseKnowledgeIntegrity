import json
import re
from pathlib import Path


INPUT_FILE = Path("data/documents_metadata.json")
OUTPUT_FILE = Path("data/chunks.json")

TARGET_WORDS = 180
MAX_WORDS = 250
MIN_WORDS = 40


def split_into_paragraphs(text):
    paragraphs = re.split(r"\n\s*\n", text)
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def split_large_text(text, max_words):
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])

        if chunk.strip():
            chunks.append(chunk.strip())

    return chunks


def create_chunks(section_text):
    paragraphs = split_into_paragraphs(section_text)

    if not paragraphs:
        return []

    chunks = []
    current = []
    current_words = 0

    for paragraph in paragraphs:
        paragraph_words = len(paragraph.split())

        if paragraph_words > MAX_WORDS:

            if current:
                chunks.append(" ".join(current))
                current = []
                current_words = 0

            large_chunks = split_large_text(paragraph, MAX_WORDS)
            chunks.extend(large_chunks)

        elif current_words + paragraph_words <= TARGET_WORDS:

            current.append(paragraph)
            current_words += paragraph_words

        else:

            if current:
                chunks.append(" ".join(current))

            current = [paragraph]
            current_words = paragraph_words

    if current:
        chunks.append(" ".join(current))

    return chunks


def main():

    print("Loading document metadata...")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    all_chunks = []
    chunk_number = 1

    for document in documents:

        document_id = document["document_id"]

        for section_index, section in enumerate(document["sections"]):

            # Skip the document metadata/header section.
            # The first level-1 heading is usually followed by
            # metadata such as version, owner, classification, etc.
            if section_index == 0 and section["level"] == 1:
                continue

            section_text = section["text"].strip()

            if not section_text:
                continue

            section_chunks = create_chunks(section_text)

            for chunk_index, chunk_text in enumerate(section_chunks):

                # Avoid creating tiny standalone chunks.
                # Attach them to the previous chunk from the same document.
                if len(chunk_text.split()) < MIN_WORDS:

                    if (
                        all_chunks
                        and all_chunks[-1]["document_id"] == document_id
                    ):
                        all_chunks[-1]["chunk_text"] += " " + chunk_text

                        all_chunks[-1]["word_count"] = len(
                            all_chunks[-1]["chunk_text"].split()
                        )

                    continue

                chunk = {
                    "chunk_id": f"chunk_{chunk_number:05d}",
                    "document_id": document_id,
                    "document_title": document["document_title"],
                    "document_type": document["document_type"],
                    "version": document["version"],
                    "date": document["date"],
                    "source_filename": document["filename"],
                    "section_index": section_index,
                    "section_heading": section["heading"],
                    "section_level": section["level"],
                    "chunk_index": chunk_index,
                    "chunk_text": chunk_text,
                    "word_count": len(chunk_text.split())
                }

                all_chunks.append(chunk)
                chunk_number += 1

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            all_chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    total_words = sum(
        chunk["word_count"]
        for chunk in all_chunks
    )

    print()
    print("========== CHUNKING SUMMARY ==========")
    print(f"Documents processed: {len(documents)}")
    print(f"Chunks created: {len(all_chunks)}")
    print(f"Total chunk words: {total_words}")
    print(f"Output: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()