# Posmiewiska.pl - Szybka Instalacja (jako root)

## 🚀 Instalacja w 10 minut

### 1. Przygotowanie serwera
```bash
# Zaloguj się jako root
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv python3-pip nginx git
```

### 2. Instalacja Node.js (do budowania frontendu)
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt install -y nodejs
npm install -g pnpm
```

### 3. Pobieranie aplikacji z GitHub
```bash
mkdir -p /opt/posmiewiska
cd /opt/posmiewiska
git clone https://github.com/CorekMeister/posm .
```

### 4. Instalacja zależności Python
```bash
cd /opt/posmiewiska/posmiewiska-backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 5. Konfiguracja aplikacji
```bash
nano /opt/posmiewiska/posmiewiska-backend/.env
```

Wklej:
```env
DATABASE_URL=sqlite:////opt/posmiewiska/posmiewiska-backend/database/app.db
FLASK_ENV=production
SECRET_KEY=zmien-na-bardzo-dluga-losowa-wartosc-123456789
JWT_SECRET_KEY=inna-bardzo-dluga-losowa-wartosc-987654321
CORS_ORIGINS=https://posmiewiska.pl,https://www.posmiewiska.pl
MINOTAR_CACHE_HOURS=24
MINOTAR_CACHE_DIR=/opt/posmiewiska/posmiewiska-backend/avatar_cache
```

### 6. Budowanie frontendu i kopiowanie
```bash
cd /opt/posmiewiska/posmiewiska-frontend
pnpm install
pnpm run build
cp -r /opt/posmiewiska/posmiewiska-frontend/dist/* /opt/posmiewiska/posmiewiska-backend/src/static/
```

### 7. Przygotowanie katalogów i bazy danych
```bash
mkdir -p /opt/posmiewiska/posmiewiska-backend/database
mkdir -p /opt/posmiewiska/posmiewiska-backend/avatar_cache
mkdir -p /opt/posmiewiska/posmiewiska-backend/logs

# Inicjalizacja bazy danych
cd /opt/posmiewiska/posmiewiska-backend
source venv/bin/activate
python -c "
from src.models.user import db
from src.main import app
with app.app_context():
    db.create_all()
    print(\'Baza danych utworzona.\')
"
```

### 8. Konfiguracja Nginx
```bash
nano /etc/nginx/sites-available/posmiewiska.pl
```

Wklej podstawową konfigurację (pamiętaj o dostosowaniu domeny):
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
        alias /opt/posmiewiska/posmiewiska-backend/src/static/;
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

### 9. Konfiguracja SSL z Cloudflare

1.  **Wygeneruj certyfikat Origin** w panelu Cloudflare (SSL/TLS -> Origin Server).
2.  **Skopiuj zawartość** Origin Certificate i Private Key.
3.  **Utwórz pliki na serwerze**:

```bash
mkdir -p /etc/nginx/ssl
nano /etc/nginx/ssl/posmiewiska.pl.pem  # Wklej Origin Certificate
nano /etc/nginx/ssl/posmiewiska.pl.key  # Wklej Private Key
chmod 600 /etc/nginx/ssl/posmiewiska.pl.key
```

4.  **Zaktualizuj konfigurację Nginx** (`/etc/nginx/sites-available/posmiewiska.pl`) dodając:

```nginx
server {
    listen 443 ssl http2;
    server_name posmiewiska.pl www.posmiewiska.pl;
    ssl_certificate /etc/nginx/ssl/posmiewiska.pl.pem;
    ssl_certificate_key /etc/nginx/ssl/posmiewiska.pl.key;
    # ... pozostała konfiguracja SSL i proxy_pass ...
}
```

5.  **Przeładuj Nginx**: `systemctl reload nginx`

### 10. Uruchomienie jako serwis
```bash
nano /etc/systemd/system/posmiewiska.service
```

Wklej (upewnij się, że `WorkingDirectory` i `Environment` wskazują na `posmiewiska-backend`):
```ini
[Unit]
Description=Posmiewiska.pl Flask Application
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/opt/posmiewiska/posmiewiska-backend
Environment=PATH=/opt/posmiewiska/posmiewiska-backend/venv/bin
EnvironmentFile=/opt/posmiewiska/posmiewiska-backend/.env
ExecStart=/opt/posmiewiska/posmiewiska-backend/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
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

### 11. Tworzenie administratora
```bash
cd /opt/posmiewiska/posmiewiska-backend
source venv/bin/activate
python create_admin.py create admin twoje_silne_haslo
```

### 12. Podstawowe zabezpieczenia
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

1. **Otwórz**: `https://twoja-domena.pl`
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
cd /opt/posmiewiska/posmiewiska-backend
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
ls -la /etc/nginx/ssl/
openssl s_client -connect twoja-domena.pl:443
```

## 📝 Ważne pliki

- **Aplikacja**: `/opt/posmiewiska/`
- **Baza danych**: `/opt/posmiewiska/posmiewiska-backend/database/app.db`
- **Logi**: `/var/log/nginx/` i `journalctl -u posmiewiska`
- **Konfiguracja Nginx**: `/etc/nginx/sites-available/posmiewiska.pl`
- **Serwis**: `/etc/systemd/system/posmiewiska.service`

---

**Gotowe!** Aplikacja powinna działać na `https://twoja-domena.pl` 🎉

