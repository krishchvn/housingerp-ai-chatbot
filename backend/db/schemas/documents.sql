-- ============================================================
-- HousingERP AI Chatbot - Document Store Schema (RAG)
-- ============================================================

-- Uploaded documents per society
CREATE TABLE ai_documents (
    documentId      UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    societyId       INT NOT NULL,
    fileName        NVARCHAR(255) NOT NULL,
    fileType        NVARCHAR(50),            -- 'pdf' | 'docx' | 'txt'
    filePath        NVARCHAR(500),
    uploadedBy      INT NOT NULL,
    uploadedOn      DATETIME DEFAULT GETDATE(),
    isActive        BIT DEFAULT 1,
    chunkCount      INT DEFAULT 0
);

-- Document chunks with embeddings (stored as JSON string for SQL Server compatibility)
-- For production, use ChromaDB or pgvector instead
CREATE TABLE ai_document_chunks (
    chunkId         INT IDENTITY(1,1) PRIMARY KEY,
    documentId      UNIQUEIDENTIFIER NOT NULL REFERENCES ai_documents(documentId),
    societyId       INT NOT NULL,
    chunkIndex      INT NOT NULL,
    content         NVARCHAR(MAX) NOT NULL,
    embedding       NVARCHAR(MAX),           -- JSON array of floats
    createdOn       DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_ai_chunks_documentId ON ai_document_chunks(documentId);
CREATE INDEX idx_ai_chunks_societyId ON ai_document_chunks(societyId);
