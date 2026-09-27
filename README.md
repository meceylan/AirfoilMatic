# ✈️ AirfoilMatic V0.3 Beta — 2B CFD Domain Generator

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

## ⚙️ Nasıl Kullanılır? (Ansys İş Akışı)
AirfoilMatic'ten indirdiğiniz `.txt` dosyasını Ansys ortamında 2B Mapped Mesh (Yapısal Ağ) kalitesinde bir CFD alanına dönüştürmek için şu adımları izleyin:
1. **İçe Aktarma:** Ansys DesignModeler'ı açın. `Concept > 3D Curve` yolunu izleyin. Koordinat dosyası olarak indirdiğiniz `.txt` dosyasını seçip `Generate` tuşuna basın.
2. **Yüzey Oluşturma:** `Concept > Surfaces from Edges` aracını seçin. Dış akış sınırlarını ve kanat profili çizgilerini seçerek ana akış yüzeyini (Surface) oluşturun (`Generate`).
3. **Yüzey Bölme (Face Split):** Kanadın etrafındaki 4-bölgeli topolojiyi oluşturmak için `Tools > Face Split` komutunu kullanın. Kesici araç (Tool Geometry) olarak dikey kesme çizgilerini ve yatay iz (wake) çizgisini seçin. Yüzeyi parçalara ayırın.
4. ART (Akışkan) yüzeylerinizi oluşturup Ansys Meshing'e geçtiğinizde, tüm alanların 4 kenarlı (Quadrilateral) olduğunu ve `Mapped Face Meshing` için %100 uyumlu olduğunu göreceksiniz.

## 🧠 Teknik Arka Plan ve Topoloji (Neden X = 0.3c?)
Klasik CFD ön-işlem yöntemlerinde kanat profili tek bir eğri veya hücum/firar kenarından ayrılmış iki parça olarak sisteme aktarıldığında, Ansys DesignModeler yüzey oluşturma aşamasında hücum kenarında dar açılı hatalı yüzeyler (sliver face) üretebilmektedir. Bu durum ağ kalitesini (skewness ve orthogonal quality) olumsuz etkiler.

AirfoilMatic, geometriyi matematiksel olarak tam **X = 0.3c** (kord uzunluğunun %30'u) noktasından dikey olarak 4 ayrı segmente (Üst-Ön, Üst-Arka, Alt-Ön, Alt-Arka) ayırır. Bunun temel mühendislik gerekçeleri şunlardır:

1. **Maksimum Kalınlık Konumu:** Birçok standart aerodinamik profilin (örn. NACA 4-digit) maksimum kalınlığı 0.3c civarında gerçekleşir. Geometriyi bu noktadan bölmek, hücum kenarının yüksek eğriliğe (curvature) sahip bölgelerini izole eder.
2. **Sliver Face Önleme:** Dikey ayrım çizgisi sayesinde akış alanı, dış sınırlara dik açılarla bağlanır. Bu sayede kesişim noktalarında oluşabilecek geçersiz topoloji (invalid topology) hataları engellenir.
3. **Yapısal Ağ (Structured Mesh) Geçişi:** Bu 4 bölgeli ayrım, Ansys Meshing modülünde hücum kenarını saran radyal ağ yapısı (C-Grid) ile firar kenarı ve iz bölgesine uzanan doğrusal ağ yapısı (H-Grid) arasında H-Grid / C-Grid hibrit geçişini standartlaştırır. Sonuç olarak tüm alanlar, Mapped Face Meshing için gerekli olan 4-kenarlı (Quadrilateral) formata zorlanmış olur.
