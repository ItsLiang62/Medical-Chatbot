from sentence_transformers import SentenceTransformer
from preprocess import get_preprocessed_dataset
from pathlib import Path

model = SentenceTransformer("all-MiniLM-L6-v2")

def form_embeddings(batch):
    embeddings = model.encode(
        batch["text"],
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    return {
        "embeddings": embeddings
    }

def main():
    root_dir = Path(__file__).resolve().parents[2]
    embedded_data_dir = root_dir / "data" / "embedded"

    train_dataset = get_preprocessed_dataset()
    train_dataset = train_dataset.map(form_embeddings, batched=True)

    train_dataset.save_to_disk(embedded_data_dir)

if __name__ == "__main__":
    main()