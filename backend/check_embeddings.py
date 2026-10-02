import psycopg


DB_NAME = "enterprise_knowledge_db"
DB_USER = "postgres"
DB_PASSWORD = "tayyiba1234"
DB_HOST = "localhost"
DB_PORT = "5432"


def main():

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
            COUNT(*) AS total_chunks,
            COUNT(embedding) AS chunks_with_embeddings
        FROM document_chunks
        """
    )

    result = cursor.fetchone()

    print("Total chunks:", result[0])
    print("Chunks with embeddings:", result[1])

    cursor.execute(
        """
        SELECT
            chunk_id,
            document_title,
            section_heading,
            word_count
        FROM document_chunks
        ORDER BY chunk_id
        LIMIT 5
        """
    )

    print()
    print("Sample records:")

    for row in cursor.fetchall():
        print(row)

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()