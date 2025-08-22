# Instrukcja Instalacji Posmiewiska.pl na VPS (jako root)

## Spis treści

1. [Wymagania systemowe](#wymagania-systemowe)
2. [Przygotowanie serwera](#przygotowanie-serwera)
3. [Instalacja zależności](#instalacja-zależności)
4. [Instalacja aplikacji](#instalacja-aplikacji)
5. [Konfiguracja bazy danych](#konfiguracja-bazy-danych)
6. [Konfiguracja Nginx](#konfiguracja-nginx)
7. [Konfiguracja SSL](#konfiguracja-ssl)
8. [Uruchomienie jako serwis](#uruchomienie-jako-serwis)
9. [Zabezpieczenia](#zabezpieczenia)
10. [Tworzenie pierwszego administratora](#tworzenie-pierwszego-administratora)
11. [Monitoring i konserwacja](#monitoring-i-konserwacja)
12. [Rozwiązywanie problemów](#rozwiązywanie-problemów)

---

## Wymagania systemowe

### Minimalne wymagania sprzętowe

- **CPU**: 1 vCPU (zalecane 2 vCPU)
- **RAM**: 1 GB (zalecane 2 GB)
- **Dysk**: 20 GB SSD (zalecane 40 GB)
- **Transfer**: 1 TB miesięcznie
- **Połączenie**: Stabilne łącze internetowe

### Wymagania systemowe

- **Ubuntu 20.04 LTS** lub **Ubuntu 22.04 LTS** (zalecane)
- **Debian 11** (Bullseye)
- Dostęp root do serwera

### Wymagane porty

- **Port 22**: SSH (administracja)
- **Port 80**: HTTP (przekierowanie na HTTPS)
- **Port 443**: HTTPS (główny ruch aplikacji)

---

## Przygotowanie serwera

### Aktualizacja systemu

Zaloguj się jako root i zaktualizuj system:

```bash
apt update && apt upgrade -y
apt autoremove -y
reboot
```

Po ponownym uruchomieniu zaloguj się ponownie jako root.

### Konfiguracja hostname (opcjonalnie)

```bash
hostnamectl set-hostname posmiewiska
echo "127.0.0.1 posmiewiska" >> /etc/hosts
```

---

## Instalacja zależności

### Python i narzędzia deweloperskie

```bash
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
apt install -y build-essential curl wget git unzip
apt install -y software-properties-common apt-transport-https ca-certificates
```

Sprawdź wersję Python:

```bash
python3.11 --version
```

### Node.js (dla budowania frontendu)

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt install -y nodejs
npm install -g pnpm
```

### Nginx

```bash
apt install -y nginx
systemctl start nginx
systemctl enable nginx
```

### Certbot (dla SSL)

```bash
apt install -y certbot python3-certbot-nginx
```

---

## Instalacja aplikacji

### Tworzenie struktury katalogów

```bash
mkdir -p /opt/posmiewiska
cd /opt/posmiewiska
```

### Pobieranie i rozpakowanie aplikacji

Skopiuj pliki aplikacji na serwer (przez SCP, SFTP lub Git):

```bash
# Jeśli masz archiwum
tar -xzf posmiewiska-final.tar.gz
mv posmiewiska-backend/* .
rmdir posmiewiska-backend

# Lub jeśli kopiujesz bezpośrednio
# scp -r posmiewiska-backend/* root@your-server:/opt/posmiewiska/
```

### Konfiguracja środowiska Python

```bash
cd /opt/posmiewiska
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### Modyfikacja konfiguracji dla root

Edytuj plik `gunicorn.conf.py`:

```bash
nano gunicorn.conf.py
```

Zmień zawartość na:

```python
# Gunicorn configuration file for root installation
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "root"
group = "root"
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
```

### Konfiguracja środowiska

Utwórz plik `.env`:

```bash
nano .env
```

```env
# Konfiguracja bazy danych
DATABASE_URL=sqlite:////opt/posmiewiska/database/app.db

# Konfiguracja Flask
FLASK_ENV=production
SECRET_KEY=zmien-na-bardzo-dluga-losowa-wartosc-123456789abcdef
JWT_SECRET_KEY=inna-bardzo-dluga-losowa-wartosc-987654321fedcba

# Konfiguracja bezpieczeństwa
CORS_ORIGINS=https://posmiewiska.pl,https://www.posmiewiska.pl

# Konfiguracja Minotar
MINOTAR_CACHE_HOURS=24
MINOTAR_CACHE_DIR=/opt/posmiewiska/avatar_cache
```

### Tworzenie katalogów

```bash
mkdir -p /opt/posmiewiska/database
mkdir -p /opt/posmiewiska/avatar_cache
mkdir -p /opt/posmiewiska/logs
```

---

## Konfiguracja bazy danych

### Inicjalizacja bazy danych SQLite

```bash
cd /opt/posmiewiska
source venv/bin/activate
python -c "
from src.models.user import db
from src.main import app
with app.app_context():
    db.create_all()
    print('Baza danych została utworzona.')
"
```

### Opcjonalnie: PostgreSQL

Jeśli wolisz PostgreSQL:

```bash
apt install -y postgresql postgresql-contrib python3-psycopg2
systemctl start postgresql
systemctl enable postgresql

# Utwórz bazę danych
sudo -u postgres psql -c "CREATE DATABASE posmiewiska_db;"
sudo -u postgres psql -c "CREATE USER posmiewiska_user WITH PASSWORD 'strong_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE posmiewiska_db TO posmiewiska_user;"

# Zmień DATABASE_URL w .env
# DATABASE_URL=postgresql://posmiewiska_user:strong_password@localhost/posmiewiska_db
```

---

## Konfiguracja Nginx

### Tworzenie konfiguracji witryny

```bash
nano /etc/nginx/sites-available/posmiewiska.pl
```

```nginx
server {
    listen 80;
    server_name posmiewiska.pl www.posmiewiska.pl;
    
    # Przekierowanie HTTP na HTTPS (zostanie skonfigurowane przez Certbot)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name posmiewiska.pl www.posmiewiska.pl;
    
    # Certyfikaty SSL (zostaną dodane przez Certbot)
    # ssl_certificate /etc/letsencrypt/live/posmiewiska.pl/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/posmiewiska.pl/privkey.pem;
    
    # Nowoczesne ustawienia SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Nagłówki bezpieczeństwa
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://minotar.net; font-src 'self'; connect-src 'self';" always;
    
    # Główna lokalizacja - proxy do aplikacji Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouty
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Buforowanie
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Statyczne pliki
    location /static/ {
        alias /opt/posmiewiska/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Cache awatarów
    location /avatars/ {
        alias /opt/posmiewiska/avatar_cache/;
        expires 1d;
        add_header Cache-Control "public";
        access_log off;
    }
    
    # Blokowanie dostępu do wrażliwych plików
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(env|log|ini)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Logi
    access_log /var/log/nginx/posmiewiska_access.log;
    error_log /var/log/nginx/posmiewiska_error.log;
    
    # Limity
    client_max_body_size 10M;
    client_body_timeout 30s;
    client_header_timeout 30s;
}
```

### Aktywacja konfiguracji

```bash
ln -s /etc/nginx/sites-available/posmiewiska.pl /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

---

## Konfiguracja SSL

### Let's Encrypt

```bash
certbot --nginx -d posmiewiska.pl -d www.posmiewiska.pl
```

Postępuj zgodnie z instrukcjami. Certbot automatycznie zaktualizuje konfigurację Nginx.

### Automatyczne odnawianie

```bash
crontab -e
```

Dodaj linię:

```
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## Uruchomienie jako serwis

### Tworzenie pliku systemd

```bash
nano /etc/systemd/system/posmiewiska.service
```

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

### Uruchomienie serwisu

```bash
systemctl daemon-reload
systemctl enable posmiewiska
systemctl start posmiewiska
systemctl status posmiewiska
```

---

## Zabezpieczenia

### Firewall UFW

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw enable
ufw status
```

### Fail2Ban

```bash
apt install -y fail2ban
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
nano /etc/fail2ban/jail.local
```

Dodaj na końcu pliku:

```ini
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/posmiewiska_error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/posmiewiska_error.log
maxretry = 10

[nginx-botsearch]
enabled = true
port = http,https
logpath = /var/log/nginx/posmiewiska_access.log
maxretry = 2
```

```bash
systemctl enable fail2ban
systemctl start fail2ban
fail2ban-client status
```

### Automatyczne aktualizacje

```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## Tworzenie pierwszego administratora

### Skrypt do tworzenia administratora

```bash
nano /opt/posmiewiska/create_admin.py
```

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
        # Sprawdź czy admin już istnieje
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            print(f"Administrator '{username}' już istnieje!")
            return False
        
        # Utwórz nowego administratora
        admin = Admin(
            username=username,
            password=generate_password_hash(password)
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Administrator '{username}' został utworzony pomyślnie!")
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
```

### Tworzenie administratora

```bash
cd /opt/posmiewiska
source venv/bin/activate
python create_admin.py admin twoje_haslo_tutaj
```

**WAŻNE**: Zmień `twoje_haslo_tutaj` na silne hasło!

---

## Monitoring i konserwacja

### Sprawdzanie statusu

```bash
# Status aplikacji
systemctl status posmiewiska

# Status Nginx
systemctl status nginx

# Logi aplikacji
journalctl -u posmiewiska -f

# Logi Nginx
tail -f /var/log/nginx/posmiewiska_access.log
tail -f /var/log/nginx/posmiewiska_error.log
```

### Backup bazy danych

```bash
nano /opt/posmiewiska/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/posmiewiska/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup SQLite
if [ -f "/opt/posmiewiska/database/app.db" ]; then
    cp /opt/posmiewiska/database/app.db $BACKUP_DIR/app_$DATE.db
fi

# Usuń stare backupy (starsze niż 30 dni)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /opt/posmiewiska/backup.sh
crontab -e
```

Dodaj:

```
0 2 * * * /opt/posmiewiska/backup.sh >> /opt/posmiewiska/logs/backup.log 2>&1
```

### Aktualizacja aplikacji

```bash
# 1. Backup
/opt/posmiewiska/backup.sh

# 2. Zatrzymaj aplikację
systemctl stop posmiewiska

# 3. Zaktualizuj kod (skopiuj nowe pliki)

# 4. Zaktualizuj zależności
cd /opt/posmiewiska
source venv/bin/activate
pip install -r requirements.txt

# 5. Uruchom aplikację
systemctl start posmiewiska
systemctl status posmiewiska
```

---

## Rozwiązywanie problemów

### Częste problemy

#### Aplikacja nie uruchamia się

```bash
# Sprawdź logi
journalctl -u posmiewiska -n 50

# Sprawdź konfigurację
cd /opt/posmiewiska
source venv/bin/activate
python -c "from src.main import app; print('OK')"

# Sprawdź uprawnienia
ls -la /opt/posmiewiska/
```

#### Błąd 502 Bad Gateway

```bash
# Sprawdź czy aplikacja działa
systemctl status posmiewiska
curl http://127.0.0.1:5000/

# Sprawdź konfigurację Nginx
nginx -t
systemctl status nginx
```

#### Błędy SSL

```bash
# Sprawdź certyfikaty
certbot certificates

# Odnów certyfikaty
certbot renew --dry-run
```

### Przydatne komendy

```bash
# Status wszystkich serwisów
systemctl status nginx posmiewiska

# Test konfiguracji Nginx
nginx -t

# Sprawdzenie portów
netstat -tulpn | grep -E ':(80|443|5000)'

# Sprawdzenie miejsca na dysku
df -h

# Sprawdzenie pamięci
free -h

# Restart wszystkich serwisów
systemctl restart nginx posmiewiska
```

---

## Testowanie instalacji

Po zakończeniu instalacji, przetestuj aplikację:

1. **Otwórz przeglądarkę** i przejdź do `https://posmiewiska.pl`
2. **Sprawdź stronę główną** - powinna wyświetlać się lista graczy
3. **Kliknij "Panel Administratora"**
4. **Zaloguj się** używając utworzonych danych administratora
5. **Dodaj testowego gracza** w panelu administracyjnym
6. **Sprawdź czy gracz pojawia się** na stronie głównej

---

**Autor**: Manus AI  
**Data**: 2025  
**Wersja**: 2.0 (Root Installation)

Ta instrukcja została przygotowana specjalnie dla instalacji jako użytkownik root bez tworzenia dodatkowych użytkowników systemowych.

