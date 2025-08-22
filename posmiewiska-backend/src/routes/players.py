from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.player import Player
from src.models.admin import Admin
from datetime import datetime
import re
from functools import wraps

players_bp = Blueprint('players', __name__)

def validate_minecraft_nickname(nickname):
    """Walidacja nicku Minecraft - tylko litery, cyfry i podkreślniki, 3-16 znaków"""
    if not nickname or len(nickname) < 3 or len(nickname) > 16:
        return False
    return re.match(r'^[a-zA-Z0-9_]+$', nickname) is not None

def sanitize_input(text):
    """Podstawowa sanityzacja tekstu - usuwanie potencjalnie niebezpiecznych znaków"""
    if not text:
        return ""
    # Usuwanie tagów HTML i potencjalnie niebezpiecznych znaków
    text = re.sub(r'<[^>]*>', '', str(text))
    text = re.sub(r'[<>"\']', '', text)
    return text.strip()

# Import dekoratora z auth.py
def admin_required(f):
    """Dekorator wymagający uwierzytelnienia administratora - uproszczona wersja"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from src.routes.auth import verify_jwt_token
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Brak autoryzacji'}), 401
        
        token = auth_header.split(' ')[1]
        admin_id = verify_jwt_token(token)
        
        if not admin_id:
            return jsonify({'error': 'Nieprawidłowy lub wygasły token'}), 401
        
        admin = Admin.query.filter_by(id=admin_id, is_active=True).first()
        if not admin:
            return jsonify({'error': 'Konto administratora nieaktywne'}), 401
        
        request.current_admin = admin
        return f(*args, **kwargs)
    return decorated_function

@players_bp.route('/players', methods=['GET'])
def get_players():
    """Pobieranie listy wszystkich aktywnych graczy"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        
        # Ograniczenie per_page dla bezpieczeństwa
        per_page = min(per_page, 100)
        
        query = Player.query.filter_by(is_active=True)
        
        if search:
            search = sanitize_input(search)
            query = query.filter(Player.nickname.ilike(f'%{search}%'))
        
        players = query.order_by(Player.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'players': [player.to_dict() for player in players.items],
            'total': players.total,
            'pages': players.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': 'Błąd serwera'}), 500

@players_bp.route('/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    """Pobieranie szczegółów konkretnego gracza"""
    try:
        player = Player.query.filter_by(id=player_id, is_active=True).first()
        if not player:
            return jsonify({'error': 'Gracz nie znaleziony'}), 404
        
        return jsonify(player.to_dict())
    except Exception as e:
        return jsonify({'error': 'Błąd serwera'}), 500

@players_bp.route('/players', methods=['POST'])
@admin_required
def add_player():
    """Dodawanie nowego gracza do czarnej listy"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Brak danych'}), 400
        
        nickname = sanitize_input(data.get('nickname', ''))
        reason = sanitize_input(data.get('reason', ''))
        reported_by = sanitize_input(data.get('reported_by', ''))
        
        # Walidacja danych
        if not validate_minecraft_nickname(nickname):
            return jsonify({'error': 'Nieprawidłowy nick Minecraft'}), 400
        
        if not reason or len(reason) < 10:
            return jsonify({'error': 'Powód musi mieć co najmniej 10 znaków'}), 400
        
        if not reported_by or len(reported_by) < 3:
            return jsonify({'error': 'Pole "zgłaszający" jest wymagane'}), 400
        
        # Sprawdzenie czy gracz już istnieje
        existing_player = Player.query.filter_by(nickname=nickname, is_active=True).first()
        if existing_player:
            return jsonify({'error': 'Gracz już znajduje się na liście'}), 409
        
        # Tworzenie nowego gracza
        new_player = Player(
            nickname=nickname,
            reason=reason,
            reported_by=reported_by
        )
        
        db.session.add(new_player)
        db.session.commit()
        
        return jsonify({
            'message': 'Gracz został dodany do czarnej listy',
            'player': new_player.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Błąd serwera'}), 500

@players_bp.route('/players/<int:player_id>', methods=['PUT'])
@admin_required
def update_player(player_id):
    """Aktualizacja danych gracza"""
    try:
        player = Player.query.filter_by(id=player_id, is_active=True).first()
        if not player:
            return jsonify({'error': 'Gracz nie znaleziony'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Brak danych'}), 400
        
        # Aktualizacja pól jeśli zostały podane
        if 'nickname' in data:
            nickname = sanitize_input(data['nickname'])
            if not validate_minecraft_nickname(nickname):
                return jsonify({'error': 'Nieprawidłowy nick Minecraft'}), 400
            
            # Sprawdzenie czy nowy nick nie jest już zajęty
            existing = Player.query.filter_by(nickname=nickname, is_active=True).filter(Player.id != player_id).first()
            if existing:
                return jsonify({'error': 'Gracz z tym nickiem już istnieje'}), 409
            
            player.nickname = nickname
        
        if 'reason' in data:
            reason = sanitize_input(data['reason'])
            if not reason or len(reason) < 10:
                return jsonify({'error': 'Powód musi mieć co najmniej 10 znaków'}), 400
            player.reason = reason
        
        if 'reported_by' in data:
            reported_by = sanitize_input(data['reported_by'])
            if not reported_by or len(reported_by) < 3:
                return jsonify({'error': 'Pole "zgłaszający" jest wymagane'}), 400
            player.reported_by = reported_by
        
        player.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Dane gracza zostały zaktualizowane',
            'player': player.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Błąd serwera'}), 500

@players_bp.route('/players/<int:player_id>', methods=['DELETE'])
@admin_required
def delete_player(player_id):
    """Usuwanie gracza z listy (soft delete)"""
    try:
        player = Player.query.filter_by(id=player_id, is_active=True).first()
        if not player:
            return jsonify({'error': 'Gracz nie znaleziony'}), 404
        
        # Soft delete - oznaczenie jako nieaktywny
        player.is_active = False
        player.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Gracz został usunięty z listy'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Błąd serwera'}), 500

