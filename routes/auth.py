from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from models.user import User
from models.university import University
from models.faculty import Faculty
from models.department import Department
from extensions import db
from services.email_service import send_verification_email
from utils.validators import validate_email, validate_password
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth/signup.html')
    
    try:
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        department = data.get('department', '').strip()
        department_id = data.get('department_id')
        faculty_id = data.get('faculty_id')  # ✨ جديد
        student_id = data.get('student_id', '').strip()
        university_id = data.get('university_id')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if not university_id:
            return jsonify({'error': 'Please select a university'}), 400
        
        if not faculty_id:  # ✨ جديد
            return jsonify({'error': 'Please select a faculty'}), 400
        
        if not department_id:  # ✨ جديد
            return jsonify({'error': 'Please select a department'}), 400
        
        # Validate university exists
        university = University.query.get(university_id)
        if not university or not university.is_active:
            return jsonify({'error': 'Invalid university selected'}), 400
        
        # Validate faculty exists and belongs to university  # ✨ جديد
        faculty = Faculty.query.get(faculty_id)
        if not faculty or faculty.university_id != int(university_id) or not faculty.is_active:
            return jsonify({'error': 'Invalid faculty selected'}), 400
        
        # Validate department if provided
        if department_id:
            dept = Department.query.get(department_id)
            if not dept or dept.faculty_id != int(faculty_id) or dept.university_id != int(university_id) or not dept.is_active:  # ✨ تحديث
                return jsonify({'error': 'Invalid department selected'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            department=department,
            university_id=university_id,
            faculty_id=faculty_id,  # ✨ جديد
            department_id=department_id,
            student_id=student_id,
            role='student'  # Default role for new signups
        )
        user.set_password(password)
        user.generate_verification_token()
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email (optional - won't fail if email service is not configured)
        try:
            send_verification_email(user)
        except Exception as email_error:
            logger.warning(f"Failed to send verification email: {email_error}")
            # Continue anyway - user is created
        
        return jsonify({
            'message': 'Account created successfully. Please check your email to verify your account.',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in signup: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to create account: {str(e)}'}), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    data = request.get_json() if request.is_json else request.form
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_verified:
        return jsonify({'error': 'Please verify your email before logging in'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create session
    session['user_id'] = user.id
    session['username'] = user.username
    session['is_admin'] = user.role in ['super_admin', 'university_admin']
    session['role'] = user.role
    session['university_id'] = user.university_id
    session.permanent = True
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return render_template('auth/verification_failed.html', message='Invalid verification token')
    
    if user.is_verified:
        return render_template('auth/verification_success.html', message='Email already verified')
    
    user.verify_email()
    db.session.commit()
    
    return render_template('auth/verification_success.html', message='Email verified successfully! You can now log in.')

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.is_verified:
        return jsonify({'message': 'Email already verified'}), 200
    
    # Generate new token and send email
    user.generate_verification_token()
    db.session.commit()
    
    send_verification_email(user)
    
    return jsonify({'message': 'Verification email sent'}), 200

@auth_bp.route('/me')
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name'].strip()
    if 'department' in data:
        user.department = data['department'].strip()
    if 'student_id' in data:
        user.student_id = data['student_id'].strip()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in update_profile: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@auth_bp.route('/universities', methods=['GET'])
def get_universities():
    """Get list of all active universities"""
    universities = University.query.filter_by(is_active=True).order_by(University.name).all()
    return jsonify({
        'universities': [uni.to_dict() for uni in universities]
    }), 200

@auth_bp.route('/universities/<int:university_id>/faculties', methods=['GET'])
def get_faculties(university_id):  # ✨ جديد
    """Get list of all active faculties for a specific university"""
    university = University.query.get(university_id)
    if not university:
        return jsonify({'error': 'University not found'}), 404
    
    faculties = Faculty.query.filter_by(
        university_id=university_id,
        is_active=True
    ).order_by(Faculty.name).all()
    
    return jsonify({
        'faculties': [fac.to_dict() for fac in faculties],
        'university': university.to_dict()
    }), 200

@auth_bp.route('/faculties/<int:faculty_id>/departments', methods=['GET'])  # ✨ جديد
def get_faculty_departments(faculty_id):
    """Get list of all active departments for a specific faculty"""
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify({'error': 'Faculty not found'}), 404
    
    departments = Department.query.filter_by(
        faculty_id=faculty_id,
        is_active=True
    ).order_by(Department.name).all()
    
    return jsonify({
        'departments': [dept.to_dict() for dept in departments],
        'faculty': faculty.to_dict()
    }), 200

@auth_bp.route('/universities/<int:university_id>/departments', methods=['GET'])
def get_departments(university_id):
    """Get list of all active departments for a specific university"""
    university = University.query.get(university_id)
    if not university:
        return jsonify({'error': 'University not found'}), 404
    
    departments = Department.query.filter_by(
        university_id=university_id,
        is_active=True
    ).order_by(Department.name).all()
    
    return jsonify({
        'departments': [dept.to_dict() for dept in departments],
        'university': university.to_dict()
    }), 200
