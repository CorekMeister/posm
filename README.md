# Posmiewiska.pl - Czarna Lista Graczy Minecraft

System do zarządzania czarną listą graczy Minecraft z nowoczesnym interfejsem web i panelem administracyjnym.

## 🚀 Funkcjonalności

### Dla użytkowników
- **Lista graczy** - Przegląd zgłoszonych graczy w formie kart z awatarami
- **Wyszukiwarka** - Szybkie wyszukiwanie graczy po nicku lub powodzie zgłoszenia
- **Responsywny design** - Działa na komputerach, tabletach i telefonach
- **Dark mode** - Nowoczesny ciemny motyw z niebieską kolorystyką
- **Awatary Minotar** - Automatyczne wyświetlanie awatarów graczy z Minotar.net

### Dla administratorów
- **Panel administracyjny** - Bezpieczny panel do zarządzania listą
- **Zarządzanie graczami** - Dodawanie, edycja i usuwanie graczy z listy
- **Uwierzytelnianie JWT** - Bezpieczne logowanie z tokenami
- **Walidacja danych** - Automatyczna walidacja nicków Minecraft i danych
- **Statystyki** - Przegląd liczby graczy i aktywności

## 🛠️ Technologie

### Backend
- **Flask** - Framework web dla Python
- **SQLAlchemy** - ORM do zarządzania bazą danych
- **JWT** - Tokeny uwierzytelniania
- **Flask-CORS** - Obsługa CORS
- **Werkzeug** - Hashowanie haseł
- **Requests** - Integracja z Minotar API

### Frontend
- **React.js** - Biblioteka do budowy interfejsu
- **Tailwind CSS** - Framework CSS
- **shadcn/ui** - Komponenty UI
- **Lucide React** - Ikony
- **Vite** - Bundler i serwer deweloperski

### Baza danych
- **SQLite** - Domyślnie (dla prostoty)
- **PostgreSQL** - Zalecane dla produkcji

## 📋 Wymagania

### Minimalne wymagania serwera
- **CPU**: 1 vCPU (zalecane 2 vCPU)
- **RAM**: 1 GB (zalecane 2 GB)
- **Dysk**: 20 GB SSD
- **System**: Ubuntu 20.04+ / Debian 11+

### Wymagane oprogramowanie
- Python 3.11+
- Node.js 18+ (do budowania frontendu)
- Nginx (serwer web)
- Certbot (SSL)

## 🚀 Szybka instalacja

### 1. Przygotowanie serwera
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv nginx certbot python3-certbot-nginx
```

### 2. Instalacja aplikacji
```bash
# Skopiuj pliki aplikacji
cd /home/ubuntu
tar -xzf posmiewiska.tar.gz
cd posmiewiska-backend

# Utwórz środowisko wirtualne
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Konfiguracja
```bash
# Utwórz plik konfiguracyjny
nano .env
```

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
CORS_ORIGINS=https://yourdomain.com
```

### 4. Uruchomienie
```bash
# Zainstaluj Gunicorn
pip install gunicorn

# Uruchom aplikację
gunicorn -c gunicorn.conf.py src.main:app
```

## 📖 Szczegółowa instrukcja

Pełna instrukcja instalacji na serwerze VPS znajduje się w pliku [INSTRUKCJA_INSTALACJI.md](INSTRUKCJA_INSTALACJI.md).

Instrukcja obejmuje:
- Konfigurację serwera i zabezpieczeń
- Instalację i konfigurację Nginx
- Konfigurację SSL z Let's Encrypt/Cloudflare
- Uruchomienie jako serwis systemd
- Monitoring i konserwację
- Rozwiązywanie problemów

## 🔧 Konfiguracja

### Zmienne środowiskowe

| Zmienna | Opis | Domyślna wartość |
|---------|------|------------------|
| `SECRET_KEY` | Klucz szyfrowania Flask | - |
| `DATABASE_URL` | URL bazy danych | `sqlite:///app.db` |
| `JWT_SECRET_KEY` | Klucz do podpisywania JWT | - |
| `CORS_ORIGINS` | Dozwolone domeny CORS | `*` |
| `MINOTAR_CACHE_HOURS` | Czas cache awatarów | `24` |

