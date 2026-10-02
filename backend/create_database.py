import psycopg


DB_USER = "postgres"
DB_PASSWORD = "tayyiba1234"
DB_HOST = "localhost"
DB_PORT = "5432"


connection = psycopg.connect(
    dbname="postgres",
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

connection.autocommit = True

cursor = connection.cursor()

try:
    cursor.execute("CREATE DATABASE enterprise_knowledge_db")
    print("Database enterprise_knowledge_db created successfully")

except psycopg.errors.DuplicateDatabase:
    print("Database enterprise_knowledge_db already exists")

cursor.close()
connection.close()