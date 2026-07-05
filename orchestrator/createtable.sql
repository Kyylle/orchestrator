USE [AMD_DB];
GO

-- 0. DROP TABLES IN REVERSE ORDER TO PREVENT DISRUPTING STRUCTURAL ARRAYS
--DROP TABLE IF EXISTS [dbo].[r_orchestrator_user_permissions];
--DROP TABLE IF EXISTS [dbo].[t_package_versions];
--DROP TABLE IF EXISTS [dbo].[m_automation_packages];
--DROP TABLE IF EXISTS [dbo].[m_orchestrator_users];
--DROP TABLE IF EXISTS [dbo].[m_departments];
--GO

-- 1. DEPARTMENT MASTER DICTIONARY CATALOG TABLE
CREATE TABLE [dbo].[m_departments] (
    [id] INT IDENTITY(1,1) NOT NULL,
    [name] VARCHAR(100) NOT NULL,
    CONSTRAINT [PK_m_departments] PRIMARY KEY CLUSTERED ([id] ASC)
);

-- Seed your 5 required replica departments immediately
INSERT INTO [dbo].[m_departments] ([name]) VALUES 
('IS'), ('PD'), ('QA'), ('SE'), ('HC');
GO

-- 2. FRESH CORE ORCHESTRATOR USERS SYSTEM TABLE
CREATE TABLE [dbo].[m_orchestrator_users] (
    [id] INT NOT NULL, -- Manual ID incrementation assignment handled directly by your create_project_folder/save_orchestrator_user pattern
    [username] VARCHAR(150) NOT NULL,
    [password] VARCHAR(255) NOT NULL,
    [is_active] BIT DEFAULT 1 NOT NULL,
    [is_admin] BIT DEFAULT 0 NOT NULL,
    [local_sync_path] VARCHAR(500) NULL,
    [created_date] DATETIME DEFAULT GETDATE() NOT NULL,
    CONSTRAINT [PK_m_orchestrator_users] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [UQ_m_orchestrator_users_username] UNIQUE ([username])
);
GO

-- 3. FRESH AUTOMATION PACKAGES (WORKSPACE FOLDERS) TABLE
CREATE TABLE [dbo].[m_automation_packages] (
    [id] INT NOT NULL, -- Manual incrementation assignment pattern
    [package_name] VARCHAR(255) NOT NULL,
    [owner_user_id] INT NOT NULL,
    [package_path] VARCHAR(500) NOT NULL,
    [is_published] BIT DEFAULT 1 NOT NULL,
    [is_active] BIT DEFAULT 1 NOT NULL,
    CONSTRAINT [PK_m_automation_packages] PRIMARY KEY CLUSTERED ([id] ASC)
);
GO

-- 4. FRESH HISTORICAL PACKAGE VERSION TRACKING TABLE
CREATE TABLE [dbo].[t_package_versions] (
    [id] INT NOT NULL, -- Manual incrementation assignment pattern
    [package_id] INT NOT NULL,
    [version_number] VARCHAR(50) NOT NULL,
    [version_file_path] VARCHAR(500) NOT NULL,
    [uploaded_by_user_id] INT NOT NULL,
    [is_current_version] BIT DEFAULT 0 NOT NULL,
    CONSTRAINT [PK_t_package_versions] PRIMARY KEY CLUSTERED ([id] ASC)
);
GO

-- 5. FRESH EXTERNAL ACCESS ROLES & VISIBILITY OVERRIDES MATRIX JUNCTION TABLE
CREATE TABLE [dbo].[r_orchestrator_user_permissions] (
    [user_id] INT NOT NULL,
    [department_id] INT NULL,
    [can_access_other_depts] BIT DEFAULT 0 NOT NULL,
    [folder_id] INT NULL -- Kept NULL unless explicitly granted individual cross-department folders
);

-- Optimization indexes for dictionary join performance filters inside db_helper
CREATE NONCLUSTERED INDEX [IX_r_orchestrator_user_permissions_user_id] 
ON [dbo].[r_orchestrator_user_permissions] ([user_id] ASC);

CREATE NONCLUSTERED INDEX [IX_r_orchestrator_user_permissions_folder_id] 
ON [dbo].[r_orchestrator_user_permissions] ([folder_id] ASC);
GO
