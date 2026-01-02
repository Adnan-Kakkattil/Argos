/**
 * Main Application Controller
 */
class App {
    constructor() {
        this.api = api;
        this.currentView = null;
        this.init();
    }

    init() {
        // Check if user is logged in
        if (this.api.token) {
            this.api.userType = localStorage.getItem('userType');
            if (this.api.userType === 'platform_admin') {
                this.showPlatformDashboard();
            } else if (this.api.userType === 'tenant') {
                this.showTenantDashboard();
            } else {
                this.showLogin();
            }
        } else {
            this.showLogin();
        }

        // Handle hash changes
        window.addEventListener('hashchange', () => this.handleRoute());
    }

    handleRoute() {
        const hash = window.location.hash.slice(1) || 'login';
        
        switch(hash) {
            case 'login':
                this.showLogin();
                break;
            case 'platform-dashboard':
                if (this.api.userType === 'platform_admin') {
                    this.showPlatformDashboard();
                } else {
                    this.showLogin();
                }
                break;
            case 'tenant-dashboard':
                if (this.api.userType === 'tenant') {
                    this.showTenantDashboard();
                } else {
                    this.showLogin();
                }
                break;
            case 'create-tenant':
                if (this.api.userType === 'platform_admin') {
                    this.showCreateTenant();
                } else {
                    this.showLogin();
                }
                break;
            case 'client360':
                if (this.api.userType === 'platform_admin') {
                    const tenantId = new URLSearchParams(window.location.hash.split('?')[1]).get('id');
                    this.showClient360(tenantId);
                } else {
                    this.showLogin();
                }
                break;
            default:
                this.showLogin();
        }
    }

    showLogin() {
        this.currentView = 'login';
        document.getElementById('content').innerHTML = this.getLoginHTML();
        document.getElementById('nav-buttons').innerHTML = '';
    }

    async showPlatformDashboard() {
        this.currentView = 'platform-dashboard';
        try {
            const data = await this.api.getTenants();
            document.getElementById('content').innerHTML = this.getPlatformDashboardHTML(data);
            document.getElementById('nav-buttons').innerHTML = `
                <button onclick="app.showCreateTenant()" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                    Create Tenant
                </button>
                <button onclick="window.api.logout()" class="text-gray-600 hover:text-gray-900">
                    Logout
                </button>
            `;
        } catch (error) {
            this.showError('Failed to load tenants: ' + error.message);
        }
    }

    async showCreateTenant() {
        this.currentView = 'create-tenant';
        document.getElementById('content').innerHTML = this.getCreateTenantHTML();
        document.getElementById('nav-buttons').innerHTML = `
            <button onclick="app.showPlatformDashboard()" class="text-gray-600 hover:text-gray-900">
                ← Back to Dashboard
            </button>
        `;
    }

    async loadClient360(tenantId) {
        if (!tenantId) {
            this.showPlatformDashboard();
            return;
        }

        try {
            const stats = await this.api.getTenantStats(tenantId);
            const tenant = await this.api.getTenant(tenantId);
            document.getElementById('content').innerHTML = this.getClient360HTML(tenant, stats);
            document.getElementById('nav-buttons').innerHTML = `
                <button onclick="app.showPlatformDashboard()" class="text-gray-600 hover:text-gray-900">
                    ← Back to Dashboard
                </button>
            `;
        } catch (error) {
            this.showError('Failed to load Client 360: ' + error.message);
        }
    }

    async showClient360(tenantId) {
        if (!tenantId) {
            const params = new URLSearchParams(window.location.hash.split('?')[1]);
            tenantId = params.get('id');
        }
        await this.loadClient360(tenantId);
    }

    showClient360(tenantId) {
        window.location.hash = `#client360?id=${tenantId}`;
    }

