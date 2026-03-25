-- ============================================================
-- HousingERP AI Chatbot - Complaints Schema Reference
-- Mirrors the existing HousingERP complaints structure
-- ============================================================

-- Complaint Categories (read from existing API, cached here)
CREATE TABLE IF NOT EXISTS ai_complaint_categories (
    complaintCategoryId   INTEGER PRIMARY KEY,
    complaintName         VARCHAR(100) NOT NULL,
    isActive              BOOLEAN DEFAULT TRUE,
    societyId             INTEGER NOT NULL,
    lastSyncedOn          TIMESTAMPTZ DEFAULT NOW()
);

-- Complaints table (mirrors QueriesComplaints in original DB)
CREATE TABLE IF NOT EXISTS ai_complaints (
    queriesComplaintId    SERIAL PRIMARY KEY,
    queriesComplaintGuid  UUID DEFAULT gen_random_uuid(),
    reqNumber             VARCHAR(50),
    societyId             INTEGER NOT NULL,
    buildingId            INTEGER NOT NULL,
    flatId                INTEGER NOT NULL,
    userId                INTEGER NOT NULL,
    createdBy             INTEGER NOT NULL,
    updatedBy             INTEGER NOT NULL,
    complaintCategoryId   INTEGER NOT NULL,
    subject               VARCHAR(255),
    description           TEXT,
    complaintComments     TEXT,
    queriesComplaintImage VARCHAR(500),
    status                INTEGER DEFAULT 0,   -- 0=New, 1=InProgress, 2=Resolved
    process               INTEGER DEFAULT 0,
    userRating            INTEGER DEFAULT 0,
    isActive              BOOLEAN DEFAULT TRUE,
    isDeleted             BOOLEAN DEFAULT FALSE,
    createdOn             TIMESTAMPTZ DEFAULT NOW(),
    updatedOn             TIMESTAMPTZ DEFAULT NOW(),
    -- AI-specific fields
    aiClassifiedCategory  VARCHAR(100),
    aiConfidenceScore     FLOAT,
    aiRawInput            TEXT,   -- original user message
    submittedViaChat      BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ai_complaints_societyId ON ai_complaints(societyId);
CREATE INDEX IF NOT EXISTS idx_ai_complaints_userId ON ai_complaints(userId);
CREATE INDEX IF NOT EXISTS idx_ai_complaints_status ON ai_complaints(status);
