-- PrismTrack Database Schema
-- MySQL Database Creation Script

CREATE DATABASE IF NOT EXISTS prismtrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE prismtrack;

-- Platform Admins Table
CREATE TABLE IF NOT EXISTS platform_admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tenants Table
CREATE TABLE IF NOT EXISTS tenants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_org_id VARCHAR(8) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    admin_email VARCHAR(255) NOT NULL,
    admin_password_hash VARCHAR(255) NOT NULL,
    admin_api_key VARCHAR(255) UNIQUE NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    INDEX idx_tenant_org_id (tenant_org_id),
    INDEX idx_admin_email (admin_email),
    INDEX idx_admin_api_key (admin_api_key),
    INDEX idx_created_by (created_by),
    FOREIGN KEY (created_by) REFERENCES platform_admins(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Companies Table
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id INT NOT NULL,
    company_org_id VARCHAR(8) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_company_org_id (company_org_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Branches Table
CREATE TABLE IF NOT EXISTS branches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    branch_org_id VARCHAR(8) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    ip_addresses TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    INDEX idx_company_id (company_id),
    INDEX idx_branch_org_id (branch_org_id),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Users Table (Client Admin Users)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id INT NOT NULL,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_username (username),
    INDEX idx_email (email),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Agents Table
CREATE TABLE IF NOT EXISTS agents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    org_id VARCHAR(8) NOT NULL,
    org_type ENUM('TENANT', 'COMPANY', 'BRANCH') NOT NULL,
    machine_name VARCHAR(255) NOT NULL,
    hardware_uuid VARCHAR(255) UNIQUE NOT NULL,
    agent_token VARCHAR(255) UNIQUE NOT NULL,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('ONLINE', 'OFFLINE') DEFAULT 'OFFLINE' NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_org_id (org_id),
    INDEX idx_hardware_uuid (hardware_uuid),
    INDEX idx_agent_token (agent_token),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Telemetry Table
CREATE TABLE IF NOT EXISTS telemetry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id INT NOT NULL,
    window_title VARCHAR(500),
    process_name VARCHAR(255),
    timestamp TIMESTAMP NOT NULL,
    is_idle BOOLEAN DEFAULT FALSE NOT NULL,
    screenshot_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agent_id (agent_id),
    INDEX idx_timestamp (timestamp),
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create initial platform admin user
-- Run scripts/create_admin.py to create admin user with proper password hash
-- Default credentials: admin / admin@prismtrack.com / admin123
-- CHANGE PASSWORD IN PRODUCTION!

