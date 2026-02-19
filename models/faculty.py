from extensions import db
from datetime import datetime

class Faculty(db.Model):
    __tablename__ = 'faculties'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_ar = db.Column(db.String(200))  # Arabic name
    name_fr = db.Column(db.String(200))  # French name
    code = db.Column(db.String(50), nullable=False)
    
    # Foreign key to university
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id', ondelete='CASCADE'), nullable=False)
    
    # Faculty details
    description = db.Column(db.Text)
    official_website = db.Column(db.String(255))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    building = db.Column(db.String(100))
    dean = db.Column(db.String(200))  # Dean of faculty
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    departments = db.relationship('Department', backref='faculty', lazy=True, cascade='all, delete-orphan')
    users = db.relationship('User', backref='faculty_info', lazy=True)
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_ar': self.name_ar,
            'name_fr': self.name_fr,
            'code': self.code,
            'university_id': self.university_id,
            'university': {
                'id': self.university.id,
                'name': self.university.name
            } if self.university else None,
            'description': self.description,
            'official_website': self.official_website,
            'email': self.email,
            'phone': self.phone,
            'building': self.building,
            'dean': self.dean,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Faculty {self.name}>'
