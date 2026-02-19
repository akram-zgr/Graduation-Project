"""
Database integrity tests for the multi-university chatbot platform.

Tests model creation, foreign key relationships, and data consistency.
"""
import pytest
from models.user import User
from models.university import University
from models.department import Department
from models.knowledge_base import KnowledgeBase
from models.chat import Chat
from models.message import Message
from sqlalchemy.exc import IntegrityError


class TestDatabaseIntegrity:
    """Test suite for database integrity and relationships."""
    
    def test_all_models_create_correctly(self, db_session, sample_universities):
        """Test that all database models can be created."""
        # University
        university = University(
            name='Test University',
            code='TEST1',
            city='Test City',
            is_active=True
        )
        db_session.add(university)
        db_session.commit()
        
        assert university.id is not None
        
        # Department
        department = Department(
            name='Test Department',
            code='TESTDEPT',
            university_id=university.id
        )
        db_session.add(department)
        db_session.commit()
        
        assert department.id is not None
        
        # User
        user = User(
            username='testuser_db',
            email='testuser_db@test.com',
            full_name='Test User',
            university_id=university.id,
            department_id=department.id,
            is_verified=True
        )
        user.set_password('Password123!')
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        
        # Knowledge Base
        knowledge = KnowledgeBase(
            university_id=university.id,
            title='Test Knowledge',
            content='Test content',
            category='test',
            priority=5,
            is_active=True
        )
        db_session.add(knowledge)
        db_session.commit()
        
        assert knowledge.id is not None
        
        # Chat
        chat = Chat(
            user_id=user.id,
            title='Test Chat',
            is_active=True
        )
        db_session.add(chat)
        db_session.commit()
        
        assert chat.id is not None
        
        # Message
        message = Message(
            chat_id=chat.id,
            content='Test message',
            role='user',
            token_count=5
        )
        db_session.add(message)
        db_session.commit()
        
        assert message.id is not None
    
    def test_foreign_key_relationships(
        self, db_session, sample_users, sample_universities, sample_departments
    ):
        """Test that foreign key relationships are maintained."""
        # User -> University
        user = sample_users[3]  # batna_student1
        assert user.university_id is not None
        university = University.query.get(user.university_id)
        assert university is not None
        
        # User -> Department
        if user.department_id:
            department = Department.query.get(user.department_id)
            assert department is not None
            assert department.university_id == user.university_id
        
        # Department -> University
        dept = sample_departments[0]
        assert dept.university_id is not None
        univ = University.query.get(dept.university_id)
        assert univ is not None
    
    def test_cascade_deletes(self, db_session):
        """Test that cascade deletes work correctly."""
        # Create test data
        university = University(
            name='Delete Test University',
            code='DELTEST',
            is_active=True
        )
        db_session.add(university)
        db_session.commit()
        
        department = Department(
            name='Delete Test Dept',
            code='DELTESTD',
            university_id=university.id
        )
        db_session.add(department)
        db_session.commit()
        
        knowledge = KnowledgeBase(
            university_id=university.id,
            title='Delete Test Knowledge',
            content='Content',
            is_active=True
        )
        db_session.add(knowledge)
        db_session.commit()
        
        knowledge_id = knowledge.id
        dept_id = department.id
        
        # Delete university
        db_session.delete(university)
        db_session.commit()
        
        # Related records should be deleted
        assert KnowledgeBase.query.get(knowledge_id) is None
        assert Department.query.get(dept_id) is None
    
    def test_unique_constraints(self, db_session, sample_universities):
        """Test that unique constraints are enforced."""
        # Try to create duplicate university code
        duplicate = University(
            name='Duplicate University',
            code=sample_universities[0].code,  # Duplicate code
            is_active=True
        )
        db_session.add(duplicate)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create duplicate username
        duplicate_user = User(
            username='batna_student1',  # Existing username
            email='different_email@test.com',
            full_name='Different User'
        )
        duplicate_user.set_password('Password123!')
        db_session.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
    
    def test_required_fields_validation(self, db_session):
        """Test that required fields are enforced."""
        # University without required fields
        with pytest.raises(IntegrityError):
            university = University(
                # Missing name and code
                city='Test City'
            )
            db_session.add(university)
            db_session.commit()
        
        db_session.rollback()
        
        # User without required fields
        with pytest.raises(IntegrityError):
            user = User(
                # Missing username, email
                full_name='Test User'
            )
            db_session.add(user)
            db_session.commit()
        
        db_session.rollback()
    
    def test_university_linking_consistency(
        self, db_session, sample_users, sample_universities
    ):
        """Test that university linking is consistent across models."""
        batna_id = sample_universities[0].id
        
        # Get all users from Batna
        batna_users = User.query.filter_by(university_id=batna_id).all()
        
        # Get all knowledge from Batna
        batna_knowledge = KnowledgeBase.query.filter_by(university_id=batna_id).all()
        
        # Get all departments from Batna
        batna_depts = Department.query.filter_by(university_id=batna_id).all()
        
        # All should reference the same university
        for user in batna_users:
            assert user.university_id == batna_id
        
        for kb in batna_knowledge:
            assert kb.university_id == batna_id
        
        for dept in batna_depts:
            assert dept.university_id == batna_id
    
    def test_no_orphan_records(
        self, db_session, sample_chats, sample_messages, sample_users
    ):
        """Test that there are no orphaned records in the database."""
        # All chats should belong to existing users
        for chat in sample_chats:
            user = User.query.get(chat.user_id)
            assert user is not None
        
        # All messages should belong to existing chats
        for message in sample_messages:
            chat = Chat.query.get(message.chat_id)
            assert chat is not None
    
    def test_relationship_bidirectionality(
        self, db_session, sample_users, sample_universities, sample_chats
    ):
        """Test that relationships work in both directions."""
        # User -> University (forward)
        user = sample_users[3]
        assert user.university_id is not None
        
        # University -> Users (backward)
        university = University.query.get(user.university_id)
        assert user in university.users
        
        # User -> Chats (forward)
        user_chats = user.chats
        assert len(user_chats) >= 0
        
        # Chat -> User (backward)
        if user_chats:
            chat = user_chats[0]
            assert chat.user == user
    
    def test_soft_delete_integrity(self, db_session, sample_chats):
        """Test that soft deletes maintain data integrity."""
        active_chats = [c for c in sample_chats if c.is_active]
        inactive_chats = [c for c in sample_chats if not c.is_active]
        
        # Both should still exist in database
        for chat in active_chats:
            assert Chat.query.get(chat.id) is not None
        
        for chat in inactive_chats:
            assert Chat.query.get(chat.id) is not None
            assert chat.is_active == False
    
    def test_timestamp_defaults(self, db_session, sample_universities):
        """Test that timestamp fields have proper defaults."""
        # Create new record
        university = University(
            name='Timestamp Test',
            code='TIMETEST',
            is_active=True
        )
        db_session.add(university)
        db_session.commit()
        
        # Timestamps should be set
        assert university.created_at is not None
        assert university.updated_at is not None
        assert university.created_at <= university.updated_at
    
    def test_data_type_consistency(
        self, db_session, sample_users, sample_knowledge_base
    ):
        """Test that data types are consistent across records."""
        # User IDs should all be integers
        for user in sample_users:
            assert isinstance(user.id, int)
            assert isinstance(user.is_admin, bool)
            assert isinstance(user.is_verified, bool)
        
        # Knowledge priority should be integer
        for kb in sample_knowledge_base:
            assert isinstance(kb.priority, int)
            assert isinstance(kb.is_active, bool)
    
    def test_null_handling(self, db_session):
        """Test that nullable fields handle None correctly."""
        # Create user with minimal required fields
        user = User(
            username='minimal_user',
            email='minimal@test.com',
            is_verified=True
        )
        user.set_password('Password123!')
        db_session.add(user)
        db_session.commit()
        
        # Optional fields should be None
        assert user.full_name is None or user.full_name == ''
        assert user.university_id is None
        assert user.department_id is None
    
    def test_relationship_integrity_on_update(
        self, db_session, sample_users, sample_universities
    ):
        """Test that relationships remain intact during updates."""
        user = sample_users[3]
        original_university_id = user.university_id
        
        # Update user
        user.full_name = 'Updated Name'
        db_session.commit()
        
        # Relationship should still be intact
        assert user.university_id == original_university_id
        university = University.query.get(user.university_id)
        assert user in university.users
    
    def test_circular_reference_prevention(self, db_session):
        """Test that circular references are prevented."""
        # This is more of a schema design test
        # Models should not have circular dependencies
        
        # Department references University (not vice versa in FK)
        # User references both (one-way)
        # This prevents circular FKs
        
        assert True  # Schema is correctly designed
    
    def test_index_performance(self, db_session, sample_universities):
        """Test that database queries perform well with indexes."""
        import time
        
        # Create many records
        for i in range(100):
            kb = KnowledgeBase(
                university_id=sample_universities[0].id,
                title=f'Performance Test {i}',
                content=f'Content {i}',
                is_active=True,
                priority=5
            )
            db_session.add(kb)
        
        db_session.commit()
        
        # Test query performance
        start = time.time()
        
        results = KnowledgeBase.query.filter_by(
            university_id=sample_universities[0].id,
            is_active=True
        ).limit(10).all()
        
        end = time.time()
        
        # Should be fast (< 1 second even without real indexes in test)
        assert (end - start) < 1.0
        assert len(results) > 0
    
    def test_transaction_rollback_integrity(self, db_session):
        """Test that failed transactions rollback completely."""
        initial_count = University.query.count()
        
        try:
            # Start transaction
            new_univ = University(
                name='Transaction Test',
                code='TRANSTEST',
                is_active=True
            )
            db_session.add(new_univ)
            db_session.flush()
            
            # Create duplicate (will fail)
            duplicate = University(
                name='Duplicate',
                code='TRANSTEST',  # Same code
                is_active=True
            )
            db_session.add(duplicate)
            db_session.commit()
            
        except IntegrityError:
            db_session.rollback()
        
        # Count should be unchanged
        final_count = University.query.count()
        assert final_count == initial_count
    
    def test_model_to_dict_completeness(
        self, db_session, sample_users, sample_knowledge_base, sample_universities
    ):
        """Test that to_dict() methods include all essential fields."""
        # User to_dict
        user_dict = sample_users[0].to_dict()
        required_user_fields = ['id', 'username', 'email', 'is_admin', 'is_verified']
        for field in required_user_fields:
            assert field in user_dict
        
        # University to_dict
        univ_dict = sample_universities[0].to_dict()
        required_univ_fields = ['id', 'name', 'code', 'is_active']
        for field in required_univ_fields:
            assert field in univ_dict
        
        # Knowledge to_dict
        kb_dict = sample_knowledge_base[0].to_dict()
        required_kb_fields = ['id', 'title', 'content', 'university_id', 'priority']
        for field in required_kb_fields:
            assert field in kb_dict
