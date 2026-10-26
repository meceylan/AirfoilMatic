# AirfoilMatic V0.4.2 Beta — 2B CFD Domain Generator

**Türkçe** | [English](README.en.md)

**[AirfoilMatic'i Tarayıcıda Çalıştır](https://airfoilmatic-gkxdkjpsclawjnbhmzng89.streamlit.app/)**

AirfoilMatic, bir kanat profili (NACA 4/5 haneli ya da özel `.dat` dosyası) etrafında 2B CFD akış alanı geometrisi oluşturur ve Ansys DesignModeler `3D Curve` metin formatında dışa aktarır. Akış alanı baştan altı adet dört kenarlı bloğa bölündüğü için Ansys Meshing yapısal (mapped) mesh üretebilir. Uygulama ayrıca bu bloklara uygun Edge Sizing ayarlarını ve mesh bağımsızlığı (GCI) hesabını da verir.

## Özellikler
* NACA 4 ve 5 haneli (standart, refleks olmayan) profiller, tam kosinüs nokta dağılımı
* Özel kanat dosyası (Selig ve Lednicer formatları), küt firar kenarının otomatik kapatılması
* C-Grid ve Dikdörtgen (rüzgar tüneli) domain, 6 adet dört kenarlı blok
* Altı bölme çizgisinden hangilerinin dışa aktarılacağını seçme (mapped mesh için altısı da gerekir; quad-dominant + inflation ile altısı ve ön eksen + iz ekseni denendi), çalışmayan tek çizgi seçimi için uyarı
* Ansys DesignModeler TXT dışa aktarma
* **Mesh / y⁺ asistanı:** hedef y⁺ için ilk hücre yüksekliği ve sınır tabaka tahmini; iki çıktı seçeneği: Ansys **Inflation** ayarları (ilk katman, büyüme oranı, maksimum katman sayısı) ya da mapped mesh için **Edge Sizing** tablosu (Number of Divisions + Bias Factor) ve tahmini hücre sayısı
* Ansys bantlarına ve Fluent sınırlarına göre **mesh kalite kontrolü** (skewness, orthogonal quality, aspect ratio)
* İlk Fluent sonucundan **y⁺ düzeltme** ve serbest akış hızı ve hücum açısından inlet X/Y hız bileşenlerini, Lift/Drag vektörlerini ve referans değerleri hesaplayan, Reynolds ve Mach'ı kontrol eden **Fluent ayar yardımcısı**
* **Mesh bağımsızlığı:** Grid Convergence Index hesabı (Celik vd., 2008), Cl/Cd yakınsama grafiği ve isteğe bağlı önerilen ağ ailesi
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
   * **Inflation (quad-dominant):** altı çizginin hepsini ya da ön eksen + iz eksenini dışa aktarın (denenmiş seçimler; tek bir çizgi yüzün içinde yarık olarak kalır ve başarısız olur). Tüm yüzeylere `Inflation` ekleyin, Boundary olarak kanat kenarlarını seçin (iz eksenini isteğe bağlı olarak da), genel Element Size'ı yaklaşık 0.5c yapın ve tablodaki Edge Sizing'leri Behavior = Soft ile ekleyin (inflation olan kenarlarda Hard desteklenmez). Firar kenarındaki elemanı yaklaşık 0.003c veya daha büyük tutun: Ansys 2024 R2 denemelerimizde (c = 1 m) yaklaşık 1 mm başarısız oldu, yaklaşık 3 mm çalıştı. Sivri firar kenarı kullanın; küt TE + inflation denemelerimizde başarısız oldu. Mesh atmadan önce Bounding Box Diagonal'ın onlarca metre mertebesinde olduğunu kontrol edin.
   * **Mapped:** altı bölme çizgisini de dışa aktarın (6 blok), tüm yüzeylere `Face Meshing` (Mapped) ekleyip tablodaki `Edge Sizing` değerlerini girin.
   * Inflation ile Mapped Face Meshing aynı yüzeyde birlikte kullanılamaz.
5. **Kontrol:** Hücre sayısını ve Fluent'te y⁺ değerini kontrol edin. Fluent y⁺'ı hücre merkezinde raporladığı için görülen değer hedefin yaklaşık yarısı olur.

## Mesh bağımsızlığı (GCI)
Bir mesh'in yeterli olup olmadığını hücre sayısı tek başına göstermez. Mesh inceltildiğinde sonucun çok az değiştiğini göstermek gerekir. **Mesh Bağımsızlığı** sekmesi:
1. Üç Fluent koşusunun hücre sayılarını ve Cl/Cd sonuçlarını alır,
2. Celik vd. (2008) yöntemine göre görünür mertebe *p*, ekstrapole değer ve GCI_ince değerlerini raporlar; salınımlı veya ıraksayan davranışta uyarır,
3. Cl ve Cd'yi h = 1/√N'ye karşı Richardson eğrisi ve ekstrapole değerle birlikte çizer,
4. İsteğe bağlı olarak tutarlı bir ağ ailesi önerir (varsayılan inceltme oranı her yönde √2, her seviyede yaklaşık 2 kat hücre).

Kaynak: Celik, I. B., Ghia, U., Roache, P. J., Freitas, C. J., Coleman, H., Raad, P. E., *Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications*, J. Fluids Eng. 130(7), 078001, 2008.

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