    async showTenantDashboard() {
        this.currentView = 'tenant-dashboard';
        try {
            const [companies, users, orgIds] = await Promise.all([
                this.api.getCompanies(),
                this.api.getUsers(),
                this.api.getOrgIds()
            ]);
            
            document.getElementById('content').innerHTML = this.getTenantDashboardHTML(companies, users, orgIds);
            document.getElementById('nav-buttons').innerHTML = `
                <button onclick="app.showCreateCompany()" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                    Create Company
                </button>
                <button onclick="app.showCreateUser()" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                    Create User
                </button>
                <button onclick="window.api.logout()" class="text-gray-600 hover:text-gray-900">
                    Logout
                </button>
            `;
        } catch (error) {
            this.showError('Failed to load dashboard: ' + error.message);
        }
    }

    showError(message) {
        document.getElementById('content').innerHTML = `
            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                <strong>Error:</strong> ${message}
            </div>
        `;
    }

    // HTML Templates
    getLoginHTML() {
        return `
            <div class="max-w-md mx-auto mt-20">
                <div class="bg-white shadow-md rounded-lg px-8 pt-6 pb-8">
                    <h2 class="text-2xl font-bold text-center mb-6">PrismTrack Login</h2>
                    
                    <div class="mb-6">
                        <button onclick="app.showPlatformLogin()" class="w-full bg-indigo-600 text-white py-3 rounded hover:bg-indigo-700 mb-3">
                            Platform Admin Login
                        </button>
                        <button onclick="app.showTenantLogin()" class="w-full bg-gray-600 text-white py-3 rounded hover:bg-gray-700">
                            Tenant Admin Login
                        </button>
                    </div>

                    <div id="login-form"></div>
                </div>
            </div>
        `;
    }

    showPlatformLogin() {
        document.getElementById('login-form').innerHTML = `
            <form onsubmit="app.handlePlatformLogin(event)">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Username</label>
                    <input type="text" name="username" required class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Password</label>
                    <input type="password" name="password" required class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
                <button type="submit" class="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700">
                    Login
                </button>
            </form>
        `;
    }

    showTenantLogin() {
        document.getElementById('login-form').innerHTML = `
            <form onsubmit="app.handleTenantLogin(event)">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Email</label>
                    <input type="email" name="email" required class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2">Password</label>
                    <input type="password" name="password" required class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
                <button type="submit" class="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700">
                    Login
                </button>
            </form>
        `;
    }

    async handlePlatformLogin(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        try {
            await this.api.platformAdminLogin(formData.get('username'), formData.get('password'));
            this.showPlatformDashboard();
        } catch (error) {
            alert('Login failed: ' + error.message);
        }
    }

    async handleTenantLogin(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        try {
            await this.api.tenantLogin(formData.get('email'), formData.get('password'));
            this.showTenantDashboard();
        } catch (error) {
            alert('Login failed: ' + error.message);
        }
    }

