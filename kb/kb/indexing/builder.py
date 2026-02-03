import json
from pathlib import Path

from kb.indexing.chunking import split_document
from kb.indexing.docstate import should_process


def load_cleaned_records(jsonl_path):
    path = Path(jsonl_path)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def build_chunks_for_record(record, chunk_size=1500, chunk_overlap=200, max_section_chars=2000):
    chunks = split_document(
        record,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        max_section_chars=max_section_chars,
    )
    for chunk in chunks:
        chunk["path"] = record.get("path")
        chunk["title"] = record.get("title")
        chunk["version"] = record.get("version", "latest")
    return chunks


def index_documents(
    input_jsonl,
    db_url,
    collection_name,
    doc_table,
    embedding_model,
    chunk_size=1500,
    chunk_overlap=200,
    max_section_chars=2000,
    embedding_device=None,
    normalize_embeddings=True,
):
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import PGVector
    import psycopg
    from kb.storage import docstore

    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": embedding_device} if embedding_device else None,
        encode_kwargs={"normalize_embeddings": normalize_embeddings},
    )

    vectorstore = PGVector(
        connection_string=db_url,
        collection_name=collection_name,
        embedding_function=embeddings,
    )

    with psycopg.connect(db_url) as conn:
        docstore.ensure_doc_table(conn, doc_table)

        for record in load_cleaned_records(input_jsonl):
            doc_id = record.get("id")
            checksum = record.get("checksum")
            if not doc_id or not checksum:
                continue

            existing = docstore.get_doc_state(conn, doc_table, doc_id)
            existing_checksum = existing["checksum"] if existing else None
            existing_chunk_ids = existing["chunk_ids"] if existing else []

            if not should_process(existing_checksum, checksum):
                continue

            if existing_chunk_ids:
                vectorstore.delete(ids=existing_chunk_ids)

            chunks = build_chunks_for_record(
                record,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                max_section_chars=max_section_chars,
            )

            texts = [chunk["content"] for chunk in chunks]
            metadatas = [
                {
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "chunk_index": chunk["chunk_index"],
                    "heading_path": chunk["heading_path"],
                    "path": chunk.get("path"),
                    "title": chunk.get("title"),
                    "version": chunk.get("version"),
                }
                for chunk in chunks
            ]
            chunk_ids = [chunk["chunk_id"] for chunk in chunks]

            if texts:
                vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=chunk_ids)

            docstore.upsert_doc_state(
                conn,
                doc_table,
                {
                    "doc_id": doc_id,
                    "path": record.get("path"),
                    "title": record.get("title"),
                    "version": record.get("version", "latest"),
                    "checksum": checksum,
                },
                chunk_ids,
            )
