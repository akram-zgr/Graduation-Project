"""
Authentication tests for the chatbot platform.

Tests user login, logout, session management, and role assignment.
"""
import pytest
from models.user import User


class TestAuthentication:
    """Test suite for authentication functionality."""
    
    def test_user_login_success(self, client, sample_users):
        """Test successful user login with valid credentials."""
        response = client.post('/auth/login', json={
            'username': 'batna_student1',
            'password': 'Student123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert 'user' in data
        assert data['user']['username'] == 'batna_student1'
        
        # Verify session was created
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert sess['username'] == 'batna_student1'
    
    def test_user_login_invalid_username(self, client, sample_users):
        """Test login fails with invalid username."""
        response = client.post('/auth/login', json={
            'username': 'nonexistent_user',
            'password': 'SomePassword123!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_user_login_invalid_password(self, client, sample_users):
        """Test login fails with incorrect password."""
        response = client.post('/auth/login', json={
            'username': 'batna_student1',
            'password': 'WrongPassword123!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_user_login_unverified_email(self, client, sample_users):
        """Test unverified users cannot login."""
        response = client.post('/auth/login', json={
            'username': 'unverified',
            'password': 'Unverified123!'
        })
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'verify' in data.get('error', '').lower()
    
    def test_user_signup_success(self, client, sample_universities, db_session):
        """Test successful user registration."""
        response = client.post('/auth/signup', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'NewUser123!',
            'full_name': 'New User',
            'university_id': sample_universities[0].id,
            'student_id': 'NEW2021001'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        
        # Verify user was created in database
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@test.com'
        assert user.is_verified == False  # Should start unverified
        assert user.verification_token is not None
    
    def test_user_signup_duplicate_username(self, client, sample_users):
        """Test signup fails with duplicate username."""
        response = client.post('/auth/signup', json={
            'username': 'batna_student1',  # Existing username
            'email': 'different@test.com',
            'password': 'Password123!',
            'full_name': 'Different User'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_user_signup_duplicate_email(self, client, sample_users):
        """Test signup fails with duplicate email."""
        response = client.post('/auth/signup', json={
            'username': 'differentuser',
            'email': 'student1@batna2.test.com',  # Existing email
            'password': 'Password123!',
            'full_name': 'Different User'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_user_logout(self, authenticated_client):
        """Test user logout clears session."""
        # Verify user is logged in
        with authenticated_client.session_transaction() as sess:
            assert 'user_id' in sess
        
        # Logout
        response = authenticated_client.post('/auth/logout')
        assert response.status_code == 200
        
        # Verify session was cleared
        with authenticated_client.session_transaction() as sess:
            assert 'user_id' not in sess
    
    def test_session_persistence(self, authenticated_client):
        """Test session persists across requests."""
        # Make first request
        response1 = authenticated_client.get('/chat/')
        assert response1.status_code == 200
        
        # Make second request - should still be authenticated
        response2 = authenticated_client.get('/chat/list')
        assert response2.status_code == 200
    
    def test_role_assignment_student(self, client, sample_users, db_session):
        """Test students are correctly assigned non-admin role."""
        user = User.query.filter_by(username='batna_student1').first()
        assert user is not None
        assert user.is_admin == False
    
    def test_role_assignment_admin(self, client, sample_users, db_session):
        """Test admins are correctly assigned admin role."""
        user = User.query.filter_by(username='batna_admin').first()
        assert user is not None
        assert user.is_admin == True
    
    def test_role_assignment_super_admin(self, client, sample_users, db_session):
        """Test super admins have admin role."""
        user = User.query.filter_by(username='superadmin').first()
        assert user is not None
        assert user.is_admin == True
        assert user.university_id is None  # Super admin has no university affiliation
    
    def test_password_hashing(self, db_session):
        """Test passwords are properly hashed and verified."""
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User'
        )
        user.set_password('TestPassword123!')
        
        # Password should be hashed, not stored in plain text
        assert user.password_hash != 'TestPassword123!'
        assert len(user.password_hash) > 50  # Hashed passwords are long
        
        # Correct password should verify
        assert user.check_password('TestPassword123!') == True
        
        # Incorrect password should not verify
        assert user.check_password('WrongPassword') == False
    
    def test_verification_token_generation(self, db_session):
        """Test verification token is generated correctly."""
        user = User(
            username='testuser2',
            email='test2@example.com',
            full_name='Test User 2'
        )
        user.set_password('Password123!')
        
        token = user.generate_verification_token()
        
        assert token is not None
        assert len(token) > 20
        assert user.verification_token == token
    
    def test_email_verification_process(self, db_session):
        """Test email verification updates user status."""
        user = User(
            username='testuser3',
            email='test3@example.com',
            full_name='Test User 3',
            is_verified=False
        )
        user.set_password('Password123!')
        user.generate_verification_token()
        
        assert user.is_verified == False
        assert user.verification_token is not None
        
        user.verify_email()
        
        assert user.is_verified == True
        assert user.verification_token is None
    
    def test_missing_credentials(self, client):
        """Test login fails when credentials are missing."""
        response = client.post('/auth/login', json={
            'username': 'someuser'
            # Missing password
        })
        
        assert response.status_code in [400, 401]
    
    def test_empty_credentials(self, client):
        """Test login fails with empty credentials."""
        response = client.post('/auth/login', json={
            'username': '',
            'password': ''
        })
        
        assert response.status_code in [400, 401]
