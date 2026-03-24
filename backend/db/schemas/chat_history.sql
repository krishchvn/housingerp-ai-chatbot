-- ============================================================
-- HousingERP AI Chatbot - Chat History Schema
-- ============================================================

-- One session per user login
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

-- Individual messages in a session
CREATE TABLE ai_chat_messages (
    messageId       INT IDENTITY(1,1) PRIMARY KEY,
    sessionId       UNIQUEIDENTIFIER NOT NULL REFERENCES ai_chat_sessions(sessionId),
    role            NVARCHAR(20) NOT NULL,   -- 'user' | 'assistant'
    content         NVARCHAR(MAX) NOT NULL,
    intent          NVARCHAR(50),            -- 'complaint' | 'document_qa' | 'general'
    createdOn       DATETIME DEFAULT GETDATE()
);

-- Questions the bot could not answer (for secretary review)
CREATE TABLE ai_unanswered_questions (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    sessionId       UNIQUEIDENTIFIER,
    societyId       INT NOT NULL,
    question        NVARCHAR(MAX) NOT NULL,
    createdOn       DATETIME DEFAULT GETDATE(),
    isReviewed      BIT DEFAULT 0
);

-- Indexes
CREATE INDEX idx_ai_messages_sessionId ON ai_chat_messages(sessionId);
CREATE INDEX idx_ai_sessions_userId ON ai_chat_sessions(userId);
