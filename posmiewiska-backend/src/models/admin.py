from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Zmienione na nullable=False
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_super_admin = db.Column(db.Boolean, default=False)  # Super admin może zarządzać innymi adminami
    
    def __repr__(self):
        return f'<Admin {self.username}>'
    
    def set_password(self, password):
        """Hashuje i zapisuje hasło"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Sprawdza czy podane hasło jest poprawne"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'is_super_admin': self.is_super_admin
        }
        
        if include_sensitive:
            # Tylko dla celów debugowania - nigdy nie wysyłać hasła do frontendu
            pass
            
        return data

