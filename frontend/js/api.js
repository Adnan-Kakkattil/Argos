/**
 * API Client for PrismTrack
 */
const API_BASE = 'http://localhost:8000/api/v1';

class API {
    constructor() {
        this.token = localStorage.getItem('token');
        this.refreshToken = localStorage.getItem('refreshToken');
        this.userType = localStorage.getItem('userType'); // 'platform_admin' or 'tenant'
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                method: options.method || 'GET',
                headers: headers,
                body: options.body,
                mode: 'cors',
                credentials: 'include'  // Include credentials for CORS
            });

            if (response.status === 401) {
                // Token expired, try to refresh
                if (await this.refresh()) {
                    return this.request(endpoint, options);
                } else {
                    this.logout();
                    return null;
                }
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async refresh() {
        if (!this.refreshToken) return false;
        
        try {
            const response = await fetch(`${API_BASE}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: this.refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.setToken(data.access_token, data.refresh_token);
                return true;
            }
        } catch (error) {
            console.error('Refresh failed:', error);
        }
        return false;
    }

    setToken(token, refreshToken) {
        this.token = token;
        this.refreshToken = refreshToken;
        localStorage.setItem('token', token);
        localStorage.setItem('refreshToken', refreshToken);
    }

    logout() {
        this.token = null;
        this.refreshToken = null;
        this.userType = null;
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userType');
        // Redirect to login page
        window.location.hash = '#login';
        // Show login view if app is available
        if (window.app) {
            window.app.showLogin();
        }
    }

    // Authentication
    async platformAdminLogin(username, password) {
        const data = await this.request('/auth/platform-admin/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        this.setToken(data.access_token, data.refresh_token);
        localStorage.setItem('userType', 'platform_admin');
        this.userType = 'platform_admin';
        return data;
    }

    async tenantLogin(email, password) {
        const data = await this.request('/auth/tenant/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        this.setToken(data.access_token, data.refresh_token);
        localStorage.setItem('userType', 'tenant');
        this.userType = 'tenant';
        return data;
    }

    // Platform Admin
    async getTenants(skip = 0, limit = 100) {
        return this.request(`/platform-admin/tenants?skip=${skip}&limit=${limit}`);
    }

    async createTenant(tenantData) {
        return this.request('/platform-admin/tenants', {
            method: 'POST',
            body: JSON.stringify(tenantData)
        });
    }

    async getTenant(tenantId) {
        return this.request(`/platform-admin/tenants/${tenantId}`);
    }

    async updateTenant(tenantId, tenantData) {
        return this.request(`/platform-admin/tenants/${tenantId}`, {
            method: 'PUT',
            body: JSON.stringify(tenantData)
        });
    }

    async deleteTenant(tenantId) {
        return this.request(`/platform-admin/tenants/${tenantId}`, {
            method: 'DELETE'
        });
    }

    async getTenantStats(tenantId) {
        return this.request(`/platform-admin/tenants/${tenantId}/stats`);
    }

    // Tenant Admin
    async getCompanies() {
        return this.request('/tenant/companies');
    }

    async createCompany(companyData) {
        return this.request('/tenant/companies', {
            method: 'POST',
            body: JSON.stringify(companyData)
        });
    }

    async getBranches(companyId) {
        return this.request(`/tenant/companies/${companyId}/branches`);
    }

    async createBranch(companyId, branchData) {
        return this.request(`/tenant/companies/${companyId}/branches`, {
            method: 'POST',
            body: JSON.stringify(branchData)
        });
    }

    async getUsers() {
        return this.request('/tenant/users');
    }

    async createUser(userData) {
        return this.request('/tenant/users', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async getOrgIds() {
        return this.request('/tenant/org-ids');
    }

    async getTenantAgents(skip = 0, limit = 100) {
        return this.request(`/tenant/agents?skip=${skip}&limit=${limit}`);
    }

    async getTenantAgent(agentId) {
        return this.request(`/tenant/agents/${agentId}`);
    }

    async getAgentTelemetry(agentId, skip = 0, limit = 100) {
        return this.request(`/tenant/agents/${agentId}/telemetry?skip=${skip}&limit=${limit}`);
    }

    async downloadAgent(orgId) {
        const response = await fetch(`${API_BASE}/tenant/download-agent/${orgId}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Download failed' }));
            throw new Error(error.detail || 'Download failed');
        }
        
        // Get filename from Content-Disposition header or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `PrismTrack_Agent_${orgId}.msi`;
        
        if (contentDisposition) {
            // Try multiple patterns to extract filename
            let extractedFilename = null;
            
            // Pattern 1: filename*=UTF-8''value (RFC 5987 - preferred)
            const rfc5987Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
            if (rfc5987Match && rfc5987Match[1]) {
                try {
                    extractedFilename = decodeURIComponent(rfc5987Match[1]);
                } catch (e) {
                    // If decoding fails, try pattern 2
                }
            }
            
            // Pattern 2: filename="value" or filename=value (fallback)
            if (!extractedFilename) {
                const standardMatch = contentDisposition.match(/filename\*?=['"]?([^'";\s]+)['"]?/i);
                if (standardMatch && standardMatch[1]) {
                    extractedFilename = standardMatch[1];
                }
            }
            
            if (extractedFilename) {
                // Clean the filename
                extractedFilename = extractedFilename.trim();
                // Remove any trailing underscores, spaces, or other unwanted characters
                extractedFilename = extractedFilename.replace(/[_\s]+$/, '');
                // Fix .msi_ to .msi (handle multiple underscores)
                extractedFilename = extractedFilename.replace(/\.msi_+$/, '.msi');
                // Ensure it ends with .msi
                if (extractedFilename.endsWith('.msi')) {
                    filename = extractedFilename;
                }
            }
        }
        
        // Final cleanup - ensure filename is properly formatted
        filename = filename.trim();
        // Remove any trailing underscores, spaces, or other characters
        filename = filename.replace(/[_\s]+$/, '');
        // Fix .msi_ to .msi (handle multiple underscores)
        filename = filename.replace(/\.msi_+$/, '.msi');
        // Ensure it ends with .msi
        if (!filename.endsWith('.msi')) {
            filename = `${filename.replace(/\.msi_?$/, '')}.msi`;
        }
        
        // Download the file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        return { success: true, filename };
    }
}

const api = new API();
// Make api globally accessible for onclick handlers
window.api = api;

