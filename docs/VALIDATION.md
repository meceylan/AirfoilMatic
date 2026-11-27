# AirfoilMatic — Ansys / Fluent denemeleri

**Türkçe** | [English](VALIDATION.en.md) · [README'ye dön](../README.md)

Bu sayfa, uygulamanın çıktılarının Ansys / Fluent'te nasıl denendiğini toplar. Burada "denendi" yazmayan hiçbir şey denenmiş sayılmamalıdır. Bütün Fluent koşuları Ansys Fluent 2024 R2 ile yapıldı.

## İçindekiler
- [Henüz denenmeyenler](#henüz-denenmeyenler)
- [Uygulamanın Fluent mesh dosyası (.msh)](#uygulamanın-fluent-mesh-dosyası-msh)
- [NACA 0012 ile karşılaştırma](#naca-0012-ile-karşılaştırma)
- [NACA 4412: mapped mesh ve "olduğu gibi" modu](#naca-4412-mapped-mesh-ve-olduğu-gibi-modu)
- [Mesh bağımsızlığı (GCI)](#mesh-bağımsızlığı-gci)
- [Fluent journal'ı ve açı taraması](#fluent-journalı-ve-açı-taraması)
- [Diğer çıktılar](#diğer-çıktılar)
- [Kapsam](#kapsam)
- [Neden X = 0.3c?](#neden-x--03c)

## Henüz denenmeyenler
* Journal'da case dosyasının üzerine yazma henüz denenmedi.
* Yalnız profil için DesignModeler TXT henüz denenmedi (domain TXT'si denendi).
* Journal Workbench içinde denendi ve çalışmaz (her açı değişikliğinde "Settings have changed" sorusu; "current and future calculations" seçilse de yeniden soruyor); standalone Fluent kullanın.

## Uygulamanın Fluent mesh dosyası (.msh)
Mapped seçiliyken uygulama C-Grid ya da dikdörtgen domain'in mesh'ini kendisi üretir: Edge Sizing tablosunun bölüm sayıları ve bias'larıyla 6 blok, içleri transfinite interpolasyonla dolu; sınırlar `inlet`, `outlet`, `wall` adlarıyla hazır. DesignModeler ve Meshing gerekmez: Fluent'te File → Read → Mesh. Hücre sayısı ve kalite (skewness, orthogonal quality) uygulamada gösterilir; dosya en çok 1 000 000 hücre olabilir.

**Mesh'in yapısı**
* Ön bloklarda ızgara çizgileri duvardan dik çıkar: NACA 4412'de max skewness 0.37, min orthogonal quality 0.84 (Ansys'in aynı tabloyla ürettiği mesh: skewness 0.45); Fluent 2024 R2'de denendi: min orthogonal quality Fluent'te de 0.845, −4…8° Cl önceki mesh'le aynı (8°: 1.22287 / önce 1.22338), Cd %0.2 içinde. Çok kamburlu profillerde burnun arkasındaki ezik hücreleri düzeltir (S9104 burunda: skewness 0.90 → 0.64, orthogonal quality 0.05 → 0.54; tüm mesh'te en kötüsü artık firar kenarında, 0.73 / 0.41).
* Ön eksen hücum kenarından duvar normaliyle çıkıp bir veter içinde yataya döner (yüksek Re'de hücum kenarı köşesi için). Fluent 2024 R2'de denendi: NACA 4412 min orthogonal quality 0.895, −4…8° Cl önceki mesh'le aynı (8°: 1.22288).
* Arka kısmın üstünde ve altında dikey sütunlar (çok kamburlu profillerde uzak sınırdaki ince hücreler için); bükülmüş eksenli NACA 4412 denemesindeki mesh'te vardı, yani onunla birlikte denendi.

**İlk denemeler (önceki mesh: max skewness 0.52, orthogonal quality 0.493)**
* Fluent 2024 R2 dosyayı okudu ve Mesh Check'ten hatasız geçirdi; min orthogonal quality 0.493 (uygulamanın hesabıyla aynı).
* NACA 4412 −4…8° (SST k-ω, Re 2 × 10⁶) bu mesh'le çözüldü: Cl ve Cd, Ansys'in mesh'iyle %0.01 / %0.05 içinde aynı (0°: Cl 0.41739 ikisinde de).
* Küt firar kenarlı bir UIUC profili, GA(W)-1 (LS(1)-0417), de bu yolla çözüldü: 91 122 hücre, −4…8° sorusuz yakınsadı, sıfır taşıma açısı −3.87° (ince profil teorisi −4.27°).

**Dikdörtgen domain:** Fluent 2024 R2'de denendi: NACA 4412 −4…8°, Cl C-Grid'le %0.2 içinde, 8°: 1.22537; Cd 8°'de %1.6 düşük, büyük olasılıkla domain biçiminden (ayrıca sınanmadı).

## NACA 0012 ile karşılaştırma
Uygulamanın ürettiği domain ve inflation mesh'i, Ladson'ın rüzgar tüneli verisiyle karşılaştırıldı (NASA TM-4074, Tablo I: M = 0.15, Re = 2 × 10⁶, serbest geçiş, α = 4.25°).

**Kurulum:** c = 1 m, C-Grid (R = 15 m, iz 20 m), ön eksen + iz ekseni, hedef y⁺ = 1. Ansys Fluent 2024 R2, Transition SST, U = 51.04 m/s, ρ = 1.225 kg/m³, μ = 3.126 × 10⁻⁵ Pa·s, girişte Tu = %1 ve viskozite oranı 100. Tüm ayarlar uygulamanın Mesh / y⁺ sekmesinden alındı.

| Mesh | Eleman | Max skewness | Min orth. quality | Cl | Cd |
|---|---|---|---|---|---|
| A (büyüme 1.15) | ~38 500 | 0.62 | 0.62 | 0.4469 | 0.00658 |
| B (büyüme 1.10) | 53 314 | 0.73 | 0.65 | 0.4481 | 0.00647 |
| Ladson (deney) | | | | 0.4450 | 0.00670 |

Cl deneyden %1'den az, Cd %2–3.5 sapıyor; NACA 0012 için farklı rüzgar tünelleri arasındaki dağılım da bu mertebede (McCroskey, NASA TM-100019). Kanat üzerinde y⁺ 0.14–1.14 arasında. Residual'lar 1000 iterasyonda tamamen yakınsadı.

**Sınırlar:** Bu karşılaştırma tek profil, tek açı ve tek Reynolds sayısıyla yapıldı. Ladson'ın tünelindeki türbülans seviyesi bilinmiyor ve girişte viskozite oranı 100 seçildi (hücum kenarına yaklaşık %0.43 Tu ulaşıyor); Cd'nin deneye yakınlığı kısmen bu seçime bağlı olabilir. Bu yüzden sonuç "deneyle uyumlu" olarak okunmalı, kesin bir doğrulama sayılmamalı.

**Açı taraması ve stall (SST k-ω, 2026-11):** Aynı mesh (B) ve velocity-inlet case'i tam türbülanslı SST k-ω ile Ladson'ın Tablo IX verisiyle (No. 80 grit, geçiş 0.05c'de sabit, Re 2 × 10⁶) aynı açılarda karşılaştırıldı (uygulamanın journal'ı, kendi açı listesiyle). 0°'de Cd deneyden %2 uzak; 0–15°'de Cl deneyden %2–3.5 yüksek (Ladson, teorinin eğimi deneyden %7'ye kadar yüksek verdiğini ve deneye %2 tünel düzeltmesi uygulandığını yazar); 6–14°'de Cd %7–19 yüksek. Deneyde stall 15–16° arasında. SST ise 16.02°'de bağlı akış verdi (Cl 1.45; deney 1.07) ve 16.99°'de URANS ile de (Δt = 0.01 c/U, 3000 adım) bağlı akışa oturdu (Cl 1.46, Cd 0.045; deney 1.09 / 0.249). Steady çözücünün bu açıdaki salınımı (Cl 0.30–1.35) fiziksel değildi. Sonuç: SST stall açısını ve Cl_max'ı yüksek verir; steady çözümde salınım her zaman stall demek değildir, URANS ile bakın. Transition SST ile steady taramada 8°'den sonra salınım görüldü.

## NACA 4412: mapped mesh ve "olduğu gibi" modu
2026-11. Kamburlu profil iki bağımsız yoldan kuruldu ve aynı Fluent kurulumuyla (SST k-ω, Re 2 × 10⁶, velocity-inlet, uygulamanın journal'ı) −4, 0, 4, 8°'de çözüldü: (1) profil aramasından, 6 bloklu **mapped mesh** (84 501 quad; uygulamanın tahmini 84 870; max skewness 0.445); (2) Selig `.dat` dosyasından, **"olduğu gibi" modu** + inflation (47 674 eleman; max skewness 0.658). İkinci mesh'e kurulum `/mesh/replace` ile taşındı. İki yol Cl'de %1.5, Cd'de %2 içinde aynı; sıfır taşıma açısı −3.90° ve −3.98° (ince profil teorisi −4.15°, deney ≈ −4°). Mapped mesh'te duvar-normal kenarlara tek bias verildi (ilk hücreyi en fazla %2 değiştirir).

## Mesh bağımsızlığı (GCI)
Aynı girişlerden kaba / orta / ince üç Fluent mesh'i (hücre boyları √2 oranıyla; kademe başına yaklaşık 2 kat hücre; orta mesh uygulamada gösterilen mesh). GCI, Celik vd. 2008 (J. Fluids Eng. 130, 078001) yöntemiyle; Celik'in örneğiyle aynı sonucu verir. Fluent 2024 R2'de NACA 4412, 4°'de denendi: Cl 0.8355 / 0.8359 / 0.8353 (kaba / orta / ince), Cd farkı %0.1'den az; varsayılan mesh bu akışta mesh'ten bağımsız.

## Fluent journal'ı ve açı taraması
* Ansys Fluent 2024 R2'de (standalone) 3 açılı bir taramayla (açı başına 50 iterasyon), 11 açılı bir taramayla (−4…16°, Convergence Conditions ile, velocity-inlet case) ve pressure-far-field case'iyle bir taramayla (M 0.3, 2…8°) denendi; kayıttan sürdürme de denendi.
* Kendi açı listesi 1.99, 4.01, 6.11, 8.08 ile denendi.
* Polar aracı Fluent 2024 R2 report file biçimiyle denendi.
* Workbench içinde denendi ve çalışmaz; case dosyasının üzerine yazma henüz denenmedi.

## Diğer çıktılar
* DesignModeler TXT ve SpaceClaim TXT: ikisi de kullanıcı tarafından denendi; SolidWorks profil çıktısı da.
* "Olduğu gibi" modu (yalnızca Inflation iş akışı: ön eksen + iz ekseni): NACA 4412 ile Fluent 2024 R2'de denendi.
* Bölme çizgileri: mapped mesh için altısı da gerekir; quad-dominant + inflation ile altısı ve ön eksen + iz ekseni denendi.
* `/mesh/replace` ile kurulu case'i yeni mesh'e taşımak: Fluent 2024 R2'de denendi.

## Kapsam
* Mesh planı düşük hız için kurulmuştur (Mach < 0.3). Mach girişi 1.0'a kadar değer alır ve Mach > 0.3'te pressure-far-field önerir, ama sıkıştırılabilir akışa özel bir mesh ayarı vermez. Fluent 2024 R2'de (NACA 0012, 15c C-Grid) pressure-far-field M 0.15'te sıfırdan farklı açıda oturmadı, M 0.3 ve 0.5'te (dış sınırın tamamı far-field, Time Scale Factor 0.2) temiz yakınsadı; düşük Mach'ta velocity-inlet kullanın. Seçkideki RAE ve NASA SC(2) gibi transonik profiller de aynı planla verilir ama şok bölgesi için ayrı bir yol yoktur.
* Domain boyutu (varsayılan 15c): yüksek Cl'de uzak alan sınırı taşıma kuvvetini etkiler. Cl arttıkça yarıçapı büyütüp sonucun değişmediğini kontrol edin.

## Neden X = 0.3c?
Kanat DesignModeler'a tek bir eğri olarak ya da yalnızca hücum ve firar kenarından bölünmüş iki eğri olarak aktarıldığında, yüzey oluşturma sırasında hücum kenarında dar açılı hatalı yüzeyler (sliver face) oluşabilir. Bu da mesh kalitesini düşürür. AirfoilMatic kanadı **X = 0.3c** noktasından dikey olarak dört parçaya (üst-ön, üst-arka, alt-ön, alt-arka) böler:
1. **Eğriliğin ayrılması:** Birçok profilin maksimum kalınlığı 0.3c civarındadır. Buradan bölmek, eğriliği yüksek hücum kenarı bölgesini ayırır.
2. **Sliver face oluşmaz:** Dikey bölme çizgileri dış sınırlara dik açıyla bağlanır, kesişimlerde geçersiz topoloji oluşmaz.
3. **Mapped mesh:** Tüm bloklar dört kenarlıdır (dikdörtgen domain'de ön bloklar için Side vertex gerekir). C-Grid'de giriş yayının merkezi bölme çizgisindedir; yay, dikey çizgilerin dış sınıra değdiği noktada biter ve 0.3c'nin önünde kısa bir düz parça kalmaz.
