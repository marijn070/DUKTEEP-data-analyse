import os
import sys

from deepface import DeepFace

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import get_connection

if __name__ == "__main__":
    # Test direct pgvector connection
    with get_connection() as conn:
        # try:
        #     with conn.cursor() as cur:
        #         cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        #         cur.execute("CREATE TABLE IF NOT EXISTS test (embedding vector(128));")
        #         conn.commit()
        # except Exception as e:
        #     print(f"Direct pgvector error: {e}")
        #     conn.rollback()

        try:
            result = DeepFace.register(
                img="known_faces/angela.jpg",
                database_type="pgvector",
                model_name="Facenet",
                connection=conn,
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"DeepFace pgvector error: {e}")
