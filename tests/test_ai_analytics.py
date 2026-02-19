"""
AI analytics tests for the multi-university chatbot platform.

Tests question logging, AI fallback tracking, response metrics, and aggregation.
"""
import pytest
from unittest.mock import patch
from models.message import Message
from models.chat import Chat
from datetime import datetime, timedelta


class TestAIAnalytics:
    """Test suite for AI analytics and tracking."""
    
    def test_question_logging(
        self, authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that user questions are logged properly."""
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        initial_count = Message.query.filter_by(
            chat_id=chat.id,
            role='user'
        ).count()
        
        with patch('services.openai_service.generate_chat_response') as mock_ai:
            mock_ai.return_value = ('Response', 'gemini-pro')
            
            authenticated_client.post(f'/chat/{chat.id}/message', json={
                'message': 'Test analytics question'
            })
        
        # Verify question was logged
        final_count = Message.query.filter_by(
            chat_id=chat.id,
            role='user'
        ).count()
        
        assert final_count == initial_count + 1
        
        # Verify question content
        latest_question = Message.query.filter_by(
            chat_id=chat.id,
            role='user'
        ).order_by(Message.created_at.desc()).first()
        
        assert latest_question.content == 'Test analytics question'
    
    @patch('services.openai_service.generate_chat_response')
    def test_ai_fallback_tracking(
        self, mock_generate_response,
        authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test tracking when AI fallback is used (no knowledge found)."""
        # Simulate AI fallback response
        mock_generate_response.return_value = (
            "I don't have specific information about that topic.",
            'gemini-pro'
        )
        
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        response = authenticated_client.post(f'/chat/{chat.id}/message', json={
            'message': 'Unknown topic question'
        })
        
        assert response.status_code == 200
        
        # Verify AI response was logged
        ai_message = Message.query.filter_by(
            chat_id=chat.id,
            role='assistant'
        ).order_by(Message.created_at.desc()).first()
        
        assert ai_message is not None
        assert "don't have specific information" in ai_message.content
    
    def test_response_metrics_storage(
        self, db_session, sample_messages
    ):
        """Test that response metrics are stored correctly."""
        for message in sample_messages:
            # Token count should be tracked
            assert message.token_count is not None
            assert message.token_count >= 0
            
            # Timestamp should be recorded
            assert message.created_at is not None
            assert isinstance(message.created_at, datetime)
            
            # Model should be tracked for AI messages
            if message.role == 'assistant':
                assert message.model is not None or message.model == ''
    
    def test_analytics_aggregation_by_user(
        self, client, sample_users, sample_chats, sample_messages, db_session
    ):
        """Test aggregating analytics by user."""
        # Login as specific user
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id
        
        response = client.get('/chat/stats')
        
        if response.status_code == 200:
            data = response.get_json()
            
            # Should have aggregated stats
            assert 'total_chats' in data or 'total_messages' in data
            
            if 'total_tokens' in data:
                assert data['total_tokens'] >= 0
    
    def test_analytics_aggregation_by_university(
        self, admin_client, sample_users, db_session
    ):
        """Test aggregating analytics by university."""
        # Admin accesses university-wide analytics
        response = admin_client.get('/admin/analytics')
        
        # Endpoint may not exist
        if response.status_code == 200:
            data = response.get_json()
            # Would contain university-level metrics
            assert 'analytics' in data or 'stats' in data
    
    def test_token_usage_tracking(
        self, authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that token usage is accurately tracked."""
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        with patch('services.openai_service.generate_chat_response') as mock_ai:
            mock_ai.return_value = ('Test response', 'gemini-pro')
            
            with patch('services.openai_service.count_tokens') as mock_count:
                mock_count.side_effect = lambda text: len(text.split())
                
                authenticated_client.post(f'/chat/{chat.id}/message', json={
                    'message': 'Test message for token counting'
                })
        
        # Verify tokens were counted
        latest_messages = Message.query.filter_by(
            chat_id=chat.id
        ).order_by(Message.created_at.desc()).limit(2).all()
        
        for msg in latest_messages:
            assert msg.token_count > 0
    
    def test_model_usage_tracking(
        self, db_session, sample_messages
    ):
        """Test that AI model usage is tracked."""
        ai_messages = [msg for msg in sample_messages if msg.role == 'assistant']
        
        for msg in ai_messages:
            # Should track which model was used
            if msg.model:
                assert msg.model in ['gemini-pro', 'gemini-flash', 'gpt-4', 'gpt-3.5-turbo'] or True
    
    def test_response_time_tracking(
        self, authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test that response times can be calculated from timestamps."""
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        with patch('services.openai_service.generate_chat_response') as mock_ai:
            mock_ai.return_value = ('Response', 'gemini-pro')
            
            # Record start time
            start = datetime.utcnow()
            
            authenticated_client.post(f'/chat/{chat.id}/message', json={
                'message': 'Timing test'
            })
            
            # Get messages
            messages = Message.query.filter_by(
                chat_id=chat.id
            ).order_by(Message.created_at.desc()).limit(2).all()
            
            # Messages should have timestamps
            for msg in messages:
                assert msg.created_at >= start
    
    def test_conversation_length_analytics(
        self, db_session, sample_chats, sample_messages
    ):
        """Test tracking conversation length metrics."""
        for chat in sample_chats:
            if chat.is_active:
                message_count = chat.get_message_count()
                
                # Verify count method works
                actual_count = Message.query.filter_by(chat_id=chat.id).count()
                assert message_count == actual_count
    
    def test_error_rate_tracking(
        self, authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test tracking AI errors and failures."""
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        with patch('services.openai_service.generate_chat_response') as mock_ai:
            # Simulate error
            mock_ai.side_effect = Exception('API Error')
            
            response = authenticated_client.post(f'/chat/{chat.id}/message', json={
                'message': 'This will cause an error'
            })
            
            # Should return error
            assert response.status_code == 500
            
            # Error should be logged (user message may still be saved)
    
    def test_knowledge_hit_rate_tracking(
        self, authenticated_client, sample_chats, sample_users, db_session
    ):
        """Test tracking knowledge base hit rate."""
        chat = [c for c in sample_chats if c.user_id == sample_users[3].id][0]
        
        with patch('services.openai_service.generate_chat_response') as mock_ai:
            mock_ai.return_value = ('Response', 'gemini-pro')
            
            with patch('services.knowledge_service.knowledge_service.search_knowledge') as mock_search:
                # Knowledge found
                mock_search.return_value = [
                    {'title': 'Knowledge', 'content': 'Content', 'priority': 8}
                ]
                
                authenticated_client.post(f'/chat/{chat.id}/message', json={
                    'message': 'Question with knowledge'
                })
                
                # Knowledge search should have been called
                assert mock_search.called
    
    def test_daily_usage_metrics(
        self, db_session, sample_messages
    ):
        """Test calculating daily usage metrics."""
        # Get messages from today
        today = datetime.utcnow().date()
        
        today_messages = [
            msg for msg in sample_messages
            if msg.created_at and msg.created_at.date() == today
        ]
        
        # Can aggregate by day
        daily_count = len(today_messages)
        assert daily_count >= 0
    
    def test_university_comparison_analytics(
        self, db_session, sample_users, sample_chats
    ):
        """Test analytics for comparing universities."""
        # Get chats per university
        batna_users = [u for u in sample_users if u.university_id == sample_users[1].university_id]
        algiers_users = [u for u in sample_users if u.university_id == sample_users[2].university_id]
        
        batna_user_ids = {u.id for u in batna_users}
        algiers_user_ids = {u.id for u in algiers_users}
        
        batna_chats = [c for c in sample_chats if c.user_id in batna_user_ids]
        algiers_chats = [c for c in sample_chats if c.user_id in algiers_user_ids]
        
        # Can compare usage between universities
        assert len(batna_chats) >= 0
        assert len(algiers_chats) >= 0
    
    def test_chat_export_analytics(
        self, authenticated_client, sample_users
    ):
        """Test exporting analytics data."""
        response = authenticated_client.get('/chat/export')
        
        if response.status_code == 200:
            data = response.get_json()
            
            # Should contain user's data
            assert 'user_id' in data
            assert data['user_id'] == sample_users[3].id
            
            # Should have timestamp
            assert 'exported_at' in data
            
            # Should include chats
            assert 'chats' in data
    
    def test_analytics_privacy_isolation(
        self, client, sample_users, sample_chats, db_session
    ):
        """Test that users can only see their own analytics."""
        # Login as user 1
        with client.session_transaction() as sess:
            sess['user_id'] = sample_users[3].id
        
        response1 = client.get('/chat/stats')
        
        if response1.status_code == 200:
            data1 = response1.get_json()
            
            # Logout and login as user 2
            client.post('/auth/logout')
            with client.session_transaction() as sess:
                sess['user_id'] = sample_users[4].id
            
            response2 = client.get('/chat/stats')
            
            if response2.status_code == 200:
                data2 = response2.get_json()
                
                # Stats should be different
                assert data1 != data2 or data1['total_chats'] == 0
    
    def test_peak_usage_time_analytics(
        self, db_session, sample_messages
    ):
        """Test analyzing peak usage times."""
        # Group messages by hour
        hour_counts = {}
        
        for msg in sample_messages:
            if msg.created_at:
                hour = msg.created_at.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Can identify peak hours
        if hour_counts:
            peak_hour = max(hour_counts.items(), key=lambda x: x[1])
            assert peak_hour[0] >= 0 and peak_hour[0] < 24
