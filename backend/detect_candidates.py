import psycopg


DB_NAME = "enterprise_knowledge_db"
DB_USER = "postgres"
DB_PASSWORD = "tayyiba1234"
DB_HOST = "localhost"
DB_PORT = "5432"

TOP_K = 5
MIN_SIMILARITY = 0.45


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
            chunk_id,
            document_id,
            document_title,
            section_heading,
            embedding
        FROM document_chunks
        WHERE embedding IS NOT NULL
        ORDER BY chunk_id
        """
    )

    chunks = cursor.fetchall()

    print(f"Chunks loaded: {len(chunks)}")
    print("Finding candidate relationships...")

    candidate_count = 0

    for chunk in chunks:

        (
            chunk_id,
            document_id,
            document_title,
            section_heading,
            embedding
        ) = chunk

        cursor.execute(
            """
            SELECT
                chunk_id,
                document_id,
                document_title,
                section_heading,
                1 - (embedding <=> %s::vector) AS similarity
            FROM document_chunks
            WHERE
                embedding IS NOT NULL
                AND chunk_id != %s
                AND document_id != %s
                AND 1 - (embedding <=> %s::vector) >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (
                embedding,
                chunk_id,
                document_id,
                embedding,
                MIN_SIMILARITY,
                embedding,
                TOP_K
            )
        )

        related_chunks = cursor.fetchall()

        for related in related_chunks:

            (
                related_chunk_id,
                related_document_id,
                related_document_title,
                related_section_heading,
                similarity
            ) = related

            if chunk_id < related_chunk_id:

                cursor.execute(
                    """
                    INSERT INTO candidate_pairs (
                        chunk_id_a,
                        chunk_id_b,
                        document_id_a,
                        document_id_b,
                        document_title_a,
                        document_title_b,
                        section_heading_a,
                        section_heading_b,
                        similarity
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    ON CONFLICT (chunk_id_a, chunk_id_b)
                    DO UPDATE SET
                        similarity = EXCLUDED.similarity
                    """,
                    (
                        chunk_id,
                        related_chunk_id,
                        document_id,
                        related_document_id,
                        document_title,
                        related_document_title,
                        section_heading,
                        related_section_heading,
                        similarity
                    )
                )

                candidate_count += 1

    connection.commit()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM candidate_pairs
        """
    )

    total_candidates = cursor.fetchone()[0]

    print()
    print("========== CANDIDATE DETECTION SUMMARY ==========")
    print(f"Chunks processed: {len(chunks)}")
    print(f"Similarity threshold: {MIN_SIMILARITY}")
    print(f"Top candidates per chunk: {TOP_K}")
    print(f"Candidate relationships: {total_candidates}")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()