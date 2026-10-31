"""User-interface strings (Turkish / English).

Every key has a "tr" and an "en" entry. Keys are referenced with t("key") in
app.py, or indirectly through curve / edge-group keys produced by the
topology and mesh modules.
"""

LANGS = {"tr": "Türkçe", "en": "English"}

STRINGS = {
    'subtitle': {
        "tr": '2B CFD Domain Generator',
        "en": '2D CFD Domain Generator',
    },
    'beta_warning': {
        "tr": "{stage} v{version}\nÇıktıları Ansys'te kontrol edin.",
        "en": '{stage} v{version}\nCheck the outputs in Ansys.',
    },
    'tab_geometry': {
        "tr": 'Geometri',
        "en": 'Geometry',
    },
    'tab_mesh': {
        "tr": 'Mesh / y⁺',
        "en": 'Mesh / y⁺',
    },
    'source': {
        "tr": 'Kanat Veri Kaynağı',
        "en": 'Airfoil Source',
    },
    'source_naca': {
        "tr": 'NACA (4 veya 5 haneli)',
        "en": 'NACA (4- or 5-digit)',
    },
    'source_file': {
        "tr": 'Özel Kanat (.dat / .txt)',
        "en": 'Custom Airfoil (.dat / .txt)',
    },
    'naca_code': {
        "tr": 'NACA Kodu',
        "en": 'NACA Code',
    },
    'upload': {
        "tr": 'Kanat Dosyası Yükle (Selig / Lednicer)',
        "en": 'Upload Airfoil File (Selig / Lednicer)',
    },
    'upload_info': {
        "tr": 'Lütfen bir kanat dosyası yükleyin.',
        "en": 'Please upload an airfoil file.',
    },
    'domain_type': {
        "tr": 'Akış Alanı (Domain) Tipi',
        "en": 'Domain Type',
    },
    'dom_cgrid': {
        "tr": 'C-Grid (Standart)',
        "en": 'C-Grid (Standard)',
    },
    'dom_rect': {
        "tr": 'Dikdörtgen',
        "en": 'Rectangle',
    },
    'chord': {
        "tr": 'Veter Uzunluğu (c) [m]',
        "en": 'Chord Length (c) [m]',
    },
    'r_inlet': {
        "tr": 'Giriş Yarıçapı (R) [m]',
        "en": 'Inlet Radius (R) [m]',
    },
    'l_inlet': {
        "tr": 'Giriş Uzaklığı [m]',
        "en": 'Inlet Distance [m]',
    },
    'l_wake': {
        "tr": "Arka İz Uzunluğu (TE'den itibaren) [m]",
        "en": 'Wake Length (from TE) [m]',
    },
    'l_top': {
        "tr": 'Üst Sınır Uzaklığı [m]',
        "en": 'Top Boundary Distance [m]',
    },
    'l_bottom': {
        "tr": 'Alt Sınır Uzaklığı [m]',
        "en": 'Bottom Boundary Distance [m]',
    },
    'download': {
        "tr": 'Ansys TXT İndir',
        "en": 'Download Ansys TXT',
    },
    'err_naca': {
        "tr": 'Lütfen geçerli 4 veya 5 haneli bir NACA kodu girin.',
        "en": 'Please enter a valid 4- or 5-digit NACA code.',
    },
    'err_geometry': {
        "tr": 'Kanat geometrisi oluşturulamadı: {msg}',
        "en": 'Could not build the airfoil geometry: {msg}',
    },
    'err_domain': {
        "tr": 'Akış alanı oluşturulamadı: {msg}',
        "en": 'Could not build the domain: {msg}',
    },
    'zoom_title': {
        "tr": 'Yakın Çekim: Kanat Profili ve Bölme Çizgileri',
        "en": 'Close-up: Airfoil and Split Lines',
    },
    'full_title': {
        "tr": 'Uzak Çekim: CFD Akış Alanı',
        "en": 'Full View: CFD Domain',
    },
    'x_axis': {
        "tr": 'X Koordinatı [m]',
        "en": 'X Coordinate [m]',
    },
    'y_axis': {
        "tr": 'Y Koordinatı [m]',
        "en": 'Y Coordinate [m]',
    },
    'blunt_info': {
        "tr": 'Küt firar kenarı algılandı (aralık = {gap:.5f} m). Firar kenarı ayrı bir kenarla kapatıldı.',
        "en": 'Blunt trailing edge detected (gap = {gap:.5f} m). It was closed with a separate edge.',
    },
    'geom_info': {
        "tr": 'Kanat X = {split}c noktasından 4 parçaya bölündü. Akış alanı 6 bloktan oluşur (Mapped Face Meshing için; C-Grid’de hepsi dört kenarlı, dikdörtgende ön bloklar için Side vertex gerekir).',
        "en": 'The airfoil is split into 4 segments at X = {split}c. The domain consists of 6 blocks (for Mapped Face Meshing; all four-sided for the C-grid, the rectangle’s front blocks need a Side vertex).',
    },
    'airfoil': {
        "tr": 'Kanat',
        "en": 'Airfoil',
    },
    'af_upper_front': {
        "tr": 'Kanat üst-ön',
        "en": 'Airfoil upper-front',
    },
    'af_upper_rear': {
        "tr": 'Kanat üst-arka',
        "en": 'Airfoil upper-rear',
    },
    'af_lower_front': {
        "tr": 'Kanat alt-ön',
        "en": 'Airfoil lower-front',
    },
    'af_lower_rear': {
        "tr": 'Kanat alt-arka',
        "en": 'Airfoil lower-rear',
    },
    'inlet': {
        "tr": 'Giriş (Inlet)',
        "en": 'Inlet',
    },
    'inlet_up': {
        "tr": 'Giriş üst yarı',
        "en": 'Inlet upper half',
    },
    'inlet_low': {
        "tr": 'Giriş alt yarı',
        "en": 'Inlet lower half',
    },
    'top': {
        "tr": 'Üst sınır',
        "en": 'Top boundary',
    },
    'bottom': {
        "tr": 'Alt sınır',
        "en": 'Bottom boundary',
    },
    'outlet': {
        "tr": 'Çıkış (Outlet)',
        "en": 'Outlet',
    },
    'outlet_up': {
        "tr": 'Çıkış üst yarı',
        "en": 'Outlet upper half',
    },
    'outlet_low': {
        "tr": 'Çıkış alt yarı',
        "en": 'Outlet lower half',
    },
    'top_front': {
        "tr": 'Üst sınır (giriş → bölme)',
        "en": 'Top boundary (inlet → split)',
    },
    'bottom_front': {
        "tr": 'Alt sınır (giriş → bölme)',
        "en": 'Bottom boundary (inlet → split)',
    },
    'top_mid': {
        "tr": 'Üst sınır (bölme → TE)',
        "en": 'Top boundary (split → TE)',
    },
    'bottom_mid': {
        "tr": 'Alt sınır (bölme → TE)',
        "en": 'Bottom boundary (split → TE)',
    },
    'top_wake': {
        "tr": 'Üst sınır (TE → çıkış)',
        "en": 'Top boundary (TE → outlet)',
    },
    'bottom_wake': {
        "tr": 'Alt sınır (TE → çıkış)',
        "en": 'Bottom boundary (TE → outlet)',
    },
    'front_axis': {
        "tr": 'Ön yatay eksen',
        "en": 'Front axis',
    },
    'split_up': {
        "tr": 'Üst dikey (bölme)',
        "en": 'Upper vertical (split)',
    },
    'split_low': {
        "tr": 'Alt dikey (bölme)',
        "en": 'Lower vertical (split)',
    },
    'te_up': {
        "tr": 'Üst dikey (TE)',
        "en": 'Upper vertical (TE)',
    },
    'te_low': {
        "tr": 'Alt dikey (TE)',
        "en": 'Lower vertical (TE)',
    },
    'wake_axis': {
        "tr": 'Arka iz ekseni',
        "en": 'Wake axis',
    },
    'te_closure': {
        "tr": 'Küt firar kenarı',
        "en": 'Blunt trailing edge',
    },
    'mesh_intro': {
        "tr": 'Akış koşulunu ve hedef y⁺ değerini girin, mesh yönteminizi seçin. **Inflation** modu Ansys Inflation ayarlarını, **Mapped** modu her kenar için Edge Sizing tablosunu verir.',
        "en": 'Enter the flow condition and target y⁺, then choose your meshing method. **Inflation** mode gives Ansys Inflation settings; **Mapped** mode gives an Edge Sizing table for every edge.',
    },
    'flow_input': {
        "tr": 'Akış koşulu girişi',
        "en": 'Flow condition input',
    },
    'flow_re': {
        "tr": 'Reynolds sayısı',
        "en": 'Reynolds number',
    },
    'flow_vel': {
        "tr": 'Hız + akışkan özellikleri',
        "en": 'Velocity + fluid properties',
    },
    're': {
        "tr": 'Reynolds sayısı (veter tabanlı)',
        "en": 'Reynolds number (chord based)',
    },
    'velocity': {
        "tr": 'Serbest akış hızı U∞ [m/s]',
        "en": 'Free-stream velocity U∞ [m/s]',
    },
    'density': {
        "tr": 'Yoğunluk ρ [kg/m³]',
        "en": 'Density ρ [kg/m³]',
    },
    'viscosity': {
        "tr": 'Dinamik viskozite μ [Pa·s]',
        "en": 'Dynamic viscosity μ [Pa·s]',
    },
    'y_plus': {
        "tr": 'Hedef y⁺',
        "en": 'Target y⁺',
    },
    'growth': {
        "tr": 'Duvar-normal büyüme oranı',
        "en": 'Wall-normal growth ratio',
    },
    'advanced': {
        "tr": 'Kanat Yüzeyi Eleman Boyları (İsteğe Bağlı)',
        "en": 'Airfoil Surface Element Sizes (Optional)',
    },
    'advanced_help': {
        "tr": 'Kanat kenarlarındaki Edge Sizing tablosunu belirler: hücum kenarında, bölme çizgisinde (0.3c) ve firar kenarında istenen eleman boyu, veterin kesri olarak (0.001 = 1 m veterde 1 mm) ve iz ekseninde elemanların büyüme oranı. Duvardan dışarı doğru büyüme (y⁺, ilk katman) bunlardan bağımsızdır. Varsayılanlar çoğu analiz için uygundur.',
        "en": 'Sets the Edge Sizing table on the airfoil edges: the element size wanted at the leading edge, at the split line (0.3c) and at the trailing edge, as a fraction of the chord (0.001 = 1 mm on a 1 m chord), and the growth ratio along the wake axis. Wall-normal growth (y⁺, first layer) does not depend on these. The defaults suit most analyses.',
    },
    'boundaries': {
        "tr": 'Dış sınırlar',
        "en": 'Outer boundaries',
    },
    'm_counts_short': {
        "tr": 'normal {n_normal} · ön {n_front} · arka {n_rear} · iz {n_wake} bölüm',
        "en": 'normal {n_normal} · front {n_front} · rear {n_rear} · wake {n_wake} divisions',
    },
    'named_sel': {
        "tr": "**Sınır adları (Named Selection):** Meshing'de giriş kenarını (C-Grid'de yay, dikdörtgende sol kenar) üst ve alt sınırla birlikte `inlet`, arka sınırı `outlet`, kanat kenarlarını `wall` olarak adlandırın. Fluent'te `inlet` velocity-inlet, `outlet` pressure-outlet, `wall` duvar olur. Dikdörtgen domain'de de üst ve alt sınır `inlet`'e dahildir: hücum açısı hız bileşenleriyle verildiği için akış bu sınırlardan girip çıkabilmelidir; symmetry veya wall burada akışı yanlış yönlendirir.",
        "en": "**Boundary names (Named Selections):** in Meshing, name the inlet edge (the arc for the C-grid, the left edge for the rectangle) together with the top and bottom boundaries `inlet`, the rear boundary `outlet` and the airfoil edges `wall`. In Fluent `inlet` becomes a velocity inlet, `outlet` a pressure outlet and `wall` a wall. The rectangle's top and bottom also belong to `inlet`: the angle of attack is set by the velocity components, so flow must be able to cross them; symmetry or wall there would turn the flow.",
    },
    'step_flow': {
        "tr": 'Akış Koşulu',
        "en": 'Flow Condition',
    },
    'step_method': {
        "tr": 'Yöntem ve y⁺',
        "en": 'Method and y⁺',
    },
    'step_growth': {
        "tr": 'Büyüme',
        "en": 'Growth',
    },
    'dev_label': {
        "tr": 'Geliştirici',
        "en": 'Developer',
    },
    'ds_le': {
        "tr": 'Hücum kenarı hücre boyu / c',
        "en": 'Leading-edge cell size / c',
    },
    'ds_split': {
        "tr": 'Bölme çizgisindeki hücre boyu / c',
        "en": 'Cell size at split line / c',
    },
    'ds_te': {
        "tr": 'Firar kenarı hücre boyu / c',
        "en": 'Trailing-edge cell size / c',
    },
    'wake_growth': {
        "tr": 'İz bölgesi büyüme oranı',
        "en": 'Wake growth ratio',
    },
    'm_dy1': {
        "tr": 'İlk hücre yüksekliği',
        "en": 'First cell height',
    },
    'm_delta': {
        "tr": 'Sınır tabaka kalınlığı (TE)',
        "en": 'Boundary layer thickness (TE)',
    },
    'm_nbl': {
        "tr": 'Sınır tabaka içindeki hücre',
        "en": 'Cells inside boundary layer',
    },
    'm_cells': {
        "tr": 'Tahmini toplam hücre',
        "en": 'Estimated total cells',
    },
    'delta_note': {
        "tr": "Sınır tabaka kalınlığı türbülanslı düz levha bağıntısıyla (δ ≈ 0.37·c·Re⁻⁰·²) tahmin edilir; laminer karşılığı δ ≈ {lam}. İlk hücre yüksekliği Schlichting sürtünme katsayısı ile hesaplanır. Fluent y⁺'ı hücre merkezinde raporladığı için çözümde görülen değer yaklaşık yarısı olur. Sonuçları her zaman Fluent'te y⁺ konturu ile kontrol edin.",
        "en": 'Boundary layer thickness uses the turbulent flat-plate estimate (δ ≈ 0.37·c·Re⁻⁰·²); the laminar value is δ ≈ {lam}. First cell height uses the Schlichting skin-friction correlation. Fluent reports y⁺ at the cell centroid, so the value in the solution will be about half. Always check the y⁺ contour in Fluent.',
    },
    'warn_growth': {
        "tr": 'Bazı kenarlarda büyüme oranı {g:.3f} > {lim}. Kalite için daha küçük bir oran önerilir.',
        "en": 'Some edges have a growth ratio of {g:.3f} > {lim}. A smaller ratio is recommended.',
    },
    'warn_bl': {
        "tr": 'Sınır tabaka içinde yalnızca {n} hücre var. Genelde en az 20–30 hücre önerilir; büyüme oranını düşürün.',
        "en": 'Only {n} cells inside the boundary layer. At least 20–30 cells are usually recommended; lower the growth ratio.',
    },
    'table_title': {
        "tr": 'Edge Sizing Tablosu',
        "en": 'Edge Sizing Table',
    },
    'col_group': {
        "tr": 'Kenar grubu',
        "en": 'Edge group',
    },
    'col_edges': {
        "tr": 'Kenarlar',
        "en": 'Edges',
    },
    'col_length': {
        "tr": 'Uzunluk [m]',
        "en": 'Length [m]',
    },
    'col_n': {
        "tr": 'Number of Divisions',
        "en": 'Number of Divisions',
    },
    'col_bias': {
        "tr": 'Bias Factor',
        "en": 'Bias Factor',
    },
    'col_small': {
        "tr": 'Küçük eleman tarafı',
        "en": 'Smaller-element side',
    },
    'col_dsmin': {
        "tr": 'En küçük eleman',
        "en": 'Smallest element',
    },
    'col_dsmax': {
        "tr": 'En büyük eleman',
        "en": 'Largest element',
    },
    'col_growth': {
        "tr": 'Büyüme oranı',
        "en": 'Growth ratio',
    },
    'download_csv': {
        "tr": 'Tabloyu CSV Olarak İndir',
        "en": 'Download Table as CSV',
    },
    'g_af_front': {
        "tr": 'Kanat ön (LE → bölme)',
        "en": 'Airfoil front (LE → split)',
    },
    'g_af_rear': {
        "tr": 'Kanat arka (bölme → TE)',
        "en": 'Airfoil rear (split → TE)',
    },
    'g_inlet': {
        "tr": 'Giriş',
        "en": 'Inlet',
    },
    'g_top_front': {
        "tr": 'Üst/alt sınır ön',
        "en": 'Top/bottom front',
    },
    'g_top_mid': {
        "tr": 'Üst/alt sınır orta',
        "en": 'Top/bottom middle',
    },
    'g_wake': {
        "tr": 'İz bölgesi (yatay)',
        "en": 'Wake (streamwise)',
    },
    'g_normal': {
        "tr": 'Duvar-normal',
        "en": 'Wall-normal',
    },
    'g_outlet': {
        "tr": 'Çıkış',
        "en": 'Outlet',
    },
    'g_te_closure': {
        "tr": 'Küt firar kenarı',
        "en": 'Blunt TE',
    },
    'end_le': {
        "tr": 'Hücum kenarı',
        "en": 'Leading edge',
    },
    'end_te': {
        "tr": 'Firar kenarı tarafı',
        "en": 'Trailing-edge side',
    },
    'end_uniform': {
        "tr": '— (eşit aralık)',
        "en": '— (uniform)',
    },
    'end_airfoil': {
        "tr": 'Kanat tarafı',
        "en": 'Airfoil side',
    },
    'end_axis': {
        "tr": 'İz ekseni tarafı',
        "en": 'Wake-axis side',
    },
    'howto_title': {
        "tr": "Ansys Meshing'de Nasıl Uygulanır?",
        "en": 'How to Apply in Ansys Meshing',
    },
    'howto': {
        "tr": "1. Projection ile yüzeyi 6 bloğa böldükten sonra Meshing'i açın.\n2. Tüm yüzeylere **Face Meshing** ekleyin (Mapped Mesh = Yes).\n3. Tablodaki her satır için **Edge Sizing** ekleyin: Type = *Number of Divisions*, Behavior = *Hard*, Bias Type = tek yönlü, Bias Factor = tablodaki değer.\n4. Küçük elemanın doğru uçta olduğunu kontrol edin; ters ise kenarı **Reverse Bias** listesine ekleyin.\n5. Mesh'i oluşturduktan sonra hücre sayısının tahmini değere yakın olduğunu ve Fluent'te y⁺'ı kontrol edin.",
        "en": '1. After splitting the surface into 6 blocks with Projection, open Meshing.\n2. Add **Face Meshing** to every face (Mapped Mesh = Yes).\n3. Add an **Edge Sizing** for each table row: Type = *Number of Divisions*, Behavior = *Hard*, single-direction Bias Type, Bias Factor = table value.\n4. Check the smallest element is at the right end; if not, add the edge to **Reverse Bias**.\n5. After meshing, confirm the cell count is close to the estimate and check y⁺ in Fluent.',
    },
    'rect_note': {
        "tr": "Dikdörtgen domain'de ön bloklar 5 köşelidir. Face Meshing ayarında giriş köşesini (üst ve alt köşe) **Side** olarak işaretleyin; giriş yarısı ve ön sınır parçası birlikte kanat ön kenarının karşısına düşer.",
        "en": 'In the rectangular domain the front blocks have 5 corners. In Face Meshing, set the inlet corners (top and bottom) as **Side** vertices; the inlet half and the front boundary segment together form the side opposite the airfoil front.',
    },
    'split_lines': {
        "tr": 'Bölme çizgileri',
        "en": 'Split lines',
    },
    'mesh_method': {
        "tr": 'Mesh yöntemi',
        "en": 'Meshing method',
    },
    'method_inflation': {
        "tr": 'Inflation (quad-dominant)',
        "en": 'Inflation (quad-dominant)',
    },
    'method_mapped': {
        "tr": 'Mapped (Edge Sizing)',
        "en": 'Mapped (Edge Sizing)',
    },
    'coverage': {
        "tr": 'Inflation kalınlığı / sınır tabaka (δ)',
        "en": 'Inflation thickness / boundary layer (δ)',
    },
    'low_re_note': {
        "tr": "Re < 5×10⁵: sınır tabakanın büyük kısmı laminer olabilir. Tahminler türbülanslı düz levha bağıntısına dayanır; Fluent'te y⁺'ı mutlaka kontrol edin.",
        "en": 'Re < 5×10⁵: much of the boundary layer may be laminar. The estimates use turbulent flat-plate correlations; check y⁺ in Fluent.',
    },
    'infl_first': {
        "tr": 'İlk katman kalınlığı',
        "en": 'First layer height',
    },
    'infl_layers': {
        "tr": 'Gereken katman sayısı',
        "en": 'Required layers',
    },
    'infl_table_title': {
        "tr": 'Ansys Inflation Ayarları',
        "en": 'Ansys Inflation Settings',
    },
    'col_setting': {
        "tr": 'Ayar',
        "en": 'Setting',
    },
    'col_value': {
        "tr": 'Değer',
        "en": 'Value',
    },
    'infl_total': {
        "tr": 'Toplam inflation kalınlığı',
        "en": 'Total inflation thickness',
    },
    'infl_last': {
        "tr": 'Son katman kalınlığı',
        "en": 'Last layer thickness',
    },
    'infl_note': {
        "tr": "Maximum Layers tam olarak hesaplanan katman sayısıdır; First Layer Thickness seçeneğinde Ansys bu sayının tamamını oluşturur, bu yüzden fazla girmeyin. **Genel Element Size uzak alan içindir** (≈ 0.5c): küçük yapmayın. **Defeature Size ve Curvature Min Size'ı da tablodaki değerlere elle girin:** varsayılanları genel boyuttan türetilir (0.5 m için 2.5 mm ve 5 mm) ve kanattaki milimetrik elemanlardan büyüktür; Ansys bu durumda uyarı verir. Bunları en küçük elemanın altında tutmak güvenli bir alışkanlıktır. Kanat çevresindeki incelik genel boyuttan değil, aşağıdaki Edge Sizing'lerden ve Growth Rate ile kademeli geçişten gelir. Genel boyutu milimetre mertebesine çekmek tüm domain'i o boyda doldurur; hücre sayısı patlar ve iz eksenindeki büyük elemanlarla küçük çevre elemanları arasında bozuk üçgenler oluşur.",
        "en": 'Maximum Layers is exactly the computed layer count; with First Layer Thickness Ansys builds all of them, so do not enter more. **The global Element Size is for the far field** (≈ 0.5c): do not make it small. **Also enter Defeature Size and Curvature Min Size from the table by hand:** their defaults are derived from the global size (2.5 mm and 5 mm for 0.5 m) and are larger than the millimetre-sized elements on the airfoil, which makes Ansys warn. Keeping them below the smallest element is a safe habit. The refinement around the airfoil comes from the Edge Sizings below and the gradual transition set by the Growth Rate. Setting the global size to millimetres fills the whole domain at that size, the cell count explodes, and badly shaped triangles appear where large wake-axis elements meet small surrounding ones.',
    },
    'howto_infl': {
        "tr": "1. Kenar çubuğunda istediğiniz bölme çizgilerini seçin (inflation için zorunlu değil; tek çizgi seçmeyin) ve TXT'yi indirin. DesignModeler'da dosyayı **Units = Meter** iken aktarın, seçtiğiniz çizgilerle Projection yapın.\n2. Mesh → Details → **Bounding Box Diagonal** onlarca metre mertebesinde olmalı (varsayılan domain'de Ansys ≈ 46.6 m gösterdi). Değer binde biri kadar küçükse geometri milimetre olarak okunmuştur; bu durumda mesher belleği tüketip çöker.\n3. Method: **Quadrilateral Dominant**, Geometry = tüm yüzeyler.\n4. **Inflation**: Geometry = tüm yüzeyler, Boundary = **kanat kenarları** (iz ekseni dışa aktarıldıysa isteğe bağlı olarak o da), Inflation Option = First Layer Thickness, değerler tablodan. Küt firar kenarı yüzünü Boundary'ye eklemeyin.\n5. Mesh → Sizing: Element Size ≈ 0.5c, Growth Rate 1.15, Defeature ve Curvature Min Size tablodan. Edge Sizing'leri tablodan **Behavior = Soft** ile ekleyin.\n6. Sorun çıkarsa kontrolleri tek tek ekleyerek deneyin (önce yalnızca yöntem, sonra Edge Sizing'ler, sonra Inflation); hangi adımda bozulduğu sebebi gösterir.\n7. Not: Inflation, **Mapped Face Meshing** ile birlikte çalışmaz.",
        "en": '1. Choose the split lines you want in the sidebar (optional for inflation; do not select a single line) and download the TXT. Import it in DesignModeler with **Units = Meter** and run Projection with the selected lines.\n2. Mesh → Details → **Bounding Box Diagonal** should be tens of meters (Ansys showed ≈ 46.6 m for the default domain). If it is a thousand times smaller the geometry was read in millimeters, and the mesher runs out of memory and crashes.\n3. Method: **Quadrilateral Dominant**, Geometry = all faces.\n4. **Inflation**: Geometry = all faces, Boundary = **airfoil edges** (optionally the wake axis too, if exported), Inflation Option = First Layer Thickness, values from the table. Do not add a blunt TE face to the Boundary.\n5. Mesh → Sizing: Element Size ≈ 0.5c, Growth Rate 1.15, Defeature and Curvature Min Size from the table. Add the Edge Sizings from the table with **Behavior = Soft**.\n6. If something fails, add the controls one at a time (method only, then the Edge Sizings, then Inflation); the step that fails shows the cause.\n7. Note: Inflation does not work together with **Mapped Face Meshing**.',
    },
    'yplus_fix_title': {
        "tr": 'y⁺ Düzeltme (Fluent Sonucundan)',
        "en": 'y⁺ Correction (from a Fluent Result)',
    },
    'yplus_fix_help': {
        "tr": "İlk çözümden sonra kanat üzerindeki y⁺ değerini girin; y⁺ ilk hücre yüksekliğiyle yaklaşık doğru orantılı olduğu için hedefe ulaşmak gereken yeni ilk hücre yüksekliği hesaplanır. Hedef y⁺ burada da Fluent'in raporladığı değer (hücre merkezi) olarak yorumlanır.",
        "en": 'Enter the y⁺ seen on the airfoil after a first solution; since y⁺ scales roughly linearly with first-cell height, the height needed for the target is computed. The target is interpreted here as the y⁺ Fluent reports (cell centroid).',
    },
    'yplus_used_dy': {
        "tr": 'Kullanılan ilk hücre yüksekliği [m]',
        "en": 'First cell height used [m]',
    },
    'yplus_seen': {
        "tr": "Fluent'te görülen y⁺ (ortalama ya da maksimum)",
        "en": 'y⁺ seen in Fluent (average or max)',
    },
    'yplus_fix_result': {
        "tr": 'Hedef y⁺ = {target:g} için yeni ilk hücre yüksekliği: **{dy}**',
        "en": 'New first cell height for target y⁺ = {target:g}: **{dy}**',
    },
    'fluent_title': {
        "tr": 'Fluent Ayar Yardımcısı (Hücum Açısı)',
        "en": 'Fluent Setup Helper (Angle of Attack)',
    },
    'aoa': {
        "tr": 'Hücum açısı α [°]',
        "en": 'Angle of attack α [°]',
    },
    'fl_vel_dir': {
        "tr": 'Inlet → Magnitude and Direction (yön)',
        "en": 'Inlet → Magnitude and Direction (direction)',
    },
    'fl_vel_comp': {
        "tr": 'Inlet → Velocity Specification = Components',
        "en": 'Inlet → Velocity Specification = Components',
    },
    'fl_drag': {
        "tr": 'Drag kuvvet vektörü',
        "en": 'Drag force vector',
    },
    'fl_lift': {
        "tr": 'Lift kuvvet vektörü',
        "en": 'Lift force vector',
    },
    'fl_ref_len': {
        "tr": 'Reference Values → Length',
        "en": 'Reference Values → Length',
    },
    'fl_ref_area': {
        "tr": 'Reference Values → Area',
        "en": 'Reference Values → Area',
    },
    'fl_ref_vel': {
        "tr": 'Reference Values → Velocity',
        "en": 'Reference Values → Velocity',
    },
    'fl_ref_rho': {
        "tr": 'Reference Values → Density',
        "en": 'Reference Values → Density',
    },
    'fluent_note': {
        "tr": "Hücum açısı geometri döndürülmeden, giriş hızının yönüyle verilir. Inlet'te Velocity Specification = Components seçip X ve Y hızlarını girin (ya da Magnitude and Direction ile hız büyüklüğü + yön). Lift ve Drag raporlarının (Report Definitions → Force) vektörlerini de bu değerlere çevirin: (1, 0) / (0, 1) bırakılırsa Cd'ye kaldırmanın bir kısmı karışır. Reference Values'ta Velocity ve Density'nin girişle aynı olduğundan emin olun.",
        "en": 'The angle of attack is set through the inlet velocity direction, without rotating the geometry. At the inlet choose Velocity Specification = Components and enter the X and Y velocities (or Magnitude and Direction with the speed and the direction). Set the Lift and Drag report vectors (Report Definitions → Force) to these values too: leaving them at (1, 0) / (0, 1) mixes part of the lift into Cd. Make sure Reference Values Velocity and Density match the inlet.',
    },
    'quality_title': {
        "tr": 'Mesh Kalite Kontrolü (Skewness / Orthogonal Quality / Aspect Ratio)',
        "en": 'Mesh Quality Check (Skewness / Orthogonal Quality / Aspect Ratio)',
    },
    'quality_help': {
        "tr": "Değerleri Ansys Meshing → Mesh → Quality → Mesh Metric ya da Fluent → Mesh → Quality'den alın. Boş bıraktıklarınız değerlendirilmez.",
        "en": 'Take the values from Ansys Meshing → Mesh → Quality → Mesh Metric or Fluent → Mesh → Quality. Empty fields are skipped.',
    },
    'q_sk_max': {
        "tr": 'Skewness (maks.)',
        "en": 'Skewness (max)',
    },
    'q_sk_avg': {
        "tr": 'Skewness (ort.)',
        "en": 'Skewness (avg)',
    },
    'q_oq_min': {
        "tr": 'Orthogonal Quality (min.)',
        "en": 'Orthogonal Quality (min)',
    },
    'q_oq_avg': {
        "tr": 'Orthogonal Quality (ort.)',
        "en": 'Orthogonal Quality (avg)',
    },
    'q_metric': {
        "tr": 'Metrik',
        "en": 'Metric',
    },
    'q_rating': {
        "tr": 'Ansys sınıfı',
        "en": 'Ansys rating',
    },
    'q_fluent': {
        "tr": 'Fluent sınırı',
        "en": 'Fluent limit',
    },
    'q_excellent': {
        "tr": 'Mükemmel',
        "en": 'Excellent',
    },
    'q_very_good': {
        "tr": 'Çok iyi',
        "en": 'Very good',
    },
    'q_good': {
        "tr": 'İyi',
        "en": 'Good',
    },
    'q_acceptable': {
        "tr": 'Kabul edilebilir',
        "en": 'Acceptable',
    },
    'q_bad': {
        "tr": 'Kötü',
        "en": 'Bad',
    },
    'q_unacceptable': {
        "tr": 'Kabul edilemez',
        "en": 'Unacceptable',
    },
    'q_verdict_ok': {
        "tr": 'Mesh kalitesi iyi; çözüme geçebilirsiniz.',
        "en": 'Mesh quality is good; you can proceed to the solution.',
    },
    'q_verdict_check': {
        "tr": 'Fluent sınırları sağlanıyor ama en kötü hücreler sınıra yakın. Mesh Metrics grafiğinde düşük çubuğa tıklayıp bu hücrelerin nerede olduğuna bakın.',
        "en": 'Fluent limits are met but the worst cells are close to them. Click the low bar in the Mesh Metrics chart to see where these cells are.',
    },
    'q_verdict_bad': {
        "tr": "Fluent sınırları sağlanıyor ama en kötü hücreler Ansys'in 'kötü' bandında. Az sayıdaysa ve kanattan uzaktaysa genelde sorun değildir; firar kenarı veya hücum kenarı gibi kritik bir yerdeyse düzeltin.",
        "en": "Fluent limits are met but the worst cells are in Ansys' 'bad' band. If they are few and away from the airfoil this is usually fine; fix them if they sit at a critical spot such as the TE or LE.",
    },
    'q_verdict_fail': {
        "tr": "Fluent'in önerdiği sınır aşılıyor (maks. skewness < 0.95, min. orthogonal quality > 0.01). Çözüm ıraksayabilir veya hatalı olabilir; bu hücreleri düzeltin.",
        "en": "Fluent's recommended limit is exceeded (max skewness < 0.95, min orthogonal quality > 0.01). The solution may diverge or be inaccurate; fix these cells.",
    },
    'q_ar_expected': {
        "tr": '**Aspect ratio:** Bu ayarlarla duvardaki ilk hücrelerin beklenen aspect ratio değeri hücum kenarında ≈ {ar_le:,.0f}, kanat ortasında ≈ {ar_mid:,.0f}. İz bölgesinde daha da yüksek olur. Sınır tabaka ve iz hücrelerinde bu normaldir.',
        "en": '**Aspect ratio:** With these settings the first wall cells have an expected aspect ratio of ≈ {ar_le:,.0f} at the LE and ≈ {ar_mid:,.0f} mid-chord, and even higher in the wake. That is normal for boundary-layer and wake cells.',
    },
    'q_explain': {
        "tr": "**Ne işe yararlar?**\n- **Skewness (0 = ideal, 1 = bozuk):** Hücrenin eşkenar/kare şeklinden ne kadar saptığı. Yüksek skewness, akı ve gradyan hesabında hata ve yakınsama sorunu doğurur. Ansys bantları: 0–0.25 mükemmel, 0.25–0.50 çok iyi, 0.50–0.80 iyi, 0.80–0.94 kabul edilebilir, 0.95–0.97 kötü, 0.98–1 kabul edilemez. Fluent: maks. < 0.95.\n- **Orthogonal Quality (1 = ideal, 0 = bozuk):** Yüz normalleri ile hücre merkezlerini birleştiren vektörlerin ne kadar hizalı olduğu. Fluent'in çözücüsü en çok buna duyarlıdır. Ansys bantları: 0–0.001 kabul edilemez, 0.001–0.14 kötü, 0.15–0.20 kabul edilebilir, 0.20–0.69 iyi, 0.70–0.95 çok iyi, 0.95–1 mükemmel. Fluent: min. > 0.01, ortalama çok daha yüksek.\n- **Aspect Ratio:** En uzun kenar / en kısa kenar. Sınır tabakada akış yönünde uzun, duvara dik ince hücreler istenir; bu yüzden 100–10 000 arası değerler orada normaldir. Fluent sayısal bir sınır vermez; önemli olan, akışın hızla değiştiği bölgelerde aspect ratio'nun ani değişmemesidir.\n- **Ortalama ve en kötü değer:** Ortalama genel resmi, maks./min. en kötü hücreyi gösterir. Az sayıda kötü hücre kanattan uzaktaysa genelde tolere edilir.\n- **Mesh bağımsızlığı ile ilişkisi:** Kalite kontrolü her ağ için ayrı yapılır ve GCI'dan önce gelir. Kaba, orta ve ince ağların üçü de bu sınırları sağlamalıdır; aksi hâlde GCI'daki fark çözünürlükten değil kötü hücrelerden gelebilir.",
        "en": "**What do they mean?**\n- **Skewness (0 = ideal, 1 = degenerate):** How far a cell deviates from an equilateral/square shape. High skewness causes flux and gradient errors and convergence problems. Ansys bands: 0–0.25 excellent, 0.25–0.50 very good, 0.50–0.80 good, 0.80–0.94 acceptable, 0.95–0.97 bad, 0.98–1 unacceptable. Fluent: max < 0.95.\n- **Orthogonal Quality (1 = ideal, 0 = degenerate):** How well face normals align with the vectors joining cell centers. Fluent's solver is most sensitive to this. Ansys bands: 0–0.001 unacceptable, 0.001–0.14 bad, 0.15–0.20 acceptable, 0.20–0.69 good, 0.70–0.95 very good, 0.95–1 excellent. Fluent: min > 0.01, with a much higher average.\n- **Aspect Ratio:** Longest / shortest edge. Boundary-layer cells should be long in the flow direction and thin normal to the wall, so values of 100–10,000 are normal there. Fluent gives no numeric limit; what matters is avoiding sudden changes where the flow changes rapidly.\n- **Average vs worst value:** The average shows the overall picture; max/min shows the worst cell. A few bad cells away from the airfoil are usually tolerated.\n- **Relation to grid independence:** The quality check is done for each grid separately and comes before the GCI. All three grids should meet these limits; otherwise differences in the GCI may come from bad cells rather than resolution.",
    },
    'infl_edges_title': {
        "tr": 'Kanat ve İz Ekseni Edge Sizing',
        "en": 'Airfoil and Wake-Axis Edge Sizing',
    },
    'infl_edges_note': {
        "tr": "**Firar kenarı:** inflation'da firar kenarındaki eleman ≈ 0.003c'nin altına indirilmez (c = 1 m için 3 mm). Ansys 2024 R2 denemelerimizde (c = 1 m) yaklaşık 1 mm'de mesh oluşmadı veya bozuk hücre çıktı, yaklaşık 3 mm'de çalıştı; başka veter uzunlukları denenmedi. Daha ince TE çözünürlüğü için mapped mesh kullanın. Type = Number of Divisions, Bias Type = tek yönlü (`--- -- -` simgesi, çift yönlü değil), Bias Factor = tablodaki değer; Behavior = Soft (inflation olan kenarlarda Hard desteklenmez). Kanat kenarlarının hepsi dosyada hücum kenarından firar kenarına doğru yazılır, bu yüzden üst ve alt kenar aynı yönde davranır. Doğru dağılım: **kanat ön** kenarlarında elemanlar hücum kenarında küçük, 0.3c'ye doğru büyür; **kanat arka** kenarlarında 0.3c'de büyük, firar kenarına doğru küçülür; **iz ekseninde** firar kenarında küçük, çıkışa doğru büyür. Bir grup ters çıkarsa o kenarları aynı Edge Sizing'in **Reverse Bias** alanına ekleyin. Böylece 0.3c'de ön ve arka kenarın elemanları, TE'de de kanat ve iz ekseninin ilk elemanları aynı boyda olur. Inflation'ın ilk hücreleri çok ince olduğu için duvardaki eleman boyunun ani değişmesi doğrudan düşük orthogonal quality olarak görünür.",
        "en": '**Trailing edge:** with inflation the TE element is kept at ≈ 0.003c or more (3 mm for c = 1 m). In our Ansys 2024 R2 tests (c = 1 m) about 1 mm failed to mesh or produced degenerate cells and about 3 mm worked; other chord lengths were not tested. Use the mapped mesh for finer TE resolution. Type = Number of Divisions, single-direction Bias Type (the `--- -- -` icon, not the two-sided one), Bias Factor = table value; Behavior = Soft (Hard is not supported on inflated edges). All airfoil edges are written from leading edge to trailing edge, so the upper and lower edges behave the same way. Correct distribution: on the **airfoil front** edges elements are small at the LE and grow towards 0.3c; on the **airfoil rear** edges they are large at 0.3c and shrink towards the TE; on the **wake axis** they are small at the TE and grow towards the outlet. If a group comes out reversed, add those edges to the **Reverse Bias** field of the same Edge Sizing. This way the front and rear elements match at 0.3c, and the airfoil and wake-axis elements match at the TE. Because the first inflation cells are very thin, any jump in surface element size shows up directly as low orthogonal quality.',
    },
    'glob_size': {
        "tr": 'Genel Element Size (Mesh → Sizing)',
        "en": 'Global Element Size (Mesh → Sizing)',
    },
    'glob_growth': {
        "tr": 'Genel Growth Rate (Mesh → Sizing)',
        "en": 'Global Growth Rate (Mesh → Sizing)',
    },
    'split_mode': {
        "tr": 'Bölme Çizgileri',
        "en": 'Split Lines',
    },
    'split_mode_help': {
        "tr": 'Mapped mesh için altısı da gerekir. Inflation için altısı ya da ön eksen + iz ekseni. Tek çizgi seçmeyin.',
        "en": 'Mapped meshing needs all six. For inflation: all six, or front axis + wake axis. Do not select a single line.',
    },
    'q_pass': {
        "tr": 'Sağlanıyor',
        "en": 'Met',
    },
    'q_fail': {
        "tr": 'Aşıldı',
        "en": 'Exceeded',
    },
    'geom_info_partial': {
        "tr": 'Seçilen bölme çizgileriyle yüzey {n} parçaya ayrılır. Mapped mesh için altı çizginin hepsi gerekir.',
        "en": 'The selected split lines divide the surface into {n} faces. Mapped meshing needs all six lines.',
    },
    'warn_single_line': {
        "tr": 'Yalnızca bir bölme çizgisi seçili ({line}). Tek çizgi yüzeyi ikiye bölmez, yüzün içinde yarık olarak kalır; Ansys bu kenardan inflation oluşturamaz ve mesh bozulabilir. Denenmiş seçimler: altı çizginin hepsi ya da ön eksen + iz ekseni.',
        "en": 'Only one split line is selected ({line}). A single line does not divide the surface and stays as a slit inside one face; Ansys cannot inflate from it and the mesh may break. Tested selections: all six lines, or front axis + wake axis.',
    },
    'warn_mapped_lines': {
        "tr": 'Mapped mesh için altı bölme çizgisinin hepsi gerekir. Kenar çubuğunda eksik çizgileri işaretleyin; aksi hâlde bazı yüzler dört kenarlı olmaz ve Mapped Face Meshing çalışmaz.',
        "en": 'Mapped meshing needs all six split lines. Tick the missing lines in the sidebar; otherwise some faces are not four-sided and Mapped Face Meshing fails.',
    },
    'warn_blunt_infl': {
        "tr": "Küt firar kenarı + inflation, Ansys 2024 R2 denemelerimizde başarısız oldu (TE yüzü Boundary'deyken mesh oluşmadı, değilken TE köşelerinde bozuk hücreler çıktı). Inflation için sivri firar kenarı veya mapped mesh kullanın.",
        "en": 'Blunt trailing edge + inflation failed in our Ansys 2024 R2 tests (with the TE face as a boundary the mesh failed; without it, degenerate cells appeared at the TE corners). Use a sharp trailing edge or the mapped mesh for inflation.',
    },
    'geom_info_one': {
        "tr": "Yüzey tek parça kalır (bölme çizgisi yok ya da yalnızca bir çizgi seçili). Mapped mesh için altı çizginin hepsi gerekir.",
        "en": "The surface stays as a single face (no split lines, or only one selected). Mapped meshing needs all six lines.",
    },
    'infl_edges_title_af': {"tr": "Kanat Edge Sizing", "en": "Airfoil Edge Sizing"},
    'fl_speed': {
        "tr": 'Serbest akış hızı U∞ [m/s]',
        "en": 'Free-stream speed U∞ [m/s]',
    },
    'fl_speed_help': {
        "tr": "Varsayılan değer, Mesh / y⁺ sekmesindeki Reynolds sayısını veren hızdır (Fluent'in varsayılan havası ile). Kendi hızınızı girebilirsiniz; Reynolds farklı çıkarsa uyarı gösterilir.",
        "en": "The default is the speed that gives the Reynolds number of the Mesh / y⁺ tab (with Fluent's default air). You can enter your own; a warning is shown if the Reynolds number differs.",
    },
    'fl_re_mach': {
        "tr": 'Bu hızla Reynolds ve Mach',
        "en": 'Reynolds and Mach at this speed',
    },
    'fl_re_mismatch': {
        "tr": "Bu hız Re = {re_fl:.4e} veriyor; Mesh / y⁺ sekmesindeki Re = {re_mesh:.4e}. İlk hücre yüksekliği o Re'ye göre hesaplandığı için ikisini eşitleyin.",
        "en": 'This speed gives Re = {re_fl:.4e}; the Mesh / y⁺ tab uses Re = {re_mesh:.4e}. The first-cell height is based on that Re, so make them match.',
    },
    'fl_mach_warn': {
        "tr": "Mach = {m:.2f} > 0.3: sıkıştırılabilirlik etkileri önemlidir; Fluent'te yoğunluğu ideal gaz olarak tanımlayın.",
        "en": 'Mach = {m:.2f} > 0.3: compressibility matters; use ideal-gas density in Fluent.',
    },
}


