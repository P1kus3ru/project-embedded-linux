import mysql.connector
import os
from dotenv import load_dotenv

# ===== CONFIG =====
load_dotenv()
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "lees")
DB_PASS = os.getenv("MYSQL_PASS", "lees")
DB_NAME = os.getenv("MYSQL_DB", "dnd")

# ===== CONNECT WITHOUT DB (to create it) =====
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS
)
cursor = conn.cursor()

cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
cursor.execute(f"CREATE DATABASE {DB_NAME}")
cursor.execute(f"USE {DB_NAME}")

# Load SQL from file
for sql_file in ["schema.sql", "dummy.sql"]:
    with open(sql_file, "r") as f:
        sql = f.read()
        for statement in sql.split(";"):
            if statement.strip():
                cursor.execute(statement)

conn.commit()
cursor.close()
conn.close()

print("✅ Database and dummy data successfully created!")