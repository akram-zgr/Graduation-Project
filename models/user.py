from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Email verification
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    
    # User info
    full_name = db.Column(db.String(120))
    department = db.Column(db.String(100))  # Legacy field, kept for compatibility
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'), nullable=True)  # New structured field
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)  # New structured field
    student_id = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Role - Extended for multi-university management
    is_admin = db.Column(db.Boolean, default=False)  # Legacy field
    role = db.Column(db.String(50), default='student')  # New: 'super_admin', 'university_admin', 'student'
    
    # Relationships
    chats = db.relationship('Chat', backref='user', lazy=True, cascade='all, delete-orphan')

    @property
    def is_super_admin(self):
        """Check if user is a super admin"""
        return self.role == 'super_admin' or (self.is_admin and self.university_id is None)
    
    @property
    def is_university_admin(self):
        """Check if user is a university admin"""
        return self.role == 'university_admin' or (self.is_admin and self.university_id is not None)
    
    def has_role(self, required_role):
        """Check if user has the specified role or higher"""
        role_hierarchy = {'super_admin': 3, 'university_admin': 2, 'student': 1}
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        """Generate a unique verification token"""
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token
    
    def verify_email(self):
        """Mark email as verified"""
        self.is_verified = True
        self.verification_token = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'student_id': self.student_id,

            # University (object)
            'university_id': self.university_id,
            'university': {
                'id': self.university.id,
                'name': self.university.name
            } if self.university else None,

            # Faculty (object)
            'faculty_id': self.faculty_id,
            'faculty': {
                'id': self.faculty_info.id,
                'name': self.faculty_info.name
            } if self.faculty_info else None,

            # Department (object)
            'department_id': self.department_id,
            'department_info': {
                'id': self.department_info.id,
                'name': self.department_info.name
            } if self.department_info else None,

            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'role': self.role,
            'is_super_admin': self.is_super_admin,
            'is_university_admin': self.is_university_admin,

            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    
    def __repr__(self):
        return f'<User {self.username}>'
