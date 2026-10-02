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

    connection.autocommit = True

    cursor = connection.cursor()

    cursor.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS document_chunks (
            chunk_id VARCHAR(100) PRIMARY KEY,
            document_id VARCHAR(200) NOT NULL,
            document_title TEXT,
            document_type VARCHAR(100),
            version VARCHAR(100),
            document_date VARCHAR(100),
            source_filename TEXT,
            section_index INTEGER,
            section_heading TEXT,
            section_level INTEGER,
            chunk_index INTEGER,
            chunk_text TEXT NOT NULL,
            word_count INTEGER,
            embedding vector(384)
        )
        """
    )

    cursor.close()
    connection.close()

    print("PostgreSQL connection successful")
    print("pgvector extension enabled")
    print("document_chunks table ready")


if __name__ == "__main__":
    main()