#!/usr/bin/env python3
import sys
import os

# Dodaj ścieżkę do aplikacji
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.user import db
from src.models.admin import Admin
from src.main import app
from werkzeug.security import generate_password_hash

def create_admin(username, password):
    """Tworzy nowego administratora"""
    with app.app_context():
        # Sprawdź czy admin już istnieje
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            print(f"❌ Administrator '{username}' już istnieje!")
            return False
        
        # Utwórz nowego administratora
        admin = Admin(
            username=username,
            password=generate_password_hash(password)
        )
        
        try:
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Administrator '{username}' został utworzony pomyślnie!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Błąd podczas tworzenia administratora: {e}")
            return False

def list_admins():
    """Wyświetla listę administratorów"""
    with app.app_context():
        admins = Admin.query.all()
        if not admins:
            print("Brak administratorów w systemie.")
        else:
            print("Lista administratorów:")
            for admin in admins:
                print(f"- {admin.username} (ID: {admin.id})")

def delete_admin(username):
    """Usuwa administratora"""
    with app.app_context():
        admin = Admin.query.filter_by(username=username).first()
        if not admin:
            print(f"❌ Administrator '{username}' nie istnieje!")
            return False
        
        try:
            db.session.delete(admin)
            db.session.commit()
            print(f"✅ Administrator '{username}' został usunięty!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Błąd podczas usuwania administratora: {e}")
            return False

def change_password(username, new_password):
    """Zmienia hasło administratora"""
    with app.app_context():
        admin = Admin.query.filter_by(username=username).first()
        if not admin:
            print(f"❌ Administrator '{username}' nie istnieje!")
            return False
        
        try:
            admin.password = generate_password_hash(new_password)
            db.session.commit()
            print(f"✅ Hasło administratora '{username}' zostało zmienione!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Błąd podczas zmiany hasła: {e}")
            return False

def print_usage():
    """Wyświetla instrukcję użycia"""
    print("Użycie:")
    print("  python create_admin.py create <username> <password>  - Tworzy nowego administratora")
    print("  python create_admin.py list                         - Wyświetla listę administratorów")
    print("  python create_admin.py delete <username>            - Usuwa administratora")
    print("  python create_admin.py password <username> <password> - Zmienia hasło administratora")
    print("")
    print("Przykłady:")
    print("  python create_admin.py create admin mojeSilneHaslo123")
    print("  python create_admin.py list")
    print("  python create_admin.py delete admin")
    print("  python create_admin.py password admin noweHaslo456")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "create":
        if len(sys.argv) != 4:
            print("❌ Błędna liczba argumentów dla komendy 'create'")
            print("Użycie: python create_admin.py create <username> <password>")
            sys.exit(1)
        
        username = sys.argv[2]
        password = sys.argv[3]
        
        if len(username) < 3:
            print("❌ Nazwa użytkownika musi mieć co najmniej 3 znaki!")
            sys.exit(1)
        
        if len(password) < 6:
            print("❌ Hasło musi mieć co najmniej 6 znaków!")
            sys.exit(1)
        
        create_admin(username, password)
    
    elif command == "list":
        list_admins()
    
    elif command == "delete":
        if len(sys.argv) != 3:
            print("❌ Błędna liczba argumentów dla komendy 'delete'")
            print("Użycie: python create_admin.py delete <username>")
            sys.exit(1)
        
        username = sys.argv[2]
        delete_admin(username)
    
    elif command == "password":
        if len(sys.argv) != 4:
            print("❌ Błędna liczba argumentów dla komendy 'password'")
            print("Użycie: python create_admin.py password <username> <new_password>")
            sys.exit(1)
        
        username = sys.argv[2]
        new_password = sys.argv[3]
        
        if len(new_password) < 6:
            print("❌ Hasło musi mieć co najmniej 6 znaków!")
            sys.exit(1)
        
        change_password(username, new_password)
    
    else:
        print(f"❌ Nieznana komenda: {command}")
        print_usage()
        sys.exit(1)

