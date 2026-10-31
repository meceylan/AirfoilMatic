# Changelog

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
