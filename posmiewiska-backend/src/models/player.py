from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(16), unique=True, nullable=False)  # Minecraft nickname (max 16 chars)
    reason = db.Column(db.Text, nullable=False)  # Powód zgłoszenia
    reported_by = db.Column(db.String(100), nullable=False)  # Kto zgłosił
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # Czy wpis jest aktywny
    
    def __repr__(self):
        return f'<Player {self.nickname}>'
    
    def get_avatar_url(self, size=64):
        """Zwraca URL do awatara gracza z Minotar"""
        from src.utils.minotar import minotar
        return minotar.get_avatar_url(self.nickname, size)
    
    def get_helm_url(self, size=64):
        """Zwraca URL do awatara z hełmem gracza z Minotar"""
        from src.utils.minotar import minotar
        return minotar.get_helm_url(self.nickname, size)
    
    def get_body_url(self, size=64):
        """Zwraca URL do pełnego ciała gracza z Minotar"""
        from src.utils.minotar import minotar
        return minotar.get_body_url(self.nickname, size)
    
    def to_dict(self, include_avatar_sizes=None):
        """
        Konwertuje obiekt do słownika
        
        Args:
            include_avatar_sizes (list): Lista rozmiarów awatarów do dołączenia
        """
        data = {
            'id': self.id,
            'nickname': self.nickname,
            'reason': self.reason,
            'reported_by': self.reported_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'avatar_url': self.get_avatar_url(64)  # Domyślny rozmiar 64px
        }
        
        # Dodanie różnych rozmiarów awatarów jeśli zostały określone
        if include_avatar_sizes:
            data['avatars'] = {}
            for size in include_avatar_sizes:
                data['avatars'][f'{size}px'] = {
                    'avatar': self.get_avatar_url(size),
                    'helm': self.get_helm_url(size),
                    'body': self.get_body_url(size)
                }
        
        return data

