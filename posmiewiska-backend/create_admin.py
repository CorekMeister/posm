#!/usr/bin/env python3
import sys
import os

# Dodaj ścieżkę do aplikacji
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from src.models.admin import Admin, db  # Załóżmy, że app i db są skonfigurowane w src.models.user lub podobnym miejscu
from src.app import app  # Załóżmy, że app jest zdefiniowane w src.app

def create_admin(username, password, email):
    """Tworzy nowego administratora"""
    with app.app_context():
        try:
            if Admin.query.filter_by(username=username).first():
                print(f"❌ Administrator z username '{username}' już istnieje.")
                return
            if Admin.query.filter_by(email=email).first():
                print(f"❌ Administrator z email '{email}' już istnieje.")
                return
            
            admin = Admin(username=username, email=email)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Administrator '{username}' został utworzony pomyślnie.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Błąd podczas tworzenia administratora: {e}")

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
            admin.password_hash = generate_password_hash(new_password)
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
    print("  python create_admin.py create <username> <password> <email>  - Tworzy nowego administratora")
    print("  python create_admin.py list                                          - Wyświetla listę administratorów")
    print("  python create_admin.py delete <username>                              - Usuwa administratora")
    print("  python create_admin.py password <username> <new_password>            - Zmienia hasło administratora")
    print("")
    print("Przykłady:")
    print("  python create_admin.py create admin mojeSilneHaslo123 admin@example.com")
    print("  python create_admin.py list")
    print("  python create_admin.py delete admin")
    print("  python create_admin.py password admin noweHaslo456")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "create":
        if len(sys.argv) != 5:
            print("❌ Błędna liczba argumentów dla komendy 'create'")
            print("Użycie: python create_admin.py create <username> <password> <email>")
            sys.exit(1)
        
        username = sys.argv[2]
        password = sys.argv[3]
        email = sys.argv[4]
        
        if len(username) < 3:
            print("❌ Nazwa użytkownika musi mieć co najmniej 3 znaki!")
            sys.exit(1)
        
        if len(password) < 6:
            print("❌ Hasło musi mieć co najmniej 6 znaków!")
            sys.exit(1)
        
        create_admin(username, password, email)
    
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
    
    else:
        print(f"❌ Nieznana komenda: {command}")
        print_usage()
        sys.exit(1)

