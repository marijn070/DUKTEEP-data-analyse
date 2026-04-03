import pickle

import psycopg
from deepface import DeepFace

dukteep_faces = [
    "known_faces/marijn.png",
    "known_faces/angela.jpg",
    "known_faces/koen.png",
    "known_faces/mees.png",
]
print(dukteep_faces)


with psycopg.connect("postgresql://postgres:postgres@localhost:5432/postgres") as conn:
    dfs = DeepFace.search(
        img=dukteep_faces,
        connection=conn,
    )

    with open("../dfs.pkl", "wb") as f:
        pickle.dump(dfs, f)
