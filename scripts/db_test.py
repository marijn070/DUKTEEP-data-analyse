import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import get_connection, get_existing_image_names

if __name__ == "__main__":
    # Test direct pgvector connection
    with get_connection() as conn:
        print(get_existing_image_names(conn))
