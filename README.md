# AirfoilMatic V0.5.3.4 Beta — 2B CFD Domain Generator

**Türkçe** | [English](README.en.md)

**[AirfoilMatic'i Tarayıcıda Çalıştır](https://airfoilmatic-gkxdkjpsclawjnbhmzng89.streamlit.app/)**

AirfoilMatic, bir kanat profili (NACA 4/5 haneli ya da özel `.dat` dosyası) etrafında 2B CFD akış alanı geometrisi oluşturur ve Ansys DesignModeler `3D Curve` metin formatında dışa aktarır. Akış alanı baştan altı adet dört kenarlı bloğa bölündüğü için Ansys Meshing yapısal (mapped) mesh üretebilir. Uygulama ayrıca bu bloklara uygun mesh ayarlarını (Inflation, Edge Sizing) ve Fluent kurulum değerlerini de verir.

## Özellikler
* NACA 4 ve 5 haneli (standart, refleks olmayan) profiller, tam kosinüs nokta dağılımı
* Özel kanat dosyası (Selig ve Lednicer formatları), küt firar kenarının otomatik kapatılması
* C-Grid ve Dikdörtgen (rüzgar tüneli) domain, 6 adet dört kenarlı blok
* Altı bölme çizgisinden hangilerinin dışa aktarılacağını seçme (mapped mesh için altısı da gerekir; quad-dominant + inflation ile altısı ve ön eksen + iz ekseni denendi), çalışmayan tek çizgi seçimi için uyarı
* Ansys DesignModeler TXT dışa aktarma
* **Mesh / y⁺ asistanı:** hedef y⁺ için ilk hücre yüksekliği ve sınır tabaka tahmini; iki çıktı seçeneği: Ansys **Inflation** ayarları (ilk katman, büyüme oranı, maksimum katman sayısı) ya da mapped mesh için **Edge Sizing** tablosu (Number of Divisions + Bias Factor) ve tahmini hücre sayısı
* Ansys bantlarına ve Fluent sınırlarına göre **mesh kalite kontrolü** (skewness, orthogonal quality, aspect ratio)
* İlk Fluent sonucundan **y⁺ düzeltme** ve serbest akış hızı ve hücum açısından inlet X/Y hız bileşenlerini, Lift/Drag vektörlerini ve referans değerleri hesaplayan, Reynolds ve Mach'ı kontrol eden **Fluent ayar yardımcısı**
* Türkçe / İngilizce arayüz

## Yerel kurulum
```bash
git clone https://github.com/meceylan/AirfoilMatic.git
cd AirfoilMatic
pip install -r requirements.txt
streamlit run app.py
```
Testleri çalıştırmak için: `pip install pytest` ve ardından `pytest`.

## Ansys iş akışı
1. **İçe aktarma:** DesignModeler'da önce `Units > Meter` seçin, sonra `Concept > 3D Curve` ile indirdiğiniz `.txt` dosyasını seçip `Generate` deyin.
2. **Yüzey:** `Concept > Surfaces from Edges` ile dış sınırları ve kanat kenarlarını seçerek akış yüzeyini oluşturun.
3. **Bölme:** `Tools > Projection` ile dışa aktarılan bölme çizgilerini kullanın.
4. **Mesh:** iki akıştan birini seçin; **Mesh / y⁺** sekmesi ikisinin de ayarlarını verir.
   * **Inflation (quad-dominant):** ön eksen + iz eksenini (ya da altı çizginin hepsini) dışa aktarın; tek çizgi ya da ön eksen olmadan iz ekseni inflation hatası verir. Tüm yüzeylere `Inflation` ekleyin, Boundary olarak kanat kenarlarını **ve iz eksenini** seçin. Genel Element Size'ı yaklaşık 0.5c yapın ve tablodaki Edge Sizing'leri girin. Uygulama firar kenarı elemanını son inflation katmanının en az 1.5 katı (ve en az 0.003c) tutar; aksi halde Ansys inflation'ı oluşturamaz. Sivri firar kenarı kullanın; küt TE + inflation denemelerimizde başarısız oldu.
   * **Mapped:** altı bölme çizgisini de dışa aktarın (6 blok), tüm yüzeylere `Face Meshing` (Mapped) ekleyip tablodaki `Edge Sizing` değerlerini girin.
   * Inflation ile Mapped Face Meshing aynı yüzeyde birlikte kullanılamaz.
5. **Kontrol:** Hücre sayısını ve Fluent'te y⁺ değerini kontrol edin. Fluent y⁺'ı hücre merkezinde raporladığı için görülen değer hedefin yaklaşık yarısı olur.

## Doğrulama: NACA 0012
Uygulamanın ürettiği domain ve inflation mesh'i, Ladson'ın rüzgar tüneli verisiyle karşılaştırıldı (NASA TM-4074, Tablo I: M = 0.15, Re = 2 × 10⁶, serbest geçiş, α = 4.25°).

**Kurulum:** c = 1 m, C-Grid (R = 15 m, iz 20 m), ön eksen + iz ekseni, hedef y⁺ = 1. Ansys Fluent 2024 R2, Transition SST, U = 51.04 m/s, ρ = 1.225 kg/m³, μ = 3.126 × 10⁻⁵ Pa·s, girişte Tu = %1 ve viskozite oranı 100. Tüm ayarlar uygulamanın Mesh / y⁺ sekmesinden alındı.

| Mesh | Eleman | Max skewness | Min orth. quality | Cl | Cd |
|---|---|---|---|---|---|
| A (büyüme 1.15) | ~38 500 | 0.62 | 0.62 | 0.4469 | 0.00658 |
| B (büyüme 1.10) | 53 314 | 0.73 | 0.65 | 0.4481 | 0.00647 |
| Ladson (deney) | | | | 0.4450 | 0.00670 |

Cl deneyden %1'den az, Cd %2–3.5 sapıyor; NACA 0012 için farklı rüzgar tünelleri arasındaki dağılım da bu mertebede (McCroskey, NASA TM-100019). Kanat üzerinde y⁺ 0.14–1.14 arasında. Residual'lar 1000 iterasyonda tamamen yakınsadı.

## Neden X = 0.3c?
Kanat DesignModeler'a tek bir eğri olarak ya da yalnızca hücum ve firar kenarından bölünmüş iki eğri olarak aktarıldığında, yüzey oluşturma sırasında hücum kenarında dar açılı hatalı yüzeyler (sliver face) oluşabilir. Bu da mesh kalitesini düşürür.

AirfoilMatic kanadı **X = 0.3c** noktasından dikey olarak dört parçaya (üst-ön, üst-arka, alt-ön, alt-arka) böler:
1. **Eğriliğin ayrılması:** Birçok profilin maksimum kalınlığı 0.3c civarındadır. Buradan bölmek, eğriliği yüksek hücum kenarı bölgesini ayırır.
2. **Sliver face oluşmaz:** Dikey bölme çizgileri dış sınırlara dik açıyla bağlanır, kesişimlerde geçersiz topoloji oluşmaz.
3. **Mapped mesh:** Tüm bloklar dört kenarlıdır (dikdörtgen domain'de ön bloklar için Side vertex gerekir). C-Grid'de giriş yayının merkezi bölme çizgisindedir; yay, dikey çizgilerin dış sınıra değdiği noktada biter ve 0.3c'nin önünde kısa bir düz parça kalmaz.

## Teknoloji
| Bileşen | Teknoloji |
|---|---|
| Framework | Streamlit |
| Hesaplama | NumPy |
| Görselleştirme | Plotly |
| Dil | Python 3.11+ |

## Geliştirici
**Muhammet Emin CEYLAN**, İskenderun Teknik Üniversitesi  
[LinkedIn](https://www.linkedin.com/in/muhammet-emin-ceylan-b79847334) · [GitHub](https://github.com/meceylan)

Hata ve önerileriniz için [Issues](https://github.com/meceylan/AirfoilMatic/issues) sayfasını kullanabilirsiniz.

## Lisans
MIT Lisansı. Arayüz yazı tipi Source Serif 4, SIL Open Font License 1.1 ile dağıtılır (`static/fonts/OFL-SourceSerif4.txt`).
