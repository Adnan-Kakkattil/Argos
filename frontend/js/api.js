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
        window.location.hash = '#login';
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

    async downloadAgent(orgId) {
        const response = await fetch(`${API_BASE}/tenant/download-agent/${orgId}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        return response.json();
    }
}

const api = new API();

