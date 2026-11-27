# AirfoilMatic V0.6.6 Beta — 2B CFD Domain Generator

**Türkçe** | [English](README.en.md)

**[AirfoilMatic'i Tarayıcıda Çalıştır](https://airfoilmatic.streamlit.app/)**

AirfoilMatic, bir kanat profili (NACA 4/5 haneli, UIUC veritabanından seçilmiş 300 profilden biri ya da özel `.dat` dosyası) etrafında 2B CFD akış alanı geometrisi oluşturur ve Ansys DesignModeler `3D Curve` metin formatında dışa aktarır. Akış alanı baştan altı adet dört kenarlı bloğa bölündüğü için Ansys Meshing yapısal (mapped) mesh üretebilir. Uygulama ayrıca bu bloklara uygun mesh ayarlarını (Inflation, Edge Sizing) ve Fluent kurulum değerlerini de verir.

## Özellikler
* NACA 4 ve 5 haneli (standart, refleks olmayan) profiller, NACA denklemlerinden 201 nokta ve tam kosinüs dağılımıyla
* **Profil arama ve rastgele profil:** UIUC Airfoil Coordinates Database'den seçilmiş 300 profil (NACA 6 ve 16 serisi, NASA SC(2)/NLF/LS, Eppler, Selig, Wortmann, Hepperle, Drela, RAE, Delft DU ve diğerleri). Ad yazınca bulunur (`63-215`, `e387`, `clark y`); 🎲 düğmesi kalınlık, kamburluk ve aileye göre filtrelenmiş rastgele bir profil getirir, geri/ileri ile önceki profillere dönülür. Uygulama profil uydurmaz: listede olmayan bir ad için "veritabanında yok" der
* Özel kanat dosyası (`.dat`, `.txt`, `.csv`; Selig ve Lednicer formatları), küt firar kenarının otomatik kapatılması. Birim, orijin ve nokta sırası fark etmez: profil hücum kenarı orijine gelecek şekilde taşınır ve veter uzunluğuna ölçeklenir. Ondalık virgül, `;` ayırıcı, bitişik Fortran sütunları, nokta numarası ya da sabit üçüncü sütun da okunur. Ters yönde çizilmiş profil çevrilir; eğik duran, çok az noktalı ya da bozuk dosyalar için uyarı verilir
* **Olduğu gibi kullan modu:** yüklenen dosyadaki kapalı çizgi sıralaması bozulmadan kullanılır; VG, flap ya da kırık profil gibi x yönünde geri dönen şekiller korunur (yalnızca Inflation iş akışı: ön eksen + iz ekseni; NACA 4412 ile Fluent 2024 R2'de denendi)
* C-Grid ve Dikdörtgen (rüzgar tüneli) domain, 6 adet dört kenarlı blok; domain boyutları veter cinsinden girilir
* Altı bölme çizgisinden hangilerinin dışa aktarılacağını seçme (mapped mesh için altısı da gerekir; quad-dominant + inflation ile altısı ve ön eksen + iz ekseni denendi), çalışmayan tek çizgi seçimi için uyarı
* Domain dışa aktarma: Ansys DesignModeler TXT ve SpaceClaim TXT (ikisi de kullanıcı tarafından denendi; SolidWorks profil çıktısı da)
* **Sadece kanat profili:** domain olmadan üst ve alt yüzey; DesignModeler TXT, SolidWorks ZIP (Curve Through XYZ Points için iki dosya) ve SpaceClaim TXT
* Kenar çubuğunda **m / mm** çıktı birimi (TXT ve profil dosyaları; Fluent mesh dosyası her zaman metre)
* **Fluent mesh dosyası (.msh):** Mapped seçiliyken uygulama C-Grid mesh'i kendisi üretir (Edge Sizing tablosunun bölüm sayıları ve bias'larıyla 6 blok, içleri transfinite interpolasyonla dolu, ön bloklarda ızgara çizgileri duvardan dik çıkar, arka kısmın üstünde ve altında dikey sütunlar (çok kamburlu profillerde uzak sınırdaki ince hücreler için); sınırlar `inlet`, `outlet`, `wall` adlarıyla hazır). DesignModeler ve Meshing gerekmez: Fluent'te File → Read → Mesh. Hücre sayısı ve kalite (skewness, orthogonal quality) uygulamada gösterilir; dosya en çok 1 000 000 hücre olabilir. NACA 4412'de max skewness 0.37, min orthogonal quality 0.84 (Ansys'in aynı tabloyla ürettiği mesh: skewness 0.45). Duvardan dik başlangıç çok kamburlu profillerde burnun arkasındaki ezik hücreleri düzeltir (S9104: skewness 0.90 → 0.64, orthogonal quality 0.05 → 0.54); Fluent 2024 R2'de denendi: NACA 4412'de min orthogonal quality Fluent'te de 0.845, −4…8° Cl önceki mesh'le aynı (8°: 1.22287 / önce 1.22338), Cd %0.2 içinde. Aşağıdaki ilk denemeler önceki mesh'le (max skewness 0.52, orthogonal quality 0.493). Fluent 2024 R2 dosyayı okudu ve Mesh Check'ten hatasız geçirdi; min orthogonal quality 0.493 (önceki mesh; uygulamanın hesabıyla aynı). Fluent'te NACA 4412 −4…8° (SST k-ω, Re 2 × 10⁶) bu mesh'le çözüldü: Cl ve Cd, Ansys'in mesh'iyle %0.01 / %0.05 içinde aynı (0°: Cl 0.41739 ikisinde de). Küt firar kenarlı bir UIUC profili, GA(W)-1 (LS(1)-0417), de bu yolla çözüldü: 91 122 hücre, −4…8° sorusuz yakınsadı, sıfır taşıma açısı −3.87° (ince profil teorisi −4.27°)
* Akış girişi: Reynolds, **Mach + Reynolds + sıcaklık** (pressure-far-field değerleriyle; Sutherland viskozitesi) ya da hız + yoğunluk + viskozite
* **Mesh / y⁺ asistanı:** hedef y⁺ için ilk hücre yüksekliği ve sınır tabaka tahmini; iki çıktı seçeneği: Ansys **Inflation** ayarları (ilk katman, büyüme oranı, maksimum katman sayısı) ya da mapped mesh için **Edge Sizing** tablosu (Number of Divisions + Bias Factor) ve tahmini hücre sayısı
* **Mesh bağımsızlığı:** aynı girişlerden kaba / orta / ince üç Fluent mesh'i tek ZIP'te (hücre boyları √2 oranıyla; kademe başına yaklaşık 2 kat hücre; orta mesh uygulamada gösterilen mesh) ve Otomasyon sekmesinde üç mesh'in Cl / Cd değerlerinden **GCI** hesabı (değerler elle girilir ya da üç mesh'in report file'ları (.out) yüklenir; adlarında coarse / medium / fine geçerse hücre sayıları mesh ailesinden alınır, üç dosyada ortak her açı için ayrı satır; Celik vd. 2008, J. Fluids Eng. 130, 078001: yakınsama mertebesi, mesh'ten bağımsız tahmin, ince mesh belirsizliği; Celik'in örneğiyle aynı sonuç). Fluent 2024 R2'de NACA 4412, 4°'de denendi: Cl 0.8355 / 0.8359 / 0.8353 (kaba / orta / ince), Cd farkı %0.1'den az; varsayılan mesh bu akışta mesh'ten bağımsız
* Ansys bantlarına ve Fluent sınırlarına göre **mesh kalite kontrolü** (skewness, orthogonal quality, aspect ratio)
* İlk Fluent sonucundan **y⁺ düzeltme** ve serbest akış hızı ve hücum açısından inlet X/Y hız bileşenlerini, Lift/Drag vektörlerini ve referans değerleri hesaplayan, Reynolds ve Mach'ı (sıcaklığa göre ses hızıyla) kontrol eden **Fluent ayar yardımcısı**; inlet'ten kanada **türbülans sönümü** (SST)
* **Otomasyon sekmesi:** polar için **hücum açısı taraması** (CSV; eşit aralıklı ya da kendi açı listeniz, ör. 1.3, 2.8, 6.8; Fluent 2024 R2'de 1.99, 4.01, 6.11, 8.08 listesiyle denendi), Fluent journal'ı ve report file'dan **polar** (açı başına son N iterasyonun ortalaması ve aralığı, salınan / az iterasyonlu açıların işaretlenmesi, Cl–α, Cd–α, Cl–Cd grafikleri, CSV; Fluent 2024 R2 report file biçimiyle denendi)
* **Fluent journal:** açı taramasının açıları boyunca `aoa` named expression'ını değiştirip iterasyon koşan bir TUI journal (`.jou`); case `aoa`'yı pressure-far-field akış yönünde ya da velocity-inlet hız bileşenlerinde ve Cl/Cd expression report'larında kullanır, uygulama bu ifadeleri (ve Cl ≈ 0 açısı için `clconv` durma ölçütünü) yazar. Case & data her k açıda bir (son açı her zaman) kaydedilebilir; yarıda kalan tarama son kayıttan sürdürülür (ilk iterasyon elle, Fluent'in yeni dosya sorusuna Yes; polar aracı iki report file'ı birlikte okur). Ansys Fluent 2024 R2'de (standalone) 3 açılı bir taramayla (açı başına 50 iterasyon) ve 11 açılı bir taramayla (−4…16°, Convergence Conditions ile, velocity-inlet case) ve pressure-far-field case'iyle bir taramayla (M 0.3, 2…8°) denendi, kayıttan sürdürme de denendi; Workbench içinde denendi ve çalışmaz (her açı değişikliğinde "Settings have changed" sorusu); case dosyasının üzerine yazma henüz denenmedi
* Türkçe / İngilizce arayüz

## Yerel kurulum
```bash
git clone https://github.com/meceylan/AirfoilMatic.git
cd AirfoilMatic
pip install -r requirements.txt
streamlit run app.py
```
Testleri çalıştırmak için: `pip install pytest` ve ardından `pytest`. `tests/test_app.py` uygulamanın kendisini (Streamlit AppTest ile) tarayıcı olmadan çalıştırır; `tests/test_hard_files.py` bilinen bir profilden üretilmiş 75 zor dosyayı okutup çıkan şekli gerçeğiyle karşılaştırır; `tests/test_database_findings.py` UIUC veritabanının tamamından çıkan hataları (iç içe giren yüzeyler) sınar; `tests/test_library.py` seçkideki her profilden temiz bir domain kurulduğunu ve aramayı sınar.

## Ansys iş akışı
1. **İçe aktarma:** DesignModeler'da önce `Units` menüsünden kenar çubuğunda seçtiğiniz çıktı birimini (m ise `Meter`, mm ise `Millimeter`) seçin, sonra `Concept > 3D Curve` ile indirdiğiniz `.txt` dosyasını seçip `Generate` deyin.
2. **Yüzey:** `Concept > Surfaces from Edges` ile dış sınırları ve kanat kenarlarını seçerek akış yüzeyini oluşturun.
3. **Bölme:** `Tools > Projection` ile dışa aktarılan bölme çizgilerini kullanın.
4. **Mesh:** iki akıştan birini seçin; **Mesh / y⁺** sekmesi ikisinin de ayarlarını verir.
   * **Inflation (quad-dominant):** ön eksen + iz eksenini (ya da altı çizginin hepsini) dışa aktarın; tek çizgi ya da ön eksen olmadan iz ekseni inflation hatası verir. Tüm yüzeylere `Inflation` ekleyin, Boundary olarak kanat kenarlarını **ve iz eksenini** seçin. Genel Element Size'ı yaklaşık 0.5c yapın ve tablodaki Edge Sizing'leri girin. Uygulama firar kenarı elemanını son inflation katmanının en az 1.5 katı (ve en az 0.003c) tutar; aksi halde Ansys inflation'ı oluşturamaz. Sivri firar kenarı kullanın; küt TE + inflation denemelerimizde başarısız oldu.
   * **Mapped:** altı bölme çizgisini de dışa aktarın (6 blok), tüm yüzeylere `Face Meshing` (Mapped) ekleyip tablodaki `Edge Sizing` değerlerini girin. Aynı sayıda bölümü olan duvar-normal kenarlarda bias'lar kenar uzunluğu yüzünden biraz farklıdır; hepsine tek bir değer vermek ilk hücreyi en fazla %2 değiştirir (NACA 4412 denemesinde böyle yapıldı).
   * Inflation ile Mapped Face Meshing aynı yüzeyde birlikte kullanılamaz.
5. **Kontrol:** Hücre sayısını ve Fluent'te y⁺ değerini kontrol edin. Fluent y⁺'ı hücre merkezinde raporladığı için görülen değer hedefin yaklaşık yarısı olur.
6. **Mesh değiştirmek:** Fluent'te kurulu bir case'i yeni bir mesh'e taşımak için case'i okuyup konsola `/mesh/replace` yazın ve dosya adını uzantısıyla verin (`ad.msh`). Zone adları aynıysa (`inlet`, `outlet`, `wall`) sınır koşulları, expression'lar ve report'lar korunur; ardından initialize edin. Fluent 2024 R2'de denendi.

## NACA 0012 ile karşılaştırma
Uygulamanın ürettiği domain ve inflation mesh'i, Ladson'ın rüzgar tüneli verisiyle karşılaştırıldı (NASA TM-4074, Tablo I: M = 0.15, Re = 2 × 10⁶, serbest geçiş, α = 4.25°).

**Kurulum:** c = 1 m, C-Grid (R = 15 m, iz 20 m), ön eksen + iz ekseni, hedef y⁺ = 1. Ansys Fluent 2024 R2, Transition SST, U = 51.04 m/s, ρ = 1.225 kg/m³, μ = 3.126 × 10⁻⁵ Pa·s, girişte Tu = %1 ve viskozite oranı 100. Tüm ayarlar uygulamanın Mesh / y⁺ sekmesinden alındı.

| Mesh | Eleman | Max skewness | Min orth. quality | Cl | Cd |
|---|---|---|---|---|---|
| A (büyüme 1.15) | ~38 500 | 0.62 | 0.62 | 0.4469 | 0.00658 |
| B (büyüme 1.10) | 53 314 | 0.73 | 0.65 | 0.4481 | 0.00647 |
| Ladson (deney) | | | | 0.4450 | 0.00670 |

Cl deneyden %1'den az, Cd %2–3.5 sapıyor; NACA 0012 için farklı rüzgar tünelleri arasındaki dağılım da bu mertebede (McCroskey, NASA TM-100019). Kanat üzerinde y⁺ 0.14–1.14 arasında. Residual'lar 1000 iterasyonda tamamen yakınsadı.

**Sınırlar:** Bu karşılaştırma tek profil, tek açı ve tek Reynolds sayısıyla yapıldı (mapped mesh ve kamburlu profil için aşağıdaki NACA 4412 denemesine bakın). Ladson'ın tünelindeki türbülans seviyesi bilinmiyor ve girişte viskozite oranı 100 seçildi (hücum kenarına yaklaşık %0.43 Tu ulaşıyor); Cd'nin deneye yakınlığı kısmen bu seçime bağlı olabilir. Bu yüzden sonuç "deneyle uyumlu" olarak okunmalı, kesin bir doğrulama sayılmamalı.

**Açı taraması ve stall (SST k-ω, 2026-11):** Aynı mesh (B) ve velocity-inlet case'i tam türbülanslı SST k-ω ile Ladson'ın Tablo IX verisiyle (No. 80 grit, geçiş 0.05c'de sabit, Re 2 × 10⁶) aynı açılarda karşılaştırıldı (uygulamanın journal'ı, kendi açı listesiyle). 0°'de Cd deneyden %2 uzak; 0–15°'de Cl deneyden %2–3.5 yüksek (Ladson, teorinin eğimi deneyden %7'ye kadar yüksek verdiğini ve deneye %2 tünel düzeltmesi uygulandığını yazar); 6–14°'de Cd %7–19 yüksek. Deneyde stall 15–16° arasında. SST ise 16.02°'de bağlı akış verdi (Cl 1.45; deney 1.07) ve 16.99°'de URANS ile de (Δt = 0.01 c/U, 3000 adım) bağlı akışa oturdu (Cl 1.46, Cd 0.045; deney 1.09 / 0.249). Steady çözücünün bu açıdaki salınımı (Cl 0.30–1.35) fiziksel değildi. Sonuç: SST stall açısını ve Cl_max'ı yüksek verir; steady çözümde salınım her zaman stall demek değildir, URANS ile bakın. Transition SST ile steady taramada 8°'den sonra salınım görüldü.

**NACA 4412: mapped mesh ve "olduğu gibi" modu (2026-11):** Kamburlu profil iki bağımsız yoldan kuruldu ve aynı Fluent kurulumuyla (SST k-ω, Re 2 × 10⁶, velocity-inlet, uygulamanın journal'ı) −4, 0, 4, 8°'de çözüldü: (1) profil aramasından, 6 bloklu **mapped mesh** (84 501 quad; uygulamanın tahmini 84 870; max skewness 0.445); (2) Selig `.dat` dosyasından, **"olduğu gibi" modu** + inflation (47 674 eleman; max skewness 0.658). İkinci mesh'e kurulum `/mesh/replace` ile taşındı. İki yol Cl'de %1.5, Cd'de %2 içinde aynı; sıfır taşıma açısı −3.90° ve −3.98° (ince profil teorisi −4.15°, deney ≈ −4°).

## Kapsam
* Mesh planı düşük hız için kurulmuştur (Mach < 0.3). Mach girişi 1.0'a kadar değer alır ve Mach > 0.3'te pressure-far-field önerir, ama sıkıştırılabilir akışa özel bir mesh ayarı vermez. Fluent 2024 R2'de (NACA 0012, 15c C-Grid) pressure-far-field M 0.15'te sıfırdan farklı açıda oturmadı, M 0.3 ve 0.5'te (dış sınırın tamamı far-field, Time Scale Factor 0.2) temiz yakınsadı; düşük Mach'ta velocity-inlet kullanın. Seçkideki RAE ve NASA SC(2) gibi transonik profiller de aynı planla verilir ama şok bölgesi için ayrı bir yol yoktur.
* Domain boyutu (varsayılan 15c): yüksek Cl'de uzak alan sınırı taşıma kuvvetini etkiler. Cl arttıkça yarıçapı büyütüp sonucun değişmediğini kontrol edin.

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

Profil seçkisindeki koordinatlar Prof. Michael S. Selig'in yürüttüğü [UIUC Airfoil Coordinates Database](https://m-selig.ae.illinois.edu/ads/coord_database.html)'den alınmıştır ve uygulamanın MIT lisansına dahil değildir. Seçki `tools/build_airfoil_library.py` ile veritabanından yeniden üretilebilir.
