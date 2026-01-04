-- Add Agent Versions Table for Version Management
-- This table stores agent versions with changelog and update files

CREATE TABLE IF NOT EXISTS agent_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version_number VARCHAR(50) UNIQUE NOT NULL,
    changelog TEXT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64),  -- SHA-256 hash for integrity verification
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_latest BOOLEAN DEFAULT FALSE NOT NULL,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    released_at TIMESTAMP NULL,
    INDEX idx_version_number (version_number),
    INDEX idx_is_latest (is_latest),
    INDEX idx_is_active (is_active),
    FOREIGN KEY (created_by) REFERENCES platform_admins(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add current_version column to agents table to track which version each agent is running
ALTER TABLE agents ADD COLUMN current_version VARCHAR(50) DEFAULT NULL;
ALTER TABLE agents ADD INDEX idx_current_version (current_version);

