import numpy as np
import faiss
from datasets import load_from_disk
from pathlib import Path
from sentence_transformers import SentenceTransformer

root_dir = Path(__file__).resolve().parents[2]
embedded_data_dir = root_dir / "data" / "embedded"

dataset = load_from_disk(embedded_data_dir)

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_index():
    embeddings = np.array(dataset["embeddings"])

    vector_dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(vector_dimension)
    index.add(embeddings)

    return index

def retrieve(query, k=5):
    query_vec = model.encode([query], normalize_embeddings=True)
    scores, indices = load_index().search(query_vec, k)

    return [dataset[i] for i in indices[0]]