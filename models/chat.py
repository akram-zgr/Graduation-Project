from extensions import db
from datetime import datetime

class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Chat metadata
    title = db.Column(db.String(255), default='New Conversation')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Chat status
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan', order_by='Message.created_at')
    
    def get_message_count(self):
        """Get total number of messages in chat"""
        return len(self.messages)
    
    def get_last_message(self):
        """Get the most recent message"""
        if self.messages:
            return self.messages[-1]
        return None
    
    def to_dict(self):
        """Convert chat object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'message_count': self.get_message_count(),
            'last_message': self.get_last_message().to_dict() if self.get_last_message() else None
        }
    
    def __repr__(self):
        return f'<Chat {self.id} - {self.title}>'
