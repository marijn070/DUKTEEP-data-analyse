import psycopg

from config import DB_URI


def get_connection():
    return psycopg.connect(DB_URI)


def get_existing_image_names(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT img_name FROM embeddings")
        return {row[0] for row in cur.fetchall()}
