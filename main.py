import joblib
import numpy as np
import pandas as pd
import yfinance as yf
import requests
import os
from pytz import timezone

from fastapi import FastAPI
from dotenv import load_dotenv

# Scheduler
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = FastAPI()

# ==========================================
# TELEGRAM MESAJ FONKSİYONU
# ==========================================

def telegram_mesaj_gonder(mesaj):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = "7401971607"

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": mesaj
        }
    )

# ==========================================
# TAHMİN FONKSİYONU
# ==========================================

def tahmin_yap():

    try:
        print("TAHMİN ÇALIŞTI")

        veri = yf.download("ASELS.IS", period="1y")

        # MultiIndex düzelt
        if isinstance(veri.columns, pd.MultiIndex):
            veri.columns = veri.columns.get_level_values(0)

        veri.columns = [col.lower() for col in veri.columns]

        # Teknik göstergeler
        veri["ma50"] = veri["close"].rolling(window=50).mean()
        veri["ma200"] = veri["close"].rolling(window=200).mean()

        kapanis_farki = veri["close"].diff()

        kazanc = kapanis_farki.clip(lower=0)
        kayip = -kapanis_farki.clip(upper=0)

        ort_kazanc = kazanc.ewm(com=13, adjust=False).mean()
        ort_kayip = kayip.ewm(com=13, adjust=False).mean()

        rs = ort_kazanc / np.where(ort_kayip == 0, 0.00001, ort_kayip)

        veri["rsi14"] = 100 - (100 / (1 + rs))

        son_satir = veri.iloc[-1]

        gercek_girdi = pd.DataFrame([{
            "open": son_satir["open"],
            "close": son_satir["close"],
        "volume": son_satir["volume"],
        "ma50": son_satir["ma50"],
        "ma200": son_satir["ma200"],
        "rsi14": son_satir["rsi14"]
}])

        # Model yükle
        model = joblib.load("model.pkl")

        tahmin = model.predict(gercek_girdi)[0]

        sonuc_metni = (
            "📈 YÜKSELİŞ (AL)"
            if tahmin == 1
            else "📉 DÜŞÜŞ / SABİT (SAT)"
        )

        mesaj = f"""
📊 ASELS Günlük Tahmin

Tarih: {str(veri.index[-1].date())}

Tahmin:
{sonuc_metni}
"""

        telegram_mesaj_gonder(mesaj)

        print("Telegram mesajı gönderildi")

    except Exception as e:
        print("HATA:", str(e))

# ==========================================
# FASTAPI ENDPOINTLERİ
# ==========================================

@app.get("/")
def ana_sayfa():
    return {"mesaj": "BIST AI API Çalışıyor"}

@app.get("/tahmin")
def manuel_tahmin():

    tahmin_yap()

    return {
        "durum": "Başarılı",
        "mesaj": "Tahmin yapıldı ve telegram mesajı gönderildi"
    }

# ==========================================
# SCHEDULER
# ==========================================

scheduler = BackgroundScheduler(
    timezone=timezone("Europe/Istanbul")
)

scheduler.add_job(
    tahmin_yap,
    trigger="cron",
    hour=9,
    minute=30
)
@app.on_event("startup")
def start_scheduler():
    scheduler.start()

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