# Turkish versions of the (English) error messages raised by the core modules.
ERRORS_TR = {
    'Speed, chord, density and viscosity must be positive': 'Hız, veter, yoğunluk ve viskozite pozitif olmalı',
    'Reynolds number must be at least 1000': 'Reynolds sayısı en az 1000 olmalı',
    'Edge is shorter than the requested cell size': 'Kenar, istenen hücre boyundan kısa; hücre boylarını küçültün',
    'NACA 4-digit code must be 4 digits': 'NACA 4 haneli kod 4 rakamdan oluşmalı',
    'Thickness must be between 1% and 40%': 'Kalınlık %1 ile %40 arasında olmalı',
    'Cambered NACA 4-digit needs a camber position (2nd digit) > 0': "Kamburlu NACA 4 haneli profilde kamburluk konumu (2. hane) 0'dan büyük olmalı",
    'Surface extends past the trailing edge (camber/thickness too large)': 'Yüzey firar kenarını aşıyor (kamburluk/kalınlık çok büyük)',
    'NACA 5-digit code must be 5 digits': 'NACA 5 haneli kod 5 rakamdan oluşmalı',
    'Unsupported NACA 5-digit camber position (only standard, non-reflexed series: 2nd-3rd digits 10, 20, 30, 40, 50)': 'Desteklenmeyen NACA 5 haneli kamburluk konumu (yalnızca standart, refleks olmayan seri: 2.-3. haneler 10, 20, 30, 40, 50)',
    'NACA code must have 4 or 5 digits': 'NACA kodu 4 veya 5 haneli olmalı',
    'File does not contain enough coordinate rows': 'Dosyada yeterli koordinat satırı yok',
    'Could not find the leading edge inside the point loop': 'Nokta dizisinde hücum kenarı bulunamadı',
    'Each surface needs at least 3 distinct points': 'Her yüzeyde en az 3 farklı nokta olmalı',
    'Invalid chord in file': 'Dosyadaki veter uzunluğu geçersiz',
    'Split location must be between 0.05c and 0.9c': 'Bölme konumu 0.05c ile 0.9c arasında olmalı',
    'Skewness must be between 0 and 1': 'Skewness 0 ile 1 arasında olmalı',
    'Orthogonal quality must be between 0 and 1': 'Orthogonal quality 0 ile 1 arasında olmalı',
    'Wake length must be at least 0.5c': 'İz uzunluğu en az 0.5c olmalı',
    'Inlet radius must be larger than the chord': 'Giriş yarıçapı veter uzunluğundan büyük olmalı',
    'Top/bottom boundaries must be at least 0.5c away from the airfoil': 'Üst/alt sınırlar kanattan en az 0.5c uzakta olmalı',
    'Inlet must be at least 0.5c upstream of the leading edge': 'Giriş, hücum kenarının en az 0.5c önünde olmalı',
    'math range error': 'Sayısal taşma: ayarlar uç değerlerde; büyüme oranını veya hücre boylarını değiştirin',
}


def tr_error(exc, lang):
    """Translate a core-module error message; unknown messages are returned as-is."""
    msg = str(exc)
    if lang == "tr":
        return ERRORS_TR.get(msg, msg)
    return msg


def tr(key, lang, **kwargs):
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry.get("en") or key
    return text.format(**kwargs) if kwargs else text
