# BIST AI Assistant 📈🤖

Bu proje, Borsa İstanbul (BIST) hisse senetleri (örnek olarak **ASELS**) için makine öğrenmesi tabanlı yön tahmini yapan ve sonuçları günlük olarak otomatik bir şekilde Telegram üzerinden kullanıcıya raporlayan uçtan uca bir yapay zeka asistanıdır.

## 🚀 Proje Mimarisi

Proje temel olarak iki ana aşamadan oluşmaktadır:
1. **Model Eğitimi (`data_and_model.py`):** Yahoo Finance üzerinden geçmiş verileri çeker, teknik göstergeleri (MA50, MA200, RSI) hesaplar, `RandomForestClassifier` modelini eğitir ve veritabanı (`SQLite`) ile eğitilmiş modeli (`model.pkl`) yerel olarak kaydeder.
2. **Canlı Tahmin ve API Servisi (`main.py`):** FastAPI kullanarak bir web servisi ayağa kaldırır. Arka planda çalışan zamanlayıcı (APScheduler) her gün belirlenen saatte güncel verileri çekerek model üzerinden tahmin üretir ve sonucu Telegram Botu aracılığıyla iletir.

---

## 🛠️ Kullanılan Teknolojiler ve Kütüphaneler

* **Programlama Dili:** Python 
* **API & Sunucu:** FastAPI, Uvicorn
* **Veri Bilimi & Makine Öğrenmesi:** Pandas, NumPy, Scikit-Learn (Random Forest), Joblib
* **Finansal Veri:** yfinance (Yahoo Finance API)
* **Veri Depolama:** SQLite & SQLAlchemy
* **Otomasyon & Zamanlayıcı:** APScheduler (BackgroundScheduler)
* **Bildirim:** Telegram Bot API & Requests

---

## 📂 Proje Yapısı

```text
├── main.py                # API + Scheduler + Telegram bot
├── data_and_model.py     # Model eğitimi ve veri hazırlama
├── model.pkl             # Eğitilmiş ML modeli
├── borsa_verileri.db     # SQLite veri tabanı
├── requirements.txt      # Python bağımlılıkları
├── Dockerfile            # Docker imajı
├── docker-compose.yml    # Container yönetimi
├── .env.example          # Ortam değişkenleri şablonu
└── README.md
```

##⚙️ Kurulum

1. Repo'yu klonla
git clone https://github.com/kullaniciadi/bist-ai-assistant.git
cd bist-ai-assistant

2. .env dosyası oluştur
Proje kök dizinine .env dosyası ekle:
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHAT_ID=YOUR_TELEGRAM_CHAT_ID

4. Telegram Bot Bilgileri
Bot oluşturmak için: @BotFather
Chat ID öğrenmek için: @userinfobot
---
