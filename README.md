# ✈️ AirfoilMatic V0.2 Beta — 2B CFD Domain Generator

**AirfoilMatik**, NACA 4 ve 5 haneli kanat profillerini veya özel kanat dosyalarını (.dat / .txt) kullanarak 2 boyutlu CFD akış alanı (domain) geometrisi oluşturan interaktif bir web uygulamasıdır.

## 🚀 Özellikler

- **NACA 4-Digit ve 5-Digit** kanat profili hesaplama
- **Özel kanat dosyası yükleme** (Selig ve Lednicer formatları desteklenir)
- **C-Grid** ve **Dikdörtgen (Rüzgar Tüneli)** domain tipleri
- **Yakın çekim** ve **uzak çekim** interaktif Plotly grafikleri
- **Ansys uyumlu TXT dışa aktarma** (nokta koordinatları)
- Küt firar kenarı (Blunt TE) otomatik algılama ve kapatma

## 📦 Kurulum (Yerel Çalıştırma)

```bash
# 1. Depoyu klonlayın
git clone https://github.com/<kullanici-adi>/AirfoilMatik.git
cd AirfoilMatik

# 2. Sanal ortam oluşturun (önerilir)
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Uygulamayı çalıştırın
streamlit run app.py
```

Uygulama varsayılan olarak `http://localhost:8501` adresinde açılır.

## ☁️ Streamlit Community Cloud'da Yayınlama

1. Bu depoyu GitHub'a push edin.
2. [share.streamlit.io](https://share.streamlit.io) adresine gidin.
3. GitHub hesabınızı bağlayın ve bu repoyu seçin.
4. **Main file path** olarak `app.py` belirtin.
5. **Deploy** butonuna tıklayın.

> Streamlit Community Cloud, `requirements.txt` dosyasını otomatik olarak okuyarak bağımlılıkları yükler.

## 🛠️ Teknoloji

| Bileşen | Teknoloji |
|---|---|
| Framework | [Streamlit](https://streamlit.io) |
| Hesaplama | [NumPy](https://numpy.org) |
| Görselleştirme | [Plotly](https://plotly.com/python/) |
| Dil | Python 3.8+ |

## 📄 Lisans

Bu proje açık kaynak olarak paylaşılmıştır.
