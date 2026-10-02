import psycopg
from sentence_transformers import SentenceTransformer


DB_NAME = "enterprise_knowledge_db"
DB_USER = "postgres"
DB_PASSWORD = "tayyiba1234"
DB_HOST = "localhost"
DB_PORT = "5432"

MODEL_NAME = "all-MiniLM-L6-v2"


def main():

    query = input("Enter your search query: ").strip()

    if not query:
        print("Query cannot be empty.")
        return

    print()
    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    connection = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            chunk_id,
            document_title,
            document_type,
            section_heading,
            chunk_text,
            1 - (embedding <=> %s::vector) AS similarity
        FROM document_chunks
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT 5
        """,
        (query_embedding, query_embedding)
    )

    results = cursor.fetchall()

    print()
    print("========== SEMANTIC SEARCH RESULTS ==========")

    for i, row in enumerate(results, start=1):

        chunk_id = row[0]
        document_title = row[1]
        document_type = row[2]
        section_heading = row[3]
        chunk_text = row[4]
        similarity = row[5]

        print()
        print(f"--- Result {i} ---")
        print("Chunk ID:", chunk_id)
        print("Document:", document_title)
        print("Type:", document_type)
        print("Section:", section_heading)
        print("Similarity:", round(similarity, 4))
        print("Text:", chunk_text[:500])

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()