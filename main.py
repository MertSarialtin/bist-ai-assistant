import joblib
import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import FastAPI
import requests

from dotenv import load_dotenv
import os
load_dotenv()
def telegram_mesaj_gonder(mesaj):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = "5649465182"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": mesaj})


app = FastAPI()
# ==========================================
# FASTAPI ENDPOINT'LERİ (SUNUCU KODLARI)
# ==========================================
@app.get("/")
def ana_sayfa():
    return {"mesaj": "BIST Yapay Zeka Asistanı API'si Çalışıyor!"}

@app.get("/tahmin")
def tahmin_et():
    try:
        print("TAHMİN FONKSİYONU ÇALIŞTI")
        veri = yf.download("ASELS.IS", period="1y")

        # MultiIndex düzeltmesi
        if isinstance(veri.columns, pd.MultiIndex):
            veri.columns = veri.columns.get_level_values(0)
        veri.columns = [col.lower() for col in veri.columns]

        # Teknik indikatörleri hesapla
        veri["ma50"] = veri["close"].rolling(window=50).mean()
        veri["ma200"] = veri["close"].rolling(window=200).mean()
        
        kapanis_farki = veri["close"].diff()
        kazanc = kapanis_farki.clip(lower=0)
        kayip = -kapanis_farki.clip(upper=0)
        ort_kazanc = kazanc.ewm(com=13, adjust=False).mean()
        ort_kayip = kayip.ewm(com=13, adjust=False).mean()
        rs = ort_kazanc / ort_kayip
        veri["rsi14"] = 100 - (100 / (1 + rs))

        son_satir = veri.iloc[-1]
        gercek_girdi = np.array([[
            son_satir["open"],
            son_satir["close"],
            son_satir["volume"],
            son_satir["ma50"],
            son_satir["ma200"],
            son_satir["rsi14"]
        ]])

        print(f"TOKEN: {os.getenv('TELEGRAM_TOKEN')}")
        model = joblib.load("model.pkl")
        tahmin = model.predict(gercek_girdi)[0]
        sonuc_metni = "YÜKSELİŞ (AL)" if tahmin == 1 else "DÜŞÜŞ/SABİT (SAT)"

        mesaj = f"📊 ASELS Tahmin - {str(veri.index[-1].date())}\n\n{sonuc_metni}"
        telegram_mesaj_gonder(mesaj)

        return {
            "durum": "Basarili",
            "tarih": str(veri.index[-1].date()),
            "tahmin_kodu": int(tahmin),
            "tahmin_yorumu": sonuc_metni
        }
    except Exception as e:
        return {"durum": "Hata", "detay": str(e)}
    
#Yahoo Finance → Veri Çekme → Teknik Analiz → Model Eğitimi → FastAPI → Telegram