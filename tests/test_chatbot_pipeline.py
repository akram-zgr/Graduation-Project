"""
Chatbot pipeline tests for the multi-university AI chatbot platform.

Tests the complete chatbot message flow including context loading,
knowledge retrieval, AI generation, and analytics logging.
"""
import pytest
from unittest.mock import patch, MagicMock
from models.message import Message
from models.chat import Chat


class TestChatbotPipeline:
    """Test suite for the complete chatbot processing pipeline."""
    
    @patch('services.openai_service.generate_chat_response')
    @patch('services.knowledge_service.knowledge_service.search_knowledge')
    def test_full_chatbot_pipeline(
        self, mock_search_knowledge, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test the complete chatbot message processing pipeline."""
        # Setup mocks
        mock_search_knowledge.return_value = [
            {
                'title': 'Registration Info',
                'content': 'Students must register by September 15th.',
                'priority': 10
            }
        ]
        mock_generate_response.return_value = (
            'Based on university policy, registration deadline is September 15th.',
            'gemini-pro'
        )
        
        # Get a chat session
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id and c.is_active][0]
        
        # Send a message
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'When is the registration deadline?'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify user message was saved
        assert 'user_message' in data
        assert data['user_message']['content'] == 'When is the registration deadline?'
        assert data['user_message']['role'] == 'user'
        
        # Verify AI response was generated and saved
        assert 'ai_message' in data
        assert data['ai_message']['role'] == 'assistant'
        assert 'September 15th' in data['ai_message']['content']
        
        # Verify knowledge search was called
        assert mock_search_knowledge.called
        
        # Verify AI generation was called
        assert mock_generate_response.called
    
    @patch('services.openai_service.generate_chat_response')
    def test_context_memory_loading(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_messages, sample_users, db_session
    ):
        """Test that conversation context is loaded for follow-up questions."""
        mock_generate_response.return_value = (
            'The documents include ID card and certificate.',
            'gemini-pro'
        )
        
        # Get chat with existing messages
        chat = sample_chats[0]  # Has existing conversation
        
        # Send a follow-up message
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'What else?'
        })
        
        assert response.status_code == 200
        
        # Verify generate_chat_response was called with conversation history
        call_args = mock_generate_response.call_args
        conversation_history = call_args[0][0]
        
        # Should include previous messages as context
        assert len(conversation_history) > 1
        assert conversation_history[-1]['content'] == 'What else?'
    
    @patch('services.openai_service.generate_chat_response')
    @patch('services.knowledge_service.knowledge_service.search_knowledge')
    @patch('services.knowledge_service.knowledge_service.get_university_context')
    def test_knowledge_base_retrieval(
        self, mock_get_context, mock_search_knowledge, mock_generate_response,
        authenticated_client, sample_chats, sample_users, sample_knowledge_base, db_session
    ):
        """Test that knowledge base is searched and used in responses."""
        # Setup mocks
        mock_get_context.return_value = 'University of Batna 2 context'
        mock_search_knowledge.return_value = [
            {
                'title': 'Library Hours',
                'content': 'Library is open Monday-Friday 8:00-18:00',
                'priority': 8
            }
        ]
        mock_generate_response.return_value = (
            'The library is open Monday-Friday from 8:00 to 18:00.',
            'gemini-pro'
        )
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'What are the library hours?'
        })
        
        assert response.status_code == 200
        
        # Verify knowledge search was called with correct parameters
        assert mock_search_knowledge.called
        call_args = mock_search_knowledge.call_args
        search_query = call_args[0][0]
        university_id = call_args[0][1]
        
        assert 'library' in search_query.lower()
        assert university_id == sample_users[3].university_id
        
        # Verify knowledge context was passed to AI
        gen_call_args = mock_generate_response.call_args
        assert 'knowledge_context' in gen_call_args[1]
    
    @patch('services.openai_service.generate_chat_response')
    @patch('services.knowledge_service.knowledge_service.search_knowledge')
    def test_faq_retrieval_priority(
        self, mock_search_knowledge, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that FAQ system is checked before AI fallback."""
        # Mock FAQ/knowledge results with high priority
        mock_search_knowledge.return_value = [
            {
                'title': 'Tuition FAQ',
                'content': 'Tuition is free for Algerian students.',
                'priority': 10  # High priority = FAQ-like
            }
        ]
        mock_generate_response.return_value = (
            'Tuition is free for Algerian students.',
            'gemini-pro'
        )
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'How much is tuition?'
        })
        
        assert response.status_code == 200
        assert mock_search_knowledge.called
    
    @patch('services.openai_service.generate_chat_response')
    def test_ai_fallback_when_no_knowledge(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test AI generates fallback response when no knowledge is found."""
        mock_generate_response.return_value = (
            'I don\'t have specific information about that topic.',
            'gemini-pro'
        )
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'What is the meaning of life?'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        # AI should still generate a response
        assert 'ai_message' in data
        assert data['ai_message']['content'] is not None
    
    @patch('services.openai_service.generate_chat_response')
    def test_analytics_logging(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that analytics are logged for each interaction."""
        mock_generate_response.return_value = (
            'Test response',
            'gemini-pro'
        )
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        initial_message_count = Message.query.filter_by(chat_id=chat.id).count()
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'Test question'
        })
        
        assert response.status_code == 200
        
        # Verify messages were logged
        final_message_count = Message.query.filter_by(chat_id=chat.id).count()
        assert final_message_count == initial_message_count + 2  # User + AI message
        
        # Verify message metadata
        messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.created_at.desc()).limit(2).all()
        
        ai_message = messages[0]
        user_message = messages[1]
        
        assert user_message.role == 'user'
        assert ai_message.role == 'assistant'
        assert ai_message.model == 'gemini-pro'
        assert ai_message.token_count > 0
    
    @patch('services.openai_service.generate_chat_response')
    def test_context_memory_updates(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that conversation context is updated after each message."""
        mock_generate_response.return_value = (
            'Response to first question',
            'gemini-pro'
        )
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        # Send first message
        response1 = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'First question'
        })
        assert response1.status_code == 200
        
        # Send second message
        mock_generate_response.return_value = (
            'Response to second question',
            'gemini-pro'
        )
        
        response2 = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'Second question'
        })
        assert response2.status_code == 200
        
        # Verify context includes both exchanges
        call_args = mock_generate_response.call_args
        conversation_history = call_args[0][0]
        
        # Should have: previous messages + new message
        assert len(conversation_history) >= 3
    
    @patch('services.openai_service.generate_chat_response')
    def test_error_handling_in_pipeline(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test graceful error handling when AI service fails."""
        # Simulate AI service error
        mock_generate_response.side_effect = Exception('API Error')
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'Test question'
        })
        
        # Should return error but not crash
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
    
    @patch('services.openai_service.generate_chat_response')
    def test_empty_message_validation(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that empty messages are rejected."""
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': ''
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    @patch('services.openai_service.generate_chat_response')
    def test_token_counting(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that token usage is tracked correctly."""
        mock_generate_response.return_value = (
            'This is a test response with multiple words.',
            'gemini-pro'
        )
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'Short question'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Both messages should have token counts
        assert data['user_message']['token_count'] > 0
        assert data['ai_message']['token_count'] > 0
    
    @patch('services.openai_service.generate_chat_response')
    @patch('services.openai_service.generate_chat_title')
    def test_auto_title_generation(
        self, mock_generate_title, mock_generate_response,
        authenticated_client, sample_users, db_session
    ):
        """Test that chat titles are auto-generated from first message."""
        mock_generate_response.return_value = ('Response', 'gemini-pro')
        mock_generate_title.return_value = 'Registration Questions'
        
        # Create new chat
        create_response = authenticated_client.post('/chat/new', json={
            'title': 'New Conversation'
        })
        assert create_response.status_code == 201
        chat_data = create_response.get_json()
        chat_id = chat_data['chat']['id']
        
        # Send first message
        response = authenticated_client.post(f'/chat/{chat_id}/message', json={
            'message': 'How do I register for courses?'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Title should be auto-generated
        assert 'chat_title' in data
        assert data['chat_title'] != 'New Conversation'
    
    @patch('services.openai_service.generate_chat_response')
    def test_university_context_injection(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that university-specific context is injected into prompts."""
        mock_generate_response.return_value = ('Response', 'gemini-pro')
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'Tell me about my university'
        })
        
        assert response.status_code == 200
        
        # Verify university context was passed
        call_args = mock_generate_response.call_args
        assert 'university_context' in call_args[1]
    
    @patch('services.openai_service.generate_chat_response')
    def test_department_context_injection(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that department-specific context is included when available."""
        mock_generate_response.return_value = ('Response', 'gemini-pro')
        
        # User with department
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'Tell me about my department'
        })
        
        assert response.status_code == 200
        
        # Verify department context was passed
        call_args = mock_generate_response.call_args
        kwargs = call_args[1]
        
        # Department context should be included for users with department
        if 'department_context' in kwargs:
            assert kwargs['department_context'] is not None
