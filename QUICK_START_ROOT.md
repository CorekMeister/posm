# Posmiewiska.pl - Szybka Instalacja (jako root)

## 🚀 Instalacja w 10 minut

### 1. Przygotowanie serwera
```bash
# Zaloguj się jako root
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx
```

### 2. Instalacja Node.js (do budowania frontendu)
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt install -y nodejs
npm install -g pnpm
```

### 3. Przygotowanie aplikacji
```bash
mkdir -p /opt/posmiewiska
cd /opt/posmiewiska

# Skopiuj pliki aplikacji (przez SCP/SFTP)
# lub rozpakuj archiwum:
# tar -xzf posmiewiska-final.tar.gz
# mv posmiewiska-backend/* .
```

### 4. Instalacja zależności Python
```bash
cd /opt/posmiewiska
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 5. Konfiguracja aplikacji
```bash
nano .env
```

Wklej:
```env
DATABASE_URL=sqlite:////opt/posmiewiska/database/app.db
FLASK_ENV=production
SECRET_KEY=zmien-na-bardzo-dluga-losowa-wartosc-123456789
JWT_SECRET_KEY=inna-bardzo-dluga-losowa-wartosc-987654321
CORS_ORIGINS=https://posmiewiska.pl,https://www.posmiewiska.pl
MINOTAR_CACHE_HOURS=24
MINOTAR_CACHE_DIR=/opt/posmiewiska/avatar_cache
```

### 6. Przygotowanie katalogów i bazy danych
```bash
mkdir -p /opt/posmiewiska/database
mkdir -p /opt/posmiewiska/avatar_cache
mkdir -p /opt/posmiewiska/logs

# Inicjalizacja bazy danych
source venv/bin/activate
python -c "
from src.models.user import db
from src.main import app
with app.app_context():
    db.create_all()
    print('Baza danych utworzona.')
"
```

### 7. Konfiguracja Nginx
```bash
nano /etc/nginx/sites-available/posmiewiska.pl
```

Wklej podstawową konfigurację:
```nginx
server {
    listen 80;
    server_name posmiewiska.pl www.posmiewiska.pl;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /opt/posmiewiska/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
ln -s /etc/nginx/sites-available/posmiewiska.pl /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

### 8. Konfiguracja SSL (Let's Encrypt)
```bash
certbot --nginx -d posmiewiska.pl -d www.posmiewiska.pl
```

### 9. Uruchomienie jako serwis
```bash
nano /etc/systemd/system/posmiewiska.service
```

Wklej:
```ini
[Unit]
Description=Posmiewiska.pl Flask Application
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/opt/posmiewiska
Environment=PATH=/opt/posmiewiska/venv/bin
EnvironmentFile=/opt/posmiewiska/.env
ExecStart=/opt/posmiewiska/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=posmiewiska

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable posmiewiska
systemctl start posmiewiska
systemctl status posmiewiska
```

### 10. Tworzenie administratora
```bash
nano /opt/posmiewiska/create_admin.py
```

Wklej skrypt:
```python
#!/usr/bin/env python3
import sys
import os
sys.path.append('/opt/posmiewiska')

from src.models.user import db
from src.models.admin import Admin
from src.main import app
from werkzeug.security import generate_password_hash

def create_admin(username, password):
    with app.app_context():
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            print(f"Administrator '{username}' już istnieje!")
            return False
        
        admin = Admin(
            username=username,
            password=generate_password_hash(password)
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Administrator '{username}' został utworzony!")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Użycie: python create_admin.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    if len(password) < 6:
        print("Hasło musi mieć co najmniej 6 znaków!")
        sys.exit(1)
    
    create_admin(username, password)
```

```bash
chmod +x /opt/posmiewiska/create_admin.py
cd /opt/posmiewiska
source venv/bin/activate
python create_admin.py admin twoje_silne_haslo
```

### 11. Podstawowe zabezpieczenia
```bash
# Firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw enable

# Fail2Ban
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

## ✅ Sprawdzenie instalacji

1. **Otwórz**: https://posmiewiska.pl
2. **Sprawdź**: Czy strona się ładuje
3. **Kliknij**: "Panel Administratora"
4. **Zaloguj się**: Używając utworzonych danych
5. **Dodaj**: Testowego gracza

## 🔧 Przydatne komendy

```bash
# Status aplikacji
systemctl status posmiewiska

# Logi aplikacji
journalctl -u posmiewiska -f

# Restart aplikacji
systemctl restart posmiewiska

# Status Nginx
systemctl status nginx

# Test konfiguracji Nginx
nginx -t

# Sprawdzenie czy aplikacja odpowiada
curl http://127.0.0.1:5000/api/players
```

## 🚨 Rozwiązywanie problemów

### Aplikacja nie uruchamia się
```bash
journalctl -u posmiewiska -n 50
cd /opt/posmiewiska
source venv/bin/activate
python src/main.py  # Test ręczny
```

### Błąd 502 Bad Gateway
```bash
systemctl status posmiewiska
curl http://127.0.0.1:5000/
nginx -t
```

### Problemy z SSL
```bash
certbot certificates
certbot renew --dry-run
```

## 📝 Ważne pliki

- **Aplikacja**: `/opt/posmiewiska/`
- **Baza danych**: `/opt/posmiewiska/database/app.db`
- **Logi**: `/var/log/nginx/` i `journalctl -u posmiewiska`
- **Konfiguracja Nginx**: `/etc/nginx/sites-available/posmiewiska.pl`
- **Serwis**: `/etc/systemd/system/posmiewiska.service`

---

**Gotowe!** Aplikacja powinna działać na https://posmiewiska.pl 🎉

