-- Auto-runs on first container start
-- Creates the HousingERPAI database

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'HousingERPAI')
BEGIN
    CREATE DATABASE HousingERPAI;
    PRINT 'Database HousingERPAI created.';
END
ELSE
BEGIN
    PRINT 'Database HousingERPAI already exists.';
END
GO
