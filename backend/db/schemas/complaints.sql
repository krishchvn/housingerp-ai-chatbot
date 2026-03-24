-- ============================================================
-- HousingERP AI Chatbot - Complaints Schema Reference
-- Mirrors the existing HousingERP complaints structure
-- ============================================================

-- Complaint Categories (read from existing API, cached here)
CREATE TABLE ai_complaint_categories (
    complaintCategoryId   INT PRIMARY KEY,
    complaintName         NVARCHAR(100) NOT NULL,
    isActive              BIT DEFAULT 1,
    societyId             INT NOT NULL,
    lastSyncedOn          DATETIME DEFAULT GETDATE()
);

-- Complaints table (mirrors QueriesComplaints in original DB)
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
    status                INT DEFAULT 0,   -- 0=New, 1=InProgress, 2=Resolved
    process               INT DEFAULT 0,
    userRating            INT DEFAULT 0,
    isActive              BIT DEFAULT 1,
    isDeleted             BIT DEFAULT 0,
    createdOn             DATETIME DEFAULT GETDATE(),
    updatedOn             DATETIME DEFAULT GETDATE(),
    -- AI-specific fields
    aiClassifiedCategory  NVARCHAR(100),
    aiConfidenceScore     FLOAT,
    aiRawInput            NVARCHAR(MAX),   -- original user message
    submittedViaChat      BIT DEFAULT 1
);

-- Indexes
CREATE INDEX idx_ai_complaints_societyId ON ai_complaints(societyId);
CREATE INDEX idx_ai_complaints_userId ON ai_complaints(userId);
CREATE INDEX idx_ai_complaints_status ON ai_complaints(status);
