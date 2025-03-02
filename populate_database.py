import argparse
import os
import sys
import shutil
import time
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma

CHROMA_PATH = "chroma"
DATA_PATH = "data"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

def reload_documents():
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

def load_documents():
    print("📂 Loading documents from data folder...")
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=80, length_function=len, is_separator_regex=False
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document]):
    start_time = time.time()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
    collection = db.get_or_create_collection(name="chatbot_data")  # Ensure collection exists


    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])

    print(f"🔍 Found {len(existing_ids)} existing documents.")

    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]

    if new_chunks:
        print(f"🚀 Adding {len(new_chunks)} new documents...")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids, batch_size=50)
        print("✅ Database updated!")
    else:
        print("✅ No new documents to add.")

    print(f"Database update took {round(time.time() - start_time, 2)} seconds.")

def calculate_chunk_ids(chunks):
    chunk_map = {}

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        chunk_map[current_page_id] = chunk_map.get(current_page_id, -1) + 1
        chunk.metadata["id"] = f"{current_page_id}:{chunk_map[current_page_id]}"

    return chunks

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    print("⚠️ Database cleared. Reloading...")
    reload_documents()

if __name__ == "__main__":
    main()