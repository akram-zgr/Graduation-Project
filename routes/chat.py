from flask import Blueprint, request, jsonify, session, render_template
from models.user import User
from models.chat import Chat
from models.message import Message
from models.university import University
from extensions import db
from services.openai_service import generate_chat_response, count_tokens, generate_chat_title
from services.knowledge_service import knowledge_service
from services.faq_service import search_faq
from services.translation_service import get_translation, get_all_translations
from utils.decorators import login_required
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
@login_required
def chat_page():
    """Render the main chat interface"""
    return render_template('chat/chat.html')

@chat_bp.route('/user-info')
@login_required
def user_info():
    user = User.query.get(session['user_id'])
    return jsonify(user.to_dict())

@chat_bp.route('/new', methods=['POST'])
@login_required
def create_chat():
    """Create a new chat session"""
    user_id = session.get('user_id')
    data = request.get_json()
    
    title = data.get('title', 'New Conversation')
    
    chat = Chat(user_id=user_id, title=title)
    
    try:
        db.session.add(chat)
        db.session.commit()
        return jsonify({'chat': chat.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create chat'}), 500

@chat_bp.route('/list', methods=['GET'])
@login_required
def list_chats():
    """Get all chats for the current user"""
    user_id = session.get('user_id')
    
    chats = Chat.query.filter_by(user_id=user_id, is_active=True).order_by(Chat.updated_at.desc()).all()
    
    return jsonify({
        'chats': [chat.to_dict() for chat in chats]
    }), 200

@chat_bp.route('/<int:chat_id>', methods=['GET'])
@login_required
def get_chat(chat_id):
    """Get a specific chat with all messages"""
    user_id = session.get('user_id')
    
    chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    messages = [msg.to_dict() for msg in chat.messages]
    
    return jsonify({
        'chat': chat.to_dict(),
        'messages': messages
    }), 200

@chat_bp.route('/<int:chat_id>/message', methods=['POST'])
@login_required
def send_message(chat_id):
    """Send a message and get AI response"""
    user_id = session.get('user_id')
    
    chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    try:
        # Get user and university info
        user = User.query.get(user_id)
        university_context = None
        knowledge_context = None
        department_context = None
        
        if user and user.university_id:
            # Get university context
            university_context = knowledge_service.get_university_context(user.university_id)
            
            # Get department context if user has department
            if user.department_id:
                from models.department import Department
                department = Department.query.get(user.department_id)
                if department:
                    department_context = f"""Department: {department.name}
Department Code: {department.code}
Official Website: {department.official_website or 'Not available'}
Email: {department.email or 'Not available'}
Building: {department.building or 'Not specified'}
Description: {department.description or 'No description available'}
Head of Department: {department.head_of_department or 'Not specified'}"""
            
            # Search knowledge base with department hierarchy
            knowledge_results = knowledge_service.search_knowledge(
                user_message, 
                user.university_id, 
                department_id=user.department_id,
                limit=3
            )
            
            if knowledge_results:
                # Build knowledge context from top results
                knowledge_pieces = []
                for result in knowledge_results:
                    knowledge_pieces.append(f"- {result['title']}: {result['content'][:300]}")
                knowledge_context = "\n".join(knowledge_pieces)
        
        # Save user message
        user_msg = Message(
            chat_id=chat_id,
            content=user_message,
            role='user',
            token_count=count_tokens(user_message)
        )
        db.session.add(user_msg)
        
        # ── FAQ FIRST: try to answer from the FAQ database ──────────────────
        # Retrieve university object for placeholder substitution
        university_obj = None
        if user and user.university_id:
            from models.university import University
            university_obj = University.query.get(user.university_id)

        faq_result = search_faq(user_message, university=university_obj)
        faq_used = False
        model_used = 'faq'

        if faq_result.get('found') and faq_result.get('confidence', 0) >= 0.40:
            # High-confidence FAQ hit → return directly in the user's language
            ai_response = faq_result['answer']
            faq_used = True
        else:
            # ── FALLBACK: use AI (Gemini) ───────────────────────────────────
            faq_used = False

            # Get conversation history
            conversation_history = [
                {'role': msg.role, 'content': msg.content}
                for msg in chat.messages
            ]
            conversation_history.append({'role': 'user', 'content': user_message})

            # Generate AI response with university, department, and knowledge context
            ai_response, model_used = generate_chat_response(
                conversation_history,
                university_context=university_context,
                knowledge_context=knowledge_context,
                department_context=department_context
            )
        # ────────────────────────────────────────────────────────────────────

        is_error = (
            not faq_used and (
                ai_response.startswith("Error:") or
                ai_response.startswith("⚠️") or
                "I apologize, but" in ai_response or
                "unable to respond" in ai_response or
                "contact the administrator" in ai_response or
                "contact your system administrator" in ai_response
            )
        )
        
        # Save AI response
        ai_msg = Message(
            chat_id=chat_id,
            content=ai_response,
            role='assistant',
            token_count=count_tokens(ai_response),
            model=model_used
        )
        db.session.add(ai_msg)
        
        # Update chat timestamp
        chat.updated_at = datetime.utcnow()
        
        # Auto-generate title from first message using AI
        if chat.get_message_count() == 0 and len(user_message) > 0:
            # Try to generate a smart title
            generated_title = generate_chat_title(user_message)
            chat.title = generated_title if generated_title else (user_message[:50] + ('...' if len(user_message) > 50 else ''))
        
        db.session.commit()
        
        response_data = {
            'user_message': user_msg.to_dict(),
            'ai_message': ai_msg.to_dict(),
            'chat_title': chat.title,
            'faq_used': faq_used,
            'faq_confidence': faq_result.get('confidence') if faq_used else None,
        }
        
        if is_error:
            response_data['warning'] = 'API_ERROR'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process message: {str(e)}'}), 500

@chat_bp.route('/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    """Delete a chat (soft delete)"""
    user_id = session.get('user_id')
    
    chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    try:
        chat.is_active = False
        db.session.commit()
        return jsonify({'message': 'Chat deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete chat'}), 500

@chat_bp.route('/<int:chat_id>/rename', methods=['PUT'])
@login_required
def rename_chat(chat_id):
    """Rename a chat"""
    user_id = session.get('user_id')
    
    chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    data = request.get_json()
    new_title = data.get('title', '').strip()
    
    if not new_title:
        return jsonify({'error': 'Title cannot be empty'}), 400
    
    try:
        chat.title = new_title
        db.session.commit()
        return jsonify({'chat': chat.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to rename chat'}), 500

@chat_bp.route('/stats', methods=['GET'])
@login_required
def get_chat_stats():
    """Get chat statistics for the current user"""
    user_id = session.get('user_id')
    
    total_chats = Chat.query.filter_by(user_id=user_id, is_active=True).count()
    
    # Get total messages
    total_messages = db.session.query(Message).join(Chat).filter(
        Chat.user_id == user_id,
        Chat.is_active == True
    ).count()
    
    # Get total tokens used
    total_tokens = db.session.query(db.func.sum(Message.token_count)).join(Chat).filter(
        Chat.user_id == user_id,
        Chat.is_active == True
    ).scalar() or 0
    
    return jsonify({
        'total_chats': total_chats,
        'total_messages': total_messages,
        'total_tokens': total_tokens
    }), 200

@chat_bp.route('/export', methods=['GET'])
@login_required
def export_data():
    """Export all chat data for the current user"""
    user_id = session.get('user_id')
    
    chats = Chat.query.filter_by(user_id=user_id, is_active=True).all()
    
    export_data = {
        'user_id': user_id,
        'exported_at': datetime.utcnow().isoformat(),
        'chats': []
    }
    
    for chat in chats:
        chat_data = chat.to_dict()
        chat_data['messages'] = [msg.to_dict() for msg in chat.messages]
        export_data['chats'].append(chat_data)
    
    return jsonify(export_data), 200

@chat_bp.route('/clear-all', methods=['DELETE'])
@login_required
def clear_all_chats():
    """Clear all chats for the current user"""
    user_id = session.get('user_id')
    
    try:
        Chat.query.filter_by(user_id=user_id).update({'is_active': False})
        db.session.commit()
        return jsonify({'message': 'All chats cleared successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to clear chats'}), 500

@chat_bp.route('/translations/<language>', methods=['GET'])
def get_translations(language):
    """Get all translations for a specific language"""
    translations = get_all_translations(language)
    return jsonify({'translations': translations, 'language': language}), 200

@chat_bp.route('/<int:chat_id>/message/<int:message_id>/regenerate', methods=['POST'])
@login_required
def regenerate_message(chat_id, message_id):
    """Regenerate an AI response"""
    user_id = session.get('user_id')
    
    chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first()
    
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    # Find the message to regenerate
    message = Message.query.filter_by(id=message_id, chat_id=chat_id, role='assistant').first()
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    try:
        # Get user and university info
        user = User.query.get(user_id)
        university_context = None
        
        if user and user.university_id:
            university_context = knowledge_service.get_university_context(user.university_id)
        
        # Get conversation history up to (but not including) the message to regenerate
        messages_before = Message.query.filter(
            Message.chat_id == chat_id,
            Message.id < message_id
        ).order_by(Message.created_at).all()
        
        conversation_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in messages_before
        ]
        
        # Get knowledge context from last user message
        knowledge_context = None
        if conversation_history and user and user.university_id:
            last_user_message = next((msg['content'] for msg in reversed(conversation_history) if msg['role'] == 'user'), None)
            if last_user_message:
                knowledge_results = knowledge_service.search_knowledge(
                    last_user_message, 
                    user.university_id, 
                    department_id=user.department_id,
                    limit=3
                )
                if knowledge_results:
                    knowledge_pieces = []
                    for result in knowledge_results:
                        knowledge_pieces.append(f"- {result['title']}: {result['content'][:300]}")
                    knowledge_context = "\n".join(knowledge_pieces)
        
        # Generate new AI response
        ai_response, model_used = generate_chat_response(
            conversation_history,
            university_context=university_context,
            knowledge_context=knowledge_context
        )
        
        # Update the message
        message.content = ai_response
        message.model = model_used
        message.token_count = count_tokens(ai_response)
        message.created_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': message.to_dict(),
            'success': True
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to regenerate message: {str(e)}'}), 500