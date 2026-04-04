import psycopg

from config import DB_URI


def get_connection():
    return psycopg.connect(DB_URI)


def get_existing_image_names(conn, table_name=None) -> set[str]:
    try:
        with conn.cursor() as cur:
            if table_name is None:
                cur.execute(
                    "SELECT table_name FROM information_schema.columns WHERE column_name = 'img_name'"
                )
                tables = [row[0] for row in cur.fetchall()]
                if len(tables) > 1:
                    raise ValueError("Multiple tables found with 'img_name' column.")
                elif not tables:
                    return set()
                table_name = tables[0]

            cur.execute(f"SELECT img_name FROM {table_name}")
            return {row[0] for row in cur.fetchall()}
    except psycopg.Error:
        return set()
