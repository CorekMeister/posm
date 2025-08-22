import requests
import os
from datetime import datetime, timedelta
from urllib.parse import quote

class MinotarAPI:
    """Klasa do obsługi Minotar API z buforowaniem awatarów"""
    
    BASE_URL = "https://minotar.net"
    CACHE_DIR = "avatar_cache"
    CACHE_DURATION_HOURS = 24  # Czas buforowania awatarów w godzinach
    
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or self.CACHE_DIR
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Tworzy katalog cache jeśli nie istnieje"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, nickname, size):
        """Zwraca ścieżkę do pliku cache dla danego nicku i rozmiaru"""
        safe_nickname = quote(nickname.lower(), safe='')
        return os.path.join(self.cache_dir, f"{safe_nickname}_{size}.png")
    
    def _is_cache_valid(self, cache_path):
        """Sprawdza czy plik cache jest nadal ważny"""
        if not os.path.exists(cache_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        expiry_time = file_time + timedelta(hours=self.CACHE_DURATION_HOURS)
        
        return datetime.now() < expiry_time
    
    def get_avatar_url(self, nickname, size=64):
        """
        Zwraca URL do awatara gracza
        
        Args:
            nickname (str): Nick gracza Minecraft
            size (int): Rozmiar awatara (8, 16, 32, 64, 128, 256, 512)
            
        Returns:
            str: URL do awatara
        """
        # Walidacja rozmiaru
        valid_sizes = [8, 16, 32, 64, 128, 256, 512]
        if size not in valid_sizes:
            size = 64
        
        # Sanityzacja nicku
        nickname = self._sanitize_nickname(nickname)
        if not nickname:
            nickname = "steve"  # Domyślny skin
        
        return f"{self.BASE_URL}/avatar/{nickname}/{size}"
    
    def get_helm_url(self, nickname, size=64):
        """
        Zwraca URL do awatara z hełmem gracza
        
        Args:
            nickname (str): Nick gracza Minecraft
            size (int): Rozmiar awatara
            
        Returns:
            str: URL do awatara z hełmem
        """
        valid_sizes = [8, 16, 32, 64, 128, 256, 512]
        if size not in valid_sizes:
            size = 64
        
        nickname = self._sanitize_nickname(nickname)
        if not nickname:
            nickname = "steve"
        
        return f"{self.BASE_URL}/helm/{nickname}/{size}"
    
    def get_body_url(self, nickname, size=64):
        """
        Zwraca URL do pełnego ciała gracza
        
        Args:
            nickname (str): Nick gracza Minecraft
            size (int): Rozmiar obrazka
            
        Returns:
            str: URL do pełnego ciała gracza
        """
        valid_sizes = [8, 16, 32, 64, 128, 256, 512]
        if size not in valid_sizes:
            size = 64
        
        nickname = self._sanitize_nickname(nickname)
        if not nickname:
            nickname = "steve"
        
        return f"{self.BASE_URL}/body/{nickname}/{size}"
    
    def download_avatar(self, nickname, size=64, use_cache=True):
        """
        Pobiera awatar gracza i zapisuje w cache
        
        Args:
            nickname (str): Nick gracza Minecraft
            size (int): Rozmiar awatara
            use_cache (bool): Czy używać cache
            
        Returns:
            str: Ścieżka do pobranego pliku lub None w przypadku błędu
        """
        nickname = self._sanitize_nickname(nickname)
        if not nickname:
            return None
        
        cache_path = self._get_cache_path(nickname, size)
        
        # Sprawdzenie cache
        if use_cache and self._is_cache_valid(cache_path):
            return cache_path
        
        try:
            # Pobieranie awatara
            url = self.get_avatar_url(nickname, size)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Zapisanie do cache
            with open(cache_path, 'wb') as f:
                f.write(response.content)
            
            return cache_path
            
        except requests.RequestException as e:
            print(f"Błąd podczas pobierania awatara dla {nickname}: {e}")
            return None
    
    def _sanitize_nickname(self, nickname):
        """
        Sanityzuje nick gracza Minecraft
        
        Args:
            nickname (str): Nick do sanityzacji
            
        Returns:
            str: Sanityzowany nick lub None jeśli nieprawidłowy
        """
        if not nickname or not isinstance(nickname, str):
            return None
        
        # Usuwanie białych znaków
        nickname = nickname.strip()
        
        # Sprawdzenie długości (3-16 znaków dla Minecraft)
        if len(nickname) < 3 or len(nickname) > 16:
            return None
        
        # Sprawdzenie czy zawiera tylko dozwolone znaki
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', nickname):
            return None
        
        return nickname
    
    def validate_nickname(self, nickname):
        """
        Sprawdza czy nick gracza jest prawidłowy
        
        Args:
            nickname (str): Nick do sprawdzenia
            
        Returns:
            bool: True jeśli nick jest prawidłowy
        """
        return self._sanitize_nickname(nickname) is not None
    
    def clear_cache(self, older_than_hours=None):
        """
        Czyści cache awatarów
        
        Args:
            older_than_hours (int): Usuwa pliki starsze niż podana liczba godzin
        """
        if not os.path.exists(self.cache_dir):
            return
        
        now = datetime.now()
        
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            
            if not os.path.isfile(file_path):
                continue
            
            if older_than_hours:
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (now - file_time).total_seconds() < older_than_hours * 3600:
                    continue
            
            try:
                os.remove(file_path)
            except OSError:
                pass

# Globalna instancja dla łatwego użycia
minotar = MinotarAPI()

