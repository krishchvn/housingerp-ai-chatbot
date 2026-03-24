USE HousingERPAI;
GO

-- ============================================================
-- Complaint Categories Cache
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ai_complaint_categories' AND xtype='U')
BEGIN
    CREATE TABLE ai_complaint_categories (
        complaintCategoryId   INT PRIMARY KEY,
        complaintName         NVARCHAR(100) NOT NULL,
        isActive              BIT DEFAULT 1,
        societyId             INT NOT NULL,
        lastSyncedOn          DATETIME DEFAULT GETDATE()
    );
    PRINT 'Created ai_complaint_categories';
END
GO

-- ============================================================
-- Complaints
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ai_complaints' AND xtype='U')
BEGIN
    CREATE TABLE ai_complaints (
        queriesComplaintId    INT IDENTITY(1,1) PRIMARY KEY,
        queriesComplaintGuid  UNIQUEIDENTIFIER DEFAULT NEWID(),
        reqNumber             NVARCHAR(50),
        societyId             INT NOT NULL,
        buildingId            INT NOT NULL,
        flatId                INT NOT NULL,
        userId                INT NOT NULL,
        createdBy             INT NOT NULL,
        updatedBy             INT NOT NULL,
        complaintCategoryId   INT NOT NULL,
        subject               NVARCHAR(255),
        description           NVARCHAR(MAX),
        complaintComments     NVARCHAR(MAX),
        queriesComplaintImage NVARCHAR(500),
        status                INT DEFAULT 0,
        process               INT DEFAULT 0,
        userRating            INT DEFAULT 0,
        isActive              BIT DEFAULT 1,
        isDeleted             BIT DEFAULT 0,
        createdOn             DATETIME DEFAULT GETDATE(),
        updatedOn             DATETIME DEFAULT GETDATE(),
        aiClassifiedCategory  NVARCHAR(100),
        aiConfidenceScore     FLOAT,
        aiRawInput            NVARCHAR(MAX),
        submittedViaChat      BIT DEFAULT 1
    );
    CREATE INDEX idx_ai_complaints_societyId ON ai_complaints(societyId);
    CREATE INDEX idx_ai_complaints_userId    ON ai_complaints(userId);
    CREATE INDEX idx_ai_complaints_status    ON ai_complaints(status);
    PRINT 'Created ai_complaints';
END
GO

-- ============================================================
-- Chat Sessions
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ai_chat_sessions' AND xtype='U')
BEGIN
    CREATE TABLE ai_chat_sessions (
        sessionId       UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        userId          INT NOT NULL,
        societyId       INT NOT NULL,
        buildingId      INT,
        flatId          INT,
        startedOn       DATETIME DEFAULT GETDATE(),
        lastActiveOn    DATETIME DEFAULT GETDATE(),
        isActive        BIT DEFAULT 1
    );
    CREATE INDEX idx_ai_sessions_userId ON ai_chat_sessions(userId);
    PRINT 'Created ai_chat_sessions';
END
GO

-- ============================================================
-- Chat Messages
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ai_chat_messages' AND xtype='U')
BEGIN
    CREATE TABLE ai_chat_messages (
        messageId       INT IDENTITY(1,1) PRIMARY KEY,
        sessionId       UNIQUEIDENTIFIER NOT NULL REFERENCES ai_chat_sessions(sessionId),
        role            NVARCHAR(20) NOT NULL,
        content         NVARCHAR(MAX) NOT NULL,
        intent          NVARCHAR(50),
        createdOn       DATETIME DEFAULT GETDATE()
    );
    CREATE INDEX idx_ai_messages_sessionId ON ai_chat_messages(sessionId);
    PRINT 'Created ai_chat_messages';
END
GO

-- ============================================================
-- Unanswered Questions Log
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ai_unanswered_questions' AND xtype='U')
BEGIN
    CREATE TABLE ai_unanswered_questions (
        id              INT IDENTITY(1,1) PRIMARY KEY,
        sessionId       UNIQUEIDENTIFIER,
        societyId       INT NOT NULL,
        question        NVARCHAR(MAX) NOT NULL,
        createdOn       DATETIME DEFAULT GETDATE(),
        isReviewed      BIT DEFAULT 0
    );
    PRINT 'Created ai_unanswered_questions';
END
GO

-- ============================================================
-- Documents (RAG)
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ai_documents' AND xtype='U')
BEGIN
    CREATE TABLE ai_documents (
        documentId      UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        societyId       INT NOT NULL,
        fileName        NVARCHAR(255) NOT NULL,
        fileType        NVARCHAR(50),
        filePath        NVARCHAR(500),
        uploadedBy      INT NOT NULL,
        uploadedOn      DATETIME DEFAULT GETDATE(),
        isActive        BIT DEFAULT 1,
        chunkCount      INT DEFAULT 0
    );
    PRINT 'Created ai_documents';
END
GO

-- ============================================================
-- Document Chunks (RAG)
-- ============================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ai_document_chunks' AND xtype='U')
BEGIN
    CREATE TABLE ai_document_chunks (
        chunkId         INT IDENTITY(1,1) PRIMARY KEY,
        documentId      UNIQUEIDENTIFIER NOT NULL REFERENCES ai_documents(documentId),
        societyId       INT NOT NULL,
        chunkIndex      INT NOT NULL,
        content         NVARCHAR(MAX) NOT NULL,
        embedding       NVARCHAR(MAX),
        createdOn       DATETIME DEFAULT GETDATE()
    );
    CREATE INDEX idx_ai_chunks_documentId ON ai_document_chunks(documentId);
    CREATE INDEX idx_ai_chunks_societyId  ON ai_document_chunks(societyId);
    PRINT 'Created ai_document_chunks';
END
GO

PRINT 'All schemas applied successfully.';
