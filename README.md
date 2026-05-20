# BIST AI Assistant 📈🤖

Bu proje, Borsa İstanbul (BIST) hisse senetleri (örnek olarak **ASELS**) için makine öğrenmesi tabanlı yön tahmini yapan ve sonuçları günlük olarak otomatik bir şekilde Telegram üzerinden kullanıcıya raporlayan uçtan uca bir yapay zeka asistanıdır.

## 🚀 Proje Mimarisi

Proje temel olarak iki ana aşamadan oluşmaktadır:
1. **Model Eğitimi (`data_and_model.py`):** Yahoo Finance üzerinden geçmiş verileri çeker, teknik göstergeleri (MA50, MA200, RSI) hesaplar, `RandomForestClassifier` modelini eğitir ve veritabanı (`SQLite`) ile eğitilmiş modeli (`model.pkl`) yerel olarak kaydeder.
2. **Canlı Tahmin ve API Servisi (`main.py`):** FastAPI kullanarak bir web servisi ayağa kaldırır. Arka planda çalışan zamanlayıcı (APScheduler) her gün belirlenen saatte güncel verileri çekerek model üzerinden tahmin üretir ve sonucu Telegram Botu aracılığıyla iletir.

---

## 🛠️ Kullanılan Teknolojiler ve Kütüphaneler

* **Programlama Dili:** Python 3.x
* **API & Sunucu:** FastAPI, Uvicorn
* **Veri Bilimi & Makine Öğrenmesi:** Pandas, NumPy, Scikit-Learn (Random Forest), Joblib
* **Finansal Veri:** yfinance (Yahoo Finance API)
* **Veri Depolama:** SQLite & SQLAlchemy
* **Otomasyon & Zamanlayıcı:** APScheduler (BackgroundScheduler)
* **Bildirim:** Telegram Bot API & Requests

---

## 📂 Proje Yapısı

```text
├── .vscode/
├── borsa_verileri.db      # Özellik mühendisliği yapılmış verilerin tutulduğu SQLite veritabanı
├── data_and_model.py      # Veri çekme, işleme ve model eğitme scripti
├── main.py                # FastAPI, Zamanlayıcı (Scheduler) ve Telegram entegrasyonu
├── model.pkl              # Eğitilmiş ve kaydedilmiş Random Forest modeli
├── Procfile               # (Opsiyonel) Canlıya alım (Deployment) yapılandırma dosyası
├── requirements.txt       # Gerekli bağımlılıkların listesi
└── README.md              # Proje dökümantasyonu
