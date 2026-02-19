// Open Modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        modal.style.flexDirection = 'column';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
    }
}

// Close Modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Clear Form
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        // Clear hidden ID
        const idField = form.querySelector('[id$="Id"]');
        if (idField) idField.value = '';
    }
}

// Show Toast Message
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#48bb78' : '#f56565'};
        color: white;
        border-radius: 4px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== UNIVERSITY FORMS ====================

// Open University Form (Add)
function openAddUniversityForm() {
    clearForm('universityForm');
    document.getElementById('universityFormTitle').textContent = '🏫 Add University';
    document.getElementById('universityId').value = '';
    openModal('universityFormModal');
}

// Edit University
async function editUniversity(univId) {
    try {
        const response = await fetch(`/admin/universities/${univId}`);
        if (!response.ok) throw new Error('Failed to fetch university');
        
        const data = await response.json();
        const uni = data.university;
        
        // Fill form
        document.getElementById('universityId').value = uni.id;
        document.getElementById('uniName').value = uni.name;
        document.getElementById('uniCode').value = uni.code;
        document.getElementById('uniCity').value = uni.city || '';
        document.getElementById('uniProvince').value = uni.province || '';
        document.getElementById('uniWebsite').value = uni.website || '';
        document.getElementById('uniEmail').value = uni.email || '';
        document.getElementById('uniPhone').value = uni.phone || '';
        document.getElementById('uniAddress').value = uni.address || '';
        document.getElementById('uniDescription').value = uni.description || '';
        document.getElementById('uniActive').checked = uni.is_active;
        
        document.getElementById('universityFormTitle').textContent = '🏫 Edit University';
        openModal('universityFormModal');
    } catch (error) {
        console.error('Error loading university:', error);
        showToast('Failed to load university', 'error');
    }
}

// Submit University Form
async function submitUniversityForm(e) {
    e.preventDefault();
    
    const univId = document.getElementById('universityId').value;
    const formData = new FormData(document.getElementById('universityForm'));
    
    // Convert to JSON
    const data = {
        name: formData.get('name'),
        code: formData.get('code'),
        city: formData.get('city'),
        province: formData.get('province'),
        website: formData.get('website'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        address: formData.get('address'),
        description: formData.get('description'),
        is_active: formData.get('is_active') ? true : false
    };
    
    try {
        const method = univId ? 'PUT' : 'POST';
        const url = univId ? `/admin/universities/${univId}` : '/admin/universities';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save university');
        }
        
        showToast(univId ? 'University updated' : 'University created', 'success');
        closeModal('universityFormModal');
        loadUniversities(); // Refresh table
    } catch (error) {
        console.error('Error saving university:', error);
        showToast(error.message, 'error');
    }
}

