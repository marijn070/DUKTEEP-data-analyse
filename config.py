# config.py
from pathlib import Path

DUKTEEP_LINK = "https://www.youtube.com/@dukteep"
VIDEO_DIR = Path("videos")
KNOWN_FACES = [
    "known_faces/marijn.png",
    "known_faces/angela.jpg",
    "known_faces/koen.png",
    "known_faces/mees.png",
]

DB_URI = "postgresql://postgres:postgres@localhost:5432/postgres"
FRAME_INTERVAL = 1.0
