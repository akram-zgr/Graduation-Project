// State management
let currentTab = 'overview';
let currentUser = null;
let universities = [];

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeEventListeners();
    loadUserInfo();
    loadInitialData();
});

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => switchTab(button.dataset.tab));
    });
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`)?.classList.add('active');
    
    currentTab = tabName;
    
    // Load data for the active tab
    loadTabData(tabName);
}

function loadTabData(tabName) {
    switch(tabName) {
        case 'overview':
            loadStats();
            break;
        case 'users':
            loadUsers();
            break;
        case 'universities':
            loadUniversities();
            break;
        case 'knowledge':
            loadKnowledgeBase();
            break;
        case 'departments':
            loadDepartments();
            break;
        case 'analytics':
            loadAnalytics();
            break;
    }
}

function initializeEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => loadTabData(currentTab));
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // User filter
    const userFilter = document.getElementById('userFilter');
    if (userFilter) {
        userFilter.addEventListener('change', (e) => loadUsers(e.target.value));
    }
    
    // University filter for knowledge base
    const knowledgeUniversityFilter = document.getElementById('knowledgeUniversityFilter');
    if (knowledgeUniversityFilter) {
        knowledgeUniversityFilter.addEventListener('change', () => loadKnowledgeBase());
    }
    
    // University filter for departments
    const departmentUniversityFilter = document.getElementById('departmentUniversityFilter');
    if (departmentUniversityFilter) {
        departmentUniversityFilter.addEventListener('change', () => loadDepartments());
    }
    
    // Add buttons
    const addUniversityBtn = document.getElementById('addUniversityBtn');
    if (addUniversityBtn) {
        addUniversityBtn.addEventListener('click', showAddUniversityModal);
    }
    
    const addKnowledgeBtn = document.getElementById('addKnowledgeBtn');
    if (addKnowledgeBtn) {
        addKnowledgeBtn.addEventListener('click', showAddKnowledgeModal);
    }
    
    const addDepartmentBtn = document.getElementById('addDepartmentBtn');
    if (addDepartmentBtn) {
        addDepartmentBtn.addEventListener('click', showAddDepartmentModal);
    }
}

async function loadUserInfo() {
    try {
        const response = await API.get('/chat/user-info');
        currentUser = response.user;
        
        // Update dashboard title based on user role
        const titleEl = document.getElementById('dashboardTitle');
        if (titleEl && currentUser) {
            if (currentUser.role === 'super_admin') {
                titleEl.textContent = 'Super Admin Dashboard';
            } else {
                titleEl.textContent = 'Admin Dashboard';
            }
        }
        
        // Display admin name
        const nameEl = document.getElementById('adminNameDisplay');
        if (nameEl && currentUser) {
            nameEl.textContent = `👤 ${currentUser.full_name || currentUser.username}`;
        }
        
        // Hide/show elements based on role
        updateUIForRole();
    } catch (error) {
        console.error('Failed to load user info:', error);
    }
}

function updateUIForRole() {
    if (!currentUser) return;
    
    const isSuperAdmin = currentUser.role === 'super_admin';
    const isUniversityAdmin = currentUser.role === 'university_admin';
    
    // Hide add university button for university admins
    const addUniversityBtn = document.getElementById('addUniversityBtn');
    if (addUniversityBtn && isUniversityAdmin) {
        addUniversityBtn.style.display = 'none';
    }
}

function loadInitialData() {
    switchTab('overview');
}



// ==================== OVERVIEW TAB ====================

async function loadStats() {
    try {
        const data = await API.get('/admin/stats');
        
        // Update stat cards
        const totalUsersEl = document.getElementById('totalUsers');
        const verifiedUsersEl = document.getElementById('verifiedUsers');
        const totalChatsEl = document.getElementById('totalChats');
        const newChatsWeekEl = document.getElementById('newChatsWeek');
        const totalMessagesEl = document.getElementById('totalMessages');
        const totalTokensEl = document.getElementById('totalTokens');
        
        if (totalUsersEl) totalUsersEl.textContent = data.users.total;
        if (verifiedUsersEl) verifiedUsersEl.textContent = `${data.users.verified} verified`;
        if (totalChatsEl) totalChatsEl.textContent = data.chats.total;
        if (newChatsWeekEl) newChatsWeekEl.textContent = `${data.chats.new_this_week} this week`;
        if (totalMessagesEl) totalMessagesEl.textContent = data.messages.total.toLocaleString();
        if (totalTokensEl) totalTokensEl.textContent = data.tokens.total.toLocaleString();
        
        // Load top users table
        const topUsersBody = document.getElementById('activeUsersBody');
        if (topUsersBody && data.top_users) {
            if (data.top_users.length === 0) {
                topUsersBody.innerHTML = '<tr><td colspan="3" style="text-align: center; padding: 20px; color: var(--text-secondary);">No users yet</td></tr>';
            } else {
                topUsersBody.innerHTML = data.top_users.map(user => `
                    <tr>
                        <td>${escapeHtml(user.username)}</td>
                        <td>${escapeHtml(user.email)}</td>
                        <td>${user.chat_count}</td>
                    </tr>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
        showNotification('Failed to load statistics', 'error');
    }
}

