from extensions import db
from datetime import datetime

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)  # Optional department-specific knowledge
    
    # Content
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_ar = db.Column(db.Text)  # Arabic content
    
    # Categorization
    category = db.Column(db.String(100))  # e.g., registration, tuition, academic, campus
    tags = db.Column(db.String(500))  # Comma-separated tags for search
    
    # Metadata
    source_type = db.Column(db.String(50))  # website, document, manual_entry, etc.
    source_url = db.Column(db.String(500))
    priority = db.Column(db.Integer, default=5)  # 1-10, higher = more important
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        """Convert knowledge base entry to dictionary"""
        return {
            'id': self.id,
            'university_id': self.university_id,
            'department_id': self.department_id,
            'title': self.title,
            'content': self.content,
            'content_ar': self.content_ar,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'source_type': self.source_type,
            'source_url': self.source_url,
            'priority': self.priority,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
    
    def __repr__(self):
        return f'<KnowledgeBase {self.title}>'