### Struktura projektu

```
posmiewiska-backend/
├── src/
│   ├── models/          # Modele bazy danych
│   ├── routes/          # Endpointy API
│   ├── utils/           # Narzędzia pomocnicze
│   ├── static/          # Pliki statyczne (frontend)
│   └── main.py          # Główny plik aplikacji
├── venv/                # Środowisko wirtualne
├── requirements.txt     # Zależności Python
├── gunicorn.conf.py     # Konfiguracja Gunicorn
└── .env                 # Zmienne środowiskowe
```

## 🔐 Bezpieczeństwo

System implementuje następujące zabezpieczenia:

- **Hashowanie haseł** - Bcrypt do bezpiecznego przechowywania haseł
- **JWT tokeny** - Bezpieczne uwierzytelnianie bez sesji
- **Walidacja danych** - Sanityzacja wszystkich danych wejściowych
- **CORS** - Kontrola dostępu z różnych domen
- **Rate limiting** - Ochrona przed nadmiernym ruchem
- **SSL/TLS** - Szyfrowanie komunikacji
- **Fail2Ban** - Ochrona przed atakami brute force

## 📊 API Endpoints

### Publiczne endpointy
- `GET /api/players` - Lista graczy (z paginacją i wyszukiwaniem)
- `GET /api/players/{id}` - Szczegóły gracza

### Endpointy administratora
- `POST /api/auth/login` - Logowanie administratora
- `POST /api/auth/logout` - Wylogowanie
- `GET /api/auth/me` - Informacje o zalogowanym adminie
- `POST /api/players` - Dodanie gracza (wymaga autoryzacji)
- `PUT /api/players/{id}` - Edycja gracza (wymaga autoryzacji)
- `DELETE /api/players/{id}` - Usunięcie gracza (wymaga autoryzacji)

## 🎨 Personalizacja

### Zmiana kolorystyki
Edytuj plik `src/App.css` w sekcji `.dark` aby zmienić kolory:

```css
.dark {
  --primary: oklch(0.6 0.2 240);  /* Niebieski główny */
  --background: oklch(0.08 0.02 240);  /* Tło */
  --card: oklch(0.12 0.03 240);  /* Karty */
}
```

### Dodanie własnego logo
Zastąp ikonę w komponencie `Header.jsx`:

```jsx
<div className="bg-primary p-2 rounded-lg">
  <img src="/logo.png" alt="Logo" className="w-6 h-6" />
</div>
```

## 🔄 Aktualizacje

### Aktualizacja aplikacji
```bash
# 1. Backup bazy danych
cp database/app.db database/app.db.backup

# 2. Zatrzymaj aplikację
sudo systemctl stop posmiewiska

# 3. Zaktualizuj kod
# (skopiuj nowe pliki)

# 4. Zaktualizuj zależności
source venv/bin/activate
pip install -r requirements.txt

# 5. Uruchom aplikację
sudo systemctl start posmiewiska
```

## 📝 Licencja

Ten projekt jest udostępniony na licencji MIT. Zobacz plik [LICENSE](LICENSE) po szczegóły.

## 🤝 Wsparcie

W przypadku problemów:

1. Sprawdź [instrukcję instalacji](INSTRUKCJA_INSTALACJI.md)
2. Przejrzyj sekcję rozwiązywania problemów
3. Sprawdź logi aplikacji: `sudo journalctl -u posmiewiska -f`

## 📈 Roadmapa

Planowane funkcjonalności:
- [ ] API do masowego importu graczy
- [ ] System powiadomień email
- [ ] Integracja z Discord
- [ ] Statystyki i raporty
- [ ] Backup automatyczny do chmury
- [ ] Multi-tenancy (wiele serwerów)

---

**Wykonanie**: Settings.lol - CorekL  
**Wersja**: 1.0  
**Data**: 2025

