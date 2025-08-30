from flask import Blueprint, request, jsonify, session
from src.models.user import db
from src.models.admin import Admin
from datetime import datetime, timedelta
import jwt
import re
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Klucz do podpisywania JWT - w produkcji powinien być w zmiennych środowiskowych
JWT_SECRET = 'your-secret-key-change-in-production'
JWT_EXPIRATION_HOURS = 24

def validate_email(email):
    """Walidacja adresu email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Walidacja hasła - minimum 8 znaków, jedna wielka litera, jedna cyfra"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

def generate_jwt_token(admin_id):
    """Generowanie JWT tokenu"""
    payload = {
        'admin_id': admin_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token):
    """Weryfikacja JWT tokenu"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['admin_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Dekorator wymagający ważnego JWT tokenu"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Brak tokenu autoryzacji'}), 401
        
        token = auth_header.split(' ')[1]
        admin_id = verify_jwt_token(token)
        
        if not admin_id:
            return jsonify({'error': 'Nieprawidłowy lub wygasły token'}), 401
        
        # Sprawdzenie czy admin nadal istnieje i jest aktywny
        admin = Admin.query.filter_by(id=admin_id, is_active=True).first()
        if not admin:
            return jsonify({'error': 'Konto administratora nieaktywne'}), 401
        
        # Dodanie informacji o adminie do kontekstu żądania
        request.current_admin = admin
        return f(*args, **kwargs)
    
    return decorated_function

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Logowanie administratora"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Brak danych'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Nazwa użytkownika i hasło są wymagane'}), 400
        
        # Znajdowanie administratora
        admin = Admin.query.filter_by(username=username, is_active=True).first()
        
        if not admin or not admin.check_password(password):
            return jsonify({'error': 'Nieprawidłowa nazwa użytkownika lub hasło'}), 401
        
        # Aktualizacja czasu ostatniego logowania
        admin.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generowanie JWT tokenu
        token = generate_jwt_token(admin.id)
        
        return jsonify({
            'message': 'Logowanie pomyślne',
            'token': token,
            'admin': admin.to_dict(),
            'expires_in': JWT_EXPIRATION_HOURS * 3600  # w sekundach
        })
        
    except Exception as e:
        return jsonify({'error': 'Błąd serwera'}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    """Wylogowanie administratora"""
    # W przypadku JWT nie ma potrzeby robić nic po stronie serwera
    # Token po prostu przestanie być używany przez klienta
    return jsonify({'message': 'Wylogowanie pomyślne'})

@auth_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_admin():
    """Pobieranie informacji o aktualnie zalogowanym administratorze"""
    return jsonify({
        'admin': request.current_admin.to_dict()
    })

@auth_bp.route('/auth/change-password', methods=['POST'])
@token_required
def change_password():
    """Zmiana hasła administratora"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Brak danych'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Aktualne i nowe hasło są wymagane'}), 400
        
        admin = request.current_admin
        
        # Sprawdzenie aktualnego hasła
        if not admin.check_password(current_password):
            return jsonify({'error': 'Nieprawidłowe aktualne hasło'}), 400
        
        # Walidacja nowego hasła
        if not validate_password(new_password):
            return jsonify({
                'error': 'Nowe hasło musi mieć co najmniej 8 znaków, jedną wielką literę i jedną cyfrę'
            }), 400
        
        # Ustawienie nowego hasła
        admin.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Hasło zostało zmienione'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Błąd serwera'}), 500

@auth_bp.route('/auth/register', methods=['POST'])
def register_admin():
    """Rejestracja nowego administratora - tylko dla super adminów lub gdy nie ma żadnych adminów"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Brak danych'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'error': 'Wszystkie pola są wymagane'}), 400
        
        # Walidacja danych
        if len(username) < 3 or len(username) > 50:
            return jsonify({'error': 'Nazwa użytkownika musi mieć 3-50 znaków'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Nieprawidłowy adres email'}), 400
        
        if not validate_password(password):
            return jsonify({
                'error': 'Hasło musi mieć co najmniej 8 znaków, jedną wielką literę i jedną cyfrę'
            }), 400
        
        # Sprawdzenie czy istnieją już administratorzy
        existing_admins_count = Admin.query.filter_by(is_active=True).count()
        
        # Jeśli istnieją administratorzy, wymagana jest autoryzacja super admina
        if existing_admins_count > 0:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Brak autoryzacji'}), 401
            
            token = auth_header.split(' ')[1]
            admin_id = verify_jwt_token(token)
            
            if not admin_id:
                return jsonify({'error': 'Nieprawidłowy token'}), 401
            
            current_admin = Admin.query.filter_by(id=admin_id, is_active=True).first()
            if not current_admin or not current_admin.is_super_admin:
                return jsonify({'error': 'Brak uprawnień do tworzenia nowych administratorów'}), 403
        
        # Sprawdzenie czy użytkownik już istnieje
        if Admin.query.filter_by(username=username).first():
            return jsonify({'error': 'Nazwa użytkownika już istnieje'}), 409
        
        # Sprawdzenie emaila tylko jeśli nie jest pusty
        if email and Admin.query.filter_by(email=email).first():
            return jsonify({'error': 'Adres email już istnieje'}), 409
        
        # Tworzenie nowego administratora
        new_admin = Admin(
            username=username,
            email=email,
            is_super_admin=(existing_admins_count == 0)  # Pierwszy admin jest super adminem
        )
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        return jsonify({
            'message': 'Administrator został utworzony',
            'admin': new_admin.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Błąd serwera'}), 500

