# ✈️ AirfoilMatic V0.2 Beta — 2B CFD Domain Generator

**[AirfoilMatic'i Tarayıcıda Çalıştır](https://airfoilmatik-rycmt6quqjnkbrqw48yeec.streamlit.app/)**

AirfoilMatik, NACA 4 ve 5 haneli kanat profillerini veya özel kanat dosyalarını (.dat / .txt) kullanarak 2 boyutlu CFD akış alanı (domain) geometrisi oluşturan interaktif bir web uygulamasıdır.

## 🚀 Özellikler
* NACA 4-Digit ve 5-Digit kanat profili hesaplama
* Özel kanat dosyası yükleme (Selig ve Lednicer formatları desteklenir)
* C-Grid ve Dikdörtgen (Rüzgar Tüneli) domain tipleri
* Yakın çekim ve uzak çekim interaktif Plotly grafikleri
* Ansys uyumlu TXT dışa aktarma (nokta koordinatları)
* Küt firar kenarı (Blunt TE) otomatik algılama ve kapatma

## 📦 Kurulum (Yerel Çalıştırma)

**1. Depoyu klonlayın**
```bash
git clone https://github.com/meceylan/AirfoilMatik.git
cd AirfoilMatik
```

**2. Bağımlılıkları yükleyin**
```bash
pip install -r requirements.txt
```

**3. Uygulamayı çalıştırın**
```bash
streamlit run app.py
```

## 🛠️ Teknoloji

| Bileşen | Teknoloji |
|---|---|
| Framework | Streamlit |
| Hesaplama | NumPy |
| Görselleştirme | Plotly |
| Dil | Python 3.8+ |

## 📄 Lisans

Bu proje MIT Lisansı altında açık kaynak olarak paylaşılmıştır.
