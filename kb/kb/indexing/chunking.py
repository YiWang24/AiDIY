import hashlib
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

HEADER_MAP = [("#", "h1"), ("##", "h2"), ("###", "h3"), ("####", "h4")]
HEADER_KEYS = ["h1", "h2", "h3", "h4"]


def build_chunk_id(doc_id, version, heading_path, chunk_index, content):
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    raw = f"{doc_id}|{version}|{heading_path}|{chunk_index}|{content_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def split_document(record, chunk_size=1500, chunk_overlap=200, max_section_chars=2000):
    doc_id = record["id"]
    version = record.get("version", "latest")
    content = record.get("content", "")

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADER_MAP, strip_headers=False
    )
    sections = header_splitter.split_text(content)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    chunks = []
    index = 0
    for section in sections:
        if len(section.page_content) > max_section_chars:
            subdocs = splitter.split_documents([section])
        else:
            subdocs = [section]

        for subdoc in subdocs:
            heading_path = [
                subdoc.metadata[key]
                for key in HEADER_KEYS
                if subdoc.metadata.get(key)
            ]
            chunk_id = build_chunk_id(
                doc_id, version, heading_path, index, subdoc.page_content
            )
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "chunk_index": index,
                    "heading_path": heading_path,
                    "content": subdoc.page_content,
                }
            )
            index += 1
    return chunks
