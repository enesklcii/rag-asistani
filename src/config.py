import os
from dotenv import load_dotenv

# .env dosyasındaki gizli değişkenleri yükle
load_dotenv()

# API Anahtarı kontrolü
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("HATA: GOOGLE_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")

# Klasör ve Veritabanı Yolları
DATA_PATH = "data"
CHROMA_DB_PATH = "chroma_db"

# Metin Parçalama (Chunking) Ayarları
CHUNK_SIZE = 1000       # Her bir metin parçasının maksimum karakter uzunluğu
CHUNK_OVERLAP = 200     # Parçalar arası bağlam kopmasın diye üst üste binecek karakter sayısı