// Delete University
async function deleteUniversity(univId) {
    if (!confirm('Are you sure? This will delete all faculties and departments.')) return;
    
    try {
        const response = await fetch(`/admin/universities/${univId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete university');
        
        showToast('University deleted', 'success');
        loadUniversities(); // Refresh table
    } catch (error) {
        console.error('Error deleting university:', error);
        showToast(error.message, 'error');
    }
}

// ==================== FACULTY FORMS ====================

// Load Universities for Faculty Form
async function loadUniversitiesForFaculty() {
    try {
        const response = await fetch('/admin/universities');
        const data = await response.json();
        
        const select = document.getElementById('facUniversity');
        select.innerHTML = '<option value="">Select University</option>';
        
        data.universities.forEach(uni => {
            const option = document.createElement('option');
            option.value = uni.id;
            option.textContent = uni.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading universities:', error);
    }
}

// Open Faculty Form (Add)
function openAddFacultyForm() {
    clearForm('facultyForm');
    document.getElementById('facultyFormTitle').textContent = '🎓 Add Faculty';
    document.getElementById('facultyId').value = '';
    loadUniversitiesForFaculty();
    openModal('facultyFormModal');
}

// Edit Faculty
async function editFaculty(facId) {
    try {
        const response = await fetch(`/admin/faculties/${facId}`);
        if (!response.ok) throw new Error('Failed to fetch faculty');
        
        const data = await response.json();
        const fac = data.faculty;
        
        // Load universities first
        await loadUniversitiesForFaculty();
        
        // Fill form
        document.getElementById('facultyId').value = fac.id;
        document.getElementById('facUniversity').value = fac.university_id;
        document.getElementById('facName').value = fac.name;
        document.getElementById('facNameAr').value = fac.name_ar || '';
        document.getElementById('facNameFr').value = fac.name_fr || '';
        document.getElementById('facCode').value = fac.code;
        document.getElementById('facDean').value = fac.dean || '';
        document.getElementById('facBuilding').value = fac.building || '';
        document.getElementById('facEmail').value = fac.email || '';
        document.getElementById('facPhone').value = fac.phone || '';
        document.getElementById('facWebsite').value = fac.official_website || '';
        document.getElementById('facDescription').value = fac.description || '';
        document.getElementById('facActive').checked = fac.is_active;
        
        document.getElementById('facultyFormTitle').textContent = '🎓 Edit Faculty';
        openModal('facultyFormModal');
    } catch (error) {
        console.error('Error loading faculty:', error);
        showToast('Failed to load faculty', 'error');
    }
}

// Submit Faculty Form
async function submitFacultyForm(e) {
    e.preventDefault();
    
    const facId = document.getElementById('facultyId').value;
    const formData = new FormData(document.getElementById('facultyForm'));
    
    const data = {
        name: formData.get('name'),
        name_ar: formData.get('name_ar'),
        name_fr: formData.get('name_fr'),
        code: formData.get('code'),
        university_id: parseInt(formData.get('university_id')),
        dean: formData.get('dean'),
        building: formData.get('building'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        official_website: formData.get('official_website'),
        description: formData.get('description'),
        is_active: formData.get('is_active') ? true : false
    };
    
    try {
        const method = facId ? 'PUT' : 'POST';
        const url = facId ? `/admin/faculties/${facId}` : '/admin/faculties';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save faculty');
        }
        
        showToast(facId ? 'Faculty updated' : 'Faculty created', 'success');
        closeModal('facultyFormModal');
        loadFaculties(); // Refresh table
    } catch (error) {
        console.error('Error saving faculty:', error);
        showToast(error.message, 'error');
    }
}

// ==================== DEPARTMENT FORMS ====================

// Load Universities for Department Form
async function loadUniversitiesForDept() {
    try {
        const response = await fetch('/admin/universities');
        const data = await response.json();
        
        const select = document.getElementById('deptUniversity');
        select.innerHTML = '<option value="">Select University</option>';
        
        data.universities.forEach(uni => {
            const option = document.createElement('option');
            option.value = uni.id;
            option.textContent = uni.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading universities:', error);
    }
}

// Load Faculties for Department (when university selected)
async function loadFacultiesForDept() {
    const univId = document.getElementById('deptUniversity').value;
    if (!univId) {
        document.getElementById('deptFaculty').innerHTML = '<option value="">Select Faculty</option>';
        return;
    }
    
    try {
        const response = await fetch(`/admin/universities/${univId}/faculties`);
        const data = await response.json();
        
        const select = document.getElementById('deptFaculty');
        select.innerHTML = '<option value="">Select Faculty</option>';
        
        data.faculties.forEach(fac => {
            const option = document.createElement('option');
            option.value = fac.id;
            option.textContent = fac.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading faculties:', error);
    }
}

// Open Department Form (Add)
function openAddDepartmentForm() {
    clearForm('departmentForm');
    document.getElementById('departmentFormTitle').textContent = '📚 Add Department';
    document.getElementById('departmentId').value = '';
    loadUniversitiesForDept();
    openModal('departmentFormModal');
}

// Edit Department
async function editDepartment(deptId) {
    try {
        const response = await fetch(`/admin/departments/${deptId}`);
        if (!response.ok) throw new Error('Failed to fetch department');
        
        const data = await response.json();
        const dept = data.department;
        
        // Load universities first
        await loadUniversitiesForDept();
        
        // Fill form
        document.getElementById('departmentId').value = dept.id;
        document.getElementById('deptUniversity').value = dept.university_id;
        
        // Load faculties for this university
        await loadFacultiesForDept();
        document.getElementById('deptFaculty').value = dept.faculty_id;
        
        document.getElementById('deptName').value = dept.name;
        document.getElementById('deptNameAr').value = dept.name_ar || '';
        document.getElementById('deptNameFr').value = dept.name_fr || '';
        document.getElementById('deptCode').value = dept.code;
        document.getElementById('deptHead').value = dept.head_of_department || '';
        document.getElementById('deptBuilding').value = dept.building || '';
        document.getElementById('deptEmail').value = dept.email || '';
        document.getElementById('deptPhone').value = dept.phone || '';
        document.getElementById('deptWebsite').value = dept.official_website || '';
        document.getElementById('deptDescription').value = dept.description || '';
        document.getElementById('deptActive').checked = dept.is_active;
        
        document.getElementById('departmentFormTitle').textContent = '📚 Edit Department';
        openModal('departmentFormModal');
    } catch (error) {
        console.error('Error loading department:', error);
        showToast('Failed to load department', 'error');
    }
}

// Submit Department Form
async function submitDepartmentForm(e) {
    e.preventDefault();
    
    const deptId = document.getElementById('departmentId').value;
    const formData = new FormData(document.getElementById('departmentForm'));
    
    const data = {
        name: formData.get('name'),
        name_ar: formData.get('name_ar'),
        name_fr: formData.get('name_fr'),
        code: formData.get('code'),
        university_id: parseInt(formData.get('university_id')),
        faculty_id: parseInt(formData.get('faculty_id')),
        head_of_department: formData.get('head_of_department'),
        building: formData.get('building'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        official_website: formData.get('official_website'),
        description: formData.get('description'),
        is_active: formData.get('is_active') ? true : false
    };
    
    try {
        const method = deptId ? 'PUT' : 'POST';
        const url = deptId ? `/admin/departments/${deptId}` : '/admin/departments';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save department');
        }
        
        showToast(deptId ? 'Department updated' : 'Department created', 'success');
        closeModal('departmentFormModal');
        loadDepartments(); // Refresh table
    } catch (error) {
        console.error('Error saving department:', error);
        showToast(error.message, 'error');
    }
}

// ==================== ADMIN FORMS ====================

// Toggle University Field based on Admin Type
function toggleUniversityField() {
    const type = document.getElementById('adminType').value;
    const univField = document.getElementById('adminUniversityField');
    
    if (type === 'admin') {
        univField.style.display = 'block';
        document.getElementById('adminUniversity').required = true;
    } else {
        univField.style.display = 'none';
        document.getElementById('adminUniversity').required = false;
    }
}

// Load Universities for Admin Form
async function loadUniversitiesForAdmin() {
    try {
        const response = await fetch('/admin/universities');
        const data = await response.json();
        
        const select = document.getElementById('adminUniversity');
        select.innerHTML = '<option value="">Select University</option>';
        
        data.universities.forEach(uni => {
            const option = document.createElement('option');
            option.value = uni.id;
            option.textContent = uni.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading universities:', error);
    }
}

// Open Admin Form (Add)
function openAddAdminForm() {
    clearForm('adminForm');
    document.getElementById('adminFormTitle').textContent = '🔑 Create Admin';
    document.getElementById('adminId').value = '';
    document.getElementById('adminPassword').required = true;
    document.getElementById('adminPassword').parentElement.querySelector('small').style.display = 'none';
    loadUniversitiesForAdmin();
    openModal('adminFormModal');
}

// Edit Admin
async function editAdmin(adminId) {
    try {
        const response = await fetch(`/admin/admins/${adminId}`);
        if (!response.ok) throw new Error('Failed to fetch admin');
        
        const data = await response.json();
        const admin = data.admin;
        
        // Load universities first
        await loadUniversitiesForAdmin();
        
        // Fill form
        document.getElementById('adminId').value = admin.id;
        document.getElementById('adminUsername').value = admin.username;
        document.getElementById('adminEmail').value = admin.email;
        document.getElementById('adminFullName').value = admin.full_name || '';
        document.getElementById('adminType').value = admin.role;
        
        if (admin.role === 'admin') {
            document.getElementById('adminUniversityField').style.display = 'block';
            document.getElementById('adminUniversity').value = admin.university_id || '';
        }
        
        // Password field optional on edit
        document.getElementById('adminPassword').required = false;
        document.getElementById('adminPassword').parentElement.querySelector('small').style.display = 'block';
        
        document.getElementById('adminFormTitle').textContent = '🔑 Edit Admin';
        openModal('adminFormModal');
    } catch (error) {
        console.error('Error loading admin:', error);
        showToast('Failed to load admin', 'error');
    }
}

// Submit Admin Form
async function submitAdminForm(e) {
    e.preventDefault();
    
    const adminId = document.getElementById('adminId').value;
    const formData = new FormData(document.getElementById('adminForm'));
    
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        full_name: formData.get('full_name'),
        role: formData.get('role'),
        university_id: formData.get('role') === 'admin' ? parseInt(formData.get('university_id')) : null
    };
    
    // Only add password if provided
    const password = formData.get('password');
    if (password) {
        data.password = password;
    }
    
    try {
        const method = adminId ? 'PUT' : 'POST';
        const url = adminId ? `/admin/admins/${adminId}` : '/admin/admins';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save admin');
        }
        
        showToast(adminId ? 'Admin updated' : 'Admin created', 'success');
        closeModal('adminFormModal');
        loadAdmins(); // Refresh table
    } catch (error) {
        console.error('Error saving admin:', error);
        showToast(error.message, 'error');
    }
}

// Delete Admin
async function deleteAdmin(adminId) {
    if (!confirm('Are you sure you want to delete this admin?')) return;
    
    try {
        const response = await fetch(`/admin/admins/${adminId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete admin');
        
        showToast('Admin deleted', 'success');
        loadAdmins(); // Refresh table
    } catch (error) {
        console.error('Error deleting admin:', error);
        showToast(error.message, 'error');
    }
}

// ==================== MODAL CLOSE ON ESC ====================

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(modal => {
            if (modal.style.display !== 'none') {
                closeModal(modal.id);
            }
        });
    }
});

// ==================== CSS ANIMATIONS ====================

if (!document.getElementById('animation-style')) {
    const animationStyle = document.createElement('style');
    animationStyle.id = 'animation-style';

    animationStyle.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;

    document.head.appendChild(animationStyle);
}
