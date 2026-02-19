let currentUser = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadCurrentUser();
    if (!currentUser || !currentUser.is_super_admin) {
        window.location.href = '/auth/login';
        return;
    }
    
    await initializeDashboard();
    setupEventListeners();
});

// Load current user
async function loadCurrentUser() {
    try {
        const response = await fetch('/auth/me');
        const data = await response.json();
        currentUser = data.user;
        
        document.getElementById('adminNameDisplay').textContent = `👤 ${currentUser.full_name || currentUser.username}`;
    } catch (error) {
        console.error('Error loading current user:', error);
        window.location.href = '/auth/login';
    }
}

// Initialize dashboard
async function initializeDashboard() {
    await loadStats();
    await loadUniversities();
    await loadFaculties();
    await loadDepartments();
    await loadUsers();
    await loadAdmins();
    await populateFilters();
}

// Setup event listeners
function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });
    
    // Action buttons
    document.getElementById('addUniversityBtn').addEventListener('click', () => {
        showUniversityForm('add');
    });
    
    document.getElementById('addAdminBtn').addEventListener('click', () => {
        showAdminForm('add');
    });
    
    // Filters
    document.getElementById('facultyUnivFilter').addEventListener('change', loadFaculties);
    document.getElementById('deptUnivFilter').addEventListener('change', loadDepartments);
    document.getElementById('userUnivFilter').addEventListener('change', loadUsers);
    document.getElementById('userFilter').addEventListener('change', loadUsers);
    
    document.getElementById('refreshBtn').addEventListener('click', initializeDashboard);
    document.getElementById('logoutBtn').addEventListener('click', logout);
}

// Switch tabs
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(el => {
        el.classList.remove('active');
    });
    
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

