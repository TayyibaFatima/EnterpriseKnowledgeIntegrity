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
        """
        CREATE TABLE IF NOT EXISTS candidate_pairs (
            candidate_id SERIAL PRIMARY KEY,
            chunk_id_a VARCHAR(100) NOT NULL,
            chunk_id_b VARCHAR(100) NOT NULL,
            document_id_a VARCHAR(200),
            document_id_b VARCHAR(200),
            document_title_a TEXT,
            document_title_b TEXT,
            section_heading_a TEXT,
            section_heading_b TEXT,
            similarity FLOAT,
            status VARCHAR(50) DEFAULT 'pending',

            UNIQUE(chunk_id_a, chunk_id_b)
        )
        """
    )

    cursor.close()
    connection.close()

    print("candidate_pairs table ready")


if __name__ == "__main__":
    main()