    getPlatformDashboardHTML(data) {
        const tenants = data.tenants || [];
        return `
            <div class="fade-in">
                <h2 class="text-3xl font-bold mb-6">Platform Admin Dashboard</h2>
                
                <div class="bg-white shadow rounded-lg p-6 mb-6">
                    <h3 class="text-xl font-semibold mb-4">All Tenants (${data.total})</h3>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Org ID</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                ${tenants.map(tenant => `
                                    <tr>
                                        <td class="px-6 py-4 whitespace-nowrap">${tenant.name}</td>
                                        <td class="px-6 py-4 whitespace-nowrap"><code class="bg-gray-100 px-2 py-1 rounded">${tenant.tenant_org_id}</code></td>
                                        <td class="px-6 py-4 whitespace-nowrap">${tenant.admin_email}</td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <span class="px-2 py-1 text-xs rounded ${tenant.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                                ${tenant.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <button onclick="app.loadClient360(${tenant.id})" class="text-indigo-600 hover:text-indigo-900 mr-2">
                                                Client 360
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    getCreateTenantHTML() {
        return `
            <div class="max-w-2xl mx-auto fade-in">
                <h2 class="text-3xl font-bold mb-6">Create New Tenant</h2>
                
                <div class="bg-white shadow rounded-lg p-6">
                    <form onsubmit="app.handleCreateTenant(event)" id="tenant-form">
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Tenant Name *</label>
                            <input type="text" name="name" required class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Admin Email *</label>
                            <input type="email" name="admin_email" required class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Admin Password *</label>
                            <input type="password" name="admin_password" required class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        
                        <h3 class="text-lg font-semibold mt-6 mb-4">Client Details (Optional)</h3>
                        
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Company Name</label>
                            <input type="text" name="company_name" class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Address</label>
                            <input type="text" name="address" class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Phone</label>
                            <input type="text" name="phone" class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        
                        <div class="mb-6">
                            <label class="block text-gray-700 text-sm font-bold mb-2">Industry Type</label>
                            <input type="text" name="industry_type" class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        </div>
                        
                        <div class="flex space-x-4">
                            <button type="submit" class="flex-1 bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700">
                                Create Tenant
                            </button>
                            <button type="button" onclick="app.showPlatformDashboard()" class="flex-1 bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400">
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    }

    async handleCreateTenant(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const tenantData = {
            name: formData.get('name'),
            admin_email: formData.get('admin_email'),
            admin_password: formData.get('admin_password'),
            company_name: formData.get('company_name') || null,
            address: formData.get('address') || null,
            phone: formData.get('phone') || null,
            industry_type: formData.get('industry_type') || null
        };

        try {
            const result = await this.api.createTenant(tenantData);
            alert(`Tenant created successfully!\nOrg ID: ${result.tenant_org_id}\nAPI Key: ${result.admin_api_key}`);
            this.loadClient360(result.id);
        } catch (error) {
            alert('Failed to create tenant: ' + error.message);
        }
    }

    getClient360HTML(tenant, stats) {
        return `
            <div class="fade-in">
                <h2 class="text-3xl font-bold mb-6">Client 360 - ${tenant.name}</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                    <div class="bg-white shadow rounded-lg p-6">
                        <h3 class="text-sm font-medium text-gray-500 mb-2">Companies</h3>
                        <p class="text-3xl font-bold text-indigo-600">${stats.statistics.companies}</p>
                    </div>
                    <div class="bg-white shadow rounded-lg p-6">
                        <h3 class="text-sm font-medium text-gray-500 mb-2">Branches</h3>
                        <p class="text-3xl font-bold text-indigo-600">${stats.statistics.branches}</p>
                    </div>
                    <div class="bg-white shadow rounded-lg p-6">
                        <h3 class="text-sm font-medium text-gray-500 mb-2">Users</h3>
                        <p class="text-3xl font-bold text-indigo-600">${stats.statistics.users}</p>
                    </div>
                    <div class="bg-white shadow rounded-lg p-6">
                        <h3 class="text-sm font-medium text-gray-500 mb-2">Agents</h3>
                        <p class="text-3xl font-bold text-indigo-600">${stats.statistics.agents}</p>
                    </div>
                </div>
                
                <div class="bg-white shadow rounded-lg p-6">
                    <h3 class="text-xl font-semibold mb-4">Tenant Information</h3>
                    <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Tenant Org ID</dt>
                            <dd class="mt-1"><code class="bg-gray-100 px-2 py-1 rounded">${tenant.tenant_org_id}</code></dd>
                        </div>
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Admin Email</dt>
                            <dd class="mt-1">${tenant.admin_email}</dd>
                        </div>
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Status</dt>
                            <dd class="mt-1">
                                <span class="px-2 py-1 text-xs rounded ${tenant.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                    ${tenant.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </dd>
                        </div>
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Created At</dt>
                            <dd class="mt-1">${new Date(tenant.created_at).toLocaleString()}</dd>
                        </div>
                    </dl>
                </div>
            </div>
        `;
    }

    getTenantDashboardHTML(companies, users, orgIds) {
        return `
            <div class="fade-in">
                <h2 class="text-3xl font-bold mb-6">Tenant Admin Dashboard</h2>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <div class="bg-white shadow rounded-lg p-6">
                        <h3 class="text-xl font-semibold mb-4">Companies (${companies.total})</h3>
                        <div class="space-y-2">
                            ${companies.companies.map(company => `
                                <div class="flex justify-between items-center p-3 bg-gray-50 rounded">
                                    <div>
                                        <p class="font-medium">${company.name}</p>
                                        <p class="text-sm text-gray-500">Org ID: <code class="bg-gray-200 px-1 rounded">${company.company_org_id}</code></p>
                                    </div>
                                    <button onclick="app.showBranches(${company.id})" class="text-indigo-600 hover:text-indigo-900">
                                        View Branches
                                    </button>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="bg-white shadow rounded-lg p-6">
                        <h3 class="text-xl font-semibold mb-4">Users (${users.total})</h3>
                        <div class="space-y-2">
                            ${users.users.map(user => `
                                <div class="flex justify-between items-center p-3 bg-gray-50 rounded">
                                    <div>
                                        <p class="font-medium">${user.username}</p>
                                        <p class="text-sm text-gray-500">${user.email} • ${user.role}</p>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="bg-white shadow rounded-lg p-6">
                    <h3 class="text-xl font-semibold mb-4">Agent Downloads</h3>
                    <div class="space-y-3">
                        <div class="p-4 bg-indigo-50 rounded">
                            <p class="font-medium">Tenant: ${orgIds.tenant.name}</p>
                            <p class="text-sm text-gray-600 mb-2">Org ID: <code class="bg-white px-2 py-1 rounded">${orgIds.tenant.org_id}</code></p>
                            <button onclick="app.downloadAgent('${orgIds.tenant.org_id}')" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                                Download Agent
                            </button>
                        </div>
                        
                        ${orgIds.companies.map(company => `
                            <div class="p-4 bg-gray-50 rounded">
                                <p class="font-medium">Company: ${company.name}</p>
                                <p class="text-sm text-gray-600 mb-2">Org ID: <code class="bg-white px-2 py-1 rounded">${company.org_id}</code></p>
                                <button onclick="app.downloadAgent('${company.org_id}')" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                                    Download Agent
                                </button>
                            </div>
                        `).join('')}
                        
                        ${orgIds.branches.map(branch => `
                            <div class="p-4 bg-gray-50 rounded">
                                <p class="font-medium">Branch: ${branch.name}</p>
                                <p class="text-sm text-gray-600 mb-2">Org ID: <code class="bg-white px-2 py-1 rounded">${branch.org_id}</code></p>
                                <button onclick="app.downloadAgent('${branch.org_id}')" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                                    Download Agent
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    async showCreateCompany() {
        const name = prompt('Enter company name:');
        if (!name) return;
        
        try {
            await this.api.createCompany({ name });
            alert('Company created successfully!');
            this.showTenantDashboard();
        } catch (error) {
            alert('Failed to create company: ' + error.message);
        }
    }

    async showCreateUser() {
        const username = prompt('Enter username:');
        if (!username) return;
        const email = prompt('Enter email:');
        if (!email) return;
        const password = prompt('Enter password:');
        if (!password) return;
        const role = prompt('Enter role (admin/manager/viewer):', 'viewer');
        
        try {
            await this.api.createUser({ username, email, password, role });
            alert('User created successfully!');
            this.showTenantDashboard();
        } catch (error) {
            alert('Failed to create user: ' + error.message);
        }
    }

    async showBranches(companyId) {
        try {
            const branches = await this.api.getBranches(companyId);
            const branchList = branches.branches.map(b => `- ${b.name} (${b.branch_org_id})`).join('\n');
            alert(`Branches:\n${branchList || 'No branches'}`);
        } catch (error) {
            alert('Failed to load branches: ' + error.message);
        }
    }

    async downloadAgent(orgId) {
        try {
            const result = await this.api.downloadAgent(orgId);
            alert(`Agent Download Info:\nOrg ID: ${result.org_id}\nFilename: ${result.filename}\n\nNote: ${result.note || 'MSI generation will be implemented in Phase 5'}`);
        } catch (error) {
            alert('Failed to download agent: ' + error.message);
        }
    }
}

const app = new App();
// Make app globally accessible for onclick handlers
window.app = app;

