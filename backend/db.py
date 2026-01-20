# backend/db.py
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        database=os.getenv("MYSQL_DB", "dnd"),
        user=os.getenv("MYSQL_USER", "lees"),
        password=os.getenv("MYSQL_PASS", "lees"),
        autocommit=True
    )
