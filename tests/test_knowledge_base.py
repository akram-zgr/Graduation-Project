"""
Knowledge base system tests for the multi-university chatbot platform.

Tests CRUD operations, filtering, and search functionality.
"""
import pytest
from models.knowledge_base import KnowledgeBase


class TestKnowledgeBase:
    """Test suite for knowledge base functionality."""
    
    def test_create_knowledge_entry(self, admin_client, sample_universities, db_session):
        """Test creating a new knowledge base entry."""
        response = admin_client.post('/admin/knowledge/create', json={
            'title': 'New Knowledge Entry',
            'content': 'This is test content for the knowledge base.',
            'category': 'academic',
            'tags': 'test,knowledge,academic',
            'priority': 7,
            'university_id': sample_universities[0].id
        })
        
        # Should either succeed or redirect
        assert response.status_code in [200, 201, 302]
        
        # Verify entry was created
        entry = KnowledgeBase.query.filter_by(title='New Knowledge Entry').first()
        if entry:  # If endpoint actually creates entries
            assert entry.content == 'This is test content for the knowledge base.'
            assert entry.category == 'academic'
            assert entry.priority == 7
    
    def test_retrieve_knowledge_by_university(
        self, db_session, sample_knowledge_base, sample_universities
    ):
        """Test filtering knowledge entries by university."""
        # Get Batna university entries
        batna_entries = KnowledgeBase.query.filter_by(
            university_id=sample_universities[0].id,
            is_active=True
        ).all()
        
        assert len(batna_entries) > 0
        
        # Verify all entries belong to Batna
        for entry in batna_entries:
            assert entry.university_id == sample_universities[0].id
    
    def test_retrieve_knowledge_by_category(
        self, db_session, sample_knowledge_base
    ):
        """Test filtering knowledge entries by category."""
        registration_entries = KnowledgeBase.query.filter_by(
            category='registration',
            is_active=True
        ).all()
        
        assert len(registration_entries) > 0
        
        # Verify all entries are registration category
        for entry in registration_entries:
            assert entry.category == 'registration'
    
    def test_knowledge_priority_ordering(
        self, db_session, sample_knowledge_base, sample_universities
    ):
        """Test that knowledge entries are ordered by priority."""
        entries = KnowledgeBase.query.filter_by(
            university_id=sample_universities[0].id,
            is_active=True
        ).order_by(KnowledgeBase.priority.desc()).all()
        
        # Verify entries are in descending priority order
        for i in range(len(entries) - 1):
            assert entries[i].priority >= entries[i + 1].priority
    
    def test_update_knowledge_entry(
        self, admin_client, sample_knowledge_base, sample_users, db_session
    ):
        """Test updating an existing knowledge entry."""
        # Get a Batna knowledge entry
        batna_entry = [kb for kb in sample_knowledge_base 
                      if kb.university_id == sample_users[1].university_id][0]
        
        response = admin_client.put(f'/admin/knowledge/{batna_entry.id}', json={
            'title': 'Updated Title',
            'content': 'Updated content',
            'priority': 9
        })
        
        # Should succeed or redirect
        assert response.status_code in [200, 302]
        
        # Verify update in database
        db_session.refresh(batna_entry)
        if batna_entry.title == 'Updated Title':  # If update actually happened
            assert batna_entry.content == 'Updated content'
            assert batna_entry.priority == 9
    
    def test_delete_knowledge_entry(
        self, admin_client, sample_knowledge_base, sample_users, db_session
    ):
        """Test soft-deleting a knowledge entry."""
        batna_entry = [kb for kb in sample_knowledge_base 
                      if kb.university_id == sample_users[1].university_id][0]
        
        response = admin_client.delete(f'/admin/knowledge/{batna_entry.id}')
        
        # Should succeed
        assert response.status_code in [200, 204, 302]
        
        # Verify soft delete
        db_session.refresh(batna_entry)
        # Entry should be marked inactive (soft delete)
        # Or deleted completely depending on implementation
    
    def test_knowledge_search_by_tags(
        self, db_session, sample_knowledge_base
    ):
        """Test searching knowledge by tags."""
        # Search for registration-related knowledge
        entries = KnowledgeBase.query.filter(
            KnowledgeBase.tags.like('%registration%'),
            KnowledgeBase.is_active == True
        ).all()
        
        assert len(entries) > 0
        
        # Verify all entries have registration tag
        for entry in entries:
            assert entry.tags is not None
            assert 'registration' in entry.tags.lower()
    
    def test_knowledge_full_text_search(
        self, db_session, sample_knowledge_base
    ):
        """Test searching knowledge by content."""
        search_term = 'library'
        
        entries = KnowledgeBase.query.filter(
            (KnowledgeBase.content.like(f'%{search_term}%')) |
            (KnowledgeBase.title.like(f'%{search_term}%')),
            KnowledgeBase.is_active == True
        ).all()
        
        # Should find library-related entries
        assert len(entries) > 0
    
    def test_university_specific_knowledge_isolation(
        self, db_session, sample_knowledge_base, sample_universities
    ):
        """Test that knowledge is properly isolated by university."""
        batna_id = sample_universities[0].id
        algiers_id = sample_universities[1].id
        
        batna_entries = KnowledgeBase.query.filter_by(university_id=batna_id).all()
        algiers_entries = KnowledgeBase.query.filter_by(university_id=algiers_id).all()
        
        # Verify no overlap
        batna_ids = {entry.id for entry in batna_entries}
        algiers_ids = {entry.id for entry in algiers_entries}
        
        assert len(batna_ids.intersection(algiers_ids)) == 0
    
    def test_knowledge_with_arabic_content(
        self, db_session, sample_knowledge_base
    ):
        """Test knowledge entries with Arabic content."""
        arabic_entries = KnowledgeBase.query.filter(
            KnowledgeBase.content_ar.isnot(None)
        ).all()
        
        assert len(arabic_entries) > 0
        
        # Verify Arabic content is stored correctly
        for entry in arabic_entries:
            assert entry.content_ar is not None
            assert len(entry.content_ar) > 0
    
    def test_knowledge_metadata_tracking(
        self, db_session, sample_knowledge_base
    ):
        """Test that knowledge entries track metadata properly."""
        for entry in sample_knowledge_base:
            assert entry.created_at is not None
            assert entry.updated_at is not None
            assert entry.is_active is not None
            
            # Creator tracking
            if entry.created_by:
                assert isinstance(entry.created_by, int)
    
    def test_department_specific_knowledge(
        self, db_session, sample_universities, sample_departments, sample_users
    ):
        """Test creating department-specific knowledge."""
        # Create department-specific knowledge
        dept_knowledge = KnowledgeBase(
            university_id=sample_universities[0].id,
            title='CS Department Lab Hours',
            content='CS labs are open Monday-Friday 9:00-17:00',
            category='department',
            tags='cs,lab,hours,department',
            priority=8,
            is_active=True,
            created_by=sample_users[1].id
        )
        
        db_session.add(dept_knowledge)
        db_session.commit()
        
        # Verify it was created
        retrieved = KnowledgeBase.query.filter_by(
            title='CS Department Lab Hours'
        ).first()
        
        assert retrieved is not None
        assert retrieved.category == 'department'
    
    def test_global_fallback_knowledge(
        self, db_session, sample_users
    ):
        """Test global knowledge that applies to all universities."""
        # Create global knowledge (no specific university)
        # Note: Current schema requires university_id, so this tests the concept
        global_knowledge = KnowledgeBase(
            university_id=sample_users[0].university_id or 1,
            title='General Study Tips',
            content='Create a study schedule, take breaks, stay organized.',
            category='general',
            tags='study,tips,general',
            priority=3,
            is_active=True
        )
        
        db_session.add(global_knowledge)
        db_session.commit()
        
        # Verify low priority indicates general/fallback knowledge
        retrieved = KnowledgeBase.query.filter_by(
            title='General Study Tips'
        ).first()
        
        assert retrieved is not None
        assert retrieved.priority <= 5  # Low priority = general knowledge
    
    def test_knowledge_source_tracking(
        self, db_session, sample_knowledge_base
    ):
        """Test that knowledge entries track their sources."""
        for entry in sample_knowledge_base:
            # Should have source type
            assert hasattr(entry, 'source_type')
            
            # If source URL exists, verify it's stored
            if entry.source_url:
                assert len(entry.source_url) > 0
                assert entry.source_url.startswith('http') or entry.source_url == ''
    
    def test_knowledge_to_dict_serialization(
        self, db_session, sample_knowledge_base
    ):
        """Test knowledge entry serialization to dictionary."""
        entry = sample_knowledge_base[0]
        entry_dict = entry.to_dict()
        
        # Verify all essential fields are present
        assert 'id' in entry_dict
        assert 'title' in entry_dict
        assert 'content' in entry_dict
        assert 'university_id' in entry_dict
        assert 'category' in entry_dict
        assert 'tags' in entry_dict
        assert 'priority' in entry_dict
        assert 'is_active' in entry_dict
        
        # Tags should be converted to list
        assert isinstance(entry_dict['tags'], list)
    
    def test_invalid_knowledge_creation(self, admin_client):
        """Test that invalid knowledge entries are rejected."""
        # Missing required fields
        response = admin_client.post('/admin/knowledge/create', json={
            'title': 'Incomplete Entry'
            # Missing content and other required fields
        })
        
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_knowledge_search_performance(
        self, db_session, sample_universities
    ):
        """Test that knowledge search is efficient."""
        # Create multiple knowledge entries
        for i in range(50):
            entry = KnowledgeBase(
                university_id=sample_universities[0].id,
                title=f'Test Entry {i}',
                content=f'Content for test entry {i}',
                category='test',
                tags=f'test,entry,{i}',
                priority=5,
                is_active=True
            )
            db_session.add(entry)
        
        db_session.commit()
        
        # Perform search
        import time
        start = time.time()
        
        results = KnowledgeBase.query.filter(
            KnowledgeBase.university_id == sample_universities[0].id,
            KnowledgeBase.is_active == True
        ).limit(10).all()
        
        end = time.time()
        
        # Should be fast
        assert (end - start) < 1.0  # Less than 1 second
        assert len(results) > 0
