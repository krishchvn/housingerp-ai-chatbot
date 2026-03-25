-- ============================================================
-- HousingERP AI Chatbot - Chat History Schema
-- ============================================================

-- One session per user login
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    sessionId       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    userId          INTEGER NOT NULL,
    societyId       INTEGER NOT NULL,
    buildingId      INTEGER,
    flatId          INTEGER,
    startedOn       TIMESTAMPTZ DEFAULT NOW(),
    lastActiveOn    TIMESTAMPTZ DEFAULT NOW(),
    isActive        BOOLEAN DEFAULT TRUE
);

-- Individual messages in a session
CREATE TABLE IF NOT EXISTS ai_chat_messages (
    messageId       SERIAL PRIMARY KEY,
    sessionId       UUID NOT NULL REFERENCES ai_chat_sessions(sessionId),
    role            VARCHAR(20) NOT NULL,   -- 'user' | 'assistant'
    content         TEXT NOT NULL,
    intent          VARCHAR(50),            -- 'complaint' | 'document_qa' | 'general'
    createdOn       TIMESTAMPTZ DEFAULT NOW()
);

-- Questions the bot could not answer (for secretary review)
CREATE TABLE IF NOT EXISTS ai_unanswered_questions (
    id              SERIAL PRIMARY KEY,
    sessionId       UUID,
    societyId       INTEGER NOT NULL,
    question        TEXT NOT NULL,
    createdOn       TIMESTAMPTZ DEFAULT NOW(),
    isReviewed      BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ai_messages_sessionId ON ai_chat_messages(sessionId);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_userId ON ai_chat_sessions(userId);
