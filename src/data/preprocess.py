import datasets
from pathlib import Path

def load_from_ingested():
    root_dir = Path(__file__).resolve().parents[2]
    parsed_data_dir = root_dir / "data" / "parsed"

    data_files = [
        str(parsed_data_dir / data_file)
        for data_file in parsed_data_dir.glob("*.json")
    ]

    return datasets.load_dataset("json", data_files=data_files)

def form_text(row):
    title = row.get("title") or ""
    abstract = row.get("abstract") or ""
    return {
        "text": title + " " + abstract
    }

def form_chunks(batch, chunk_size=150, overlap=30):
    pmids = []
    chunks = []

    for pmid, text in zip(batch["pmid"], batch["text"]):
        words = text.split()
        if not words:
            continue

        start_idx = 0
        while start_idx < len(words):
            end_idx = start_idx + chunk_size
            chunk = " ".join(words[start_idx:end_idx])
            pmids.append(pmid)
            chunks.append(chunk)
            start_idx += chunk_size - overlap

    return {
        "pmid": pmids,
        "text": chunks
    }

def get_preprocessed_dataset():
    train_dataset = load_from_ingested()["train"]
    train_dataset = train_dataset.map(form_text, load_from_cache_file=False)
    train_dataset = train_dataset.map(
        form_chunks,
        remove_columns=train_dataset.column_names,
        batched=True,
        load_from_cache_file=False
    )
    return train_dataset