from extensions import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    
    # Message content
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    token_count = db.Column(db.Integer)
    model = db.Column(db.String(50))
    
    def to_dict(self):
        """Convert message object to dictionary"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'content': self.content,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'token_count': self.token_count,
            'model': self.model
        }
    
    def __repr__(self):
        return f'<Message {self.id} - {self.role}>'