// ==================== USERS TAB ====================

async function loadUsers(filter = 'all') {
    try {
        let url = '/admin/users';
        if (filter === 'verified') url += '?verified=true';
        if (filter === 'unverified') url += '?verified=false';
        
        const data = await API.get(url);
        const tbody = document.getElementById('usersTableBody');
        
        if (!tbody) return;
        
        if (data.users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">No users found</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.users.map(user => {
            const badges = [];
            if (user.is_verified) badges.push('<span class="status-badge verified">Verified</span>');
            else badges.push('<span class="status-badge unverified">Unverified</span>');
            
            if (user.role === 'super_admin') badges.push('<span class="status-badge admin">Super Admin</span>');
            else if (user.role === 'university_admin') badges.push('<span class="status-badge admin">Univ Admin</span>');
            
            return `
                <tr>
                    <td>${escapeHtml(user.username)}</td>
                    <td>${escapeHtml(user.email)}</td>
                    <td>${escapeHtml(user.university_name || '-')}</td>
                    <td>${badges.join(' ')}</td>
                    <td>${formatDate(user.created_at)}</td>
                    <td>
                        <button class="action-btn" onclick="viewUser(${user.id})">View</button>
                        ${currentUser?.is_super_admin ? `
                            <button class="action-btn" onclick="toggleAdmin(${user.id}, '${user.role}')">${user.role === 'student' ? 'Make Admin' : 'Remove Admin'}</button>
                        ` : ''}
                        <button class="action-btn danger" onclick="deleteUser(${user.id})">Delete</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Failed to load users:', error);
        showNotification('Failed to load users', 'error');
    }
}

async function viewUser(userId) {
    try {
        const data = await API.get(`/admin/users/${userId}`);
        const user = data.user;
        
        const details = `
User Details:

Username: ${user.username}
Email: ${user.email}
Full Name: ${user.full_name || 'N/A'}
University ID: ${user.university_id || 'N/A'}
Department: ${user.department || 'N/A'}
Student ID: ${user.student_id || 'N/A'}
Role: ${user.role}
Verified: ${user.is_verified ? 'Yes' : 'No'}
Created: ${new Date(user.created_at).toLocaleString()}

Statistics:
Chats: ${user.stats?.chat_count || 0}
Messages: ${user.stats?.message_count || 0}
Tokens: ${user.stats?.total_tokens || 0}
        `.trim();
        
        alert(details);
    } catch (error) {
        console.error('Failed to load user details:', error);
        showNotification('Failed to load user details', 'error');
    }
}

async function toggleAdmin(userId, currentRole) {
    const action = currentRole === 'student' ? 'make admin' : 'remove admin from';
    if (!confirm(`Are you sure you want to ${action} this user?`)) {
        return;
    }
    
    try {
        await API.post(`/admin/users/${userId}/toggle-admin`);
        loadUsers(document.getElementById('userFilter')?.value || 'all');
        showNotification('User updated successfully', 'success');
    } catch (error) {
        console.error('Failed to update user:', error);
        showNotification(error.message || 'Failed to update user', 'error');
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
    }
    
    try {
        await API.delete(`/admin/users/${userId}`);
        loadUsers(document.getElementById('userFilter')?.value || 'all');
        loadStats();
        showNotification('User deleted successfully', 'success');
    } catch (error) {
        console.error('Failed to delete user:', error);
        showNotification(error.message || 'Failed to delete user', 'error');
    }
}

// ==================== UNIVERSITIES TAB ====================

async function loadUniversities() {
    try {
        const data = await API.get('/admin/universities');
        const tbody = document.getElementById('universitiesTableBody');
        
        if (!tbody) return;
        
        universities = data.universities || [];
        
        if (universities.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">No universities found</td></tr>';
            return;
        }
        
        const isSuperAdmin = currentUser && currentUser.role === 'super_admin';
        
        tbody.innerHTML = universities.map(uni => `
            <tr>
                <td>${escapeHtml(uni.name)}</td>
                <td>${escapeHtml(uni.code)}</td>
                <td>${escapeHtml(uni.city || '-')}</td>
                <td>${uni.website ? `<a href="${escapeHtml(uni.website)}" target="_blank">Link</a>` : '-'}</td>
                <td><span class="status-badge ${uni.is_active ? 'verified' : 'unverified'}">${uni.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="action-btn" onclick="editUniversity(${uni.id})">Edit</button>
                    ${isSuperAdmin ? `<button class="action-btn danger" onclick="deleteUniversity(${uni.id})">Delete</button>` : ''}
                </td>
            </tr>
        `).join('');
        
        // Update knowledge base filter
        updateUniversityFilters();
    } catch (error) {
        console.error('Failed to load universities:', error);
        showNotification('Failed to load universities', 'error');
    }
}

function updateUniversityFilters() {
    const knowledgeFilter = document.getElementById('knowledgeUniversityFilter');
    const departmentFilter = document.getElementById('departmentUniversityFilter');
    
    if (universities.length > 0) {
        const options = '<option value="">All Universities</option>' +
            universities.map(uni => `<option value="${uni.id}">${escapeHtml(uni.name)}</option>`).join('');
        
        if (knowledgeFilter) {
            knowledgeFilter.innerHTML = options;
        }
        
        if (departmentFilter) {
            // For university admins, hide the filter
            if (currentUser && currentUser.role === 'university_admin') {
                departmentFilter.style.display = 'none';
            } else {
                departmentFilter.innerHTML = options;
            }
        }
    }
}

function showAddUniversityModal() {
    if (currentUser && currentUser.role !== 'super_admin') {
        showNotification('Only Super Admins can add universities', 'error');
        return;
    }
    
    showModal('Add University', `
        <form id="universityForm">
            <div class="form-group">
                <label>Name (English) *</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Name (Arabic)</label>
                <input type="text" name="name_ar">
            </div>
            <div class="form-group">
                <label>Code *</label>
                <input type="text" name="code" required>
            </div>
            <div class="form-group">
                <label>City</label>
                <input type="text" name="city">
            </div>
            <div class="form-group">
                <label>Province</label>
                <input type="text" name="province">
            </div>
            <div class="form-group">
                <label>Address</label>
                <textarea name="address" rows="2"></textarea>
            </div>
            <div class="form-group">
                <label>Phone</label>
                <input type="text" name="phone">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email">
            </div>
            <div class="form-group">
                <label>Website</label>
                <input type="url" name="website">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" rows="3"></textarea>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" name="is_active" checked> Active
                </label>
            </div>
        </form>
    `, () => {
        const form = document.getElementById('universityForm');
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            if (key === 'is_active') {
                data[key] = form.querySelector(`[name="${key}"]`).checked;
            } else {
                data[key] = value;
            }
        });
        createUniversity(data);
    });
}

async function createUniversity(data) {
    try {
        await API.post('/admin/universities', data);
        loadUniversities();
        closeModal();
        showNotification('University created successfully', 'success');
    } catch (error) {
        console.error('Failed to create university:', error);
        showNotification(error.message || 'Failed to create university', 'error');
    }
}

async function editUniversity(id) {
    const university = universities.find(u => u.id === id);
    if (!university) return;
    
    // Check permissions for university admins
    if (currentUser && currentUser.role === 'university_admin') {
        if (currentUser.university_id !== id) {
            showNotification('You can only edit your own university', 'error');
            return;
        }
    }
    
    showModal('Edit University', `
        <form id="universityEditForm">
            <div class="form-group">
                <label>Name (English) *</label>
                <input type="text" name="name" value="${escapeHtml(university.name)}" required>
            </div>
            <div class="form-group">
                <label>Name (Arabic)</label>
                <input type="text" name="name_ar" value="${escapeHtml(university.name_ar || '')}">
            </div>
            <div class="form-group">
                <label>Code *</label>
                <input type="text" name="code" value="${escapeHtml(university.code)}" required>
            </div>
            <div class="form-group">
                <label>City</label>
                <input type="text" name="city" value="${escapeHtml(university.city || '')}">
            </div>
            <div class="form-group">
                <label>Province</label>
                <input type="text" name="province" value="${escapeHtml(university.province || '')}">
            </div>
            <div class="form-group">
                <label>Address</label>
                <textarea name="address" rows="2">${escapeHtml(university.address || '')}</textarea>
            </div>
            <div class="form-group">
                <label>Phone</label>
                <input type="text" name="phone" value="${escapeHtml(university.phone || '')}">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" value="${escapeHtml(university.email || '')}">
            </div>
            <div class="form-group">
                <label>Website</label>
                <input type="url" name="website" value="${escapeHtml(university.website || '')}">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" rows="3">${escapeHtml(university.description || '')}</textarea>
            </div>
            ${currentUser && currentUser.role === 'super_admin' ? `
            <div class="form-group">
                <label>
                    <input type="checkbox" name="is_active" ${university.is_active ? 'checked' : ''}> Active
                </label>
            </div>
            ` : ''}
        </form>
    `, async () => {
        const form = document.getElementById('universityEditForm');
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            if (key === 'is_active') {
                data[key] = form.querySelector(`[name="${key}"]`)?.checked ?? university.is_active;
            } else {
                data[key] = value;
            }
        });
        
        try {
            await API.put(`/admin/universities/${id}`, data);
            loadUniversities();
            closeModal();
            showNotification('University updated successfully', 'success');
        } catch (error) {
            console.error('Failed to update university:', error);
            showNotification(error.message || 'Failed to update university', 'error');
        }
    });
}

async function deleteUniversity(id) {
    if (currentUser && currentUser.role !== 'super_admin') {
        showNotification('Only Super Admins can delete universities', 'error');
        return;
    }
    
    if (!confirm('Are you sure you want to delete this university? This will affect all related data.')) {
        return;
    }
    
    try {
        await API.delete(`/admin/universities/${id}`);
        loadUniversities();
        showNotification('University deleted successfully', 'success');
    } catch (error) {
        console.error('Failed to delete university:', error);
        showNotification(error.message || 'Failed to delete university', 'error');
    }
}

// ==================== KNOWLEDGE BASE TAB ====================

async function loadKnowledgeBase() {
    try {
        let url = '/admin/knowledge';
        const universityFilter = document.getElementById('knowledgeUniversityFilter');
        if (universityFilter && universityFilter.value) {
            url += `?university_id=${universityFilter.value}`;
        }
        
        const data = await API.get(url);
        const tbody = document.getElementById('knowledgeTableBody');
        
        if (!tbody) return;
        
        const knowledge = data.knowledge || [];
        
        if (knowledge.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">No knowledge entries found</td></tr>';
            return;
        }
        
        tbody.innerHTML = knowledge.map(kb => `
            <tr>
                <td>${escapeHtml(kb.title)}</td>
                <td>${escapeHtml(kb.university_name || kb.university_id || '-')}</td>
                <td>${escapeHtml(kb.category || '-')}</td>
                <td>${kb.priority || '-'}</td>
                <td>${formatDate(kb.updated_at)}</td>
                <td>
                    <button class="action-btn" onclick="viewKnowledge(${kb.id})">View</button>
                    <button class="action-btn" onclick="editKnowledge(${kb.id})">Edit</button>
                    <button class="action-btn danger" onclick="deleteKnowledge(${kb.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load knowledge base:', error);
        showNotification('Failed to load knowledge base', 'error');
    }
}

function showAddKnowledgeModal() {
    const title = prompt('Knowledge Title:');
    if (!title) return;
    
    const content = prompt('Content:');
    if (!content) return;
    
    const category = prompt('Category (e.g., admission, courses):');
    const priority = prompt('Priority (1-5):', '3');
    
    const data = { title, content, category, priority: parseInt(priority) || 3 };
    
    if (currentUser?.is_university_admin) {
        data.university_id = currentUser.university_id;
    } else if (currentUser?.is_super_admin) {
        const universityId = prompt('University ID:');
        if (universityId) {
            data.university_id = parseInt(universityId);
        }
    }
    
    createKnowledge(data);
}

async function createKnowledge(data) {
    try {
        await API.post('/admin/knowledge', data);
        loadKnowledgeBase();
        showNotification('Knowledge entry created successfully', 'success');
    } catch (error) {
        console.error('Failed to create knowledge:', error);
        showNotification(error.message || 'Failed to create knowledge', 'error');
    }
}

async function viewKnowledge(id) {
    try {
        const data = await API.get(`/admin/knowledge/${id}`);
        const kb = data.knowledge;
        
        alert(`
Title: ${kb.title}
Category: ${kb.category || 'N/A'}
University: ${kb.university_name || kb.university_id}
Priority: ${kb.priority || 'N/A'}

Content:
${kb.content}

Source: ${kb.source_url || 'N/A'}
Tags: ${kb.tags || 'N/A'}
        `.trim());
    } catch (error) {
        console.error('Failed to load knowledge:', error);
        showNotification('Failed to load knowledge details', 'error');
    }
}

async function editKnowledge(id) {
    try {
        const data = await API.get(`/admin/knowledge/${id}`);
        const kb = data.knowledge;
        
        const title = prompt('Title:', kb.title);
        if (title === null) return;
        
        const content = prompt('Content:', kb.content);
        if (content === null) return;
        
        const category = prompt('Category:', kb.category || '');
        const priority = prompt('Priority (1-5):', kb.priority || '3');
        
        await API.put(`/admin/knowledge/${id}`, {
            title,
            content,
            category,
            priority: parseInt(priority) || 3
        });
        
        loadKnowledgeBase();
        showNotification('Knowledge updated successfully', 'success');
    } catch (error) {
        console.error('Failed to update knowledge:', error);
        showNotification(error.message || 'Failed to update knowledge', 'error');
    }
}

async function deleteKnowledge(id) {
    if (!confirm('Are you sure you want to delete this knowledge entry?')) {
        return;
    }
    
    try {
        await API.delete(`/admin/knowledge/${id}`);
        loadKnowledgeBase();
        showNotification('Knowledge deleted successfully', 'success');
    } catch (error) {
        console.error('Failed to delete knowledge:', error);
        showNotification(error.message || 'Failed to delete knowledge', 'error');
    }
}

// ==================== DEPARTMENTS TAB ====================

async function loadDepartments() {
    try {
        let url = '/admin/departments';
        const universityFilter = document.getElementById('departmentUniversityFilter');
        if (universityFilter && universityFilter.value) {
            url += `?university_id=${universityFilter.value}`;
        }
        
        const data = await API.get(url);
        const tbody = document.getElementById('departmentsTableBody');
        
        if (!tbody) return;
        
        const departments = data.departments || [];
        
        if (departments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px;">No departments found</td></tr>';
            return;
        }
        
        tbody.innerHTML = departments.map(dept => `
            <tr>
                <td>${escapeHtml(dept.name)}</td>
                <td>${escapeHtml(dept.code)}</td>
                <td>${escapeHtml(dept.university_name || dept.university_id)}</td>
                <td><span class="status-badge ${dept.is_active ? 'verified' : 'unverified'}">${dept.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="action-btn" onclick="editDepartment(${dept.id})">Edit</button>
                    <button class="action-btn danger" onclick="deleteDepartment(${dept.id})">Deactivate</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load departments:', error);
        showNotification('Failed to load departments', 'error');
    }
}

function showAddDepartmentModal() {
    // For university admin, auto-fill university
    const universityHtml = currentUser?.role === 'university_admin' ? 
        `<input type="hidden" name="university_id" value="${currentUser.university_id}">
         <div class="form-group">
             <label>University</label>
             <input type="text" value="${escapeHtml(universities.find(u => u.id === currentUser.university_id)?.name || 'Your University')}" disabled>
         </div>` :
        `<div class="form-group">
             <label>University *</label>
             <select name="university_id" required>
                 <option value="">Select University</option>
                 ${universities.map(u => `<option value="${u.id}">${escapeHtml(u.name)}</option>`).join('')}
             </select>
         </div>`;
    
    showModal('Add Department', `
        <form id="departmentForm">
            ${universityHtml}
            <div class="form-group">
                <label>Name (English) *</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Name (Arabic)</label>
                <input type="text" name="name_ar">
            </div>
            <div class="form-group">
                <label>Code *</label>
                <input type="text" name="code" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" rows="3"></textarea>
            </div>
            <div class="form-group">
                <label>Building</label>
                <input type="text" name="building">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email">
            </div>
            <div class="form-group">
                <label>Phone</label>
                <input type="text" name="phone">
            </div>
            <div class="form-group">
                <label>Official Website</label>
                <input type="url" name="official_website">
            </div>
            <div class="form-group">
                <label>Head of Department</label>
                <input type="text" name="head_of_department">
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" name="is_active" checked> Active
                </label>
            </div>
        </form>
    `, () => {
        const form = document.getElementById('departmentForm');
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            if (key === 'is_active') {
                data[key] = form.querySelector(`[name="${key}"]`).checked;
            } else if (key === 'university_id') {
                data[key] = parseInt(value);
            } else {
                data[key] = value;
            }
        });
        createDepartment(data);
    });
}

async function createDepartment(data) {
    try {
        await API.post('/admin/departments', data);
        loadDepartments();
        closeModal();
        showNotification('Department created successfully', 'success');
    } catch (error) {
        console.error('Failed to create department:', error);
        showNotification(error.message || 'Failed to create department', 'error');
    }
}

async function editDepartment(id) {
    try {
        const response = await API.get(`/admin/departments/${id}`);
        const dept = response.department;
        
        // Check permissions
        if (currentUser && currentUser.role === 'university_admin') {
            if (currentUser.university_id !== dept.university_id) {
                showNotification('You can only edit departments from your university', 'error');
                return;
            }
        }
        
        const universityHtml = currentUser?.role === 'university_admin' ? 
            `<div class="form-group">
                 <label>University</label>
                 <input type="text" value="${escapeHtml(dept.university_name || '')}" disabled>
             </div>` :
            `<div class="form-group">
                 <label>University *</label>
                 <select name="university_id" required>
                     ${universities.map(u => 
                         `<option value="${u.id}" ${u.id === dept.university_id ? 'selected' : ''}>${escapeHtml(u.name)}</option>`
                     ).join('')}
                 </select>
             </div>`;
        
        showModal('Edit Department', `
            <form id="departmentEditForm">
                ${universityHtml}
                <div class="form-group">
                    <label>Name (English) *</label>
                    <input type="text" name="name" value="${escapeHtml(dept.name)}" required>
                </div>
                <div class="form-group">
                    <label>Name (Arabic)</label>
                    <input type="text" name="name_ar" value="${escapeHtml(dept.name_ar || '')}">
                </div>
                <div class="form-group">
                    <label>Code *</label>
                    <input type="text" name="code" value="${escapeHtml(dept.code)}" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" rows="3">${escapeHtml(dept.description || '')}</textarea>
                </div>
                <div class="form-group">
                    <label>Building</label>
                    <input type="text" name="building" value="${escapeHtml(dept.building || '')}">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" value="${escapeHtml(dept.email || '')}">
                </div>
                <div class="form-group">
                    <label>Phone</label>
                    <input type="text" name="phone" value="${escapeHtml(dept.phone || '')}">
                </div>
                <div class="form-group">
                    <label>Official Website</label>
                    <input type="url" name="official_website" value="${escapeHtml(dept.official_website || '')}">
                </div>
                <div class="form-group">
                    <label>Head of Department</label>
                    <input type="text" name="head_of_department" value="${escapeHtml(dept.head_of_department || '')}">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="is_active" ${dept.is_active ? 'checked' : ''}> Active
                    </label>
                </div>
            </form>
        `, async () => {
            const form = document.getElementById('departmentEditForm');
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                if (key === 'is_active') {
                    data[key] = form.querySelector(`[name="${key}"]`).checked;
                } else if (key === 'university_id') {
                    data[key] = parseInt(value);
                } else {
                    data[key] = value;
                }
            });
            
            try {
                await API.put(`/admin/departments/${id}`, data);
                loadDepartments();
                closeModal();
                showNotification('Department updated successfully', 'success');
            } catch (error) {
                console.error('Failed to update department:', error);
                showNotification(error.message || 'Failed to update department', 'error');
            }
        });
    } catch (error) {
        console.error('Failed to load department:', error);
        showNotification('Failed to load department details', 'error');
    }
}

async function deleteDepartment(id) {
    if (!confirm('Are you sure you want to deactivate this department?')) {
        return;
    }
    
    try {
        await API.delete(`/admin/departments/${id}`);
        loadDepartments();
        showNotification('Department deactivated successfully', 'success');
    } catch (error) {
        console.error('Failed to deactivate department:', error);
        showNotification(error.message || 'Failed to deactivate department', 'error');
    }
}

// ==================== ANALYTICS TAB ====================

async function loadAnalytics() {
    try {
        const data = await API.get('/admin/analytics');
        // Implement analytics visualization
        console.log('Analytics data:', data);
        showNotification('Analytics loaded', 'info');
    } catch (error) {
        console.error('Failed to load analytics:', error);
        showNotification('Failed to load analytics', 'error');
    }
}

// ==================== UTILITY FUNCTIONS ====================

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function showNotification(message, type = 'info') {
    if (window.showNotification) {
        window.showNotification(message, type);
    } else {
        alert(message);
    }
}

async function handleLogout() {
    try {
        await API.post('/auth/logout');
        window.location.href = '/auth/login';
    } catch (error) {
        console.error('Logout failed:', error);
        window.location.href = '/auth/login';
    }
}

// Modal functions
function showModal(title, content, onConfirm) {
    // Remove existing modal if any
    const existingModal = document.getElementById('adminModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.id = 'adminModal';
    modal.className = 'admin-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeModal()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="window.modalConfirm()">Save</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Store callback
    window.modalConfirm = () => {
        if (onConfirm) {
            onConfirm();
        }
    };
}

function closeModal() {
    const modal = document.getElementById('adminModal');
    if (modal) {
        modal.remove();
    }
    window.modalConfirm = null;
}

// Make functions globally available
window.viewUser = viewUser;
window.toggleAdmin = toggleAdmin;
window.deleteUser = deleteUser;
window.editUniversity = editUniversity;
window.deleteUniversity = deleteUniversity;
window.viewKnowledge = viewKnowledge;
window.editKnowledge = editKnowledge;
window.deleteKnowledge = deleteKnowledge;
window.editDepartment = editDepartment;
window.deleteDepartment = deleteDepartment;
window.closeModal = closeModal;
