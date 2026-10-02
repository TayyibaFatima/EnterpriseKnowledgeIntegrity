import json

import psycopg
from sentence_transformers import SentenceTransformer


INPUT_FILE = "data/chunks.json"

DB_NAME = "enterprise_knowledge_db"
DB_USER = "postgres"
DB_PASSWORD = "tayyiba1234"
DB_HOST = "localhost"
DB_PORT = "5432"

MODEL_NAME = "all-MiniLM-L6-v2"


def main():

    print("Loading chunks...")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    print(f"Chunks loaded: {len(chunks)}")

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Generating embeddings...")

    texts = []

    for chunk in chunks:
        texts.append(chunk["chunk_text"])

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    print("Embeddings generated")

    connection = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    cursor = connection.cursor()

    print("Inserting chunks into PostgreSQL...")

    for i in range(len(chunks)):

        chunk = chunks[i]
        embedding = embeddings[i].tolist()

        cursor.execute(
            """
            INSERT INTO document_chunks (
                chunk_id,
                document_id,
                document_title,
                document_type,
                version,
                document_date,
                source_filename,
                section_index,
                section_heading,
                section_level,
                chunk_index,
                chunk_text,
                word_count,
                embedding
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (chunk_id)
            DO UPDATE SET
                document_id = EXCLUDED.document_id,
                document_title = EXCLUDED.document_title,
                document_type = EXCLUDED.document_type,
                version = EXCLUDED.version,
                document_date = EXCLUDED.document_date,
                source_filename = EXCLUDED.source_filename,
                section_index = EXCLUDED.section_index,
                section_heading = EXCLUDED.section_heading,
                section_level = EXCLUDED.section_level,
                chunk_index = EXCLUDED.chunk_index,
                chunk_text = EXCLUDED.chunk_text,
                word_count = EXCLUDED.word_count,
                embedding = EXCLUDED.embedding
            """,
            (
                chunk["chunk_id"],
                chunk["document_id"],
                chunk["document_title"],
                chunk["document_type"],
                chunk["version"],
                chunk["date"],
                chunk["source_filename"],
                chunk["section_index"],
                chunk["section_heading"],
                chunk["section_level"],
                chunk["chunk_index"],
                chunk["chunk_text"],
                chunk["word_count"],
                embedding
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    print()
    print("========== EMBEDDING SUMMARY ==========")
    print(f"Chunks processed: {len(chunks)}")
    print("Embedding model: all-MiniLM-L6-v2")
    print("Embedding dimensions: 384")
    print("Database: enterprise_knowledge_db")
    print("Table: document_chunks")
    print("Status: Complete")


if __name__ == "__main__":
    main()