-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for LlamaIndex nodes with vector embeddings
CREATE TABLE IF NOT EXISTS kb_llama_nodes (
    id BIGSERIAL PRIMARY KEY,
    node_id TEXT NOT NULL UNIQUE,
    text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(384),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector similarity search (IVFFlat is good for medium datasets)
-- For larger datasets (>1M rows), consider HNSW instead
CREATE INDEX IF NOT EXISTS kb_llama_nodes_embedding_idx
    ON kb_llama_nodes USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Create index on node_id for faster lookups
CREATE INDEX IF NOT EXISTS kb_llama_nodes_node_id_idx
    ON kb_llama_nodes(node_id);

-- Create GIN index on metadata for JSONB queries
CREATE INDEX IF NOT EXISTS kb_llama_nodes_metadata_idx
    ON kb_llama_nodes USING GIN (metadata);

-- Add comment for documentation
COMMENT ON TABLE kb_llama_nodes IS 'Stores document chunks with vector embeddings for semantic search';
COMMENT ON COLUMN kb_llama_nodes.node_id IS 'Unique identifier for the node (SHA1 hash)';
COMMENT ON COLUMN kb_llama_nodes.embedding IS '384-dimensional vector embedding from BGE-small model';
COMMENT ON COLUMN kb_llama_nodes.metadata IS 'JSONB metadata including doc_id, path, title, heading_path, etc.';
