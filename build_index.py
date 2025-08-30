import warnings

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from transformers import pipeline
from tqdm import tqdm
import pandas as pd
import numpy as np
import torch

warnings.filterwarnings("ignore")

# Configuration
RAW_DATA_PATH = "data/books.csv"
ENRICHED_DATA_PATH = "artifacts/enriched_books.parquet"
FAISS_INDEX_PATH = "artifacts/faiss_index"

# Models
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
ZERO_SHOT_MODEL = "facebook/bart-large-mnli"
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

# Labels
CANDIDATE_LABELS = [
    "Science Fiction",
    "Fantasy",
    "Mystery",
    "Thriller",
    "Romance",
    "History",
    "Biography",
    "Self-Help",
    "Non-Fiction",
    "Horror",
]


def preprocess_data(filepath: str) -> pd.DataFrame:
    """
    Loads raw data, cleans it, and creates a combined text field for embedding.
    """
    df = pd.read_csv(filepath)

    df["description"].fillna("No descripiton available", inplace=True)
    df["authors"].fillna("Unknown", inplace=True)
    df["title"].fillna("No title", inplace=True)

    df.replace({np.nan: None}, inplace=True)

    df["full_text"] = df["title"] + ". By " + df["authors"] + ". " + df["description"]

    df = df[df["full_text"].str.strip() != ""]
    print(f"Loaded and preprocessed {len(df)} records.")
    return df


def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches the dataframe with predicted categories and sentiment labels.
    """
    device = 0 if torch.cuda.is_available() else -1
    print(f"Using device: {'GPU' if device == 0 else 'CPU'}")

    # Zero-shot classsification
    category_classifier = pipeline(
        "zero-shot-classification", model=ZERO_SHOT_MODEL, device=device
    )
    descriptions = df["description"].tolist()
    category_results = category_classifier(
        descriptions, CANDIDATE_LABELS, batch_size=8, multi_label=False, truncation=True
    )
    df["predicted_category"] = [
        res["labels"][0]
        for res in tqdm(category_results, desc="Assigning categories", colour="cyan")
    ]

    # Sentiment analysis
    sentiment_analyzer = pipeline(
        "sentiment-analysis", model=SENTIMENT_MODEL, device=device
    )
    sentiment_results = sentiment_analyzer(descriptions, batch_size=8, truncation=True)

    df["sentiment"] = [
        res["label"]
        for res in tqdm(sentiment_results, desc="Assigning sentiments", colour="green")
    ]

    print("Data enrichment complete.")
    return df


def build_and_save_vector_store(df: pd.DataFrame):
    """
    Build a FAISS vector store from the enriched data and save it.
    """
    documents = []
    for row in tqdm(df.to_dict("records"), desc="Creating documents"):
        metadata = {
            "title": row.get("title"),
            "authors": row.get("authors"),
            "average_rating": row.get("average_rating"),
            "thumbnail": row.get("thumbnail"),
            "predicted_category": row.get("predicted_category"),
            "sentiment": row.get("sentiment"),
        }
        doc = Document(page_content=row["full_text"], metadata=metadata)
        documents.append(doc)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = FAISS.from_documents(documents, embeddings)

    vector_store.save_local(FAISS_INDEX_PATH)
    print(f"FAISS index saved successfully to {FAISS_INDEX_PATH}")


if __name__ == "__main__":
    df = preprocess_data(RAW_DATA_PATH)

    enriched_df = enrich_data(df)
    enriched_df.to_parquet(ENRICHED_DATA_PATH, index=False)

    build_and_save_vector_store(enriched_df)
