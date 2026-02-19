from extensions import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_ar = db.Column(db.String(200))
    name_fr = db.Column(db.String(200))
    code = db.Column(db.String(50), nullable=False)
    
    # Foreign keys
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id', ondelete='CASCADE'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id', ondelete='CASCADE'), nullable=False)
    
    official_website = db.Column(db.String(255))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    building = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    head_of_department = db.Column(db.String(200))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = db.relationship('User', backref='department_info', lazy=True)
    
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

            'faculty_id': self.faculty_id,
            'faculty': {
                'id': self.faculty.id,
                'name': self.faculty.name
            } if self.faculty else None,

            'official_website': self.official_website,
            'email': self.email,
            'phone': self.phone,
            'building': self.building,
            'description': self.description,
            'head_of_department': self.head_of_department,
            'is_active': self.is_active,

            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    
    def __repr__(self):
        return f'<Department {self.name}>'
