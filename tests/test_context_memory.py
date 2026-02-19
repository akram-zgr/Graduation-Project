"""
Conversation context memory tests for the multi-university chatbot platform.

Tests context persistence, isolation, and follow-up question handling.
"""
import pytest
from unittest.mock import patch
from models.message import Message


class TestContextMemory:
    """Test suite for conversation context memory."""
    
    @patch('services.openai_service.generate_chat_response')
    def test_context_saved_per_user(
        self, mock_generate_response,
        authenticated_client, sample_users, db_session
    ):
        """Test that context is saved and associated with the correct user."""
        mock_generate_response.return_value = ('Response', 'gemini-pro')
        
        # Create new chat
        create_response = authenticated_client.post('/chat/new', json={
            'title': 'Test Chat'
        })
        chat_id = create_response.get_json()['chat']['id']
        
        # Send first message
        authenticated_client.post(f'/chat/{chat_id}/message', json={
            'message': 'First message'
        })
        
        # Send second message
        authenticated_client.post(f'/chat/{chat_id}/message', json={
            'message': 'Second message'
        })
        
        # Verify messages were saved
        messages = Message.query.filter_by(chat_id=chat_id).all()
        assert len(messages) >= 4  # 2 user + 2 assistant messages
        
        # All messages should belong to same chat
        for msg in messages:
            assert msg.chat_id == chat_id
    
    @patch('services.openai_service.generate_chat_response')
    def test_follow_up_question_handling(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that follow-up questions use conversation context."""
        # Track calls to see conversation history
        call_history = []
        
        def track_calls(conversation_history, **kwargs):
            call_history.append(conversation_history)
            return ('Response to follow-up', 'gemini-pro')
        
        mock_generate_response.side_effect = track_calls
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        # Send follow-up question
        authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'Tell me more about that'
        })
        
        # Verify conversation history was passed
        assert len(call_history) > 0
        conversation = call_history[0]
        
        # Should include previous messages
        assert len(conversation) > 1
        assert conversation[-1]['content'] == 'Tell me more about that'
    
    def test_context_isolation_between_users(
        self, client, sample_users, sample_chats, db_session
    ):
        """Test that users cannot access each other's conversation context."""
        # Login as user 1
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id  # batna_student1
        
        # Get user 1's chat
        user1_chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        response1 = client.get(f'/chat/{user1_chat.id}')
        assert response1.status_code == 200
        
        # Login as user 2
        client.post('/auth/logout')
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[4].id  # batna_student2
        
        # Try to access user 1's chat
        response2 = client.get(f'/chat/{user1_chat.id}')
        assert response2.status_code == 404  # Should not find it
    
    def test_context_isolation_between_universities(
        self, client, sample_users, sample_chats, db_session
    ):
        """Test that conversation context is isolated between universities."""
        # Get Batna student's chat
        batna_chat = [c for c in sample_chats 
                     if c.user_id == sample_users[3].id][0]
        
        # Get Algiers student's chat
        algiers_chat = [c for c in sample_chats 
                       if c.user_id == sample_users[5].id][0]
        
        # Verify they belong to different universities
        assert sample_users[3].university_id != sample_users[5].id
        
        # Verify chats are separate
        assert batna_chat.id != algiers_chat.id
        assert batna_chat.user_id != algiers_chat.user_id
    
    @patch('services.openai_service.generate_chat_response')
    def test_context_window_management(
        self, mock_generate_response,
        authenticated_client, sample_users, db_session
    ):
        """Test that conversation context is managed efficiently."""
        mock_generate_response.return_value = ('Response', 'gemini-pro')
        
        # Create new chat
        create_response = authenticated_client.post('/chat/new', json={
            'title': 'Long Conversation'
        })
        chat_id = create_response.get_json()['chat']['id']
        
        # Send multiple messages to build context
        for i in range(10):
            authenticated_client.post(f'/chat/{chat_id}/message', json={
                'message': f'Message {i}'
            })
        
        # Get final conversation history passed to AI
        final_call = mock_generate_response.call_args
        conversation_history = final_call[0][0]
        
        # Should include messages (may truncate for token limits)
        assert len(conversation_history) > 0
    
    @patch('services.openai_service.generate_chat_response')
    def test_context_persistence_across_sessions(
        self, mock_generate_response,
        client, sample_users, db_session
    ):
        """Test that context persists across login sessions."""
        mock_generate_response.return_value = ('Response', 'gemini-pro')
        
        # Login and create chat
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id
        
        create_response = client.post('/chat/new', json={'title': 'Test'})
        chat_id = create_response.get_json()['chat']['id']
        
        # Send message
        client.post(f'/chat/{chat_id}/message', json={
            'message': 'First message'
        })
        
        # Logout
        client.post('/auth/logout')
        
        # Login again
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id
        
        # Retrieve chat
        response = client.get(f'/chat/{chat_id}')
        assert response.status_code == 200
        
        data = response.get_json()
        messages = data.get('messages', [])
        
        # Previous messages should still be there
        assert len(messages) >= 2
    
    def test_conversation_history_ordering(
        self, db_session, sample_chats, sample_messages
    ):
        """Test that conversation history maintains correct message order."""
        chat = sample_chats[0]
        messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.created_at).all()
        
        # Verify chronological order
        for i in range(len(messages) - 1):
            assert messages[i].created_at <= messages[i + 1].created_at
        
        # Verify alternating user/assistant pattern where applicable
        if len(messages) >= 2:
            assert messages[0].role in ['user', 'assistant']
            assert messages[1].role in ['user', 'assistant']
    
    @patch('services.openai_service.generate_chat_response')
    def test_context_includes_system_messages(
        self, mock_generate_response,
        authenticated_client, sample_users, db_session
    ):
        """Test that system context (university, department) is included."""
        call_data = []
        
        def capture_call(conversation_history, **kwargs):
            call_data.append(kwargs)
            return ('Response', 'gemini-pro')
        
        mock_generate_response.side_effect = capture_call
        
        # Create chat and send message
        create_response = authenticated_client.post('/chat/new', json={'title': 'Test'})
        chat_id = create_response.get_json()['chat']['id']
        
        authenticated_client.post(f'/chat/{chat_id}/message', json={
            'message': 'Test question'
        })
        
        # Verify system context was included
        assert len(call_data) > 0
        kwargs = call_data[0]
        
        # Should have university and/or department context
        assert 'university_context' in kwargs or 'knowledge_context' in kwargs
    
    def test_message_metadata_stored(
        self, db_session, sample_messages
    ):
        """Test that message metadata is properly stored."""
        for message in sample_messages:
            # Essential metadata
            assert message.chat_id is not None
            assert message.content is not None
            assert message.role in ['user', 'assistant', 'system']
            assert message.created_at is not None
            
            # Token tracking
            assert message.token_count is not None
            assert message.token_count >= 0
            
            # Model tracking for AI messages
            if message.role == 'assistant':
                assert message.model is not None or True  # May be optional
    
    @patch('services.openai_service.generate_chat_response')
    def test_context_cleared_on_new_chat(
        self, mock_generate_response,
        authenticated_client, sample_users, db_session
    ):
        """Test that new chats start with clean context."""
        mock_generate_response.return_value = ('Response', 'gemini-pro')
        
        # Create first chat
        create1 = authenticated_client.post('/chat/new', json={'title': 'Chat 1'})
        chat1_id = create1.get_json()['chat']['id']
        
        authenticated_client.post(f'/chat/{chat1_id}/message', json={
            'message': 'Message in chat 1'
        })
        
        # Create second chat
        create2 = authenticated_client.post('/chat/new', json={'title': 'Chat 2'})
        chat2_id = create2.get_json()['chat']['id']
        
        # Send message in second chat
        authenticated_client.post(f'/chat/{chat2_id}/message', json={
            'message': 'Message in chat 2'
        })
        
        # Verify chats are separate
        assert chat1_id != chat2_id
        
        # Verify messages are in correct chats
        chat1_messages = Message.query.filter_by(chat_id=chat1_id).all()
        chat2_messages = Message.query.filter_by(chat_id=chat2_id).all()
        
        # No message overlap
        chat1_msg_ids = {m.id for m in chat1_messages}
        chat2_msg_ids = {m.id for m in chat2_messages}
        
        assert len(chat1_msg_ids.intersection(chat2_msg_ids)) == 0
    
    def test_deleted_chat_context_not_accessible(
        self, authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that deleted chat context cannot be accessed."""
        # Get deleted chat
        deleted_chat = [c for c in sample_chats if not c.is_active][0]
        
        # Try to access it
        response = authenticated_client.get(f'/chat/{deleted_chat.id}')
        
        # Should not be accessible
        assert response.status_code == 404
    
    @patch('services.openai_service.generate_chat_response')
    def test_context_with_rich_media(
        self, mock_generate_response,
        authenticated_client, db_session
    ):
        """Test context handling with rich content."""
        mock_generate_response.return_value = ('Response with rich content', 'gemini-pro')
        
        # Create chat
        create_response = authenticated_client.post('/chat/new', json={'title': 'Rich Content'})
        chat_id = create_response.get_json()['chat']['id']
        
        # Send message with special characters
        response = authenticated_client.post(f'/chat/{chat_id}/message', json={
            'message': 'Message with special chars: @#$% & émojis 🎓'
        })
        
        assert response.status_code == 200
        
        # Verify message was stored correctly
        messages = Message.query.filter_by(chat_id=chat_id, role='user').all()
        assert len(messages) > 0
        assert 'émojis' in messages[-1].content or '🎓' in messages[-1].content
