from functools import wraps
from flask import session, jsonify, redirect, url_for, request

def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Require university_admin or super_admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from models.user import User
        
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.query.get(session['user_id'])

        if not user:
            return jsonify({'error': 'User not found'}), 401

        if user.role not in ['super_admin', 'university_admin']:
            return jsonify({'error': 'Admin privileges required'}), 403

        return f(*args, **kwargs)

    return decorated_function

def require_role(required_role):
    """Decorator to require specific role or higher"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from models.user import User
            
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login'))
            
            user = User.query.get(session['user_id'])
            
            if not user:
                if request.is_json:
                    return jsonify({'error': 'User not found'}), 401
                return redirect(url_for('auth.login'))
            
            # Check role
            role_hierarchy = {'super_admin': 3, 'university_admin': 2, 'student': 1}
            user_level = role_hierarchy.get(user.role, 0)
            required_level = role_hierarchy.get(required_role, 0)
            
            if user_level < required_level:
                if request.is_json:
                    return jsonify({'error': f'{required_role} privileges required'}), 403
                return jsonify({'error': 'Access denied'}), 403
            
            # Store user in kwargs for easy access
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def super_admin_required(f):
    """Decorator to require super admin privileges"""
    return require_role('super_admin')(f)

def university_admin_required(f):
    """Decorator to require university admin privileges or higher"""
    return require_role('university_admin')(f)
