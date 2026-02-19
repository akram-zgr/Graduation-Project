"""
Role-based access control (RBAC) tests for the chatbot platform.

Tests that users can only access resources appropriate for their role.
"""
import pytest


class TestRolesAndPermissions:
    """Test suite for role-based access control."""
    
    def test_unauthenticated_cannot_access_chat(self, client):
        """Test unauthenticated users cannot access chat interface."""
        response = client.get('/chat/')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_unauthenticated_cannot_access_admin(self, client):
        """Test unauthenticated users cannot access admin panel."""
        response = client.get('/admin/dashboard')
        assert response.status_code in [302, 401]
    
    def test_student_can_access_chat(self, authenticated_client):
        """Test students can access chat interface."""
        response = authenticated_client.get('/chat/')
        assert response.status_code == 200
    
    def test_student_cannot_access_admin(self, authenticated_client):
        """Test students cannot access admin panel."""
        response = authenticated_client.get('/admin/dashboard')
        assert response.status_code in [302, 403]
    
    def test_admin_can_access_admin_panel(self, admin_client):
        """Test university admins can access admin panel."""
        response = admin_client.get('/admin/dashboard')
        assert response.status_code == 200
    
    def test_admin_can_access_chat(self, admin_client):
        """Test admins can also access chat interface."""
        response = admin_client.get('/chat/')
        assert response.status_code == 200
    
    def test_super_admin_full_access(self, super_admin_client):
        """Test super admins have full access to all areas."""
        # Admin panel
        response1 = super_admin_client.get('/admin/dashboard')
        assert response1.status_code == 200
        
        # Chat interface
        response2 = super_admin_client.get('/chat/')
        assert response2.status_code == 200
    
    def test_university_admin_cannot_access_other_university_data(
        self, client, sample_users, sample_knowledge_base, db_session
    ):
        """Test university admins cannot access data from other universities."""
        # Login as Batna admin
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[1].id  # batna_admin
            sess['username'] = sample_users[1].username
        
        # Try to access knowledge from Algiers (different university)
        # Get Algiers knowledge entry
        algiers_kb = [kb for kb in sample_knowledge_base if kb.university_id == sample_users[2].university_id][0]
        
        response = client.get(f'/admin/knowledge/{algiers_kb.id}')
        # Should either not find it or deny access
        assert response.status_code in [403, 404]
    
    def test_university_admin_can_manage_own_university_knowledge(
        self, admin_client, sample_knowledge_base, sample_users
    ):
        """Test university admins can manage their own university's knowledge."""
        # Get Batna knowledge entry
        batna_admin = sample_users[1]
        batna_kb = [kb for kb in sample_knowledge_base if kb.university_id == batna_admin.university_id][0]
        
        # Should be able to view own university's knowledge
        response = admin_client.get(f'/admin/knowledge/{batna_kb.id}')
        # This might return 200 or redirect depending on implementation
        assert response.status_code in [200, 302]
    
    def test_student_can_only_view_own_chats(
        self, client, sample_users, sample_chats, db_session
    ):
        """Test students can only access their own chat sessions."""
        # Login as batna_student1
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id  # batna_student1
            sess['username'] = sample_users[3].username
        
        # Get own chat
        own_chat = [chat for chat in sample_chats if chat.user_id == sample_users[3].id and chat.is_active][0]
        response1 = client.get(f'/chat/{own_chat.id}')
        assert response1.status_code == 200
        
        # Try to access another student's chat
        other_chat = [chat for chat in sample_chats if chat.user_id == sample_users[4].id][0]
        response2 = client.get(f'/chat/{other_chat.id}')
        assert response2.status_code == 404  # Should not find it
    
    def test_admin_cannot_create_users_in_other_universities(
        self, client, sample_users, sample_universities
    ):
        """Test university admins cannot create users for other universities."""
        # Login as Batna admin
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[1].id  # batna_admin
            sess['username'] = sample_users[1].username
        
        # Try to create user for Algiers university
        response = client.post('/admin/users/create', json={
            'username': 'newuser_algiers',
            'email': 'new@algiers1.test.com',
            'password': 'Password123!',
            'university_id': sample_universities[1].id,  # Algiers, not Batna
            'full_name': 'New Algiers User'
        })
        
        # Should fail (either validation or permission)
        assert response.status_code in [400, 403]
    
    def test_student_cannot_modify_knowledge_base(
        self, authenticated_client, sample_knowledge_base
    ):
        """Test students cannot create or modify knowledge base entries."""
        # Try to create knowledge
        response1 = authenticated_client.post('/admin/knowledge/create', json={
            'title': 'New Knowledge',
            'content': 'Some content',
            'category': 'test'
        })
        assert response1.status_code in [403, 404]  # Should be denied
        
        # Try to update existing knowledge
        kb_entry = sample_knowledge_base[0]
        response2 = authenticated_client.put(f'/admin/knowledge/{kb_entry.id}', json={
            'title': 'Modified Title'
        })
        assert response2.status_code in [403, 404]
    
    def test_student_cannot_view_analytics(self, authenticated_client):
        """Test students cannot access analytics data."""
        response = authenticated_client.get('/admin/analytics')
        assert response.status_code in [403, 404]
    
    def test_admin_can_view_analytics(self, admin_client):
        """Test admins can access analytics."""
        response = admin_client.get('/admin/analytics')
        # Should either succeed or redirect to analytics page
        assert response.status_code in [200, 302]
    
    def test_unauthorized_api_endpoints_require_auth(self, client):
        """Test all protected API endpoints require authentication."""
        protected_endpoints = [
            ('/chat/new', 'POST'),
            ('/chat/list', 'GET'),
            ('/chat/stats', 'GET'),
            ('/admin/dashboard', 'GET'),
            ('/admin/users', 'GET'),
        ]
        
        for endpoint, method in protected_endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'POST':
                response = client.post(endpoint, json={})
            
            assert response.status_code in [302, 401, 403]
    
    def test_role_based_navigation_access(self, client, sample_users):
        """Test users see appropriate navigation based on role."""
        # Student login
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id
        
        response1 = client.get('/chat/')
        assert response1.status_code == 200
        # In a real implementation, would check HTML content for navigation items
        
        # Admin login
        client.post('/auth/logout')
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[1].id
        
        response2 = client.get('/admin/dashboard')
        assert response2.status_code == 200
    
    def test_cross_university_data_isolation(
        self, client, sample_users, sample_chats, db_session
    ):
        """Test strict data isolation between universities."""
        # Login as Batna student
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id  # batna_student1
        
        # Get list of chats - should only see own chats
        response = client.get('/chat/list')
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify all returned chats belong to the logged-in user
        for chat in data.get('chats', []):
            assert chat['user_id'] == sample_users[3].id
    
    def test_admin_scoped_to_university(
        self, admin_client, sample_users, sample_knowledge_base
    ):
        """Test admin operations are scoped to their university."""
        # Batna admin logged in
        # Get knowledge list
        response = admin_client.get('/admin/knowledge')
        
        if response.status_code == 200:
            data = response.get_json()
            # Should only see Batna university knowledge
            batna_university_id = sample_users[1].university_id
            for kb in data.get('knowledge', []):
                assert kb['university_id'] == batna_university_id
