# Changelog

## V0.6.6 Beta

An angle-of-attack sweep journal for Fluent, tried on an 11-angle NACA 0012 sweep against Ladson's data, and the fixes from an independent code review.

- **Section library: 300 sections (was 200).** Rebuilt from the current UIUC database (coord_seligFmt.zip, February 2026; the coordinates of the sections already in the library are unchanged) with the same quality rules, the family quotas scaled by 1.5. Every section of the old 200 is kept. The undashed 6-series files are no longer skipped, so the real symmetric 64-012 and 64-015 are in the library (searching "64012" finds them). `tools/build_airfoil_library.py` takes `--target N` for another size; with 500 the small families run out and the same section enters twice under two file names, so 300 was chosen.
- **Automation tab.** A third tab collects everything for running many angles: the angle-of-attack sweep table (moved from the Fluent helper on the Mesh / y⁺ tab, which keeps the single-angle helper and the turbulence decay), the Fluent journal and the new polar.
- **Polar from the report file.** Upload the report file (.out) Fluent wrote during the sweep. The columns are found by name (Fluent writes them in alphabetical order; angle, Cl and Cd can also be picked by hand), the angle column is read in radians by default (an expression report of a [deg] expression is written in radians) or in degrees. Each angle is the block of iterations in which it stays the same; the table gives the mean of the last N iterations (default 50), the max – min range of Cl and Cd over them, Cl/Cd, the iteration range and a status: steady, oscillating (Cl moves more than 1e-3 or Cd more than 1 % over the last N iterations; both limits adjustable) or few iterations. If an angle was run again later the latest block is used, and iterations written twice by a sweep continued from a saved case use the later lines. Cl–α, Cd–α and Cl–Cd charts with the range as error bars, and a CSV. Tried with the report file of the 11-angle NACA 0012 sweep (Fluent 2024 R2): −4…6° steady, 8–16° oscillating, as in the table worked out by hand; at 10° the mean of the last 50 iterations gives Cl 1.043, Cd 0.0131 (Ladson 10.15°: 1.045, 0.0135) where the last value was 1.056.
- **Fluent journal.** On the Automation tab, under the angle sweep table (angles always run from the smallest to the largest), there is a download of a Fluent TUI journal (`.jou`) and a list of what the case needs. You set up the case in Fluent yourself: a named expression `aoa` (the angle), the pressure-far-field flow direction X = `cos(aoa)`, Y = `sin(aoa)` or the velocity-inlet components `U [m s^-1]*cos(aoa)`, `U [m s^-1]*sin(aoa)`, and Cl and Cd as expression report definitions that use `aoa` (the app prints the exact expressions with your density, speed and chord; report files should hold only expression reports and the moment, because a changed force-vector lift/drag report makes Fluent ask a question about its file, and inside a journal the next line becomes the answer). Residual convergence checks off; set `aoa` to the first angle, initialise and run at least one iteration yourself. At each angle the journal only changes the expression (`/define/named-expressions/edit aoa definition "6 [deg]" q`), runs the chosen number of iterations (default 1000) and continues from the previous solution. Inputs: iterations per angle (an upper limit: with Convergence Conditions in the case, Fluent ends an angle early and the journal goes on to the next one), expression name, how often case and data are saved (every k angles, the last angle always; 0 = only the last angle) and the save folder. The setup list also gives `clconv` = Cl + 1, an expression report to use instead of Cl in Convergence Conditions: Fluent's criterion is a relative change, so at an angle where Cl ≈ 0 (a symmetric profile at 0°) it is never met and the angle runs to the iteration limit (seen in the 11-angle sweep); Cl + 1 stays near 1, so its relative change is the absolute change of Cl. Tried in Fluent 2024 R2: at 0° the angle stopped by itself after 366 iterations with the same Cl and Cd as the 2000-iteration run. To continue a stopped sweep: read the last saved case and data, set the first angle to the next angle and download a new journal (not tried yet). Cl and Cd come from the report files, one block of iterations per angle. Tried in Ansys Fluent 2024 R2 (standalone, 2D): the edit command, the Cl/Cd expressions (same values as Fluent's force reports to about 1e-6) and the report files (no question asked after changing the expression). A 3-angle sweep (−2°, 0°, 2°, 50 iterations each) ran to the end without a question, and so did an 11-angle sweep (−4° … 16°, up to 2000 iterations each, Convergence Conditions, velocity-inlet case). Not tried yet: Fluent inside Workbench (it asks about changed settings; the journal is meant for standalone Fluent) and overwriting a case file with `/file/confirm-overwrite? no`. Read it with File > Read > Journal.
- **Fixes from a code review:**
  - In Mach mode, a temperature changed after choosing Mach did not reach the Fluent helper, so its speed of sound and far-field Mach number were computed at the old temperature (M 0.15 at 100 °C was shown as 0.171).
  - An undashed NACA 6-series name ("64012", "63010") was drawn as a 5-digit section with design Cl 0.9. A 5-digit code starting with 6 is now refused with that reason, and the search shows only library sections for it.
  - The mesh quality verdict now also counts the two averages: a bad average skewness or orthogonal quality no longer shows the green "good" box.
  - A language switch kept most inputs but reset the Fluent free-stream speed and the y⁺ correction's "first cell height used"; both are kept now, and still follow a new Reynolds number or plan.
  - Inputs hidden by a mode switch (Re ↔ speed, inflation ↔ mapped, search ↔ file, C-grid ↔ rectangle) came back at their defaults; they keep their values now.
  - README: the DesignModeler unit is the output unit chosen in the sidebar, not always metres.
  - The search buttons no longer use Streamlit's deprecated `use_container_width`.
  - The journal setup list also gives the velocity-inlet components (`U [m s^-1]*cos(aoa)`, `U [m s^-1]*sin(aoa)`), as used in the 11-angle Fluent sweep; copying the flow-direction lines (cos/sin alone) into a velocity inlet set by Components would have given 1 m/s. The journal title and note no longer say pressure-far-field only.
  - Text corrections: the journal note no longer counts "four lines" and says that overwriting a case file is untried; the profile help points to the output unit in the sidebar; the temperature and speed help match each flow mode; the not-found message says which NACA codes are drawn from the equations; the tilt note says a strongly cambered nose can show 1–2° without tilt; the Mach entry above calls 57 989 Pa the hand-entered pressure-far-field value (the validated NACA 0012 run used a velocity inlet).
  - Library: the maximum camber is now measured from the chord line, not from the x axis. 16 sections changed by more than 0.2 % c (for example ag38 showed −1.7 % at the trailing edge, now +2.1 % at 0.35c); no section moved between symmetric and cambered. `tools/build_airfoil_library.py --restat` recomputes these numbers from the stored files.
  - A symmetric 4-digit code with a camber position ("0312") is refused instead of drawing 0012 under another name.
  - Mach mode warns when the Mach and Reynolds numbers give a near-vacuum (Knudsen number above 1e-3), where Fluent's no-slip continuum model no longer holds.
  - The journal file-name prefix no longer accepts ':' (not allowed in Windows file names); wall zone names still may contain it.
  - README: the feature list now includes the SpaceClaim TXT, the profile-only files, the m/mm unit, the Mach input and the velocity-inlet journal lines; the scope note says what the Mach input does above 0.3.
  - CI runs on Linux and Windows, each with the newest and the lowest Streamlit that requirements.txt allows. Its first run showed that Streamlit 1.55's test tool has no file-upload accessor (it came with 1.56), so the lowest supported Streamlit is now 1.56.

## V0.6.6 Beta (Türkçe)

Fluent için hücum açısı taraması journal'ı (Ladson verisine karşı 11 açılı NACA 0012 taramasıyla denendi) ve bağımsız bir kod incelemesinden gelen düzeltmeler.

