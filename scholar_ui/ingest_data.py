"""
BIGDADDY - Step 3: Data Ingestion into ChromaDB
================================================
Loads the structured legal parameters from BIGDADDY_Legal_Architecture.json
into a ChromaDB vector database, creating searchable embeddings (the "Legal Brain").
"""

import json
import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

LEGAL_DATA_FILE = os.path.join(os.path.dirname(__file__), "BIGDADDY_Legal_Architecture.json")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "legal_parameters")


def load_legal_data(filepath: str = LEGAL_DATA_FILE) -> list[dict]:
    """Load legal parameter definitions from the JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[+] Loaded {len(data)} legal parameters from {filepath}")
    return data


def build_document_text(param: dict) -> str:
    """
    Build a rich text document from a legal parameter for embedding.
    Combines definition, keywords, category, and penalty info for maximum searchability.
    """
    parts = [
        f"Legal Source: {param.get('Legal_Source', 'N/A')}",
        f"Section: {param.get('Section_Number', 'N/A')}",
        f"Category: {param.get('Fraud_Category', 'N/A')}",
        f"Risk Level: {param.get('Risk_Level', 'N/A')}",
        f"Definition: {param.get('Definition', 'N/A')}",
        f"Trigger Keywords: {', '.join(param.get('Trigger_Keywords', []))}",
        f"Penalty: {param.get('Penalty_Brief', 'N/A')}",
    ]
    return "\n".join(parts)


def get_chroma_client():
    """Get or create the ChromaDB persistent client."""
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client


def ingest_legal_data(force_reingest: bool = False):
    """
    Ingest all legal parameters into ChromaDB.
    Uses ChromaDB's default embedding function (all-MiniLM-L6-v2).
    """
    client = get_chroma_client()

    # Use default sentence-transformer embedding
    ef = embedding_functions.DefaultEmbeddingFunction()

    if force_reingest:
        try:
            client.delete_collection(COLLECTION_NAME)
            print("[!] Deleted existing collection for re-ingestion.")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={
            "description": "BIGDADDY Legal Fraud Parameters - Indian Cyber Law Database",
            "hnsw:space": "cosine"
        }
    )

    # Check if already ingested
    if collection.count() > 0 and not force_reingest:
        print(f"[*] Collection '{COLLECTION_NAME}' already has {collection.count()} documents. Skipping ingestion.")
        print("    Use --force to re-ingest.")
        return collection

    legal_data = load_legal_data()

    documents = []
    metadatas = []
    ids = []

    for param in legal_data:
        doc_text = build_document_text(param)
        documents.append(doc_text)

        metadata = {
            "parameter_id": param["Parameter_ID"],
            "legal_source": param["Legal_Source"],
            "section_number": param["Section_Number"],
            "risk_level": param["Risk_Level"],
            "fraud_category": param["Fraud_Category"],
            "penalty_brief": param["Penalty_Brief"],
            "trigger_keywords": json.dumps(param["Trigger_Keywords"]),
        }
        metadatas.append(metadata)
        ids.append(param["Parameter_ID"])

    # Batch upsert into ChromaDB
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )

    print(f"[+] Successfully ingested {len(documents)} legal parameters into ChromaDB.")
    print(f"    Collection: '{COLLECTION_NAME}' | Persist Dir: '{CHROMA_PERSIST_DIR}'")
    return collection


def query_legal_brain(query_text: str, n_results: int = 5) -> list[dict]:
    """
    Query the Legal Brain (ChromaDB) for relevant legal parameters.
    Returns top-N matching legal definitions with similarity scores.
    """
    client = get_chroma_client()
    ef = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
    )

    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    matches = []
    for i in range(len(results["ids"][0])):
        match = {
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
            "similarity_score": max(0.0, round(1 - results["distances"][0][i], 4)),
        }
        matches.append(match)

    return matches


if __name__ == "__main__":
    import sys

    force = "--force" in sys.argv
    print("=" * 60)
    print("  BIGDADDY Legal Brain - Data Ingestion")
    print("=" * 60)

    collection = ingest_legal_data(force_reingest=force)

    # Test query
    print("\n" + "-" * 60)
    print("  Testing Legal Brain Query...")
    print("-" * 60)
    test_query = "Someone called me saying they are from CBI and I need to pay money to avoid arrest"
    print(f"\n  Query: \"{test_query}\"\n")

    results = query_legal_brain(test_query, n_results=3)
    for i, r in enumerate(results):
        print(f"  [{i+1}] {r['metadata']['section_number']} ({r['metadata']['legal_source']})")
        print(f"      Category: {r['metadata']['fraud_category']}")
        print(f"      Risk: {r['metadata']['risk_level']} | Score: {r['similarity_score']}")
        print()
