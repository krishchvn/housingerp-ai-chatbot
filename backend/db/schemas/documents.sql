-- ============================================================
-- HousingERP AI Chatbot - Document Store Schema (RAG)
-- ============================================================

-- Uploaded documents per society
CREATE TABLE IF NOT EXISTS ai_documents (
    documentId      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    societyId       INTEGER NOT NULL,
    fileName        VARCHAR(255) NOT NULL,
    fileType        VARCHAR(50),            -- 'pdf' | 'docx' | 'txt'
    filePath        VARCHAR(500),
    uploadedBy      INTEGER NOT NULL,
    uploadedOn      TIMESTAMPTZ DEFAULT NOW(),
    isActive        BOOLEAN DEFAULT TRUE,
    chunkCount      INTEGER DEFAULT 0
);

-- Document chunks with embeddings (stored as JSONB for PostgreSQL)
-- For production, enable pgvector extension for native vector similarity search
CREATE TABLE IF NOT EXISTS ai_document_chunks (
    chunkId         SERIAL PRIMARY KEY,
    documentId      UUID NOT NULL REFERENCES ai_documents(documentId),
    societyId       INTEGER NOT NULL,
    chunkIndex      INTEGER NOT NULL,
    content         TEXT NOT NULL,
    embedding       JSONB,           -- JSON array of floats
    createdOn       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_chunks_documentId ON ai_document_chunks(documentId);
CREATE INDEX IF NOT EXISTS idx_ai_chunks_societyId ON ai_document_chunks(societyId);