- **Profil kütüphanesi: 300 profil (önceden 200).** Güncel UIUC veritabanından (coord_seligFmt.zip, şubat 2026; kütüphanede zaten olan profillerin koordinatları değişmedi) aynı kalite kurallarıyla, aile kotaları 1.5 katına çıkarılarak yeniden üretildi. Eski 200 profilin hepsi duruyor. Tiresiz 6 serisi dosyalar artık atlanmıyor; gerçek simetrik 64-012 ve 64-015 kütüphanede ("64012" araması onları buluyor). `tools/build_airfoil_library.py` başka bir boyut için `--target N` alıyor; 500'de küçük aileler tükeniyor ve aynı profil iki farklı dosya adıyla iki kez giriyor, bu yüzden 300 seçildi.
- **Otomasyon sekmesi.** Üçüncü bir sekme çok açı koşmak için gereken her şeyi topluyor: hücum açısı taraması tablosu (Mesh / y⁺ sekmesindeki Fluent yardımcısından taşındı; orada tek açılık yardımcı ve türbülans sönümü kaldı), Fluent journal'ı ve yeni polar aracı.
- **Report file'dan polar.** Taramada Fluent'in yazdığı report file (.out) yüklenir. Sütunlar adlarından bulunur (Fluent alfabetik sırayla yazar; açı, Cl ve Cd elle de seçilebilir); açı sütunu varsayılan olarak radyan okunur ([deg] birimli bir expression'ın expression report'u radyan yazılır), istenirse derece. Her açı, açının sabit kaldığı iterasyon bloğudur; tablo son N iterasyonun (varsayılan 50) ortalamasını, aynı iterasyonlarda Cl ve Cd'nin en büyük – en küçük farkını, Cl/Cd'yi, iterasyon aralığını ve bir durumu verir: oturdu, salınıyor (son N iterasyonda Cl 1e-3'ten ya da Cd %1'den fazla oynuyorsa; iki sınır da değiştirilebilir) ya da az iterasyon. Aynı açı sonradan yeniden koşulduysa en son blok, kayıttan sürdürülen taramada iki kez yazılan iterasyonlarda sonraki satırlar kullanılır. Aralığı hata çubuğu olarak gösteren Cl–α, Cd–α ve Cl–Cd grafikleri ve CSV. 11 açılı NACA 0012 taramasının report file'ıyla denendi (Fluent 2024 R2): −4…6° oturdu, 8–16° salınıyor, elle çıkarılan tabloyla aynı; 10°'de son 50 iterasyonun ortalaması Cl 1.043, Cd 0.0131 (Ladson 10.15°: 1.045, 0.0135), son değer ise 1.056 idi.
- **Fluent journal.** Otomasyon sekmesinde, açı taraması tablosunun altında bir Fluent TUI journal (`.jou`) indirme düğmesi ve case'in neye ihtiyaç duyduğunun listesi var (açılar her zaman küçükten büyüğe koşulur). Case'i Fluent'te kendiniz kurarsınız: açıyı tutan `aoa` named expression'ı, pressure-far-field akış yönü X = `cos(aoa)`, Y = `sin(aoa)` ya da velocity-inlet bileşenleri `U [m s^-1]*cos(aoa)`, `U [m s^-1]*sin(aoa)` ve `aoa`'yı kullanan expression report definition olarak Cl ve Cd (uygulama yoğunluk, hız ve veterinize göre tam ifadeleri yazar; report file'larda yalnızca expression report'lar ve moment olmalı, çünkü kuvvet vektörü değişen bir lift/drag report'u Fluent'e dosyası için soru sordurur ve journal'da sonraki satır cevap sayılır). Residual convergence checks kapalı; `aoa`'yı ilk açıya ayarlayıp initialize edin ve en az bir iterasyonu kendiniz koşun. Journal her açıda yalnızca expression'ı değiştirir (`/define/named-expressions/edit aoa definition "6 [deg]" q`), seçilen sayıda iterasyon koşar (varsayılan 1000) ve önceki çözümden devam eder. Girişler: açı başına iterasyon (üst sınır: case'te Convergence Conditions varsa Fluent açıyı erken bitirir, journal sonraki açıya geçer), expression adı, case & data'nın ne sıklıkla kaydedileceği (her k açıda bir, son açı her zaman; 0 = yalnızca son açı) ve kayıt klasörü. Kurulum listesi ayrıca `clconv` = Cl + 1 expression report'unu veriyor; Convergence Conditions'ta Cl yerine kullanılır: Fluent'in ölçütü göreli değişimdir, bu yüzden Cl ≈ 0 olan açıda (simetrik profilde 0°) hiç dolmaz ve açı iterasyon üst sınırına kadar koşar (11 açılı taramada görüldü); Cl + 1 değeri 1 civarında kaldığı için göreli değişimi Cl'nin mutlak değişimidir. Fluent 2024 R2'de denendi: 0°'de açı 366 iterasyonda kendisi durdu, Cl ve Cd 2000 iterasyonluk koşuyla aynı çıktı. Yarıda kalan taramayı sürdürmek için: son kaydedilen case & data açılır, ilk açı bir sonraki açı yapılır ve yeni journal indirilir (henüz denenmedi). Cl ve Cd report file'lardan gelir; her açı bir iterasyon bloğudur. Ansys Fluent 2024 R2'de (standalone, 2B) denendi: düzenleme komutu, Cl/Cd expression'ları (Fluent'in kendi kuvvet raporlarıyla yaklaşık 1e-6 farkla aynı değerler) ve report file'lar (expression değişince soru sorulmadı). 3 açılı bir tarama (−2°, 0°, 2°, açı başına 50 iterasyon) ve 11 açılı bir tarama (−4° … 16°, açı başına en çok 2000 iterasyon, Convergence Conditions, velocity-inlet case) soru sorulmadan sonuna kadar koştu. Henüz denenmedi: Workbench içindeki Fluent (ayar değişikliği için soru sorar; journal standalone Fluent içindir) ve `/file/confirm-overwrite? no` ile case dosyasının üzerine yazma. File > Read > Journal ile okunur.
- **Kod incelemesinden gelen düzeltmeler:**
  - Mach modunda, Mach seçildikten sonra değiştirilen sıcaklık Fluent yardımcısına geçmiyordu; ses hızı ve far-field Mach sayısı eski sıcaklıkla hesaplanıyordu (100 °C'de M 0.15, 0.171 görünüyordu).
  - Tiresiz yazılan NACA 6 serisi adı ("64012", "63010") tasarım Cl'si 0.9 olan 5 haneli profil olarak çiziliyordu. 6 ile başlayan 5 haneli kod artık bu gerekçeyle reddediliyor; arama yalnızca kütüphanedeki profilleri gösteriyor.
  - Mesh kalite kararı artık iki ortalamayı da sayıyor: kötü ortalama skewness ya da orthogonal quality artık yeşil "iyi" kutusunu göstermiyor.
  - Dil değişince girişlerin çoğu korunuyordu ama Fluent serbest akış hızı ve y⁺ düzeltmesindeki "kullanılan ilk hücre yüksekliği" sıfırlanıyordu; ikisi de artık korunuyor ve yeni bir Reynolds sayısını ya da planı yine izliyor.
  - Mod değişince gizlenen girişler (Re ↔ hız, inflation ↔ mapped, arama ↔ dosya, C-grid ↔ dikdörtgen) varsayılana dönüyordu; artık değerlerini koruyor.
  - README: DesignModeler birimi her zaman metre değil, kenar çubuğunda seçilen çıktı birimi.
  - Arama düğmeleri Streamlit'in kaldırılacak `use_container_width` parametresini artık kullanmıyor.
  - Journal kurulum listesi velocity-inlet bileşenlerini de veriyor (`U [m s^-1]*cos(aoa)`, `U [m s^-1]*sin(aoa)`), 11 açılı Fluent taramasında kullanıldığı gibi; akış yönü satırlarını (yalnız cos/sin) Components ile ayarlanmış bir velocity-inlet'e kopyalamak 1 m/s verirdi. Journal başlığı ve notu artık yalnızca pressure-far-field demiyor.
  - Metin düzeltmeleri: journal notu artık "dört satır" demiyor ve case dosyasının üzerine yazmanın denenmediğini söylüyor; profil yardımı kenar çubuğundaki çıktı birimini gösteriyor; sıcaklık ve hız yardımları her akış moduna uyuyor; "bulunamadı" mesajı hangi NACA kodlarının denklemle çizildiğini söylüyor; eğiklik notu çok kamburlu bir burnun eğik olmadan 1–2° gösterebileceğini söylüyor; yukarıdaki Mach girdisi 57 989 Pa'yı pressure-far-field kurulumunda elle girilen değer olarak anıyor (doğrulanan NACA 0012 koşusu velocity-inlet idi).
  - Kütüphane: en büyük kamburluk artık x ekseninden değil veter çizgisinden ölçülüyor. 16 profil %0.2 c'den fazla değişti (ör. ag38 firar kenarında −%1.7 gösteriyordu, şimdi 0.35c'de +%2.1); hiçbir profil simetrik ile kamburlu arasında yer değiştirmedi. `tools/build_airfoil_library.py --restat` bu sayıları saklanan dosyalardan yeniden hesaplar.
  - Kamburluk konumu olan simetrik 4 haneli kod ("0312") artık 0012'yi başka adla çizmek yerine reddediliyor.
  - Mach modu, Mach ve Reynolds sayısı neredeyse vakum verdiğinde (Knudsen sayısı 1e-3'ün üzerinde) uyarıyor; orada Fluent'in kaymasız sürekli ortam modeli geçerli değil.
  - Journal dosya adı öneki artık ':' kabul etmiyor (Windows dosya adlarında geçersiz); duvar bölgesi adlarında hâlâ olabilir.
  - README: özellik listesine SpaceClaim TXT, yalnız profil dosyaları, m/mm birimi, Mach girişi ve velocity-inlet journal satırları eklendi; kapsam notu Mach girişinin 0.3 üzerinde ne yaptığını söylüyor.
  - CI, Linux ve Windows'ta, requirements.txt'in izin verdiği en yeni ve en eski Streamlit ile çalışıyor. İlk çalışması Streamlit 1.55'in test aracında dosya yükleme erişimi olmadığını gösterdi (1.56 ile geldi); desteklenen en düşük Streamlit artık 1.56.

## V0.6.5 Beta

An independent check of the mesh and Fluent formulas found no formula errors; these are the notes and warnings it asked for.

- **Warnings:** target y⁺ above 2 (Transition SST wants about 1, and the largest y⁺ is near the leading edge), inflation coverage below 1, Reynolds number above 10⁹ (the skin-friction correlation stops there).
- **Fluent helper:** a Mach above 0.3 now also points to pressure-far-field for external flow; for a temperature other than 15 °C the ideal-gas density and Sutherland viscosity are suggested so Re and Mach belong to the same state; the turbulence note adds Fluent's 1–10 viscosity-ratio advice (the default of 100 stays: it is what the NACA 0012 validation used) and that the Ansys documentation labels the SST constants the other way round.
- **SpaceClaim:** the profile section also writes a point-curve text file for SpaceClaim (header `3d=true`, `polyline=false`, `fit=false`; `0 x y` per line; blank line between the upper, lower and trailing-edge curves). The DesignModeler file (group and point numbers in the first columns) is not that format. Written from SpaceClaim's help; not tried in SpaceClaim yet. The whole domain has a SpaceClaim TXT download too (same layout), next to the Ansys TXT.
- **Mach input.** The Mesh / y⁺ tab has a third flow input, Mach + Reynolds + temperature: the speed follows from the Mach number, the viscosity from Sutherland's law, the density from Re and the static pressure from the density (Mach 0.15, Re 2×10⁶, 15 °C, c = 1 m gives 57 989 Pa, the value entered by hand in the pressure-far-field NACA 0012 setup). The Fluent helper then also lists the pressure-far-field values (Mach, gauge pressure, temperature).
- **Output unit.** A sidebar switch, m or mm, sets the unit of every downloaded file (Ansys TXT, SpaceClaim TXT and the profile files); before, the domain files were always in metres. The unit is not written inside the files: choose the same Units in DesignModeler, SpaceClaim or SolidWorks. A file in mm gets `_mm` in its name.
- **y⁺ correction tool:** the help says the plan's target is the full first-cell height, so Fluent reports about half of it.
- **README:** the NACA 0012 section is now a comparison, with its limits stated (one section, one angle, one Reynolds number, inflation mesh only, viscosity ratio 100), and a scope note (low speed, far-field size at high Cl). The same note is in the help of the inlet radius.
- Tests run automatically on GitHub for every push.

## V0.6.5 Beta (Türkçe)

Mesh ve Fluent formüllerinin bağımsız denetiminde formül hatası çıkmadı; aşağıdakiler denetimin istediği not ve uyarılar.

- **Uyarılar:** hedef y⁺ 2'nin üzerinde (Transition SST yaklaşık 1 ister, en büyük y⁺ hücum kenarı yakınında olur), Inflation kapsaması 1'in altında, Reynolds sayısı 10⁹'un üzerinde (sürtünme bağıntısı orada sona erer).
- **Fluent yardımcısı:** Mach 0.3'ün üzerinde dış akış için pressure-far-field de öneriliyor; sıcaklık 15 °C'den farklıysa Re ve Mach aynı duruma ait olsun diye ideal gaz yoğunluğu ve Sutherland viskozitesi öneriliyor; türbülans notuna Fluent'in 1–10 viskozite oranı önerisi eklendi (varsayılan 100 kalıyor: NACA 0012 doğrulamasında bu kullanıldı) ve Ansys belgesinin SST sabitlerini ters etiketlediği yazıldı.
- **SpaceClaim:** profil bölümü SpaceClaim için nokta-eğri metin dosyası da yazıyor (başlık `3d=true`, `polyline=false`, `fit=false`; satırda `0 x y`; üst, alt ve arka kenar eğrileri arasında boş satır). DesignModeler dosyası (ilk sütunlarda grup ve nokta numarası) bu biçim değil. SpaceClaim yardımına göre yazıldı; SpaceClaim'de henüz denenmedi. Tüm domain için de Ansys TXT'nin yanında bir SpaceClaim TXT indirme düğmesi var (aynı biçim).
- **Mach girişi.** Mesh / y⁺ sekmesinde üçüncü bir akış girişi var: Mach + Reynolds + sıcaklık. Hız Mach sayısından, viskozite Sutherland yasasından, yoğunluk Re'den ve statik basınç yoğunluktan hesaplanır (Mach 0.15, Re 2×10⁶, 15 °C, c = 1 m için 57 989 Pa, pressure-far-field NACA 0012 kurulumunda elle girilen değer). Fluent yardımcısı pressure-far-field değerlerini (Mach, gauge pressure, sıcaklık) de listeliyor.
- **Çıktı birimi.** Kenar çubuğundaki m / mm anahtarı indirilen tüm dosyaların birimini belirliyor (Ansys TXT, SpaceClaim TXT ve profil dosyaları); önceden domain dosyaları hep metreydi. Birim dosyanın içinde yazmıyor: DesignModeler, SpaceClaim ya da SolidWorks'te aynı Units'i seçin. mm dosyanın adında `_mm` olur.
- **y⁺ düzeltme aracı:** yardım metni, plandaki hedefin tam ilk hücre yüksekliği olduğunu ve Fluent'in bunun yaklaşık yarısını raporladığını söylüyor.
- **README:** NACA 0012 bölümü artık bir karşılaştırma; sınırları yazılı (tek profil, tek açı, tek Reynolds sayısı, yalnızca inflation mesh, viskozite oranı 100) ve bir kapsam notu var (düşük hız, yüksek Cl'de uzak alan boyutu). Aynı not giriş yarıçapının yardım metninde de duruyor.
- Testler her push'ta GitHub'da otomatik çalışıyor.

## V0.6.4 Beta

- **Domain sizes in chords.** Inlet radius / distance, wake length and the rectangle's top and bottom distances are entered as multiples of the chord (defaults 15c and 20c, as before for a 1 m chord); the sidebar shows them in metres. Before, the defaults were metres, so a 10 m chord got a domain only 1.5c across and a 5 cm chord one of 300c.
- **Use the outline as drawn.** A new box for uploaded files keeps the closed outline in its own point order and cuts it only at the leading edge (smallest x) and the trailing edge (largest x), so a vortex generator, a flap or a kinked section survives; the normal reader sorts the surfaces along x and loses such shapes. The domain then has the front axis and the wake axis only (the validated inflation workflow); mapped meshing is not offered, and the wall edges are sized by hand (the app gives the LE/TE sizes and the wake axis). Self-crossing outlines are refused. Not tried in Ansys yet.
- **Free-stream turbulence decay** in the Fluent helper: the turbulence intensity that reaches the leading edge for an inlet Tu and viscosity ratio, the highest value that can reach it, and the inlet Tu needed for a wanted value at the airfoil (closed-form SST decay, Spalart & Rumsey 2007). With the domain defaults, 1% at the inlet leaves about 0.43% at the airfoil with ratio 100 and 0.14% with ratio 10. The numbers match the table used in the NACA 0012 validation.
- **Temperature input** for the speed of sound and Mach (15 °C gives the old 340.29 m/s).
- **Angle-of-attack sweep:** inlet velocity components and lift/drag vectors for a range of angles, with a CSV download, for running a polar.
- **Airfoil profile only.** A new section on the Geometry tab downloads just the upper and lower surface, without a domain: a DesignModeler `3D Curve` TXT (group 1 upper, group 2 lower, group 3 the trailing-edge line when it is blunt) and a ZIP with two SolidWorks `Curve Through XYZ Points` files (one curve per file, tab-separated X Y Z). Unit m or mm. Not tried in SolidWorks / DesignModeler yet.
- At 0° the lift vector no longer prints "-0.000000".

## V0.6.4 Beta (Türkçe)

- **Domain boyutları veter cinsinden.** Giriş yarıçapı / uzaklığı, iz uzunluğu ve dikdörtgenin üst ve alt uzaklıkları veterin katı olarak giriliyor (varsayılan 15c ve 20c; 1 m veterde eskisiyle aynı); kenar çubuğu metre karşılığını gösteriyor. Önceden varsayılanlar metreydi, 10 m veterde domain yalnızca 1.5c, 5 cm veterde 300c oluyordu.
- **Çizgiyi olduğu gibi kullan.** Yüklenen dosyalar için yeni bir kutu, kapalı çizgiyi kendi nokta sırasıyla tutup yalnızca hücum kenarında (en küçük x) ve firar kenarında (en büyük x) kesiyor; böylece vortex generator, flap ya da kırık profil korunuyor (normal okuyucu yüzeyleri x'e göre dizip bu şekilleri kaybediyor). Domain'de yalnızca ön eksen ve iz ekseni var (doğrulanmış Inflation iş akışı); mapped mesh sunulmuyor, duvar kenarlarının eleman boyu elle veriliyor (uygulama LE/TE boylarını ve iz eksenini veriyor). Kendini kesen çizgiler reddediliyor. Henüz Ansys'te denenmedi.
- Fluent yardımcısında **serbest akış türbülansının sönümü**: verilen inlet Tu ve viskozite oranıyla hücum kenarına ulaşan türbülans yoğunluğu, ulaşabilecek en yüksek değer ve kanatta istenen değer için gereken inlet Tu (SST'nin kapalı çözümü, Spalart & Rumsey 2007). Varsayılan domain'de inlet'te %1, oran 100 ile kanatta yaklaşık %0.43, oran 10 ile %0.14 kalıyor. Sayılar NACA 0012 doğrulamasında kullanılan tabloyla aynı.
- Ses hızı ve Mach için **sıcaklık girişi** (15 °C eski 340.29 m/s'yi veriyor).
- **Hücum açısı taraması:** bir açı aralığı için inlet hız bileşenleri ve lift/drag vektörleri, CSV indirme ile; polar çıkarmak için.
- **Sadece kanat profili.** Geometri sekmesinde yeni bir bölüm, alan olmadan yalnızca üst ve alt yüzeyi indiriyor: DesignModeler `3D Curve` TXT (grup 1 üst, grup 2 alt, arka kenar kalınsa grup 3 arka kenar çizgisi) ve iki SolidWorks `Curve Through XYZ Points` dosyası içeren bir ZIP (dosya başına bir eğri, sekmeyle ayrılmış X Y Z). Birim m ya da mm. SolidWorks / DesignModeler'da henüz denenmedi.
- 0°'de lift vektörü artık "-0.000000" yazmıyor.

## V0.6.3 Beta

Fixes from a four-part review (geometry and file reading, mesh math, page behaviour, topology and export). Each fix has a test that failed before it.

- **Switching the language reset the inputs.** Chord, domain, Reynolds number, mesh settings and the uploaded file went back to their defaults after a TR ↔ EN switch. They are kept now.
- **Two input boxes could stop the page** with an error: the y⁺ correction box at very high Reynolds numbers or tiny chords, and the Fluent speed box for a long chord at very low Reynolds numbers.
- **Inflation Growth Rate was rounded** to 3 digits (1.105 shown as 1.1) while the layer count used the full value. It is shown as entered now.
- **Search:** `n0012`, `N2412` (the UIUC way of writing NACA names) found the wrong section or nothing; now they give the NACA section. A 6-series name such as `64-012` was drawn as a 5-digit NACA section (cambered, a different airfoil); now it is only looked up in the selection.
- **← after a search with no result** skipped a section; it now returns to the last section shown.
- **Download names:** titles with a dot were cut short, so "HQ 1.0/12" and "HQ 1.0/8" downloaded under the same name. Every section now gets its own name.
- **Mirror box** kept its tick when a corrected file with the same name and size was uploaded again.
- **Overlap repair at the nose:** when the overlapping stretch reached the leading edge, the repair moved the two surfaces apart there too and the outline was left open at the nose.
- **Slanted blunt trailing edge:** the wake axis could start a fraction of a micrometre inside the airfoil after rounding in the TXT. It now starts on a point of the closure line.
- **TXT export:** two points that print alike are written once.
- Number of divisions: a length that n cells fill exactly no longer gets n + 1 (round-off). No change in any plan the app gives with its own inputs.

## V0.6.3 Beta (Türkçe)

Dört bölümlü bir incelemeden (geometri ve dosya okuma, mesh hesapları, sayfa davranışı, topoloji ve dışa aktarma) çıkan düzeltmeler. Her düzeltmenin, düzeltmeden önce başarısız olan bir testi var.

- **Dil değiştirmek girdileri sıfırlıyordu.** TR ↔ EN geçişinden sonra veter, domain, Reynolds sayısı, mesh ayarları ve yüklenen dosya varsayılana dönüyordu. Artık korunuyor.
- **İki giriş kutusu sayfayı hatayla durdurabiliyordu:** çok yüksek Reynolds sayısında ya da çok küçük veterde y⁺ düzeltme kutusu, uzun veter ve çok düşük Reynolds sayısında Fluent hız kutusu.
- **Inflation Growth Rate 3 haneye yuvarlanıyordu** (1.105 yerine 1.1), katman sayısı ise tam değerle hesaplanıyordu. Artık girildiği gibi gösteriliyor.
- **Arama:** `n0012`, `N2412` (NACA adlarının UIUC yazımı) yanlış profili ya da hiçbir şey bulmuyordu; artık NACA profilini veriyor. `64-012` gibi bir 6 serisi adı 5 haneli NACA profili olarak çiziliyordu (kamburlu, başka bir profil); artık yalnızca seçkide aranıyor.
- **Sonuç bulunmayan bir aramadan sonra ←** bir profil atlıyordu; artık en son gösterilen profile dönüyor.
- **İndirme adları:** nokta içeren başlıklar kesiliyordu, "HQ 1.0/12" ile "HQ 1.0/8" aynı adla iniyordu. Artık her profilin kendi adı var.
- **Çevir kutusu**, aynı ad ve boyutta düzeltilmiş bir dosya yeniden yüklenince işaretli kalıyordu.
- **Burunda örtüşme onarımı:** örtüşen bölge hücum kenarına ulaşınca onarım iki yüzeyi orada da ayırıyor, profil burunda açık kalıyordu.
- **Eğik küt firar kenarı:** TXT'deki yuvarlamadan sonra wake ekseni profilin mikrometrenin altında bir kesir kadar içinden başlayabiliyordu. Artık kapama çizgisinin bir noktasından başlıyor.
- **TXT çıktısı:** aynı yazılan iki nokta bir kez yazılıyor.
- Bölüntü sayısı: tam n hücrenin doldurduğu bir uzunluk yuvarlama hatasıyla n + 1 almıyor. Uygulamanın kendi girdileriyle verdiği planlarda bir değişiklik yok.

## V0.6.2 Beta

- **Phone layout.** The 🎲 ← → buttons stay in one compact row on a phone (Streamlit stacked them into three full-width buttons).
- The forward arrow was drawn as a larger colour emoji than the back arrow; both are now the same plain arrow character.

## V0.6.2 Beta (Türkçe)

- **Telefon görünümü.** 🎲 ← → düğmeleri telefonda tek satırda, küçük boyutta duruyor (Streamlit onları üç ayrı tam genişlikli düğme olarak alt alta diziyordu).
- İleri oku geri okundan büyük, renkli bir emoji olarak çiziliyordu; ikisi de artık aynı düz ok karakteri.

## V0.6.1 Beta

- The 🎲 ⬅ ➡ buttons no longer show a hover tooltip; it floated over the page.

## V0.6.1 Beta (Türkçe)

- 🎲 ⬅ ➡ düğmelerinin üzerine gelince çıkan açıklama kaldırıldı; sayfanın üstünde havada kalıyordu.

## V0.6.0 Beta

- **Section search.** The NACA box is now a search box for every section the app knows. A 4- or 5-digit NACA code is drawn from the NACA equations as before (201 points, sharp trailing edge; this is the NACA 0012 used in the validation). Every other section comes from a selection of 200 sections from the UIUC Airfoil Coordinates Database: NACA 6 and 16 series, NASA SC(2), NLF and LS, Eppler, Selig, Wortmann FX, Hepperle MH, Drela AG/HT, Althaus, Quabeck, Girsberger, RAE, Delft DU, Clark Y, Göttingen and others. Spaces, dashes and brackets do not matter (`63-215`, `n63215` and `NACA 63-215` find the same section). The app does not invent a section: a name that is neither a NACA code nor in the selection is reported as not in the database.
- **Random section 🎲**, with filters for maximum thickness, camber (symmetric / cambered) and family, and ⬅ ➡ to go back to earlier sections.
- The geometry tab names the source of the section: the NACA equations, or the UIUC file with its maximum thickness, camber and point count.
- How the 200 were chosen (`tools/build_airfoil_library.py`, run on the full database): at least 25 points per surface, no chordwise gap over 0.07c, no kink over 30° behind the nose, no overlapping surfaces, not tilted or reversed, at least 3% thick; within a family the well-known sections first, the rest spread over thickness, camber and their positions. NACA 4/5-digit files are left out: the database copies have 18 points and a blunt trailing edge, and NACA 0012 is not in the database.
- Every section in the selection is tested to give a domain without crossing curves and a mesh plan (`tests/test_library.py`).
- The coordinates are credited to the UIUC database (Prof. M. S. Selig) in the README and the About box; they are not covered by the app's MIT license.

## V0.6.0 Beta (Türkçe)

- **Profil arama.** NACA kutusu artık uygulamanın bildiği tüm profiller için bir arama kutusu. 4 ya da 5 haneli NACA kodu eskisi gibi NACA denklemlerinden çiziliyor (201 nokta, keskin firar kenarı; doğrulamada kullanılan NACA 0012 budur). Diğer her profil UIUC Airfoil Coordinates Database'den seçilmiş 200 profilden geliyor: NACA 6 ve 16 serisi, NASA SC(2), NLF ve LS, Eppler, Selig, Wortmann FX, Hepperle MH, Drela AG/HT, Althaus, Quabeck, Girsberger, RAE, Delft DU, Clark Y, Göttingen ve diğerleri. Boşluk, tire ve parantez önemli değil (`63-215`, `n63215` ve `NACA 63-215` aynı profili bulur). Uygulama profil uydurmuyor: ne NACA kodu ne de seçkide olan bir ad için "veritabanında yok" diyor.
- **Rastgele profil 🎲**: maksimum kalınlık, kamburluk (simetrik / kamburlu) ve aile filtreleriyle; ⬅ ➡ ile önceki profillere dönülüyor.
- Geometri sekmesi profilin kaynağını yazıyor: NACA denklemleri ya da UIUC dosyası, maksimum kalınlığı, kamburluğu ve nokta sayısıyla.
- 200 profilin seçimi (`tools/build_airfoil_library.py`, veritabanının tamamı üzerinde): yüzey başına en az 25 nokta, veter boyunca 0.07c'den büyük boşluk yok, burnun gerisinde 30°'den keskin kırık yok, iç içe giren yüzey yok, eğik ya da ters değil, en az %3 kalın; her ailede önce bilinen profiller, kalanı kalınlık, kamburluk ve konumlarına göre yayılarak. NACA 4/5 haneli dosyalar alınmadı: veritabanındaki kopyalar 18 noktalı ve küt firar kenarlı, NACA 0012 ise veritabanında yok.
- Seçkideki her profilin kesişen eğri olmadan domain ve mesh planı verdiği test ediliyor (`tests/test_library.py`).
- Koordinatlar README'de ve Hakkında kutusunda UIUC veritabanına (Prof. M. S. Selig) atfediliyor; uygulamanın MIT lisansına dahil değiller.

## V0.5.6 Beta

The whole UIUC airfoil coordinate database (1665 files, Selig format) was run through the app: file reader, domain, Ansys TXT export and mesh plans for Re 1e5, 1e6 and 6e6 (`tests/test_database_findings.py` holds the cases found). 1662 files are read; the other three are refused correctly (two multi-element slat/flap files and one single-surface engine cowl).

- **Surfaces that overlap by a few ten-thousandths of the chord.** Eleven files let the upper and the lower surface cross each other, mostly at a cusped trailing edge (Wortmann FX 62-K-131 and FX 63-147, Eppler STE 871-514 and others, 0.001–0.05 % c) or in a thin section (Eppler 378). Nine of them were exported without any warning with curves that cross each other, which DesignModeler cannot build a face from; two were refused with a message that did not say why. Now the surfaces are moved apart by at most the overlap (half to each) so that they are never closer than 2×10⁻⁵ c, a note on the geometry tab says by how much, and an overlap beyond 0.1 % c is still refused. Overlaps below 10⁻⁵ c (22 more files, rounded coordinates) are repaired without a note.
- **Lower surface that stops short of the upper one** (Eppler STE files: the lower surface ends 0.4 % c before the upper surface, which then sticks out below it): the shorter surface is continued along its end direction to the same x, so the trailing-edge closure is no longer a near-horizontal line that the wake axis ran through.
- Not tested in Ansys: no mesh was built from a repaired file. The repair is a few 10⁻⁴ c at most, far below the trailing-edge element size (0.003 c or more).

## V0.5.6 Beta (Türkçe)

UIUC kanat koordinat veritabanının tamamı (1665 dosya, Selig formatı) uygulamadan geçirildi: dosya okuyucu, domain, Ansys TXT çıktısı ve Re 1e5, 1e6, 6e6 için mesh planları (bulunan durumlar `tests/test_database_findings.py` içinde). 1662 dosya okunuyor; kalan üçü doğru olarak reddediliyor (slat/flap'lı iki çok elemanlı dosya ve tek yüzeyli bir motor kaportası).

- **Veterin on binde birleri kadar iç içe giren yüzeyler.** On bir dosyada üst ve alt yüzey birbirini kesiyordu; çoğu sivri uçlu (cusp) firar kenarında (Wortmann FX 62-K-131 ve FX 63-147, Eppler STE 871-514 ve diğerleri, %0.001–0.05 c), biri ince bir kesitte (Eppler 378). Dokuzu hiçbir uyarı olmadan, birbirini kesen eğrilerle dışa aktarılıyordu; DesignModeler bunlardan yüzey kuramaz. İkisi nedeni belirtmeyen bir mesajla reddediliyordu. Artık yüzeyler en çok örtüşme kadar (yarısı her yüzeye) birbirinden uzaklaştırılıyor, iki yüzey hiçbir yerde 2×10⁻⁵ c'den yakın kalmıyor, geometri sekmesinde ne kadar olduğunu söyleyen bir not çıkıyor; %0.1 c'den fazla örtüşme hâlâ reddediliyor. 10⁻⁵ c'nin altındaki örtüşmeler (22 dosya daha, yuvarlanmış koordinatlar) not düşülmeden düzeltiliyor.
- **Üst yüzeyden kısa biten alt yüzey** (Eppler STE dosyaları: alt yüzey üstten %0.4 c önce bitiyor, üst yüzey de onun altına taşıyor): kısa yüzey, ucundaki yön boyunca aynı x'e kadar uzatılıyor; firar kenarı kapama çizgisi artık wake ekseninin içinden geçen, neredeyse yatay bir çizgi olmuyor.
- Ansys'te denenmedi: düzeltilmiş bir dosyadan mesh kurulmadı. Onarım en fazla birkaç 10⁻⁴ c; firar kenarı eleman boyunun (0.003 c ya da daha büyük) çok altında.

## V0.5.5 Beta

Custom airfoil files were tested with 75 hard files written from a known profile; the outline the app reads is compared with the true one (`tests/test_hard_files.py`). 14 of them went wrong before this version.

- **Zigzag nose.** Cambered sections whose nose wraps around x = 0 (as XFOIL writes NACA sections), stored as two LE → TE blocks, came out with a jagged leading edge: the points were sorted by x. The file order is kept now.
- **Profile off-centre.** Only x was normalised, so a file with an origin far away (a CAD section at y = 800 mm) put the airfoil chords away from the middle of the domain. The leading edge is now moved to the origin.
- **Wrong shape without a message:** a numeric parameter line such as `12.0 40.0 2.0` was taken as Lednicer point counts; a file with x, 0, z columns was read as a flat line; Lednicer counts that do not match the rows dropped a trailing-edge point.
- **Good files that were rejected** are read now: touching Fortran columns (`0.99893-0.00016`), `D` exponents, a point-number column, a constant first or third column, UTF-16 without a byte-order mark, a small-number parameter line, `.csv` files.
- **Broken files that were accepted** are rejected with a clear message: surfaces that cross, more than one element in a file, a profile without thickness.
- **Profile drawn backwards** (leading edge at the right) is recognised and mirrored; a "Mirror the profile in x" box in the sidebar shows it and lets you change it.
- New notes on the geometry tab: fewer than 12 points per surface, and a profile that is tilted in the file (the angle adds to the angle of attack).
- Download names keep Turkish letters readable (`Ölçü kanadı.dat` → `AirfoilMatic_Olcu_kanadi_CGrid.txt`).

## V0.5.5 Beta (Türkçe)

Özel kanat dosyaları, bilinen bir profilden üretilmiş 75 zor dosyayla denendi; uygulamanın okuduğu şekil gerçeğiyle karşılaştırılıyor (`tests/test_hard_files.py`). Bu sürümden önce 14'ünde sorun vardı.

- **Zikzaklı burun.** Burnu x = 0'ın önüne taşan kamburluklu profiller (XFOIL'in NACA profillerini yazdığı gibi), iki LE → TE bloğu olarak kaydedildiğinde hücum kenarı tırtıklı çıkıyordu: noktalar x'e göre sıralanıyordu. Artık dosyadaki sıra korunuyor.
- **Merkezden kaçık profil.** Yalnızca x normalize ediliyordu; orijini uzakta olan bir dosya (y = 800 mm'deki bir CAD kesiti) kanadı domain'in ortasından veterlerce uzağa koyuyordu. Hücum kenarı artık orijine taşınıyor.
- **Mesaj vermeden yanlış şekil:** `12.0 40.0 2.0` gibi sayısal bir parametre satırı Lednicer nokta sayısı sanılıyordu; x, 0, z sütunlu dosya düz çizgi olarak okunuyordu; satırlarla uyuşmayan Lednicer sayıları firar kenarı noktasını düşürüyordu.
- **Reddedilen sağlam dosyalar** artık okunuyor: bitişik Fortran sütunları (`0.99893-0.00016`), `D` üslü sayılar, nokta numarası sütunu, sabit ilk ya da üçüncü sütun, BOM'suz UTF-16, küçük sayılı parametre satırı, `.csv` dosyaları.
- **Kabul edilen bozuk dosyalar** artık açık bir mesajla reddediliyor: birbirini kesen yüzeyler, dosyada birden fazla eleman, kalınlığı olmayan profil.
- **Ters çizilmiş profil** (hücum kenarı sağda) tanınıp çevriliyor; kenar çubuğundaki "Profili x yönünde çevir" kutusu bunu gösteriyor ve değiştirmenize izin veriyor.
- Geometri sekmesinde yeni notlar: yüzey başına 12'den az nokta ve dosyada eğik duran profil (bu açı hücum açısına eklenir).
- İndirilen dosya adlarında Türkçe harfler okunur kalıyor (`Ölçü kanadı.dat` → `AirfoilMatic_Olcu_kanadi_CGrid.txt`).

## V0.5.4 Beta

Fixes from a line-by-line review of the geometry, topology and sizing code. Every item has a test that failed before the fix.

- **Wrong bias direction (Edge Sizing).** The "Smaller-element side" column always said "Trailing-edge side" for the airfoil rear edges. In inflation mode the TE element is at least 1.5x the last layer, so at low Reynolds numbers (below about 2×10⁵ with the defaults) or with a small split-line size it is larger than the element at the split line, and the small elements belong at the split line. The column now names the end that really has the smallest element (also when the LE size is set larger than the split size).
- **Custom files that silently lost their first point.** A file saved as "UTF-8 with BOM" without a title line, and files written in millimetres or percent whose first point has y > 1.5, lost the upper trailing-edge point; the airfoil then got a false blunt trailing edge (0.16% c in the test). Both are read correctly now.
- **More coordinate files are read:** decimal commas (`0,500000`, as Excel writes in a Turkish locale), `;` separators, UTF-16 files, and files that start at the leading edge (two LE → TE blocks without the count line, or one LE → TE → LE loop). These were rejected before.
- **Crash at very low Reynolds number.** With velocity input and Re below 1000 the page stopped with a traceback; it now shows the error message only.
- **Inflation mode: wake growth input removed.** The wake axis ends at the far-field element size, which fixes its progression, so the input changed nothing in the table.
- A first cell longer than an edge (extreme y⁺ at very low Re in a small domain) is rejected instead of showing a Bias Factor of 1e+48.
- Fluent helper lists the viscosity the Reynolds number is based on.
- New `tests/test_app.py`: runs the app headless in both languages, both domains and both mesh modes.

## V0.5.4 Beta (Türkçe)

Geometri, topoloji ve eleman boyu kodunun satır satır incelenmesinden çıkan düzeltmeler. Her madde, düzeltmeden önce başarısız olan bir testle kanıtlandı.

- **Yanlış bias yönü (Edge Sizing).** "Küçük eleman tarafı" sütunu kanat arka kenarları için her zaman "Firar kenarı tarafı" yazıyordu. Inflation modunda firar kenarı elemanı en az son katmanın 1.5 katı olduğu için, düşük Reynolds sayılarında (varsayılanlarla yaklaşık 2×10⁵ altı) ya da küçük bölme çizgisi boyunda bu eleman bölme çizgisindeki elemandan büyük çıkıyor; küçük elemanlar bölme çizgisinde olmalı. Sütun artık gerçekten en küçük elemanın olduğu ucu yazıyor (hücum kenarı boyu bölme boyundan büyük girildiğinde de).
- **İlk noktasını sessizce kaybeden özel dosyalar.** Başlık satırı olmadan "UTF-8 with BOM" olarak kaydedilmiş dosyalar ve ilk noktasında y > 1.5 olan milimetre ya da yüzde birimli dosyalar üst firar kenarı noktasını kaybediyordu; kanat sahte bir küt firar kenarı alıyordu (testte %0.16 c). İkisi de artık doğru okunuyor.
- **Daha fazla koordinat dosyası okunuyor:** ondalık virgül (`0,500000`; Türkçe Excel böyle yazar), `;` ayırıcı, UTF-16 dosyalar ve hücum kenarından başlayan dosyalar (sayı satırı olmadan iki LE → TE bloğu ya da tek LE → TE → LE döngüsü). Bunlar önceden reddediliyordu.
- **Çok düşük Reynolds sayısında çökme.** Hız girişiyle Re 1000'in altına düştüğünde sayfa hata dökümüyle duruyordu; artık yalnızca hata mesajı gösteriliyor.
- **Inflation modu: iz büyüme oranı girişi kaldırıldı.** İz ekseni genel eleman boyunda bittiği için dağılım zaten belirli; giriş tabloda hiçbir şeyi değiştirmiyordu.
- İlk hücrenin bir kenardan uzun olduğu durum (küçük domain'de çok düşük Re ve çok yüksek y⁺) artık reddediliyor; önceden Bias Factor 1e+48 gösteriliyordu.
- Fluent yardımcısı Reynolds sayısının dayandığı viskoziteyi de listeliyor.
- Yeni `tests/test_app.py`: uygulamayı iki dilde, iki domain tipinde ve iki mesh modunda tarayıcı olmadan çalıştırır.

## V0.5.3.4 Beta

- Edge Sizing tables show Number of Divisions and Bias Factor as text, so a Turkish-locale browser no longer turns 2.154 into 2,154 and values can be pasted into Ansys directly.

## V0.5.3.4 Beta (Türkçe)

- Edge Sizing tablolarında Number of Divisions ve Bias Factor metin olarak gösteriliyor; Türkçe tarayıcı artık 2.154'ü 2,154 yapmıyor, değerler doğrudan Ansys'e yapıştırılabilir.

## V0.5.3.3 Beta

- Inflation guidance corrected after the NACA 0012 tests in Ansys 2024 R2: add the wake axis to the Inflation Boundary and export the front axis too. With front axis + wake axis the mesh had max skewness 0.62 and min orthogonal quality 0.62; without the wake axis the sharp TE tip had degenerate cells, without the front axis inflation failed.
- New warning when the wake axis is selected without the front axis.

## V0.5.3.3 Beta (Türkçe)

- NACA 0012 denemelerinden (Ansys 2024 R2) sonra inflation talimatı düzeltildi: iz eksenini Inflation Boundary'sine ekleyin ve ön ekseni de dışa aktarın. Ön eksen + iz ekseniyle mesh'te max skewness 0.62, min orthogonal quality 0.62 çıktı; iz ekseni olmadan sivri firar kenarının ucunda dejenere hücreler, ön eksen olmadan inflation hatası oluştu.
- İz ekseni ön eksen olmadan seçildiğinde yeni uyarı.

## V0.5.3.2 Beta

- Inflation mode: the trailing-edge surface element is now at least 1.5 times the last inflation layer (and at least 0.003c). With a 3 mm TE element and a 4.3 mm last layer (NACA 0012, Re 2×10⁶) Ansys 2024 R2 inflation failed; with a larger TE element it worked.
- How-to: do not add the wake axis to the Inflation Boundary; the "Hard edges are not supported" warning alone is harmless.

## V0.5.3.2 Beta (Türkçe)

- Inflation modu: firar kenarındaki yüzey elemanı artık en az son inflation katmanının 1.5 katı (ve en az 0.003c). 3 mm TE elemanı ve 4.3 mm son katmanla (NACA 0012, Re 2×10⁶) Ansys 2024 R2'de inflation başarısız oldu; daha büyük TE elemanıyla çalıştı.
- Nasıl uygulanır: iz eksenini Inflation'ın Boundary'sine eklemeyin; "Hard edges are not supported" uyarısı tek başına zararsızdır.

## V0.5.3.1 Beta

- Mesh / y⁺ tab: the three input cards have the same height.
- Shorter beta note and split-line help in the sidebar.

## V0.5.3.1 Beta (Türkçe)

- Mesh / y⁺ sekmesi: üç giriş kartı aynı yükseklikte.
- Kenar çubuğunda beta notu ve bölme çizgisi açıklaması kısaldı.

## V0.5.3 Beta

- Fixed: the "Split Lines" box closed after every checkbox click.
- Downloaded files are named `AirfoilMatic_NACA4412_CGrid.txt` (airfoil and domain type in the name).

## V0.5.3 Beta (Türkçe)

- Düzeltildi: "Bölme Çizgileri" kutusu her onay kutusu tıklamasında kapanıyordu.
- İndirilen dosyaların adı `AirfoilMatic_NACA4412_CGrid.txt` şeklinde (kanat ve domain tipi adında).

## V0.5.2 Beta

- Geometry plots no longer fill a desktop screen (close-up at most 430 px high, full domain 520 px).
- Rectangular domain: top and bottom boundaries belong to the velocity inlet (the angle of attack is set through the velocity components); "(Wind Tunnel)" removed from its name. The "How to apply" boxes now list the Named Selections: `inlet`, `outlet`, `wall`.

## V0.5.2 Beta (Türkçe)

- Geometri grafikleri bilgisayar ekranını artık kaplamıyor (yakın çekim en fazla 430 px, akış alanı 520 px yüksekliğinde).
- Dikdörtgen domain: üst ve alt sınırlar velocity inlet'e dahil (hücum açısı hız bileşenleriyle veriliyor); adındaki "(Rüzgar Tüneli)" kaldırıldı. "Nasıl Uygulanır?" kutuları artık Named Selection adlarını veriyor: `inlet`, `outlet`, `wall`.

## V0.5.1 Beta

- Fixed: on Streamlit Cloud (Python 3.14) the app could stop at the first plot with "AttributeError … Series". Plotly read pandas while another server thread was still importing it; the app now imports pandas fully before drawing.

## V0.5.1 Beta (Türkçe)

- Düzeltildi: Streamlit Cloud'da (Python 3.14) uygulama ilk grafikte "AttributeError … Series" hatasıyla durabiliyordu. Plotly, pandas'ı sunucunun başka bir iş parçacığı henüz yüklerken okuyordu; uygulama artık çizimden önce pandas'ı tamamen yüklüyor.

## V0.5.0 Beta

Simpler app; no change to the geometry, mesh or Fluent calculations.

- Grid Independence (GCI) tab removed, together with its code and tests.
- Default inlet radius / inlet distance is 15 m (top and bottom distances of the rectangular domain too).
- Close-up plot sized like the full-domain plot: it shows the airfoil with a small margin at 1:1 and is much shorter on phones.
- The six split-line checkboxes are in a collapsed "Split Lines (6/6)" box in the sidebar.
- Mesh / y⁺ tab: the long notes (Inflation settings, trailing-edge limit, boundary-layer formula) moved into the "How to apply in Ansys Meshing" box; the division counts are shown under the cell-count card.
- Deprecated `use_container_width` replaced (no warnings in the logs).

## V0.5.0 Beta (Türkçe)

Daha sade uygulama; geometri, mesh ve Fluent hesaplarında değişiklik yok.

- Mesh Bağımsızlığı (GCI) sekmesi, kodu ve testleriyle birlikte kaldırıldı.
- Giriş yarıçapı / giriş uzaklığı varsayılanı 15 m (dikdörtgen domain'in üst ve alt uzaklıkları da).
- Yakın çekim grafiği akış alanı grafiği gibi boyutlanıyor: kanadı küçük bir payla 1:1 gösteriyor, telefonda çok daha kısa.
- Altı bölme çizgisi onay kutusu kenar çubuğunda kapalı bir "Bölme Çizgileri (6/6)" kutusunda.
- Mesh / y⁺ sekmesi: uzun notlar (Inflation ayarları, firar kenarı sınırı, sınır tabaka bağıntısı) "Ansys Meshing'de Nasıl Uygulanır?" kutusuna taşındı; bölüm sayıları hücre sayısı kartının altında.
- Eskiyen `use_container_width` değiştirildi (kayıtlarda uyarı yok).

## V0.4.3 Beta

- Switching between light and dark mode no longer breaks the page; the colors follow the switch without reloading.
- Light mode: greener sidebar and page gradient; table rows separated by thin emerald lines that fade to the right.
- Phones: a finger on a plot now scrolls the page instead of zooming the plot; the full-domain plot shows exactly the domain and its height follows the domain shape (it no longer shows a much larger area); the Ansys Inflation, quality and Fluent tables wrap to fit the screen; wide Edge Sizing tables become one card per row.
- Full-domain legend: the outer boundaries share one entry.

## V0.4.3 Beta (Türkçe)

- Açık ve koyu tema arasında geçiş yapınca sayfa artık bozulmuyor; renkler yeniden yüklemeden değişiyor.
- Açık tema: daha yeşil kenar çubuğu ve sayfa geçişi; tablo satırları sağa doğru solan ince zümrüt çizgilerle ayrılıyor.
- Telefon: grafiğin üzerinde parmakla kaydırınca grafik büyümüyor, sayfa kayıyor; akış alanı grafiği tam olarak domain'i gösteriyor ve yüksekliği domain'in şekline göre ayarlanıyor (artık çok daha büyük bir alan göstermiyor); Ansys Inflation, kalite ve Fluent tabloları ekrana sığacak şekilde satır kaydırıyor; geniş Edge Sizing tabloları her satır bir kart olacak şekilde gösteriliyor.
- Akış alanı grafiğinde dış sınırlar tek açıklama satırında.

## V0.4.2 Beta

New look; no change to the geometry, mesh or GCI calculations.

- Emerald theme for light and dark mode: page gradient, crystal (gradient) result card and buttons, emerald frames on inputs, cards, plots and tables. Plot colors follow the theme; the airfoil fill is a leading-to-trailing-edge gradient.
- Source Serif 4 font, self-hosted (works without Google Fonts, includes Turkish characters).
- Short header: "AirfoilMatic" with a small version badge and subtitle.
- Mesh / y⁺ tab: inputs grouped as 1 Flow condition, 2 Method and y⁺, 3 Growth; results shown as compact cards (Reynolds is no longer shown as a large result, since it is an input). "Advanced: chordwise cell sizes" is renamed "Airfoil Surface Element Sizes (Optional)" and explains what it sets.
- Consistent capitalization of headings (Turkish and English).
- Beta note restyled; developer name, university, LinkedIn and GitHub at the bottom of the sidebar and in the ⋮ → About menu; "Report a bug" opens GitHub Issues.
- Requires Streamlit 1.55–1.66 and Plotly ≥ 5.20.

## V0.4.2 Beta (Türkçe)

Yeni görünüm; geometri, mesh ve GCI hesaplarında değişiklik yok.

- Açık ve koyu tema için zümrüt yeşili: sayfa geçişi, kristal (geçişli) sonuç kartı ve düğmeler, giriş kutularında, kartlarda, grafiklerde ve tablolarda zümrüt çerçeveler. Grafik renkleri temaya uyar; kanat içi hücum kenarından firar kenarına renk geçişiyle dolar.
- Source Serif 4 yazı tipi, uygulamanın içinden yüklenir (Google Fonts gerekmez, Türkçe karakterler dahil).
- Kısa başlık: "AirfoilMatic", yanında küçük sürüm etiketi ve alt başlık.
- Mesh / y⁺ sekmesi: girişler 1 Akış Koşulu, 2 Yöntem ve y⁺, 3 Büyüme olarak gruplandı; sonuçlar küçük kartlarda (Reynolds bir girdi olduğu için artık büyük sonuç olarak gösterilmiyor). "Gelişmiş: veter yönü hücre boyutları" bölümünün adı "Kanat Yüzeyi Eleman Boyları (İsteğe Bağlı)" oldu ve neyi ayarladığını açıklıyor.
- Başlıklarda büyük/küçük harf tutarlı hale getirildi (Türkçe ve İngilizce).
- Beta notu yeniden tasarlandı; geliştirici adı, üniversite, LinkedIn ve GitHub kenar çubuğunun altında ve ⋮ → About menüsünde; "Report a bug" GitHub Issues sayfasını açar.
- Streamlit 1.55–1.66 ve Plotly ≥ 5.20 gerekir.

## V0.4.1 Beta

- Fluent setup helper: enter the free-stream speed; the app gives the inlet X/Y velocity components for the angle of attack, the Lift/Drag vectors, reference values, Reynolds and Mach, and warns if the Reynolds number differs from the Mesh / y⁺ tab or Mach > 0.3.
- The blunt trailing-edge option for NACA airfoils was removed (it did not help in the Ansys tests; blunt edges in uploaded files are still handled).
- The GitHub page now opens in Turkish (README.md); the English version is README.en.md.

## V0.4.1 Beta (Türkçe)

- Fluent ayar yardımcısı: serbest akış hızını girin; uygulama hücum açısına göre inlet X/Y hız bileşenlerini, Lift/Drag vektörlerini, referans değerleri, Reynolds ve Mach'ı verir; Reynolds Mesh / y⁺ sekmesindekinden farklıysa veya Mach > 0.3 ise uyarır.
- NACA profilleri için küt firar kenarı seçeneği kaldırıldı (Ansys denemelerinde yarar sağlamadı; yüklenen dosyalardaki küt kenarlar yine işleniyor).
- GitHub sayfası artık Türkçe açılıyor (README.md); İngilizcesi README.en.md.

## V0.4 Beta

Adds a mesh and y⁺ assistant, a mesh quality check, a Fluent helper and a grid-independence (GCI) calculator to the V0.3 domain generator, and splits the code into a tested package.

**New**
- Mesh / y⁺ tab: first-cell height for a target y⁺, boundary-layer estimate, Ansys Inflation settings or a mapped-mesh Edge Sizing table with the expected cell count.
- Mesh quality check (skewness, orthogonal quality, aspect ratio) against Ansys bands and Fluent limits.
- y⁺ correction from a first Fluent result; Fluent helper for the velocity direction and Lift/Drag vectors at an angle of attack.
- Grid Independence tab: GCI after Celik et al. (2008) with a Cl/Cd convergence plot and an optional suggested grid family.
- Selectable split lines (six checkboxes) with warnings for selections that cannot work.
- Optional blunt trailing edge (original NACA definition).
- Turkish / English interface; lengths shown in m and mm.

**Changed**
- Code moved from a single `app.py` into the `airfoilmatic/` package, with 48 automated tests.
- Full-cosine point distribution on the airfoil (clustered at both the leading and trailing edge).
- All four airfoil edges are written from leading edge to trailing edge, so one Edge Sizing bias acts the same way on the upper and lower edge.
- The C-grid inlet arc is centered on the 0.3c split line, so no short straight piece is left in front of the split.
- Dependencies pinned to tested ranges (Streamlit 1.40–1.66).

**Fixed**
- NACA 22xxx airfoils had about 24% too little camber (wrong mean-line constant k1; now 51.640).
- The custom-file parser could mix up upper and lower surface points for some point orders and blunt trailing edges; it was rewritten and is covered by tests (Selig, Lednicer, blunt TE).
- Invalid inputs show a clear message (in Turkish too) instead of an error trace.

**Known limitations**
- The Ansys meshing guidance is based on tests in Ansys 2024 R2 with a 1 m chord.
- With inflation, keep the trailing-edge element at about 0.003c or larger (about 1 mm failed, about 3 mm worked); blunt TE + inflation failed in our tests.
- Tested split-line selections: all six, and front axis + wake axis. A single line does not work.
- DesignModeler units must be meters (Units > Meter before import).
- Streamlit is pinned below 1.67.

## V0.4 Beta (Türkçe)

V0.3 domain üreticisine mesh ve y⁺ asistanı, mesh kalite kontrolü, Fluent yardımcısı ve mesh bağımsızlığı (GCI) hesabı eklendi; kod test edilmiş bir pakete ayrıldı.

**Yeni**
- Mesh / y⁺ sekmesi: hedef y⁺ için ilk hücre yüksekliği, sınır tabaka tahmini, Ansys Inflation ayarları ya da tahmini hücre sayısıyla mapped mesh Edge Sizing tablosu.
- Ansys bantlarına ve Fluent sınırlarına göre mesh kalite kontrolü (skewness, orthogonal quality, aspect ratio).
- İlk Fluent sonucundan y⁺ düzeltme; hücum açısı için hız yönü ve Lift/Drag vektörlerini veren Fluent yardımcısı.
- Mesh Bağımsızlığı sekmesi: Celik vd. (2008) ile GCI, Cl/Cd yakınsama grafiği ve isteğe bağlı önerilen ağ ailesi.
- Seçilebilir bölme çizgileri (altı onay kutusu), çalışmayacak seçimler için uyarılar.
- İsteğe bağlı küt firar kenarı (orijinal NACA tanımı).
- Türkçe / İngilizce arayüz; uzunluklar m ve mm olarak.

**Değişenler**
- Kod tek `app.py` dosyasından 48 otomatik testli `airfoilmatic/` paketine taşındı.
- Kanatta tam kosinüs nokta dağılımı (hücum ve firar kenarında sık).
- Dört kanat kenarı da hücum kenarından firar kenarına doğru yazılır; tek bir Edge Sizing biası üst ve alt kenarda aynı davranır.
- C-Grid giriş yayı 0.3c bölme çizgisine merkezlendi; bölmenin önünde kısa düz parça kalmaz.
- Bağımlılıklar test edilen aralıklara sabitlendi (Streamlit 1.40–1.66).

**Düzeltilenler**
- NACA 22xxx profillerinde kamburluk yaklaşık %24 eksikti (ortalama çizgi sabiti k1 yanlıştı; artık 51.640).
- Özel dosya okuyucu bazı nokta sıralamalarında ve küt firar kenarlarında üst ve alt yüzey noktalarını karıştırabiliyordu; yeniden yazıldı ve testlerle kontrol ediliyor (Selig, Lednicer, küt TE).
- Geçersiz girdilerde hata dökümü yerine (Türkçe de) açık bir mesaj gösteriliyor.

**Bilinen sınırlamalar**
- Ansys mesh önerileri, 1 m veterle Ansys 2024 R2'de yapılan denemelere dayanır.
- Inflation'da firar kenarı elemanını yaklaşık 0.003c veya daha büyük tutun (yaklaşık 1 mm başarısız oldu, yaklaşık 3 mm çalıştı); küt TE + inflation denemelerimizde başarısız oldu.
- Denenmiş bölme çizgisi seçimleri: altısı birden ve ön eksen + iz ekseni. Tek çizgi çalışmaz.
- DesignModeler birimi metre olmalı (içe aktarmadan önce Units > Meter).
- Streamlit 1.67'nin altına sabitlendi.
