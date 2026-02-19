let currentUser = null;
let currentUniversity = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadCurrentUser();
    if (!currentUser || 
        (currentUser.role !== 'university_admin' && currentUser.role !== 'super_admin')) {
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
        
        // Load user's university
        if (currentUser.university_id) {
            await loadUniversity(currentUser.university_id);
        }
        
        document.getElementById('adminNameDisplay').textContent = `👤 ${currentUser.full_name || currentUser.username}`;
    } catch (error) {
        console.error('Error loading current user:', error);
        window.location.href = '/auth/login';
    }
}

// Load university data
async function loadUniversity(univId) {
    try {
        const response = await fetch(`/admin/universities/${univId}`);
        if (response.ok) {
            const data = await response.json();
            currentUniversity = data.university;
            updateUniversityInfo();
        }
    } catch (error) {
        console.error('Error loading university:', error);
    }
}

// Update university info display
function updateUniversityInfo() {
    if (currentUniversity) {
        document.getElementById('universityInfo').textContent = 
            `📍 ${currentUniversity.name} - ${currentUniversity.city}`;
        document.getElementById('univName').textContent = currentUniversity.name;
    }
}

// Initialize dashboard
async function initializeDashboard() {
    await loadStats();
    await loadFaculties();
    await loadDepartments();
    await loadUsers();
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
    document.getElementById('addFacultyBtn').addEventListener('click', () => {
        showFacultyForm('add');
    });
    
    document.getElementById('addDepartmentBtn').addEventListener('click', () => {
        showDepartmentForm('add');
    });
    
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
        const response = await fetch(`/admin/dashboard/stats`);
        if (response.ok) {
            const data = await response.json();
            
            document.getElementById('totalFaculties').textContent = data.faculties_count || 0;
            document.getElementById('activeFaculties').textContent = `${data.faculties_count || 0} active`;
            
            document.getElementById('totalDepartments').textContent = data.departments_count || 0;
            document.getElementById('activeDepartments').textContent = `${data.departments_count || 0} active`;
            
            document.getElementById('totalUsers').textContent = data.users_count || 0;
            document.getElementById('verifiedUsers').textContent = `${data.verified_users_count || 0} verified`;
            
            document.getElementById('univFaculties').textContent = data.faculties_count || 0;
            document.getElementById('univDepartments').textContent = data.departments_count || 0;
            document.getElementById('univStudents').textContent = data.students_count || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load faculties
async function loadFaculties() {
    try {
        const response = await fetch(`/admin/faculties?university_id=${currentUser.university_id}`);
        if (response.ok) {
            const data = await response.json();
            const faculties = data.faculties || [];
            
            const tableBody = document.getElementById('facultiesTableBody');
            tableBody.innerHTML = '';
            
            if (faculties.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px;">No faculties found</td></tr>';
                return;
            }
            
            faculties.forEach(faculty => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${faculty.name}</td>
                    <td>${faculty.name_ar || '-'}</td>
                    <td>${faculty.code}</td>
                    <td>${faculty.dean || '-'}</td>
                    <td><span class="badge">${faculty.departments_count || 0}</span></td>
                    <td><span class="status-badge ${faculty.is_active ? 'active' : 'inactive'}">
                        ${faculty.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="editFaculty(${faculty.id})">Edit</button>
                    </td>
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
        const response = await fetch(`/admin/departments?university_id=${currentUser.university_id}`);
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
                    <td>${dept.code}</td>
                    <td>${dept.faculty_name || '-'}</td>
                    <td>${dept.head_of_department || '-'}</td>
                    <td><span class="status-badge ${dept.is_active ? 'active' : 'inactive'}">
                        ${dept.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="editDepartment(${dept.id})">Edit</button>
                    </td>
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
        const filter = document.getElementById('userFilter').value;
        const response = await fetch(`/admin/users?university_id=${currentUser.university_id}&status=${filter}`);
        
        if (response.ok) {
            const data = await response.json();
            const users = data.users || [];
            
            const tableBody = document.getElementById('usersTableBody');
            tableBody.innerHTML = '';
            
            if (users.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px;">No users found</td></tr>';
                return;
            }
            
            users.forEach(user => {
                const row = document.createElement('tr');
                const joinDate = new Date(user.created_at).toLocaleDateString();
                row.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>${user.full_name || '-'}</td>
                    <td>${user.department_id ? 'Assigned' : 'Not Assigned'}</td>
                    <td><span class="status-badge ${user.is_verified ? 'active' : 'inactive'}">
                        ${user.is_verified ? '✓' : '✗'}</span></td>
                    <td>${joinDate}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="viewUser(${user.id})">View</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Edit faculty
function editFaculty(facultyId) {
    alert('Edit Faculty: ' + facultyId + '\n(Form implementation in progress)');
}

// Edit department
function editDepartment(deptId) {
    alert('Edit Department: ' + deptId + '\n(Form implementation in progress)');
}

// View user
function viewUser(userId) {
    alert('View User: ' + userId + '\n(User details in progress)');
}

// Show faculty form
function showFacultyForm(mode) {
    alert('Add Faculty Form\n(Form implementation in progress)');
}

// Show department form
function showDepartmentForm(mode) {
    alert('Add Department Form\n(Form implementation in progress)');
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
if (!document.getElementById('global-dashboard-style')) {
    const style = document.createElement('style');
    style.id = 'global-dashboard-style';

    style.textContent = `
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
        }
    `;

    document.head.appendChild(style);
}

