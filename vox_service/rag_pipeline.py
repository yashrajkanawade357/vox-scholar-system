"""
VOX Service — RAG Pipeline
Project BigDaddy | Anti-Vishing System

ChromaDB-based Retrieval-Augmented Generation pipeline.
Indexes Indian legal PDFs and provides semantic search for
legal context during call analysis.

- 100% offline — no cloud APIs
- Uses sentence-transformers "all-MiniLM-L6-v2" for embeddings
- ChromaDB PersistentClient for storage
- PyMuPDF (fitz) for PDF text extraction
"""

import os
import glob
import fitz  # PyMuPDF
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
COLLECTION_NAME = "indian_legal_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500       # words
CHUNK_OVERLAP = 50     # words


# ──────────────────────────────────────────────
# ChromaDB Collection (singleton)
# ──────────────────────────────────────────────
_collection = None


def get_collection():
    """Return (or create) the ChromaDB collection with sentence-transformer embeddings."""
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ──────────────────────────────────────────────
# PDF Text Extraction
# ──────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF using PyMuPDF (fitz)."""
    text_parts = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


# ──────────────────────────────────────────────
# Text Chunking
# ──────────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into chunks of `chunk_size` words with `overlap` word overlap.
    Uses a sliding-window approach on word boundaries.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # slide forward

    return chunks


# ──────────────────────────────────────────────
# PDF Indexing
# ──────────────────────────────────────────────
def _get_existing_sources(collection) -> set[str]:
    """Return the set of filenames already indexed in the collection."""
    if collection.count() == 0:
        return set()
    # Fetch all IDs and extract unique source filenames
    all_ids = collection.get()["ids"]
    sources = set()
    for chunk_id in all_ids:
        # IDs follow the pattern: "filename.pdf_chunk_0"
        parts = chunk_id.rsplit("_chunk_", 1)
        if parts:
            sources.add(parts[0])
    return sources


def index_pdfs(docs_dir: str = DOCS_DIR) -> int:
    """
    Recursively find and index all PDFs in `docs_dir`.
    Skips PDFs that are already indexed (based on chunk IDs).

    Returns the number of newly indexed PDFs.
    """
    collection = get_collection()

    # Find all PDF files recursively
    pdf_pattern = os.path.join(docs_dir, "**", "*.pdf")
    pdf_files = glob.glob(pdf_pattern, recursive=True)

    if not pdf_files:
        print("📂 No PDF files found in", docs_dir)
        return 0

    print(f"📚 Found {len(pdf_files)} PDF(s) in {docs_dir}")

    # Check which are already indexed
    existing_sources = _get_existing_sources(collection)
    indexed_count = 0

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)

        # Skip if already indexed
        if filename in existing_sources:
            print(f"  ⏭️  Skipping (already indexed): {filename}")
            continue

        print(f"  📄 Processing: {filename}")

        # Extract text
        try:
            text = extract_text_from_pdf(pdf_path)
        except Exception as e:
            print(f"  ❌ Failed to read {filename}: {e}")
            continue

        if not text.strip():
            print(f"  ⚠️  No text extracted from {filename}, skipping")
            continue

        # Chunk the text
        chunks = chunk_text(text)
        print(f"     ✂️  Created {len(chunks)} chunks")

        # Prepare batch data
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {"source": filename, "chunk_index": i, "path": pdf_path}
            for i in range(len(chunks))
        ]

        # Add to ChromaDB in batches of 100
        batch_size = 100
        for batch_start in range(0, len(chunks), batch_size):
            batch_end = batch_start + batch_size
            collection.add(
                ids=ids[batch_start:batch_end],
                documents=chunks[batch_start:batch_end],
                metadatas=metadatas[batch_start:batch_end],
            )

        print(f"     ✅ Indexed {len(chunks)} chunks from {filename}")
        indexed_count += 1

    print(f"\n🎉 Indexing complete! {indexed_count} new PDF(s) indexed.")
    print(f"📊 Total chunks in collection: {collection.count()}")
    return indexed_count


# ──────────────────────────────────────────────
# Semantic Query
# ──────────────────────────────────────────────
def query_legal(question: str, top_k: int = 3) -> list[dict]:
    """
    Query the legal document collection with a natural language question.

    Args:
        question: The search query (e.g., "penalties for OTP fraud")
        top_k:    Number of top results to return

    Returns:
        List of dicts with keys: source, chunk_id, text, distance
    """
    collection = get_collection()

    if collection.count() == 0:
        print("⚠️  Collection is empty — no documents indexed yet.")
        return []

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, collection.count()),
    )

    # Flatten the nested result structure
    output = []
    for i in range(len(results["ids"][0])):
        output.append({
            "chunk_id": results["ids"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i],
        })

    return output


# ──────────────────────────────────────────────
# Main — Index + Test Query
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("🔷 VOX Service — RAG Pipeline")
    print("   Project BigDaddy | Anti-Vishing System")
    print("=" * 60)

    # Step 1: Index all PDFs in ./docs
    print("\n📥 STEP 1: Indexing PDFs from ./docs\n")
    index_pdfs()

    # Step 2: Run test query
    test_query = "What are the penalties for vishing and OTP fraud in India?"
    print("\n" + "=" * 60)
    print(f"🔍 STEP 2: Test Query")
    print(f"   \"{test_query}\"")
    print("=" * 60)

    results = query_legal(test_query, top_k=3)

    if not results:
        print("\n📭 No results found. Add PDFs to ./docs and re-run!")
    else:
        for i, r in enumerate(results, 1):
            print(f"\n{'─' * 50}")
            print(f"📌 Result {i} / {len(results)}")
            print(f"   Source:   {r['source']}")
            print(f"   Chunk:    {r['chunk_id']}")
            print(f"   Distance: {r['distance']:.4f}")
            print(f"   Text:     {r['text'][:300]}...")

    print("\n" + "=" * 60)
    print("✅ RAG Pipeline test complete.")
    print("=" * 60)
