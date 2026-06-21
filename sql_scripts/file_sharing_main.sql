DROP DATABASE IF EXISTS file_sharing_main;
CREATE DATABASE file_sharing_main;
USE file_sharing_main;

CREATE TABLE user_status (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE activities (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    activity_name VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE outcomes (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    outcome VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE organisations (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    organisation_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE permissions (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    permission_name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE user_types (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    user_type_name VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE projects (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    organisation_id INT NOT NULL,
    
    project_name VARCHAR(100) NOT NULL,
    folder_name VARCHAR(100) NOT NULL UNIQUE,
    project_status_id INT,

    CONSTRAINT fk_projects_org
        FOREIGN KEY (organisation_id)
        REFERENCES organisations(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_projects_status
        FOREIGN KEY (project_status_id)
        REFERENCES user_status(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
        
	CONSTRAINT uq_orgid_project
    UNIQUE(organisation_id, project_name)
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    passwords VARCHAR(100) NOT NULL,
    secret VARCHAR(200),

    organisation_id INT NOT NULL,
    status_id INT NOT NULL,
    user_type_id INT NOT NULL DEFAULT 1,

    CONSTRAINT fk_users_org
        FOREIGN KEY (organisation_id)
        REFERENCES organisations(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_users_status
        FOREIGN KEY (user_status_id)
        REFERENCES user_status(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_users_type
        FOREIGN KEY (user_type_id)
        REFERENCES user_types(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE user_activity_logs (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    
    user_id INT NOT NULL,
    activity_id INT NOT NULL,
    outcome_id INT,

    activity_time DATETIME NOT NULL,
    details TEXT NOT NULL,

    CONSTRAINT fk_logs_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_logs_activity
        FOREIGN KEY (activity_id)
        REFERENCES activities(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_logs_outcome
        FOREIGN KEY (outcome_id)
        REFERENCES outcomes(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE files (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    
    file_name VARCHAR(100),

    project_id INT NOT NULL,
    user_activity_id INT NOT NULL,

    CONSTRAINT fk_files_project
        FOREIGN KEY (project_id)
        REFERENCES projects(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_files_activity
        FOREIGN KEY (user_activity_id)
        REFERENCES user_activity_logs(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE proj_permissions (
    ID INT AUTO_INCREMENT PRIMARY KEY,

    project_id INT,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,

    CONSTRAINT fk_proj_perm_project
        FOREIGN KEY (project_id)
        REFERENCES projects(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_proj_perm_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_proj_perm_permission
        FOREIGN KEY (permission_id)
        REFERENCES permissions(ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_project_user
        UNIQUE (project_id, user_id)
);

CREATE OR REPLACE VIEW user_projects AS
SELECT
    u.full_name AS "Full name",
    u.username AS "Username",
    org.organisation_name AS Organisation,
    p.project_name AS "Project",
    p.folder_name AS Folder,
    ps.permission_name AS "Permission"
FROM users u
LEFT JOIN proj_permissions p_p
    ON u.user_id = p_p.user_id
LEFT JOIN projects p
    ON p_p.project_id = p.ID
LEFT JOIN organisations org
    ON p.organisation_id = org.ID
LEFT JOIN permissions ps
    ON p_p.permission_id = ps.ID;
    
INSERT INTO user_types(user_type_name)
SELECT user_type_name FROM file_sharing_staging.user_types;

INSERT INTO user_status(status_name)
SELECT status_name FROM file_sharing_staging.user_status;
    
INSERT INTO permissions(permission_name)
SELECT permission_name FROM file_sharing_staging.permissions;

INSERT INTO activities(activity_name)
SELECT activity_name FROM file_sharing_staging.activities;

INSERT INTO outcomes(outcome)
SELECT outcome FROM file_sharing_staging.outcomes;

ALTER TABLE file_sharing_main.users RENAME COLUMN user_status_id TO status_id;