// Load stats
async function loadStats() {
    try {
        const response = await fetch(`/admin/system-stats`);
        if (response.ok) {
            const data = await response.json();
            
            // Overview cards
            document.getElementById('totalUniversities').textContent = data.universities_count || 0;
            document.getElementById('activeUniversities').textContent = `${data.active_universities_count || 0} active`;
            
            document.getElementById('totalFaculties').textContent = data.faculties_count || 0;
            document.getElementById('activeFaculties').textContent = `${data.active_faculties_count || 0} active`;
            
            document.getElementById('totalDepartments').textContent = data.departments_count || 0;
            document.getElementById('activeDepartments').textContent = `${data.active_departments_count || 0} active`;
            
            document.getElementById('totalUsers').textContent = data.users_count || 0;
            document.getElementById('verifiedUsers').textContent = `${data.verified_users_count || 0} verified`;
            
            // System summary
            document.getElementById('sysUniversities').textContent = data.universities_count || 0;
            document.getElementById('sysFaculties').textContent = data.faculties_count || 0;
            document.getElementById('sysDepartments').textContent = data.departments_count || 0;
            document.getElementById('sysUsers').textContent = data.users_count || 0;
            document.getElementById('sysAdmins').textContent = data.admins_count || 0;
            document.getElementById('sysActiveUnis').textContent = data.active_universities_count || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load universities
async function loadUniversities() {
    try {
        const response = await fetch(`/admin/universities`);
        if (response.ok) {
            const data = await response.json();
            const universities = data.universities || [];
            
            const tableBody = document.getElementById('universitiesTableBody');
            tableBody.innerHTML = '';
            
            if (universities.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 20px;">No universities found</td></tr>';
                return;
            }
            
            universities.forEach(uni => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${uni.name}</strong></td>
                    <td>${uni.code}</td>
                    <td>${uni.city}</td>
                    <td><span class="badge">${uni.faculties_count || 0}</span></td>
                    <td><span class="badge">${uni.departments_count || 0}</span></td>
                    <td><span class="badge">${uni.users_count || 0}</span></td>
                    <td><span class="status-badge ${uni.is_active ? 'active' : 'inactive'}">
                        ${uni.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="editUniversity(${uni.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteUniversity(${uni.id})">Delete</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading universities:', error);
    }
}

// Load faculties
async function loadFaculties() {
    try {
        const univId = document.getElementById('facultyUnivFilter').value;
        const url = univId 
            ? `/admin/faculties?university_id=${univId}` 
            : `/admin/faculties`;
            
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            const faculties = data.faculties || [];
            
            const tableBody = document.getElementById('facultiesTableBody');
            tableBody.innerHTML = '';
            
            if (faculties.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">No faculties found</td></tr>';
                return;
            }
            
            faculties.forEach(faculty => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${faculty.name}</td>
                    <td>${faculty.university ? faculty.university.name : '-'}</td>
                    <td>${faculty.code}</td>
                    <td>${faculty.dean || '-'}</td>
                    <td><span class="badge">${faculty.departments_count || 0}</span></td>
                    <td><span class="status-badge ${faculty.is_active ? 'active' : 'inactive'}">
                        ${faculty.is_active ? 'Active' : 'Inactive'}</span></td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading faculties:', error);
    }
}

// Load departments
async function loadDepartments() {
    try {
        const univId = document.getElementById('deptUnivFilter').value;
        const url = univId 
            ? `/admin/departments?university_id=${univId}` 
            : `/admin/departments`;
            
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            const departments = data.departments || [];
            
            const tableBody = document.getElementById('departmentsTableBody');
            tableBody.innerHTML = '';
            
            if (departments.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">No departments found</td></tr>';
                return;
            }
            
            departments.forEach(dept => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${dept.name}</td>
                    <td>${dept.university ? dept.university.name : '-'}</td>
                    <td>${dept.faculty ? dept.faculty.name : '-'}</td>
                    <td>${dept.code}</td>
                    <td>${dept.head_of_department || '-'}</td>
                    <td><span class="status-badge ${dept.is_active ? 'active' : 'inactive'}">
                        ${dept.is_active ? 'Active' : 'Inactive'}</span></td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

// Load users
async function loadUsers() {
    try {
        const univId = document.getElementById('userUnivFilter').value;
        const filter = document.getElementById('userFilter').value;
        
        let url = `/admin/users?status=${filter}`;
        if (univId) url += `&university_id=${univId}`;
        
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            const users = data.users || [];
            
            const tableBody = document.getElementById('usersTableBody');
            tableBody.innerHTML = '';
            
            if (users.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">No users found</td></tr>';
                return;
            }
            
            users.forEach(user => {
                const row = document.createElement('tr');
                const joinDate = new Date(user.created_at).toLocaleDateString();
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>${user.university ? user.university.name : '-'}</td>
                    <td>${user.department_id ? 'Assigned' : 'Not Assigned'}</td>
                    <td><span class="status-badge ${user.is_verified ? 'active' : 'inactive'}">
                        ${user.is_verified ? '✓' : '✗'}</span></td>
                    <td>${joinDate}</td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Load admins
async function loadAdmins() {
    try {
        const response = await fetch(`/admin/admins`);
        if (response.ok) {
            const data = await response.json();
            const admins = data.admins || [];
            
            const tableBody = document.getElementById('adminsTableBody');
            tableBody.innerHTML = '';
            
            if (admins.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">No admins found</td></tr>';
                return;
            }
            
            admins.forEach(admin => {
                const row = document.createElement('tr');
                const createdDate = new Date(admin.created_at).toLocaleDateString();
                row.innerHTML = `
                    <td>${admin.username}</td>
                    <td>${admin.email}</td>
                    <td><span class="badge">${admin.role === 'super_admin' ? 'Super Admin' : 'Admin'}</span></td>
                    <td>${admin.university ? admin.university.name : 'System-wide'}</td>
                    <td>${createdDate}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="editAdmin(${admin.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteAdmin(${admin.id})">Delete</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading admins:', error);
    }
}

// Populate filters
async function populateFilters() {
    try {
        const response = await fetch(`/admin/universities`);
        if (response.ok) {
            const data = await response.json();
            const universities = data.universities || [];
            
            const filters = [
                'facultyUnivFilter',
                'deptUnivFilter',
                'userUnivFilter'
            ];
            
            filters.forEach(filterId => {
                const filterEl = document.getElementById(filterId);
                universities.forEach(uni => {
                    const option = document.createElement('option');
                    option.value = uni.id;
                    option.textContent = uni.name;
                    filterEl.appendChild(option);
                });
            });
        }
    } catch (error) {
        console.error('Error populating filters:', error);
    }
}

// Edit university
function editUniversity(univId) {
    alert('Edit University: ' + univId + '\n(Form implementation in progress)');
}

// Delete university
function deleteUniversity(univId) {
    if (confirm('Are you sure you want to delete this university?')) {
        alert('Delete University: ' + univId + '\n(Implementation in progress)');
    }
}

// Edit admin
function editAdmin(adminId) {
    alert('Edit Admin: ' + adminId + '\n(Form implementation in progress)');
}

// Delete admin
function deleteAdmin(adminId) {
    if (confirm('Are you sure you want to delete this admin?')) {
        alert('Delete Admin: ' + adminId + '\n(Implementation in progress)');
    }
}

// Show university form
function showUniversityForm(mode) {
    alert('Add University Form\n(Form implementation in progress)');
}

// Show admin form
function showAdminForm(mode) {
    alert('Create Admin Form\n(Form implementation in progress)');
}

// Logout
async function logout() {
    try {
        await fetch('/auth/logout', { method: 'POST' });
        window.location.href = '/auth/login';
    } catch (error) {
        console.error('Error logging out:', error);
    }
}

// Add CSS styling
if (!document.getElementById('dashboard-global-style')) {
    const dashboardStyle = document.createElement('style');
    dashboardStyle.id = 'dashboard-global-style';

    dashboardStyle.textContent = `
        .badge {
            display: inline-block;
            background: var(--primary-color);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .status-badge.active {
            background: #c6f6d5;
            color: #22543d;
        }
        
        .status-badge.inactive {
            background: #fed7d7;
            color: #742a2a;
        }
        
        .btn-sm {
            padding: 6px 12px;
            font-size: 12px;
            margin: 0 2px;
        }
        
        .btn-danger {
            background: #f56565;
            color: white;
        }
        
        .btn-danger:hover {
            background: #e53e3e;
        }
    `;

    document.head.appendChild(dashboardStyle);
}

