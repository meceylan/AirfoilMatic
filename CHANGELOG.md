# Changelog

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
