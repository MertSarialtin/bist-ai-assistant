import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sqlalchemy import create_engine
import yfinance as yf

# ==========================================
# 1. ADIM: VERİ ÇEKME VE ÖZELLİK MÜHENDİSLİĞİ
# ==========================================
if __name__ == "__main__": #sadece manuel çalıştırıldığında çalışmayı sağlar onun dışında çalışmaz güvenlik amaçlı
    # Veritabanı bağlantısı
    engine = create_engine("sqlite:///borsa_verileri.db")

    hisse_sembolleri = ["ASELS.IS"]
    baslangic_tarihi = "2020-01-01"
    bitis_tarihi = "2026-05-19"

    print("Veriler çekiliyor, özellik mühendisliği yapılıyor ve kaydediliyor...")

    #burası her hisse için sırayla veri getirir
    for sembol in hisse_sembolleri: 
        print(f"\n{sembol} için işlemler başliyor...")
        veri = yf.download(sembol, start=baslangic_tarihi, end=bitis_tarihi) #yahoo'dan veri çekip, değişkene kaydet

        if not veri.empty: #eğer veri boş değil ise...
            if isinstance(veri.columns, pd.MultiIndex):         #eğer üst üste binen sütun var ise
                veri.columns = veri.columns.get_level_values(0) # Tertemiz, tek katmanlı başlık!

            #date sütunu index halinden çıkarılır, sütun hale getirilir
            veri.reset_index(inplace=True)
            #bütün sütun isimleri küçük harfe dönüştürülür
            veri.columns = [col.lower() for col in veri.columns]

            #date, open, close, volume
            df = veri.copy() #çağırdığımız DataFrame de ki sütunlar

            #ma50 ma200 rsi target sütunları oluşturma aşaması
#-----------------------------------------------------------------------------------------
            df["ma50"] = df["close"].rolling(window=50).mean()
            df["ma200"] = df["close"].rolling(window=200).mean()

            # 2. 14 Günlük RSI Hesaplaması
            kapanis_farki = df["close"].diff()
            kazanc = kapanis_farki.clip(lower=0)
            kayip = -kapanis_farki.clip(upper=0)

            ort_kazanc = kazanc.ewm(com=13, adjust=False).mean()
            ort_kayip = kayip.ewm(com=13, adjust=False).mean()

            rs = ort_kazanc / np.where(ort_kayip == 0, 0.00001, ort_kayip)
            df["rsi14"] = 100 - (100 / (1 + rs))

            df["yarin_kapanis"] = df["close"].shift(-1)
            df["target"] = (df["yarin_kapanis"] > df["close"]).astype(int)
            df.drop(columns=["yarin_kapanis"], inplace=True)
#------------------------------------------------------------------------------------------------

            #veritabanına yazıyoruz
            tablo_adi = sembol.replace(".", "_")
            df.to_sql(tablo_adi, con=engine, if_exists="replace", index=False)

            print(f" Başarili: {sembol} verileri kaydedildi! (Toplam Satir: {len(df)})")
        else:
            print(f" Hata: {sembol} için veri çekilemedi.")

    print("\nTüm işlemler tamamlandi. Veritabanınız güncel!")

# ==========================================
# 2. ADIM: MODELİ EĞİTME VE KAYDETME
# ==========================================
    print("\n--- Model Eğitim Süreci Başlıyor ---")

    tablo_adi = "ASELS_IS"
    df_model = pd.read_sql(f"SELECT * FROM {tablo_adi}", con=engine)
    df_model.dropna(inplace=True)
    df_model = df_model.sort_values(by="date", ascending=True).reset_index(drop=True)

    ozellikler = ["open", "close", "volume", "ma50", "ma200", "rsi14"]
    X = df_model[ozellikler]
    y = df_model["target"]

    bolme_noktasi = int(len(df_model) * 0.8)
    X_train, X_test = X.iloc[:bolme_noktasi], X.iloc[bolme_noktasi:]
    y_train, y_test = y.iloc[:bolme_noktasi], y.iloc[bolme_noktasi:]

    print(f"-> Eğitim veri boyutu: {X_train.shape[0]} satir")
    print(f"-> Test veri boyutu: {X_test.shape[0]} satir")

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    print("\nModel eğitiliyor...")
    model.fit(X_train, y_train)

    tahminler = model.predict(X_test)
    basari_skoru = accuracy_score(y_test, tahminler)

    print("\n[MODEL SONUÇLARI]")
    print(f"Doğruluk Orani (Accuracy): %{basari_skoru * 100:.2f}")
    print("\nSiniflandirma Raporu:")
    print(classification_report(y_test, tahminler))

    model_dosya_adi = "model.pkl"
    joblib.dump(model, model_dosya_adi)
    print(f"\n Model '{model_dosya_adi}' adiyla başariyla kaydedildi!")