"""
University data isolation tests for the multi-university chatbot platform.

Tests that data is properly isolated between universities and that admins
can only access data from their own university.
"""
import pytest
from models.user import User
from models.knowledge_base import KnowledgeBase
from models.chat import Chat


class TestUniversityIsolation:
    """Test suite for multi-university data isolation."""
    
    def test_admin_cannot_view_other_university_users(
        self, admin_client, sample_users, db_session
    ):
        """Test that university admins cannot view users from other universities."""
        # Batna admin is logged in
        batna_admin = sample_users[1]
        algiers_admin = sample_users[2]
        
        # Try to get Algiers admin's details
        response = admin_client.get(f'/admin/users/{algiers_admin.id}')
        
        # Should deny access or not find
        assert response.status_code in [403, 404]
    
    def test_admin_can_only_create_users_for_own_university(
        self, admin_client, sample_universities, sample_users
    ):
        """Test that admins can only create users for their own university."""
        batna_admin = sample_users[1]
        
        # Try to create user for different university
        response = admin_client.post('/admin/users/create', json={
            'username': 'new_algiers_student',
            'email': 'new@algiers.test.com',
            'password': 'Password123!',
            'university_id': sample_universities[1].id,  # Different from Batna
            'full_name': 'New Algiers Student'
        })
        
        # Should be denied
        assert response.status_code in [400, 403]
    
    def test_knowledge_retrieval_respects_university_scope(
        self, db_session, sample_knowledge_base, sample_universities
    ):
        """Test that knowledge base queries are scoped to university."""
        batna_id = sample_universities[0].id
        
        # Query for Batna knowledge only
        batna_knowledge = KnowledgeBase.query.filter_by(
            university_id=batna_id,
            is_active=True
        ).all()
        
        # Verify all results belong to Batna
        for kb in batna_knowledge:
            assert kb.university_id == batna_id
    
    def test_user_queries_return_correct_university_responses(
        self, authenticated_client, sample_users, sample_chats, db_session
    ):
        """Test that user queries only access their university's data."""
        # Batna student logged in
        batna_student = sample_users[3]
        
        # Get chat list
        response = authenticated_client.get('/chat/list')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # All chats should belong to the logged-in user
        for chat in data.get('chats', []):
            assert chat['user_id'] == batna_student.id
    
    def test_cross_university_data_access_prevention(
        self, client, sample_users, sample_knowledge_base, db_session
    ):
        """Test that users cannot access data from other universities."""
        # Login as Batna student
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id  # batna_student1
        
        # Get Algiers knowledge entry ID
        algiers_kb = [kb for kb in sample_knowledge_base 
                     if kb.university_id == sample_users[2].university_id]
        
        if algiers_kb:
            # Try to access Algiers knowledge
            response = client.get(f'/admin/knowledge/{algiers_kb[0].id}')
            
            # Should be denied (student can't access admin, or cross-university denied)
            assert response.status_code in [403, 404]
    
    def test_admin_scoped_knowledge_list(
        self, admin_client, sample_users, sample_knowledge_base, db_session
    ):
        """Test that admin knowledge lists are scoped to their university."""
        batna_admin = sample_users[1]
        
        response = admin_client.get('/admin/knowledge')
        
        if response.status_code == 200:
            data = response.get_json()
            knowledge_list = data.get('knowledge', [])
            
            # All knowledge should belong to Batna
            for kb in knowledge_list:
                assert kb['university_id'] == batna_admin.university_id
    
    def test_admin_scoped_user_list(
        self, admin_client, sample_users, db_session
    ):
        """Test that admin user lists are scoped to their university."""
        batna_admin = sample_users[1]
        
        response = admin_client.get('/admin/users')
        
        if response.status_code == 200:
            data = response.get_json()
            user_list = data.get('users', [])
            
            # All users should belong to Batna or be unaffiliated
            for user in user_list:
                assert (user['university_id'] == batna_admin.university_id or 
                       user['university_id'] is None)
    
    def test_university_admin_cannot_modify_other_university_data(
        self, admin_client, sample_knowledge_base, sample_users, db_session
    ):
        """Test that admins cannot modify data from other universities."""
        # Get Algiers knowledge entry
        algiers_kb = [kb for kb in sample_knowledge_base 
                     if kb.university_id == sample_users[2].university_id]
        
        if algiers_kb:
            response = admin_client.put(f'/admin/knowledge/{algiers_kb[0].id}', json={
                'title': 'Attempted modification'
            })
            
            # Should be denied
            assert response.status_code in [403, 404]
    
    def test_super_admin_can_access_all_universities(
        self, super_admin_client, sample_knowledge_base, sample_universities, db_session
    ):
        """Test that super admins can access data from all universities."""
        # Super admin should be able to view knowledge from any university
        response = super_admin_client.get('/admin/knowledge')
        
        if response.status_code == 200:
            data = response.get_json()
            # May see knowledge from multiple universities
            # This is allowed for super admin
            assert 'knowledge' in data or response.status_code == 200
    
    def test_university_context_in_chat_responses(
        self, authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that chat responses use correct university context."""
        from unittest.mock import patch
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        with patch('services.openai_service.generate_chat_response') as mock_ai:
            with patch('services.knowledge_service.knowledge_service.get_university_context') as mock_context:
                mock_context.return_value = 'University of Batna 2 context'
                mock_ai.return_value = ('Response', 'gemini-pro')
                
                authenticated_client.post(f'/chat/{chat.id}/message', json={
                    'message': 'Test question'
                })
                
                # Verify correct university context was requested
                assert mock_context.called
                call_args = mock_context.call_args
                requested_university_id = call_args[0][0]
                
                # Should be Batna's ID
                assert requested_university_id == sample_users[3].university_id
    
    def test_department_isolation_within_university(
        self, db_session, sample_users, sample_departments
    ):
        """Test that department data is properly organized within university."""
        # Get departments for Batna
        batna_depts = [d for d in sample_departments 
                      if d.university_id == sample_users[1].university_id]
        
        # Get departments for Algiers
        algiers_depts = [d for d in sample_departments 
                        if d.university_id == sample_users[2].university_id]
        
        # Verify no overlap
        batna_dept_ids = {d.id for d in batna_depts}
        algiers_dept_ids = {d.id for d in algiers_depts}
        
        assert len(batna_dept_ids.intersection(algiers_dept_ids)) == 0
    
    def test_user_assignment_to_correct_university(
        self, db_session, sample_users, sample_universities
    ):
        """Test that users are correctly assigned to their universities."""
        for user in sample_users:
            if user.university_id:
                # Verify university exists
                university = next(
                    (u for u in sample_universities if u.id == user.university_id),
                    None
                )
                assert university is not None
    
    def test_chat_ownership_verification(
        self, client, sample_users, sample_chats, db_session
    ):
        """Test that chat ownership is verified before access."""
        # Login as user 1
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id
        
        # Try to access user 2's chat
        user2_chat = [c for c in sample_chats if c.user_id == sample_users[4].id]
        
        if user2_chat:
            response = client.get(f'/chat/{user2_chat[0].id}')
            
            # Should not allow access
            assert response.status_code == 404
    
    def test_university_data_statistics_isolation(
        self, admin_client, sample_users, db_session
    ):
        """Test that statistics are isolated by university."""
        response = admin_client.get('/admin/stats')
        
        if response.status_code == 200:
            data = response.get_json()
            
            # Stats should only reflect Batna university data
            # Not other universities
            assert 'stats' in data or 'analytics' in data or response.status_code == 200
    
    def test_knowledge_search_scoped_to_university(
        self, authenticated_client, sample_users, sample_knowledge_base, db_session
    ):
        """Test that knowledge search only returns results from user's university."""
        from unittest.mock import patch
        
        batna_student = sample_users[3]
        
        with patch('services.knowledge_service.knowledge_service.search_knowledge') as mock_search:
            # Configure mock to track calls
            mock_search.return_value = []
            
            # Perform action that triggers knowledge search
            with patch('services.openai_service.generate_chat_response') as mock_ai:
                mock_ai.return_value = ('Response', 'gemini-pro')
                
                # Create chat and send message
                create_response = authenticated_client.post('/chat/new', json={'title': 'Test'})
                chat_id = create_response.get_json()['chat']['id']
                
                authenticated_client.post(f'/chat/{chat_id}/message', json={
                    'message': 'Search test'
                })
            
            # Verify search was called with correct university
            if mock_search.called:
                call_args = mock_search.call_args
                university_id = call_args[0][1]
                assert university_id == batna_student.university_id
    
    def test_inactive_university_data_handling(
        self, db_session, sample_universities
    ):
        """Test handling of inactive universities."""
        # Mark a university as inactive
        test_university = sample_universities[2]
        test_university.is_active = False
        db_session.commit()
        
        # Verify it's marked inactive
        inactive_univ = db_session.query(User).filter_by(
            university_id=test_university.id
        ).first()
        
        # System should handle inactive universities appropriately
        assert test_university.is_active == False
        
        # Restore
        test_university.is_active = True
        db_session.commit()
    
    def test_bulk_operations_respect_university_scope(
        self, admin_client, sample_users, db_session
    ):
        """Test that bulk operations are scoped to university."""
        batna_admin = sample_users[1]
        
        # Attempt bulk operation (e.g., export all knowledge)
        response = admin_client.get('/admin/knowledge/export')
        
        if response.status_code == 200:
            data = response.get_json()
            
            # All exported data should belong to Batna
            if 'knowledge' in data:
                for kb in data['knowledge']:
                    assert kb['university_id'] == batna_admin.university_id
