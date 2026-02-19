from flask import Blueprint, request, jsonify, render_template, session , redirect
from models.user import User
from models.chat import Chat
from models.message import Message
from models.university import University
from models.department import Department
from models.knowledge_base import KnowledgeBase
from services.knowledge_service import knowledge_service
from extensions import db
from utils.decorators import admin_required, require_role, super_admin_required, university_admin_required
from sqlalchemy import func, desc
from models.faculty import Faculty


admin_bp = Blueprint('admin', __name__)

# ==================== HELPER FUNCTIONS ====================

def get_current_user():
    """Get the current logged-in user"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def check_university_access(resource_university_id, current_user):
    """
    Check if current user can access a resource from a specific university.
    Super admins can access all universities.
    University admins can only access their own university.
    """
    if current_user.is_super_admin:
        return True
    
    if current_user.is_university_admin:
        return current_user.university_id == resource_university_id
    
    return False

def filter_by_university(query, model, current_user):
    """
    Filter query by university based on user role.
    Super admins see all data.
    University admins see only their university data.
    """
    if current_user.is_super_admin:
        return query
    
    if current_user.is_university_admin and current_user.university_id:
        return query.filter(model.university_id == current_user.university_id)
    
    return query

# ==================== DASHBOARD ====================

@admin_bp.route('/')
@admin_required
def admin_dashboard():
    """Render appropriate dashboard based on role"""
    current_user = get_current_user()
    if not current_user:
        return redirect('/auth/login')
    
    # Super Admin → Super Admin Dashboard
    if current_user.is_super_admin:
        return render_template('admin/super_admin_dashboard.html')
    
    # Admin (University Admin) → Admin Dashboard
    elif current_user.is_university_admin:
        return render_template('admin/admin_dashboard.html')
    
    # Not authorized
    else:
        return redirect('/auth/login')

@admin_bp.route('/system-stats', methods=['GET'])
@admin_required
def get_system_stats():
    try:
        current_user = get_current_user()
        if not current_user or not current_user.is_super_admin:
            return jsonify({'error': 'Unauthorized'}), 403

        universities_count = University.query.count()
        active_universities_count = University.query.filter_by(is_active=True).count()

        faculties_count = Faculty.query.count()
        active_faculties_count = Faculty.query.filter_by(is_active=True).count()

        departments_count = Department.query.count()
        active_departments_count = Department.query.filter_by(is_active=True).count()

        users_count = User.query.count()
        verified_users_count = User.query.filter_by(is_verified=True).count()

        admins_count = User.query.filter(
            User.role.in_(['admin', 'super_admin'])
        ).count()

        return jsonify({
            "universities_count": universities_count,
            "active_universities_count": active_universities_count,
            "faculties_count": faculties_count,
            "active_faculties_count": active_faculties_count,
            "departments_count": departments_count,
            "active_departments_count": active_departments_count,
            "users_count": users_count,
            "verified_users_count": verified_users_count,
            "admins_count": admins_count
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    """Get system-wide statistics with university scoping"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
        
        # Base queries
        users_query = User.query
        chats_query = Chat.query.filter_by(is_active=True)
        messages_query = Message.query
        
        # Apply university filtering for university admins
        if current_user.is_university_admin and current_user.university_id:
            users_query = users_query.filter_by(university_id=current_user.university_id)
            chats_query = chats_query.join(User).filter(User.university_id == current_user.university_id)
            messages_query = messages_query.join(Chat).join(User).filter(User.university_id == current_user.university_id)
        
        # User stats
        total_users = users_query.count()
        verified_users = users_query.filter_by(is_verified=True).count()
        unverified_users = total_users - verified_users
        
        # Chat stats
        total_chats = chats_query.count()
        total_messages = messages_query.count()
        
        # Token usage
        total_tokens = messages_query.with_entities(func.sum(Message.token_count)).scalar() or 0
        
        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        new_users_week = users_query.filter(User.created_at >= week_ago).count()
        new_chats_week = chats_query.filter(Chat.created_at >= week_ago).count()
        
        # Most active users (scoped to university)
        active_users_query = db.session.query(
            User.username,
            User.email,
            func.count(Chat.id).label('chat_count')
        ).join(Chat).group_by(User.id)

        if current_user.is_university_admin and current_user.university_id:
            active_users_query = active_users_query.filter(User.university_id == current_user.university_id)

        active_users_query = active_users_query.order_by(desc('chat_count')).limit(5)
        
        return jsonify({
            'users': {
                'total': total_users,
                'verified': verified_users,
                'unverified': unverified_users,
                'new_this_week': new_users_week
            },
            'chats': {
                'total': total_chats,
                'new_this_week': new_chats_week
            },
            'messages': {
                'total': total_messages
            },
            'tokens': {
                'total': total_tokens
            },
            'top_users': [
                {
                    'username': user.username,
                    'email': user.email,
                    'chat_count': user.chat_count
                }
                for user in active_users_query
            ],
            'scope': 'university' if current_user.is_university_admin else 'global'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def dashboard_stats():
    try:
        # Universities
        total_universities = University.query.count()
        active_universities = University.query.filter_by(is_active=True).count()

        # Faculties
        total_faculties = Faculty.query.count()
        active_faculties = Faculty.query.filter_by(is_active=True).count()

        # Departments
        total_departments = Department.query.count()
        active_departments = Department.query.filter_by(is_active=True).count()

        # Users
        total_users = User.query.count()
        verified_users = User.query.filter_by(is_verified=True).count()

        # Admins
        total_admins = User.query.filter(
            User.role.in_(['super_admin', 'university_admin'])
        ).count()

        return jsonify({
            'universities_count': total_universities,
            'active_universities_count': active_universities,

            'faculties_count': total_faculties,
            'active_faculties_count': active_faculties,

            'departments_count': total_departments,
            'active_departments_count': active_departments,

            'users_count': total_users,
            'verified_users_count': verified_users,

            'admins_count': total_admins
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """Get all users with pagination and university scoping"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 401
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    users_query = User.query
    
    # Apply university filtering for university admins
    if current_user.is_university_admin and current_user.university_id:
        users_query = users_query.filter_by(university_id=current_user.university_id)
    
    # Apply additional filters
    if request.args.get('verified') == 'true':
        users_query = users_query.filter_by(is_verified=True)
    elif request.args.get('verified') == 'false':
        users_query = users_query.filter_by(is_verified=False)
    
    pagination = users_query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get detailed user information with access control"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 401
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check access: university admins can only view users from their university
    if current_user.is_university_admin:
        if user.university_id != current_user.university_id:
            return jsonify({'error': 'Access denied'}), 403
    
    # Get user's chats and messages count
    chat_count = Chat.query.filter_by(user_id=user_id, is_active=True).count()
    message_count = db.session.query(Message).join(Chat).filter(Chat.user_id == user_id).count()
    total_tokens = db.session.query(func.sum(Message.token_count)).join(Chat).filter(Chat.user_id == user_id).scalar() or 0
    
    user_data = user.to_dict()
    user_data['stats'] = {
        'chat_count': chat_count,
        'message_count': message_count,
        'total_tokens': total_tokens
    }
    
    return jsonify({'user': user_data}), 200

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@super_admin_required
def toggle_admin(user_id, current_user):
    """Toggle admin status for a user (super admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent modifying self
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot modify your own admin status'}), 400
    
    try:
        # Toggle between student and university_admin
        if user.role == 'student':
            user.role = 'university_admin'
            user.is_admin = True
        else:
            user.role = 'student'
            user.is_admin = False
        
        db.session.commit()
        
        return jsonify({
            'message': f'User role updated to {user.role}',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update user: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user and all associated data"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 401
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check access: university admins can only delete users from their university
    if current_user.is_university_admin:
        if user.university_id != current_user.university_id:
            return jsonify({'error': 'Access denied'}), 403
    
    # Prevent deleting self
    if user.id == session.get('user_id'):
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user'}), 500

@admin_bp.route('/chats', methods=['GET'])
@admin_required
def list_all_chats():
    """Get all chats across all users"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    chats_query = db.session.query(Chat, User).join(User).filter(Chat.is_active == True).order_by(Chat.updated_at.desc())
    
    pagination = chats_query.paginate(page=page, per_page=per_page, error_out=False)
    
    chats_data = []
    for chat, user in pagination.items:
        chat_dict = chat.to_dict()
        chat_dict['username'] = user.username
        chat_dict['user_email'] = user.email
        chats_data.append(chat_dict)
    
    return jsonify({
        'chats': chats_data,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@admin_bp.route('/chats/<int:chat_id>/messages', methods=['GET'])
@admin_required
def get_chat_messages(chat_id):
    """Get all messages for a specific chat"""
    chat = Chat.query.get(chat_id)
    
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    messages = [msg.to_dict() for msg in chat.messages]
    
    return jsonify({
        'chat': chat.to_dict(),
        'messages': messages
    }), 200

# ==================== UNIVERSITY MANAGEMENT ====================

@admin_bp.route('/universities', methods=['GET'])
@admin_required
def list_universities():
    """Get all universities"""
    universities = University.query.order_by(University.name).all()
    return jsonify({
        'universities': [uni.to_dict() for uni in universities]
    }), 200

@admin_bp.route('/universities', methods=['POST'])
@super_admin_required
def create_university(current_user):
    """Create a new university (super admin only)"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    code = data.get('code', '').strip().upper()
    
    if not name or not code:
        return jsonify({'error': 'Name and code are required'}), 400
    
    # Check if code already exists
    if University.query.filter_by(code=code).first():
        return jsonify({'error': 'University code already exists'}), 409
    
    try:
        university = University(
            name=name,
            name_ar=data.get('name_ar', '').strip(),
            code=code,
            city=data.get('city', '').strip(),
            province=data.get('province', '').strip(),
            website=data.get('website', '').strip(),
            email=data.get('email', '').strip(),
            phone=data.get('phone', '').strip(),
            address=data.get('address', '').strip(),
            description=data.get('description', '').strip(),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(university)
        db.session.commit()
        
        return jsonify({
            'message': 'University created successfully',
            'university': university.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create university: {str(e)}'}), 500

@admin_bp.route('/universities/<int:university_id>', methods=['GET'])
@admin_required
def get_university(university_id):
    university = University.query.get(university_id)

    if not university:
        return jsonify({'error': 'University not found'}), 404

    return jsonify({
        'university': university.to_dict()
    }), 200


@admin_bp.route('/universities/<int:university_id>', methods=['PUT'])
@admin_required
def update_university(university_id):
    """Update university information with access control"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 401
    
    university = University.query.get(university_id)
    
    if not university:
        return jsonify({'error': 'University not found'}), 404
    
    # Only super admins or the university's own admin can update
    if not current_user.is_super_admin:
        if not (current_user.is_university_admin and current_user.university_id == university_id):
            return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            university.name = data['name'].strip()
        if 'name_ar' in data:
            university.name_ar = data['name_ar'].strip()
        if 'city' in data:
            university.city = data['city'].strip()
        if 'province' in data:
            university.province = data['province'].strip()
        if 'website' in data:
            university.website = data['website'].strip()
        if 'email' in data:
            university.email = data['email'].strip()
        if 'phone' in data:
            university.phone = data['phone'].strip()
        if 'address' in data:
            university.address = data['address'].strip()
        if 'description' in data:
            university.description = data['description'].strip()
        
        # Only super admin can change is_active status
        if 'is_active' in data and current_user.is_super_admin:
            university.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'University updated successfully',
            'university': university.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update university: {str(e)}'}), 500

@admin_bp.route('/universities/<int:university_id>', methods=['DELETE'])
@super_admin_required
def delete_university(university_id, current_user):
    """Soft delete a university (super admin only)"""
    university = University.query.get(university_id)
    
    if not university:
        return jsonify({'error': 'University not found'}), 404
    
    try:
        university.is_active = False
        db.session.commit()
        return jsonify({'message': 'University deactivated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete university'}), 500

# ==================== KNOWLEDGE BASE MANAGEMENT ====================

@admin_bp.route('/knowledge', methods=['GET'])
@admin_required
def list_knowledge():
    """Get all knowledge entries with optional filtering and university scoping"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 401
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    university_id = request.args.get('university_id', type=int)
    category = request.args.get('category')
    
    query = KnowledgeBase.query
    
    # Apply university filtering for university admins
    if current_user.is_university_admin and current_user.university_id:
        query = query.filter_by(university_id=current_user.university_id)
    elif university_id:
        # Super admin can filter by specific university
        query = query.filter_by(university_id=university_id)
    
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.order_by(KnowledgeBase.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'knowledge': [entry.to_dict() for entry in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@admin_bp.route('/knowledge', methods=['POST'])
@admin_required
def create_knowledge():
    """Create new knowledge entry with university validation"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 401
    
    data = request.get_json()
    
    university_id = data.get('university_id')
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    if not university_id or not title or not content:
        return jsonify({'error': 'University, title, and content are required'}), 400
    
    # Verify university exists
    university = University.query.get(university_id)
    if not university:
        return jsonify({'error': 'University not found'}), 404
    
    # University admins can only create knowledge for their own university
    if current_user.is_university_admin:
        if current_user.university_id != university_id:
            return jsonify({'error': 'Can only create knowledge for your own university'}), 403
    
    try:
        # Optional department validation
        department_id = data.get('department_id')
        if department_id:
            department = Department.query.get(department_id)
            if not department or department.university_id != university_id:
                return jsonify({'error': 'Invalid department for this university'}), 400
        
        entry = knowledge_service.add_knowledge(
            university_id=university_id,
            department_id=department_id,
            title=title,
            content=content,
            content_ar=data.get('content_ar', '').strip(),
            category=data.get('category', '').strip(),
            tags=data.get('tags', '').strip(),
            source_url=data.get('source_url', '').strip(),
            priority=data.get('priority', 5),
            created_by=session.get('user_id')
        )
        
        return jsonify({
            'message': 'Knowledge entry created successfully',
            'knowledge': entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create knowledge entry: {str(e)}'}), 500

@admin_bp.route('/knowledge/<int:knowledge_id>', methods=['PUT'])
@admin_required
def update_knowledge(knowledge_id):
    """Update knowledge entry"""
    data = request.get_json()
    
    try:
        entry = knowledge_service.update_knowledge(knowledge_id, **data)
        
        if not entry:
            return jsonify({'error': 'Knowledge entry not found'}), 404
        
        return jsonify({
            'message': 'Knowledge entry updated successfully',
            'knowledge': entry.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update knowledge entry: {str(e)}'}), 500

@admin_bp.route('/knowledge/<int:knowledge_id>', methods=['DELETE'])
@admin_required
def delete_knowledge(knowledge_id):
    """Delete knowledge entry"""
    try:
        success = knowledge_service.delete_knowledge(knowledge_id)
        
        if not success:
            return jsonify({'error': 'Knowledge entry not found'}), 404
        
        return jsonify({'message': 'Knowledge entry deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete knowledge entry: {str(e)}'}), 500

@admin_bp.route('/knowledge/categories', methods=['GET'])
@admin_required
def get_knowledge_categories():
    """Get all knowledge categories for a university"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 401
    
    university_id = request.args.get('university_id', type=int)
    
    # University admins can only get categories for their university
    if current_user.is_university_admin:
        university_id = current_user.university_id
    
    if not university_id:
        return jsonify({'error': 'University ID is required'}), 400
    
    categories = knowledge_service.get_all_categories(university_id)
    
    return jsonify({
        'categories': categories,
        'university_id': university_id
    }), 200

# ==================== DEPARTMENT MANAGEMENT ====================

@admin_bp.route('/departments', methods=['GET'])
@university_admin_required
def list_departments(current_user):
    """Get all departments with university scoping"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    query = Department.query
    
    # Apply university filtering
    if current_user.is_university_admin and current_user.university_id:
        query = query.filter_by(university_id=current_user.university_id)
    elif request.args.get('university_id'):
        query = query.filter_by(university_id=request.args.get('university_id', type=int))
    
    pagination = query.order_by(Department.name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'departments': [dept.to_dict() for dept in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@admin_bp.route('/departments/<int:department_id>', methods=['GET'])
@admin_required
def get_department(department_id):
    """Get single department details"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 401
    
    department = Department.query.get(department_id)
    
    if not department:
        return jsonify({'error': 'Department not found'}), 404
    
    # Check access for university admins
    if current_user.is_university_admin:
        if department.university_id != current_user.university_id:
            return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({'department': department.to_dict()}), 200

@admin_bp.route('/departments', methods=['POST'])
@university_admin_required
def create_department(current_user):
    """Create a new department"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    code = data.get('code', '').strip().upper()
    university_id = data.get('university_id')
    
    if not name or not code:
        return jsonify({'error': 'Name and code are required'}), 400
    
    # University admins can only create departments for their own university
    if current_user.is_university_admin:
        university_id = current_user.university_id
    
    if not university_id:
        return jsonify({'error': 'University ID is required'}), 400
    
    # Verify university exists
    university = University.query.get(university_id)
    if not university:
        return jsonify({'error': 'University not found'}), 404
    
    # Check if code already exists for this university
    existing = Department.query.filter_by(
        university_id=university_id,
        code=code
    ).first()
    
    if existing:
        return jsonify({'error': 'Department code already exists for this university'}), 409
    
    try:
        department = Department(
            name=name,
            name_ar=data.get('name_ar', '').strip(),
            code=code,
            university_id=university_id,
            description=data.get('description', '').strip(),
            building=data.get('building', '').strip(),
            email=data.get('email', '').strip(),
            phone=data.get('phone', '').strip(),
            official_website=data.get('official_website', '').strip(),
            head_of_department=data.get('head_of_department', '').strip()
        )
        
        db.session.add(department)
        db.session.commit()
        
        return jsonify({
            'message': 'Department created successfully',
            'department': department.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create department: {str(e)}'}), 500

@admin_bp.route('/departments/<int:department_id>', methods=['PUT'])
@university_admin_required
def update_department(department_id, current_user):
    """Update department information"""
    department = Department.query.get(department_id)
    
    if not department:
        return jsonify({'error': 'Department not found'}), 404
    
    # Check access
    if current_user.is_university_admin:
        if department.university_id != current_user.university_id:
            return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            department.name = data['name'].strip()
        if 'name_ar' in data:
            department.name_ar = data['name_ar'].strip()
        if 'description' in data:
            department.description = data['description'].strip()
        if 'building' in data:
            department.building = data['building'].strip()
        if 'email' in data:
            department.email = data['email'].strip()
        if 'phone' in data:
            department.phone = data['phone'].strip()
        if 'official_website' in data:
            department.official_website = data['official_website'].strip()
        if 'head_of_department' in data:
            department.head_of_department = data['head_of_department'].strip()
        if 'is_active' in data:
            department.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Department updated successfully',
            'department': department.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update department: {str(e)}'}), 500

@admin_bp.route('/departments/<int:department_id>', methods=['DELETE'])
@university_admin_required
def delete_department(department_id, current_user):
    """Soft delete a department"""
    department = Department.query.get(department_id)
    
    if not department:
        return jsonify({'error': 'Department not found'}), 404
    
    # Check access
    if current_user.is_university_admin:
        if department.university_id != current_user.university_id:
            return jsonify({'error': 'Access denied'}), 403
    
    try:
        department.is_active = False
        db.session.commit()
        return jsonify({'message': 'Department deactivated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete department'}), 500

# ==================== USER ROLE MANAGEMENT ====================

@admin_bp.route('/users/create-admin', methods=['POST'])
@super_admin_required
def create_university_admin(current_user):
    """Create a university admin account (super admin only)"""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    university_id = data.get('university_id')
    
    if not username or not email or not password or not university_id:
        return jsonify({'error': 'All fields are required'}), 400
    
    # Verify university exists
    university = University.query.get(university_id)
    if not university:
        return jsonify({'error': 'University not found'}), 404
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409
    
    try:
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            university_id=university_id,
            role='university_admin',
            is_admin=True,
            is_verified=True  # Auto-verify admin accounts
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'University admin created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create admin: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@super_admin_required
def update_user_role(user_id, current_user):
    """Update user role (super admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent modifying self
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot modify your own role'}), 400
    
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in ['student', 'university_admin', 'super_admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    try:
        user.role = new_role
        
        # Update is_admin flag for backward compatibility
        if new_role in ['university_admin', 'super_admin']:
            user.is_admin = True
        else:
            user.is_admin = False
        
        db.session.commit()
        
        return jsonify({
            'message': f'User role updated to {new_role}',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update role: {str(e)}'}), 500

@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """Get analytics data with university scoping"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 401
    
    # This is a placeholder for detailed analytics
    # Implementation would depend on specific analytics requirements
    return jsonify({
        'message': 'Analytics endpoint',
        'scope': 'university' if current_user.is_university_admin else 'global',
        'university_id': current_user.university_id if current_user.is_university_admin else None
    }), 200

@admin_bp.route('/faculties', methods=['GET'])
@admin_required
def list_faculties():
    university_id = request.args.get('university_id', type=int)

    query = Faculty.query

    if university_id:
        query = query.filter_by(university_id=university_id)

    faculties = query.all()

    return jsonify({
        'faculties': [faculty.to_dict() for faculty in faculties]
    }), 200

@admin_bp.route('/admins', methods=['GET'])
@super_admin_required
def list_admins(current_user):
    admins = User.query.filter(
        User.role.in_(['super_admin', 'university_admin'])
    ).all()

    return jsonify({
        'admins': [admin.to_dict() for admin in admins]
    }), 200


