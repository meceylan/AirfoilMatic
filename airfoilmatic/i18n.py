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
    'tab_auto': {
        "tr": 'Otomasyon',
        "en": 'Automation',
    },
    'auto_intro': {
        "tr": "Fluent'te çok açıyı art arda koşmak için: açı taraması tablosu, açıyı adım adım değiştiren journal ve tarama bitince report file'dan polar. Hız, yoğunluk ve veter Mesh / y⁺ sekmesindeki Fluent yardımcısından gelir.",
        "en": "For running many angles in a row in Fluent: the angle sweep table, the journal that steps the angle, and the polar from the report file once the sweep is done. Speed, density and chord come from the Fluent helper on the Mesh / y⁺ tab.",
    },
    'auto_need_speed': {
        "tr": "Tarama ve journal için Mesh / y⁺ sekmesindeki Fluent yardımcısında geçerli bir serbest akış hızı gerekir.",
        "en": "The sweep and the journal need a valid free-stream speed in the Fluent helper on the Mesh / y⁺ tab.",
    },
    'polar_title': {
        "tr": "Polar (report file'dan)",
        "en": 'Polar (from the report file)',
    },
    'polar_note': {
        "tr": "Taramada Fluent'in yazdığı report file'ı (.out) yükleyin; içinde açı (expression report, ör. alfa = aoa), Cl ve Cd sütunları olmalı. Her açı, açının sabit kaldığı iterasyon bloğudur; değer bloğun son N iterasyonunun ortalamasıdır, Δ ise aynı iterasyonlardaki en büyük – en küçük farkıdır. Aynı açı sonradan yeniden koşulduysa en son blok, kayıttan sürdürülen taramada tekrar yazılan iterasyonlarda sonraki satırlar kullanılır. Fluent 2024 R2'nin report file biçimiyle (11 açılı NACA 0012 taraması) denendi.",
        "en": "Upload the report file (.out) Fluent wrote during the sweep; it needs an angle column (an expression report, e.g. alfa = aoa), Cl and Cd. Each angle is the block of iterations in which the angle stays the same; the value is the mean of the block's last N iterations and Δ the max – min over the same iterations. If an angle was run again later the latest block is used; iterations written twice by a sweep continued from a saved case use the later lines. Tried with the report file format of Fluent 2024 R2 (11-angle NACA 0012 sweep).",
    },
    'polar_upload': {
        "tr": "Report file (.out); kayıttan sürdürülen taramada hepsi",
        "en": 'Report file (.out); for a sweep continued from a saved case, all of them',
    },
    'polar_upload_help': {
        "tr": "Kayıttan sürdürülen bir taramada Fluent kalan kısmı <ad>_<iterasyon>.out adlı yeni bir dosyaya yazar (ör. surdurme.out + surdurme_1929.out). İkisini birlikte seçin; aynı iterasyon iki dosyada varsa daha geç başlayan dosyanınki kullanılır. Yalnızca aynı report definition'ın dosyalarını seçin.",
        "en": 'For a sweep continued from a saved case Fluent writes the rest to a new file <name>_<iteration>.out (e.g. surdurme.out + surdurme_1929.out). Select both; where both hold the same iteration, the file that starts later is used. Select files of the same report definition only.',
    },
    'polar_error': {
        "tr": 'Polar çıkarılamadı: {msg}',
        "en": 'Could not build the polar: {msg}',
    },
    'polar_col_angle': {
        "tr": 'Açı sütunu',
        "en": 'Angle column',
    },
    'polar_col_cl': {
        "tr": 'Cl sütunu',
        "en": 'Cl column',
    },
    'polar_col_cd': {
        "tr": 'Cd sütunu',
        "en": 'Cd column',
    },
    'polar_unit': {
        "tr": 'Açı sütununun birimi',
        "en": 'Unit of the angle column',
    },
    'polar_unit_help': {
        "tr": "[deg] birimli bir named expression'ın expression report'u Fluent'te radyan olarak yazılır (−4° → −0.0698).",
        "en": 'An expression report of a named expression in [deg] is written in radians by Fluent (−4° → −0.0698).',
    },
    'polar_last_n': {
        "tr": 'Ortalama: son N iterasyon',
        "en": 'Mean over the last N iterations',
    },
    'polar_last_n_help': {
        "tr": 'Her açının son N iterasyonunun ortalaması alınır. Bundan kısa bloklar "az iterasyon" olarak işaretlenir.',
        "en": 'Each angle uses the mean of its last N iterations. Shorter blocks are marked "few iterations".',
    },
    'polar_cl_tol': {
        "tr": 'Salınım sınırı ΔCl',
        "en": 'Oscillation limit ΔCl',
    },
    'polar_cl_tol_help': {
        "tr": "Son N iterasyonda Cl bundan fazla oynuyorsa (ya da Cd ortalamasının %1'inden fazla) açı \"salınıyor\" sayılır.",
        "en": 'An angle counts as "oscillating" if Cl moves more than this over the last N iterations (or Cd more than 1 % of its mean).',
    },
    'polar_steady': {
        "tr": 'oturdu',
        "en": 'steady',
    },
    'polar_osc': {
        "tr": 'salınıyor',
        "en": 'oscillating',
    },
    'polar_short': {
        "tr": 'az iterasyon',
        "en": 'few iterations',
    },
    'polar_iters': {
        "tr": 'İterasyon (aralık)',
        "en": 'Iterations (range)',
    },
    'polar_status': {
        "tr": 'Durum',
        "en": 'Status',
    },
    'polar_steps': {
        "tr": 'Zaman adımı (aralık)',
        "en": 'Time steps (range)',
    },
    'polar_transient': {
        "tr": "Transient report file (ilk sütun Time Step): satırlar zaman adımıdır; \"son N\" son N zaman adımıdır. Salınan bir çözümde N'yi birkaç tam periyodu kapsayacak kadar seçin (yarım periyot ortalamayı kaydırır).",
        "en": 'Transient report file (first column Time Step): rows are time steps and "last N" means the last N time steps. For an oscillating solution choose N to cover several whole periods (half a period shifts the mean).',
    },
    'polar_model_note': {
        "tr": "Model notu (Fluent 2024 R2, NACA 0012, Re 2×10⁶, Ladson NASA TM-4074 ile): tam türbülanslı SST k-ω 15°'ye kadar oturdu ve Cl'yi deneyden %2.5–3.5 yüksek verdi; stall'u geç verdi: 16.02°'de akış bağlı (Cl 1.45), 16.99°'de URANS ile de bağlı (Cl 1.46; deneyde stall, Cl 1.09). Transition SST 8°'den sonra steady çözümde salındı. Stall yakınındaki değerleri deneyle doğrulamadan kullanmayın.",
        "en": 'Model note (Fluent 2024 R2, NACA 0012, Re 2×10⁶, against Ladson NASA TM-4074): fully turbulent SST k-ω settled up to 15° with Cl 2.5–3.5 % above the experiment, and gave stall late: attached flow at 16.02° (Cl 1.45) and at 16.99° also with URANS (Cl 1.46; the experiment has stalled, Cl 1.09). Transition SST oscillated in the steady solution above 8°. Do not use values near stall without checking them against experiment.',
    },
    'polar_warn_osc': {
        "tr": "Salınan açılar: {angles}°. Steady çözüm oturmamış; değer son iterasyonların ortalamasıdır ve güvenilirliği düşüktür. Steady çözümde salınım her zaman stall demek değildir: iterasyonların fiziksel zaman karşılığı yoktur. Salınan açıyı URANS (transient) ile kontrol edin. Fluent 2024 R2'de (NACA 0012, SST k-ω) 16.99°'de steady Cl 0.30–1.35 arasında salındı, URANS'ta akış bağlı akışa oturdu (Cl 1.46).",
        "en": "Oscillating angles: {angles}°. The steady solution has not settled; the value is the mean of the last iterations and is less reliable. An oscillating steady solution is not always stall: iterations have no physical time. Check an oscillating angle with URANS (transient). In Fluent 2024 R2 (NACA 0012, SST k-ω) the steady Cl at 16.99° swung between 0.30 and 1.35, while URANS settled to attached flow (Cl 1.46).",
    },
    'polar_warn_short': {
        "tr": "{angles}° açılarında {n} iterasyondan az veri var; ortalama eldeki iterasyonlardan alındı.",
        "en": 'Angles {angles}° have fewer than {n} iterations; the mean uses the iterations there are.',
    },
    'polar_repeats': {
        "tr": 'Bazı açılar dosyada birden fazla kez koşulmuş; her biri için en son blok kullanıldı.',
        "en": 'Some angles were run more than once in the file; the latest block of each is used.',
    },
    'polar_csv': {
        "tr": 'Poları CSV olarak indir',
        "en": 'Download the polar as CSV',
    },
    'source': {
        "tr": 'Kanat Veri Kaynağı',
        "en": 'Airfoil Source',
    },
    'source_search': {
        "tr": 'Profil ara (NACA + UIUC veritabanı)',
        "en": 'Search sections (NACA + UIUC database)',
    },
    'search_label': {
        "tr": 'Profil adı',
        "en": 'Section name',
    },
    'search_help': {
        "tr": '4 ya da 5 haneli NACA kodları NACA denklemlerinden çizilir (201 nokta, keskin firar kenarı). Diğer profiller UIUC veritabanından seçilmiş 300 profilden gelir. Boşluk, tire ve parantez önemli değil: "63-215", "n63215" ve "NACA 63-215" aynı profili bulur.',
        "en": '4- and 5-digit NACA codes are drawn from the NACA equations (201 points, sharp trailing edge). Every other section comes from 300 sections selected from the UIUC database. Spaces, dashes and brackets do not matter: "63-215", "n63215" and "NACA 63-215" find the same section.',
    },
    'search_placeholder': {
        "tr": 'ör. 4412, e387, clark y, 63-215',
        "en": 'e.g. 4412, e387, clark y, 63-215',
    },
    'results': {
        "tr": 'Bulunan profiller ({n})',
        "en": 'Sections found ({n})',
    },
    'not_found': {
        "tr": '"{q}" veritabanında yok. Geçerli bir 4/5 haneli NACA kodu ya da seçkideki bir profil adı yazın; listede olmayan bir profili dosya olarak yükleyebilirsiniz. Denklemle yalnızca 4 haneli ve standart (refleks olmayan) 5 haneli kodlar çizilir; refleks kodlar (ör. 23112) ve 6 serisi (ör. 64-012) yalnızca seçkide varsa bulunur.',
        "en": '"{q}" is not in the database. Type a valid 4/5-digit NACA code or the name of a section in the selection; a section that is not listed can be uploaded as a file. Only 4-digit and standard (non-reflexed) 5-digit codes are drawn from the equations; reflexed codes (e.g. 23112) and the 6-series (e.g. 64-012) are found only if they are in the selection.',
    },
    'search_empty': {
        "tr": 'Bir profil adı yazın ya da 🎲 ile rastgele seçin.',
        "en": 'Type a section name or pick one at random with 🎲.',
    },
    'random_filters': {
        "tr": 'Rastgele seçim filtreleri',
        "en": 'Random pick filters',
    },
    'f_thickness': {
        "tr": 'Maksimum kalınlık (% veter)',
        "en": 'Maximum thickness (% chord)',
    },
    'f_camber': {
        "tr": 'Kamburluk',
        "en": 'Camber',
    },
    'cam_any': {
        "tr": 'Hepsi',
        "en": 'Any',
    },
    'cam_sym': {
        "tr": 'Simetrik',
        "en": 'Symmetric',
    },
    'cam_cambered': {
        "tr": 'Kamburlu',
        "en": 'Cambered',
    },
    'f_family': {
        "tr": 'Aile (boş = hepsi)',
        "en": 'Family (empty = all)',
    },
    'f_family_ph': {
        "tr": 'Aile seçin',
        "en": 'Choose families',
    },
    'pool_size': {
        "tr": 'Filtrelere uyan profil: {n}',
        "en": 'Sections matching the filters: {n}',
    },
    'dice_empty': {
        "tr": 'Filtrelere uyan profil yok; filtreleri genişletin.',
        "en": 'No section matches the filters; widen them.',
    },
    'info_naca': {
        "tr": '**{title}**: NACA denklemlerinden çizildi. Maks. kalınlık %{t:.1f}c, x = {xt:.2f}c.',
        "en": '**{title}**: drawn from the NACA equations. Max. thickness {t:.1f}% c at x = {xt:.2f}c.',
    },
    'info_uiuc': {
        "tr": '**{title}** ({family}, dosya `{id}.dat`): UIUC Airfoil Coordinates Database. Maks. kalınlık %{t:.1f}c (x = {xt:.2f}c), maks. kamburluk %{camber:.1f}c (x = {xc:.2f}c), {points} nokta.',
        "en": '**{title}** ({family}, file `{id}.dat`): UIUC Airfoil Coordinates Database. Max. thickness {t:.1f}% c (x = {xt:.2f}c), max. camber {camber:.1f}% c (x = {xc:.2f}c), {points} points.',
    },
    'source_file': {
        "tr": 'Özel Kanat (.dat / .txt / .csv)',
        "en": 'Custom Airfoil (.dat / .txt / .csv)',
    },
    'upload': {
        "tr": 'Kanat Dosyası Yükle (Selig / Lednicer)',
        "en": 'Upload Airfoil File (Selig / Lednicer)',
    },
    'mirror_x': {
        "tr": 'Profili x yönünde çevir',
        "en": 'Mirror the profile in x',
    },
    'mirror_x_help': {
        "tr": 'Akış soldan gelir; hücum kenarı solda olmalı. Dosyada hücum kenarı sağdaysa bu kutu işaretlenir.',
        "en": 'The flow comes from the left, so the leading edge must be at the left. The box is ticked when the file has its leading edge at the right.',
    },
    'note_mirrored': {
        "tr": 'Dosyada hücum kenarı sağda görünüyordu; profil x yönünde çevrildi. Yanlışsa kenar çubuğundaki “Profili x yönünde çevir” kutusunu kaldırın.',
        "en": 'The file seems to have its leading edge at the right, so the profile was mirrored in x. If that is wrong, untick “Mirror the profile in x” in the sidebar.',
    },
    'note_reversed': {
        "tr": 'Profilin yuvarlak ucu sağda görünüyor: akış firar kenarına çarpar. Kenar çubuğundaki “Profili x yönünde çevir” kutusunu kontrol edin.',
        "en": 'The round end of the profile seems to be at the right: the flow would meet the trailing edge first. Check “Mirror the profile in x” in the sidebar.',
    },
    'note_few_points': {
        "tr": 'Dosyada yüzey başına yalnızca {n} nokta var. DesignModeler eğriyi bu noktalardan geçirir; {need} noktanın altında hücum kenarı köşeli çıkar. Daha sık noktalı bir dosya kullanın.',
        "en": 'The file has only {n} points per surface. DesignModeler fits its curve through these points; below {need} points the leading edge comes out angular. Use a file with more points.',
    },
    'note_tilt': {
        "tr": 'Dosyadaki profil eğik duruyor: hücum kenarı–firar kenarı doğrusu x ekseniyle {angle:+.1f}° yapıyor (artı = burun yukarı). Bu açı, Fluent yardımcısına gireceğiniz hücum açısına eklenir. Hücum kenarı en öndeki nokta alınır; çok kamburlu bir burunda (ör. NACA 9940) eğik olmayan bir dosya da 1–2° gösterebilir.',
        "en": 'The profile in the file is tilted: the leading edge–trailing edge line makes {angle:+.1f}° with the x axis (positive = nose up). This angle adds to the angle of attack you enter in the Fluent helper. The leading edge is taken as the most forward point; on a strongly cambered nose (e.g. NACA 9940) an untilted file can also show 1–2°.',
    },
    'note_overlap': {
        "tr": 'Dosyada üst ve alt yüzey birbirinin içine giriyor (en fazla {amount:.2g}c, çoğunlukla firar kenarında). Eğriler kesişirse DesignModeler yüzey oluşturamaz; bu yüzden yüzeyler en çok bu kadar birbirinden uzaklaştırıldı. Geometri bundan fazla değişmedi.',
        "en": 'In this file the upper and lower surfaces overlap (by up to {amount:.2g}c, mostly at the trailing edge). Curves that cross keep DesignModeler from building a surface, so the surfaces were moved apart by at most that much. The shape did not change by more than this.',
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
    'domain_help': {
        "tr": "Yüksek Cl'de uzak alan sınırı taşıma kuvvetini etkiler: Cl arttıkça yarıçapı büyütüp sonucun değişmediğini kontrol edin. Plan düşük hız (Mach < 0.3) içindir.",
        "en": 'At high Cl the far-field boundary affects the lift: as Cl grows, enlarge the radius and check that the result does not change. The plan is for low speed (Mach < 0.3).',
    },
    'r_inlet': {
        "tr": 'Giriş Yarıçapı (R) [× veter]',
        "en": 'Inlet Radius (R) [× chord]',
    },
    'l_inlet': {
        "tr": 'Giriş Uzaklığı [× veter]',
        "en": 'Inlet Distance [× chord]',
    },
    'l_wake': {
        "tr": "Arka İz Uzunluğu (TE'den itibaren) [× veter]",
        "en": 'Wake Length (from TE) [× chord]',
    },
    'domain_in_m': {
        "tr": 'Metre olarak: R = {r:g} m, iz = {w:g} m',
        "en": 'In metres: R = {r:g} m, wake = {w:g} m',
    },
    'domain_in_m_rect': {
        "tr": 'Metre olarak: giriş {r:g} m, iz {w:g} m, üst {top:g} m, alt {bot:g} m',
        "en": 'In metres: inlet {r:g} m, wake {w:g} m, top {top:g} m, bottom {bot:g} m',
    },
    'l_top': {
        "tr": 'Üst Sınır Uzaklığı [× veter]',
        "en": 'Top Boundary Distance [× chord]',
    },
    'l_bottom': {
        "tr": 'Alt Sınır Uzaklığı [× veter]',
        "en": 'Bottom Boundary Distance [× chord]',
    },
    'download_sc': {
        "tr": 'SpaceClaim TXT İndir',
        "en": 'Download SpaceClaim TXT',
    },
    'download_sc_help': {
        "tr": "SpaceClaim TXT: aynı domain (soldaki birimde), SpaceClaim'in nokta-eğri metin biçiminde; File → Open ile açın, her çizgi ayrı eğri gelir. SpaceClaim yardımına göre yazıldı, henüz denenmedi.",
        "en": 'SpaceClaim TXT: the same domain (in the unit chosen on the left) in SpaceClaim\'s point-curve text format; open it with File → Open, every line comes in as its own curve. Written from the SpaceClaim help; not tried yet.',
    },
    'profile_title': {
        "tr": 'Sadece kanat profili',
        "en": 'Airfoil profile only',
    },
    'profile_help': {
        "tr": "Alan (domain) olmadan yalnızca profilin üst ve alt yüzeyi. **DesignModeler:** Concept → 3D Curve → Coordinates File ile okuyun (Units, kenar çubuğunda seçtiğiniz çıktı birimiyle aynı olsun), sonra Concept → Surfaces From Edges. **SolidWorks:** Insert → Curve → Curve Through XYZ Points ile önce üst, sonra alt dosyayı seçin (belge birimi kenar çubuğundaki çıktı birimiyle aynı olsun). Arka kenar kalınsa iki ucu bir çizgiyle birleştirin. **SpaceClaim:** File → Open (ya da Insert) ile TXT dosyasını açın; üst, alt (ve kalın arka kenarda uç çizgisi) ayrı eğriler olarak gelir. Bu biçim SpaceClaim yardımındaki nokta-eğri metin dosyasına göre yazıldı, henüz denenmedi; hata verirse satır numarasını bildirin.",
        "en": "Only the upper and lower surface of the airfoil, without a domain. **DesignModeler:** read it with Concept → 3D Curve → Coordinates File (set Units to the output unit chosen in the sidebar), then Concept → Surfaces From Edges. **SolidWorks:** Insert → Curve → Curve Through XYZ Points, pick the upper file, then the lower one (document units = the output unit in the sidebar). With a blunt trailing edge, join the two ends with a line. **SpaceClaim:** open the TXT file with File → Open (or Insert); the upper, lower (and, for a blunt trailing edge, the end line) come in as separate curves. This format follows the point-curve text file in the SpaceClaim help and has not been tried yet; if it gives an error, report the line number.",
    },
    'out_unit': {
        "tr": 'İndirilen dosyaların birimi',
        "en": 'Unit of the downloaded files',
    },
    'out_unit_help': {
        "tr": "Domain (Ansys ve SpaceClaim TXT) ve profil dosyalarındaki koordinatlar bu birimde yazılır; dosyanın içinde birim yazmaz, DesignModeler / SpaceClaim / SolidWorks'te aynı birimi seçin. Mesh / y⁺ sekmesindeki ölçüler hem metre hem milimetre olarak verilir.",
        "en": 'The coordinates of the domain (Ansys and SpaceClaim TXT) and profile files are written in this unit; the file does not state it, so choose the same unit in DesignModeler / SpaceClaim / SolidWorks. The sizes on the Mesh / y⁺ tab are given in both metres and millimetres.',
    },
    'profile_dm': {
        "tr": 'DesignModeler TXT',
        "en": 'DesignModeler TXT',
    },
    'profile_sc': {
        "tr": 'SpaceClaim TXT',
        "en": 'SpaceClaim TXT',
    },
    'profile_sw': {
        "tr": 'SolidWorks (ZIP)',
        "en": 'SolidWorks (ZIP)',
    },
    'download': {
        "tr": 'Ansys TXT İndir',
        "en": 'Download Ansys TXT',
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
    'flow_mach': {
        "tr": 'Mach + Reynolds',
        "en": 'Mach + Reynolds',
    },
    'mach': {
        "tr": 'Mach sayısı',
        "en": 'Mach number',
    },
    'mach_state': {
        "tr": 'Hız = {u:.5g} m/s, yoğunluk = {rho:.5g} kg/m³, viskozite = {mu:.4e} Pa·s (Sutherland), statik basınç = {p:.0f} Pa. Yoğunluk Re\'den, basınç yoğunluktan hesaplanır.',
        "en": 'Speed = {u:.5g} m/s, density = {rho:.5g} kg/m³, viscosity = {mu:.4e} Pa·s (Sutherland), static pressure = {p:.0f} Pa. The density follows from Re, the pressure from the density.',
    },
    'fl_ff_mach': {
        "tr": 'Pressure Far-Field: Mach Number',
        "en": 'Pressure Far-Field: Mach Number',
    },
    'fl_ff_pressure': {
        "tr": 'Pressure Far-Field: Gauge Pressure (Operating Pressure = 0 Pa)',
        "en": 'Pressure Far-Field: Gauge Pressure (Operating Pressure = 0 Pa)',
    },
    'fl_ff_temp': {
        "tr": 'Pressure Far-Field: Temperature',
        "en": 'Pressure Far-Field: Temperature',
    },
    'fl_ff_note': {
        "tr": "Pressure far-field girişi için: Mach, yukarıdaki akış yönü bileşenleri, Gauge Pressure ve Temperature (Operating Pressure = 0 Pa varsayımıyla; Operating Pressure başka ise onu çıkarın), enerji denklemi açık, yoğunluk ideal gaz, viskozite Sutherland. Basınç Re'yi tutturmak için seçilir. Dış sınırın tamamını (outlet dahil) aynı değerlerle pressure-far-field yapın. Fluent 2024 R2'de NACA 0012, 15c C-Grid, Transition SST ile M 0.3 ve 0.5'te bu şekilde ve Run Calculation → Time Scale Factor 0.2 ile temiz yakınsadı. M 0.3'te Operating Pressure 0 / gauge 101325 ile Operating Pressure 101325 / gauge 0 aynı sonucu verdi (double precision). Time Scale Factor 1 (varsayılan) ile de aynı Cl çıktı ama residual'lar takıldı ve Convergence Conditions dolmadı; 0.2 önerilir.",
        "en": 'For a pressure-far-field inlet: Mach, the flow-direction components above, Gauge Pressure and Temperature (assuming Operating Pressure = 0 Pa; subtract it otherwise), energy equation on, ideal-gas density, Sutherland viscosity. The pressure is chosen to match Re. Make the whole outer boundary (the outlet too) pressure-far-field with the same values. In Fluent 2024 R2 (NACA 0012, 15c C-grid, Transition SST) this converged cleanly at M 0.3 and 0.5 with Run Calculation → Time Scale Factor 0.2. At M 0.3, Operating Pressure 0 / gauge 101325 and Operating Pressure 101325 / gauge 0 gave the same result (double precision). With Time Scale Factor 1 (the default) Cl was the same but the residuals stalled and the Convergence Conditions were never met; 0.2 is recommended.',
    },
    'warn_ff_low_mach': {
        "tr": "Mach {m:.2f} < 0.3: bu hızda velocity-inlet + pressure-outlet kullanın (hız bileşenleri Fluent yardımcısında). Fluent 2024 R2'de NACA 0012, 15c C-Grid ile pressure-far-field M 0.15'te sıfırdan farklı hücum açısında oturmadı (akışın sığ açıyla çıktığı düz kenar ve köşesi kararsızlaştı); aynı kurulum M 0.3 ve 0.5'te temiz yakınsadı. Aşağıdaki far-field değerleri yalnızca bilgi içindir.",
        "en": 'Mach {m:.2f} < 0.3: at this speed use velocity-inlet + pressure-outlet (velocity components in the Fluent helper). In Fluent 2024 R2 (NACA 0012, 15c C-grid) a pressure far field did not converge at M 0.15 at a non-zero angle of attack (the straight edge where the flow leaves at a shallow angle, and its corner, went unstable); the same setup converged cleanly at M 0.3 and 0.5. The far-field values below are for information only.',
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
    'advanced_help_infl': {
        "tr": "Kanat kenarlarındaki Edge Sizing tablosunu belirler: hücum kenarında, bölme çizgisinde (0.3c) ve firar kenarında istenen eleman boyu, veterin kesri olarak (0.001 = 1 m veterde 1 mm). Firar kenarı elemanı son inflation katmanının 1.5 katından ve 0.003c'den küçük olamaz; daha küçük bir değer girilirse bu alt sınır kullanılır. İz ekseninde elemanlar firar kenarındaki boydan başlayıp çıkışa doğru büyür ve genel Element Size'ı (0.5c) aşmaz; son eleman bu boyda sabitlendiği için ayrıca bir büyüme oranı girilmez. Varsayılanlar çoğu analiz için uygundur.",
        "en": 'Sets the Edge Sizing table on the airfoil edges: the element size wanted at the leading edge, at the split line (0.3c) and at the trailing edge, as a fraction of the chord (0.001 = 1 mm on a 1 m chord). The trailing-edge element cannot be smaller than 1.5 times the last inflation layer and 0.003c; a smaller input is raised to that limit. Along the wake axis the elements start at the trailing-edge size, grow towards the outlet and never exceed the global Element Size (0.5c); because the last element is fixed at that size, there is no separate growth ratio. The defaults suit most analyses.',
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
        "tr": "**Sınır adları (Named Selection):** Meshing'de giriş kenarını (C-Grid'de yay, dikdörtgende sol kenar) üst ve alt sınırla birlikte `inlet`, arka sınırı `outlet`, kanat kenarlarını `wall` olarak adlandırın. Fluent'te `inlet` velocity-inlet, `outlet` pressure-outlet, `wall` duvar olur. Dikdörtgen domain'de de üst ve alt sınır `inlet`'e dahildir: hücum açısı hız bileşenleriyle verildiği için akış bu sınırlardan girip çıkabilmelidir; symmetry veya wall burada akışı yanlış yönlendirir. Mach > 0.3 ile pressure-far-field kullanıyorsanız `inlet`'i ve `outlet`'i ikisini de pressure-far-field yapın (Fluent yardımcısındaki far-field notuna bakın).",
        "en": "**Boundary names (Named Selections):** in Meshing, name the inlet edge (the arc for the C-grid, the left edge for the rectangle) together with the top and bottom boundaries `inlet`, the rear boundary `outlet` and the airfoil edges `wall`. In Fluent `inlet` becomes a velocity inlet, `outlet` a pressure outlet and `wall` a wall. The rectangle's top and bottom also belong to `inlet`: the angle of attack is set by the velocity components, so flow must be able to cross them; symmetry or wall there would turn the flow. With a pressure far field (Mach > 0.3) make both `inlet` and `outlet` pressure-far-field (see the far-field note in the Fluent helper).",
    },
    'warn_wake_no_front': {
        "tr": 'İz ekseni ön eksen olmadan seçildi. Ansys 2024 R2 denemelerimizde inflation bu seçimde başarısız oldu; ön ekseni de işaretleyin.',
        "en": 'The wake axis is selected without the front axis. In our Ansys 2024 R2 tests inflation failed with this selection; also tick the front axis.',
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
    'end_corners': {
        "tr": 'İki uç (köşeler); Bias Type iki yönlü, ortası büyük',
        "en": 'Both ends (corners); two-way bias, largest in the middle',
    },
    'end_airfoil': {
        "tr": 'Kanat tarafı',
        "en": 'Airfoil side',
    },
    'end_axis': {
        "tr": 'İz ekseni tarafı',
        "en": 'Wake-axis side',
    },
    'end_split': {
        "tr": 'Bölme çizgisi tarafı',
        "en": 'Split-line side',
    },
    'end_outlet': {
        "tr": 'Çıkış tarafı',
        "en": 'Outlet side',
    },
    'end_outer': {
        "tr": 'Dış sınır tarafı',
        "en": 'Outer-boundary side',
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
        "tr": "1. Kenar çubuğunda istediğiniz bölme çizgilerini seçin (inflation için zorunlu değil; tek çizgi seçmeyin) ve TXT'yi indirin. DesignModeler'da dosyayı **Units = Meter** iken aktarın (soldaki çıktı birimi mm ise **Millimeter**), seçtiğiniz çizgilerle Projection yapın.\n2. Mesh → Details → **Bounding Box Diagonal** onlarca metre mertebesinde olmalı (varsayılan domain'de Ansys ≈ 46.6 m gösterdi). Değer binde biri kadar küçükse geometri milimetre olarak okunmuştur; bu durumda mesher belleği tüketip çöker. Çıktı birimi mm ise aynı değer 46 600 mm gibi görünür; DesignModeler'daki Units dosyanın birimiyle aynı olmalı.\n3. Method: **Quadrilateral Dominant**, Geometry = tüm yüzeyler.\n4. **Inflation**: Geometry = tüm yüzeyler, Boundary = **kanat kenarları** **ve iz ekseni** (geometride ön eksen + iz ekseni ya da altı çizginin hepsi olmalı), Inflation Option = First Layer Thickness, değerler tablodan. Küt firar kenarı yüzünü Boundary'ye eklemeyin.\n5. Mesh → Sizing: Element Size ≈ 0.5c, Growth Rate 1.15, Defeature ve Curvature Min Size tablodan. Edge Sizing'leri tablodan ekleyin; varsa Behavior = Soft. “Hard edges are not supported…” uyarısı tek başına zararsızdır, katmanlar oluştuysa yok sayın.\n6. Sorun çıkarsa kontrolleri tek tek ekleyerek deneyin (önce yalnızca yöntem, sonra Edge Sizing'ler, sonra Inflation); hangi adımda bozulduğu sebebi gösterir.\n7. Not: Inflation, **Mapped Face Meshing** ile birlikte çalışmaz.",
        "en": '1. Choose the split lines you want in the sidebar (optional for inflation; do not select a single line) and download the TXT. Import it in DesignModeler with **Units = Meter** (**Millimeter** if the output unit on the left is mm) and run Projection with the selected lines.\n2. Mesh → Details → **Bounding Box Diagonal** should be tens of meters (Ansys showed ≈ 46.6 m for the default domain). If it is a thousand times smaller the geometry was read in millimeters, and the mesher runs out of memory and crashes. With the output unit set to mm the same value reads like 46,600 mm; Units in DesignModeler must match the unit of the file.\n3. Method: **Quadrilateral Dominant**, Geometry = all faces.\n4. **Inflation**: Geometry = all faces, Boundary = **airfoil edges** **and the wake axis** (the geometry needs the front axis + wake axis, or all six lines), Inflation Option = First Layer Thickness, values from the table. Do not add a blunt TE face to the Boundary.\n5. Mesh → Sizing: Element Size ≈ 0.5c, Growth Rate 1.15, Defeature and Curvature Min Size from the table. Add the Edge Sizings from the table; Behavior = Soft where offered. The “Hard edges are not supported…” warning alone is harmless if the layers were built.\n6. If something fails, add the controls one at a time (method only, then the Edge Sizings, then Inflation); the step that fails shows the cause.\n7. Note: Inflation does not work together with **Mapped Face Meshing**.',
    },
    'yplus_fix_title': {
        "tr": 'y⁺ Düzeltme (Fluent Sonucundan)',
        "en": 'y⁺ Correction (from a Fluent Result)',
    },
    'yplus_fix_help': {
        "tr": "İlk çözümden sonra kanat üzerindeki y⁺ değerini girin; y⁺ ilk hücre yüksekliğiyle yaklaşık doğru orantılı olduğu için hedefe ulaşmak gereken yeni ilk hücre yüksekliği hesaplanır. Hedef y⁺ burada Fluent'in raporladığı değer (hücre merkezi) olarak yorumlanır. Plandaki ilk hücre yüksekliği ise tam hücre yüksekliğidir; Fluent'te raporlanan y⁺ planlanan hedefin yaklaşık yarısı çıkar, bu yüzden bu araçta aynı hedef daha küçük bir yükseklik verir.",
        "en": 'Enter the y⁺ seen on the airfoil after a first solution; since y⁺ scales roughly linearly with first-cell height, the height needed for the target is computed. The target is interpreted here as the y⁺ Fluent reports (cell centroid). The plan on the other tab uses the full cell height, so the y⁺ Fluent reports comes out at about half the planned target; for the same target this tool therefore gives a smaller height.',
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
    'fl_visc': {
        "tr": 'Materials → Fluid → Viscosity',
        "en": 'Materials → Fluid → Viscosity',
    },
    'fl_ref_rho': {
        "tr": 'Reference Values → Density',
        "en": 'Reference Values → Density',
    },
    'fluent_note': {
        "tr": "Hücum açısı geometri döndürülmeden, giriş hızının yönüyle verilir. Inlet'te Velocity Specification = Components seçip X ve Y hızlarını girin (ya da Magnitude and Direction ile hız büyüklüğü + yön). Lift ve Drag raporlarının (Report Definitions → Force) vektörlerini de bu değerlere çevirin: (1, 0) / (0, 1) bırakılırsa Cd'ye kaldırmanın bir kısmı karışır. Reference Values'ta Velocity ve Density'nin girişle aynı olduğundan emin olun. Reynolds sayısı tablodaki yoğunluk ve viskoziteyle hesaplanır; akışkanın (Materials) yoğunluğu ve viskozitesi bu değerlerden farklıysa Fluent'teki Reynolds sayısı mesh'in hesaplandığı değerden farklı olur.",
        "en": 'The angle of attack is set through the inlet velocity direction, without rotating the geometry. At the inlet choose Velocity Specification = Components and enter the X and Y velocities (or Magnitude and Direction with the speed and the direction). Set the Lift and Drag report vectors (Report Definitions → Force) to these values too: leaving them at (1, 0) / (0, 1) mixes part of the lift into Cd. Make sure Reference Values Velocity and Density match the inlet. The Reynolds number is computed with the density and viscosity in the table; if the fluid (Materials) has a different density or viscosity, the Reynolds number in Fluent differs from the one the mesh was sized for.',
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
    'q_verdict_avg': {
        "tr": "Ortalama değer Ansys'in '{band}' bandında: sorun birkaç hücrede değil, mesh'in büyük bölümünde. Eleman boyutlarını, büyüme oranını ve inflation ayarlarını gözden geçirin.",
        "en": "An average is in Ansys' '{band}' band: the problem is not a few cells but much of the mesh. Review the element sizes, growth rate and inflation settings.",
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
        "tr": "**Firar kenarı:** inflation'da firar kenarındaki eleman en az son inflation katmanının 1.5 katı ve en az 0.003c alınır. Sivri firar kenarında alt ve üst yüzeyin katmanları birleşir; Ansys 2024 R2 denemelerimizde TE elemanı son katmandan küçükken (NACA 0012, Re 2×10⁶: 3 mm'ye karşı 4.3 mm) inflation başarısız oldu, daha büyükken çalıştı. Daha ince TE çözünürlüğü için mapped mesh kullanın. **İz eksenini Inflation'ın Boundary'sine ekleyin** ve geometride **ön ekseni de** dışa aktarın: katmanlar firar kenarından ize düz devam eder. İz ekseni olmadan sivri firar kenarının ucunda dejenere hücreler oluştu; ön eksen olmadan da inflation başarısız oldu. Type = Number of Divisions, Bias Type = tek yönlü (`--- -- -` simgesi, çift yönlü değil), Bias Factor = tablodaki değer; Kanat kenarlarının hepsi dosyada hücum kenarından firar kenarına doğru yazılır, bu yüzden üst ve alt kenar aynı yönde davranır. Küçük elemanın hangi uçta olacağı tablonun **Küçük eleman tarafı** sütununda yazar. Genelde **kanat ön** kenarlarında elemanlar hücum kenarında küçük, 0.3c'ye doğru büyür; **kanat arka** kenarlarında 0.3c'de büyük, firar kenarına doğru küçülür; **iz ekseninde** firar kenarında küçük, çıkışa doğru büyür. Firar kenarı elemanı bölme çizgisindeki elemandan büyük çıktığında (düşük Reynolds sayısı ya da kalın son katman) kanat arka kenarında yön tersine döner ve tablo “Bölme çizgisi tarafı” yazar. Bir grup tabloya göre ters çıkarsa o kenarları aynı Edge Sizing'in **Reverse Bias** alanına ekleyin. Böylece 0.3c'de ön ve arka kenarın elemanları, TE'de de kanat ve iz ekseninin ilk elemanları aynı boyda olur. Inflation'ın ilk hücreleri çok ince olduğu için duvardaki eleman boyunun ani değişmesi doğrudan düşük orthogonal quality olarak görünür.",
        "en": '**Trailing edge:** with inflation the TE element is at least 1.5 times the last inflation layer and at least 0.003c. The upper and lower inflation stacks meet at a sharp TE; in our Ansys 2024 R2 tests inflation failed whenever the TE element was smaller than the last layer (NACA 0012, Re 2×10⁶: 3 mm vs 4.3 mm) and worked when it was larger. Use the mapped mesh for finer TE resolution. **Add the wake axis to the Inflation Boundary** and also export the **front axis**: the layers then run straight from the TE into the wake. Without the wake axis, degenerate cells formed at the sharp TE tip; without the front axis, inflation failed. Type = Number of Divisions, single-direction Bias Type (the `--- -- -` icon, not the two-sided one), Bias Factor = table value; All airfoil edges are written from leading edge to trailing edge, so the upper and lower edges behave the same way. The **Smaller-element side** column of the table says at which end the small elements go. Usually the **airfoil front** edges have small elements at the LE that grow towards 0.3c; on the **airfoil rear** edges they are large at 0.3c and shrink towards the TE; on the **wake axis** they are small at the TE and grow towards the outlet. When the TE element comes out larger than the element at the split line (low Reynolds number or a thick last layer), the direction on the airfoil rear edges is reversed and the table says “Split-line side”. If a group comes out reversed relative to the table, add those edges to the **Reverse Bias** field of the same Edge Sizing. This way the front and rear elements match at 0.3c, and the airfoil and wake-axis elements match at the TE. Because the first inflation cells are very thin, any jump in surface element size shows up directly as low orthogonal quality.',
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
        "tr": 'Mapped mesh için altısı da gerekir. Inflation için altısı ya da ön eksen + iz ekseni (iz ekseni inflation Boundary\'sine eklenir). Tek çizgi seçmeyin.',
        "en": 'Mapped meshing needs all six. For inflation: all six, or front axis + wake axis (add the wake axis to the inflation Boundary). Do not select a single line.',
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
        "tr": "Varsayılan değer, Mesh / y⁺ sekmesindeki akış girişinin hızıdır (Re modunda Fluent'in varsayılan havasıyla o Reynolds sayısını veren hız, Mach modunda Mach sayısından gelen hız). Kendi hızınızı girebilirsiniz; Reynolds farklı çıkarsa uyarı gösterilir.",
        "en": "The default is the speed of the Mesh / y⁺ flow input (in Re mode the speed that gives that Reynolds number with Fluent's default air, in Mach mode the speed from the Mach number). You can enter your own; a warning is shown if the Reynolds number differs.",
    },
    'fl_re_mach': {
        "tr": 'Bu hızla Reynolds ve Mach',
        "en": 'Reynolds and Mach at this speed',
    },
    'fl_re_mismatch': {
        "tr": "Bu hız Re = {re_fl:.4e} veriyor; Mesh / y⁺ sekmesindeki Re = {re_mesh:.4e}. İlk hücre yüksekliği o Re'ye göre hesaplandığı için ikisini eşitleyin.",
        "en": 'This speed gives Re = {re_fl:.4e}; the Mesh / y⁺ tab uses Re = {re_mesh:.4e}. The first-cell height is based on that Re, so make them match.',
    },
    'fl_temp': {
        "tr": 'Sıcaklık [°C]',
        "en": 'Temperature [°C]',
    },
    'fl_temp_help': {
        "tr": "Yalnızca ses hızı ve Mach için (ideal gaz hava, γ = 1.4). Yoğunluk ve viskozite bunu izlemez: Re modunda Fluent'in varsayılan havası, hız modunda girdiğiniz değerler kullanılır.",
        "en": "Only for the speed of sound and Mach (ideal-gas air, γ = 1.4). Density and viscosity do not follow it: Re mode uses Fluent's default air, speed mode the values you entered.",
    },
    'fl_sound': {
        "tr": 'Ses hızı',
        "en": 'Speed of sound',
    },
    'tu_title': {
        "tr": 'Serbest akış türbülansının sönümü (SST / Transition SST)',
        "en": 'Free-stream turbulence decay (SST / Transition SST)',
    },
    'tu_inlet': {
        "tr": 'Inlet Tu [%]',
        "en": 'Inlet Tu [%]',
    },
    'tu_vr': {
        "tr": 'Turbulent Viscosity Ratio',
        "en": 'Turbulent Viscosity Ratio',
    },
    'tu_goal': {
        "tr": 'Kanatta istenen Tu [%] (isteğe bağlı)',
        "en": 'Wanted Tu at the airfoil [%] (optional)',
    },
    'tu_dist': {
        "tr": 'Inlet → hücum kenarı mesafesi',
        "en": 'Inlet → leading edge distance',
    },
    'tu_at_le': {
        "tr": 'Hücum kenarına ulaşan Tu',
        "en": 'Tu reaching the leading edge',
    },
    'tu_max': {
        "tr": 'Bu viskozite oranıyla ulaşabilecek en yüksek Tu',
        "en": 'Highest Tu that can reach it with this viscosity ratio',
    },
    'tu_need': {
        "tr": 'Kanatta %{goal:g} için inlet Tu',
        "en": 'Inlet Tu for {goal:g}% at the airfoil',
    },
    'tu_unreachable': {
        "tr": 'Bu viskozite oranıyla ulaşılamaz; oranı artırın',
        "en": 'Not reachable with this viscosity ratio; raise the ratio',
    },
    'tu_note': {
        "tr": "Akış kayma gerilmesi olmayan serbest akışta k ve ω sönümünün kapalı çözümüyle (Spalart & Rumsey, AIAA J. 2007) hesaplanır: inlet'te girdiğiniz Tu, kanada gelene kadar azalır ve Transition SST'de geçişi kanattaki değer belirler. Deneyle karşılaştırırken kanattaki Tu'yu rüzgâr tünelininkine eşitleyin. Daha yüksek inlet Tu daha hızlı söner; kanatta daha yüksek bir Tu için viskozite oranını artırın. Fluent girişte yaklaşık 1–10 oranını önerir; 100'ün üzerinde yüzey sürtünmesi laminer değerden belirgin sapabilir. Ansys belgesindeki sabitlerin etiketleri (β, β*) SST'nin kendi sabitlerine göre ters yazılmış, belgedeki haliyle elle hesaplarsanız burada gösterilenden %5–55 yüksek çıkar; burada NASA Turbulence Modeling Resource sabitleri kullanılır.",
        "en": 'Computed from the closed-form decay of k and ω in a shear-free free stream (Spalart & Rumsey, AIAA J. 2007): the Tu set at the inlet drops before it reaches the airfoil, and in Transition SST transition follows the value at the airfoil. When comparing with an experiment, match the Tu at the airfoil to the wind tunnel. A higher inlet Tu decays faster; for more Tu at the airfoil raise the viscosity ratio. Fluent suggests a ratio of about 1–10 at the inlet; above 100 the skin friction can depart clearly from the laminar value. The Ansys documentation labels the constants β and β* the other way round from SST itself; calculated by hand as written there the Tu comes out 5–55 % higher than shown here, which uses the NASA Turbulence Modeling Resource constants.',
    },
    'sweep_title': {
        "tr": 'Hücum açısı taraması (polar için)',
        "en": 'Angle-of-attack sweep (for a polar)',
    },
    'sweep_from': {
        "tr": 'İlk açı [°]',
        "en": 'First angle [°]',
    },
    'sweep_to': {
        "tr": 'Son açı [°]',
        "en": 'Last angle [°]',
    },
    'sweep_step': {
        "tr": 'Adım [°]',
        "en": 'Step [°]',
    },
    'msh_family': {
        "tr": 'Mesh bağımsızlığı için 3 mesh hazırla (kaba / orta / ince)',
        "en": 'Make 3 meshes for a mesh independence study (coarse / medium / fine)',
    },
    'msh_family_help': {
        "tr": 'Aynı girişlerden üç mesh: hücre boyları √2 oranıyla küçülür (kademe başına yaklaşık 2 kat hücre); orta mesh yukarıdaki mesh ile aynıdır. Üçünü aynı Fluent kurulumuyla (ör. /mesh/replace ile) çözüp Cl ve Cd değerlerini Otomasyon sekmesindeki GCI hesabına girin.',
        "en": 'Three meshes from the same inputs: cell sizes shrink by √2 (about 2x the cells per step); the medium mesh is the one above. Solve all three with the same Fluent setup (e.g. with /mesh/replace) and enter Cl and Cd in the GCI section on the Automation tab.',
    },
    'msh_family_download': {
        "tr": '3 mesh (ZIP) indir',
        "en": 'Download the 3 meshes (ZIP)',
    },
    'msh_family_cells': {
        "tr": "İlk hücre yüksekliği de aileyle birlikte değişir: hedef y⁺ kaba mesh'te yaklaşık 1.4, ince mesh'te 0.7 katı olur (ailenin doğru tanımı: tüm boyutlar birlikte küçülür). Fluent 2024 R2'de denendi (NACA 4412, 4°, SST k-ω, Re 2×10⁶; 42 944 / 84 870 / 169 824 hücre): Cl 0.8355 / 0.8359 / 0.8353, Cd 0.012580 / 0.012567 / 0.012573; üç mesh arasındaki fark %0.1'in altında (salınımlı, yani çok küçük farklar).",
        "en": 'The first-cell height changes with the family as well: the target y⁺ becomes about 1.4 times on the coarse and 0.7 times on the fine mesh (a proper family refines every size together). Tried in Fluent 2024 R2 (NACA 4412, 4°, SST k-ω, Re 2×10⁶; 42 944 / 84 870 / 169 824 cells): Cl 0.8355 / 0.8359 / 0.8353, Cd 0.012580 / 0.012567 / 0.012573; the three meshes differ by less than 0.1 % (oscillatory, i.e. very small differences).',
    },
    'gci_title': {
        "tr": 'Mesh bağımsızlığı (GCI)',
        "en": 'Mesh independence (GCI)',
    },
    'gci_note': {
        "tr": "Üç mesh'in (Mesh / y⁺ sekmesinden kaba / orta / ince) Fluent report file'larını (.out) yükleyin ya da hücre sayısını ve aynı açıdaki Cl, Cd değerlerini elle girin. Hesap Celik vd. (2008, J. Fluids Eng. 130, 078001) yöntemidir: p yakınsama mertebesi, mesh'ten bağımsız tahmini değer (Richardson) ve ince mesh'in belirsizliği GCI (güvenlik katsayısı 1.25). Değerler salınıyorsa (orta mesh'in değeri diğer ikisinin arasında değilse) GCI daha az güvenilirdir.",
        "en": 'Upload the Fluent report files (.out) of three meshes (coarse / medium / fine from the Mesh / y⁺ tab), or type in the cell counts and Cl, Cd at the same angle. The method is that of Celik et al. (2008, J. Fluids Eng. 130, 078001): p the order of convergence, the mesh-independent estimate (Richardson) and the uncertainty of the fine mesh, GCI (safety factor 1.25). If the values oscillate (the medium value is not between the other two) the GCI is less reliable.',
    },
    'gci_fine': {
        "tr": 'İnce',
        "en": 'Fine',
    },
    'gci_medium': {
        "tr": 'Orta',
        "en": 'Medium',
    },
    'gci_coarse': {
        "tr": 'Kaba',
        "en": 'Coarse',
    },
    'gci_cells': {
        "tr": 'Hücre sayısı',
        "en": 'Cell count',
    },
    'gci_ext': {
        "tr": "Tahmini değer (mesh'ten bağımsız)",
        "en": 'Extrapolated value (mesh independent)',
    },
    'gci_conv': {
        "tr": 'Yakınsama',
        "en": 'Convergence',
    },
    'gci_mono': {
        "tr": 'tek yönlü',
        "en": 'monotonic',
    },
    'gci_osc': {
        "tr": 'salınımlı (GCI daha az güvenilir)',
        "en": 'oscillatory (GCI less reliable)',
    },
    'gci_upload': {
        "tr": "Üç mesh'in report file'ları (.out)",
        "en": 'Report files (.out) of the three meshes',
    },
    'gci_upload_help': {
        "tr": "Dosya adında coarse / medium / fine (ya da kaba / orta / ince) ayrı bir kelime olarak geçerse (ör. naca4412_coarse.out) mesh'ler adlardan tanınır ve hücre sayıları Mesh / y⁺ sekmesindeki mesh ailesinden (aynı girişler) alınır. Adlar böyle değilse tam üç dosya seçin ve hücre sayılarını girin. Kayıttan sürdürülen bir mesh'in ek dosyası (ör. fine_1929.out) aynı adı taşıdığı için birlikte okunur. Cl ve Cd, her açının son N iterasyonunun ortalamasıdır (polar aracıyla aynı); üç dosyada da bulunan her açı için GCI hesaplanır.",
        "en": 'When the file name has coarse / medium / fine (or kaba / orta / ince) as a separate word (e.g. naca4412_coarse.out) the meshes are recognised by name and the cell counts are taken from the mesh family of the Mesh / y⁺ tab (same inputs). Otherwise select exactly three files and enter the cell counts. The extra file of a mesh continued from a saved case (e.g. fine_1929.out) carries the same name and is read together with it. Cl and Cd are the mean of the last N iterations of each angle (as in the polar tool); the GCI is computed for every angle found in all three files.',
    },
    'gci_cells_family': {
        "tr": "Hücre sayıları Mesh / y⁺ sekmesindeki mevcut girişlerle üretilen mesh ailesinden alındı. Mesh'leri başka girişlerle ürettiyseniz ya da Ansys mesh'i kullandıysanız sayıları düzeltin (Fluent'te Mesh → Info → Size ya da mesh okunurken konsoldaki \"quadrilateral cells\" satırı).",
        "en": 'The cell counts were taken from the mesh family built with the current inputs of the Mesh / y⁺ tab. If the meshes were made with other inputs, or in Ansys Meshing, correct them (in Fluent: Mesh → Info → Size, or the "quadrilateral cells" line in the console when the mesh is read).',
    },
    'gci_cells_no_family': {
        "tr": "Hücre sayıları mesh ailesinden yalnızca Mesh / y⁺ sekmesinde Mapped ve C-Grid seçiliyken alınır.",
        "en": 'The cell counts are taken from the mesh family only while Mapped and C-Grid are selected on the Mesh / y⁺ tab.',
    },
    'gci_need_cells': {
        "tr": "Hücre sayılarını girin (her sütun bir dosya; sıra önemli değil, en çok hücreli mesh ince sayılır). Fluent'te: Mesh → Info → Size ya da mesh okunurken konsoldaki \"quadrilateral cells\" satırı.",
        "en": 'Enter the cell counts (each column is one file; the order does not matter, the mesh with the most cells counts as fine). In Fluent: Mesh → Info → Size, or the "quadrilateral cells" line in the console when the mesh is read.',
    },
    'gci_files_bad': {
        "tr": "Dosyalar eşleştirilemedi: ya her dosyanın adında coarse / medium / fine (kaba / orta / ince) kelimelerinden biri geçmeli ve üçü de bulunmalı, ya da adlarda bu kelimeler olmadan tam üç dosya seçilmeli.",
        "en": 'The files could not be matched: either every file name has one of coarse / medium / fine (kaba / orta / ince) and all three occur, or exactly three files without these words are selected.',
    },
    'gci_file': {
        "tr": '{name} okunamadı: {msg}',
        "en": 'Could not read {name}: {msg}',
    },
    'gci_no_common': {
        "tr": "Üç dosyada ortak bir açı yok; GCI aynı açıdaki değerlerle hesaplanır. Açı sütununun birimini (rad / deg) kontrol edin.",
        "en": 'The three files have no angle in common; the GCI needs values at the same angle. Check the unit of the angle column (rad / deg).',
    },
    'gci_warn_unsteady': {
        "tr": "Şu açılarda bir mesh'in değeri oturmamış (salınıyor ya da son N iterasyondan az): {angles}. Mesh'ler arasındaki fark iterasyon salınımından küçükse GCI anlamlı değildir; o açıyı daha uzun koşun ya da Polar bölümünde Δ değerlerine bakın.",
        "en": 'At these angles the value of a mesh has not settled (oscillating or fewer than N iterations): {angles}. If the difference between the meshes is smaller than the iteration oscillation the GCI means little; run that angle longer or look at the Δ values in the Polar section.',
    },
    'auto_steps': {
        "tr": "**Akış:** 1) Mesh / y⁺ → Mapped → Fluent mesh (.msh) indir (mesh bağımsızlığı için 3 mesh) → 2) aşağıda açı taraması ve journal → 3) Fluent'in report file'ından polar → 4) üç mesh'in sonuçlarıyla GCI.",
        "en": "**Workflow:** 1) Mesh / y⁺ → Mapped → download the Fluent mesh (.msh) (3 meshes for mesh independence) → 2) the angle sweep and journal below → 3) the polar from Fluent's report file → 4) the GCI from the results of the three meshes.",
    },
    'msh_title': {
        "tr": 'Fluent mesh dosyası (.msh)',
        "en": 'Fluent mesh file (.msh)',
    },
    'msh_download': {
        "tr": 'Fluent mesh (.msh) indir',
        "en": 'Download the Fluent mesh (.msh)',
    },
    'msh_cells': {
        "tr": 'Hücre',
        "en": 'Cells',
    },
    'msh_skew': {
        "tr": 'Skewness (maks.)',
        "en": 'Skewness (max.)',
    },
    'msh_oq': {
        "tr": 'Orthogonal Quality (min.)',
        "en": 'Orthogonal Quality (min.)',
    },
    'msh_rect': {
        "tr": 'Mesh dosyası şimdilik yalnızca C-Grid domain için üretilir.',
        "en": 'The mesh file is made for the C-grid domain only, for now.',
    },
    'msh_note': {
        "tr": "Uygulamanın kendi ürettiği mapped C-Grid mesh'i: yukarıdaki Edge Sizing tablosunun bölüm sayıları ve bias'larıyla 6 blok; blokların içi transfinite interpolasyonla doldurulur; ön bloklarda (LE → bölme çizgisi) ızgara çizgileri duvardan dik çıkar ve yaklaşık yarım veter içinde iç çizgilere kavuşur (çok kamburlu profillerde burnun arkasındaki ezik hücreler için: S9104 skewness 0.90 → 0.64; NACA 4412 0.52 → 0.37, min orthogonal quality 0.49 → 0.84). Fluent 2024 R2'de denendi (NACA 4412, −4…8°, SST k-ω, Re 2×10⁶): min orthogonal quality Fluent'te de 0.845, Cl önceki mesh'le aynı (−0.01079 / 0.41741 / 0.83588 / 1.22287; önce −0.01088 / 0.41739 / 0.83590 / 1.22338), Cd %0.2 içinde. DesignModeler ve Meshing gerekmez: Fluent'te File → Read → Mesh ile açın (birim metre). Sınırlar hazır gelir: inlet (velocity-inlet; giriş yayı + üst + alt sınır), outlet (pressure-outlet), wall (kanat). Kurulu bir case'iniz varsa konsolda /mesh/replace yazıp dosya adını uzantısıyla verin. Kalite değerleri Fluent'in tanımlarıyla burada hesaplanır (NACA 4412'de Fluent 2024 R2 aynı minimum orthogonal quality'yi verdi; dosyayı okudu, Mesh Check hatasız). Dik başlangıçtan önce de Fluent'te NACA 4412 −4…8° (SST k-ω, Re 2×10⁶) çözüldü: Cl ve Cd, Ansys Meshing'in aynı tablodan ürettiği mesh'le %0.01 / %0.05 içinde aynı (ör. 0°: Cl 0.41739 ikisinde de).",
        "en": "The app's own mapped C-grid mesh: 6 blocks with the divisions and bias factors of the Edge Sizing table above; the inside of each block is filled by transfinite interpolation; on the front blocks (LE → split line) the grid lines leave the wall at right angles and join the inner lines within about half a chord (for the squeezed cells behind the nose of strongly cambered sections: S9104 skewness 0.90 → 0.64; NACA 4412 0.52 → 0.37, minimum orthogonal quality 0.49 → 0.84). Tried in Fluent 2024 R2 (NACA 4412, −4…8°, SST k-ω, Re 2×10⁶): minimum orthogonal quality 0.845 in Fluent too, Cl the same as on the earlier mesh (−0.01079 / 0.41741 / 0.83588 / 1.22287; before −0.01088 / 0.41739 / 0.83590 / 1.22338), Cd within 0.2 %. No DesignModeler or Meshing needed: open it in Fluent with File → Read → Mesh (units: metres). The boundaries come named: inlet (velocity-inlet; inlet arc + top + bottom boundary), outlet (pressure-outlet), wall (airfoil). With a set-up case, type /mesh/replace in the console and give the file name with its extension. The quality values are computed here with Fluent's definitions (for NACA 4412 Fluent 2024 R2 gave the same minimum orthogonal quality; it read the file and Mesh Check found no error). Before the start at right angles it was also solved in Fluent, NACA 4412 at −4…8° (SST k-ω, Re 2×10⁶): Cl and Cd match the mesh Ansys Meshing made from the same table within 0.01 % / 0.05 % (e.g. 0°: Cl 0.41739 on both).",
    },
    'sweep_mode': {
        "tr": 'Açılar',
        "en": 'Angles',
    },
    'sweep_mode_range': {
        "tr": 'Eşit aralıklı',
        "en": 'Even steps',
    },
    'sweep_mode_list': {
        "tr": 'Kendi açılarım',
        "en": 'My own angles',
    },
    'sweep_list': {
        "tr": 'Açı listesi [°]',
        "en": 'List of angles [°]',
    },
    'sweep_list_help': {
        "tr": "Örnek: 1.3, 2.8, 6.8. Ondalık için nokta; açıları boşluk, ; ya da virgül ve boşlukla ayırın. Açılar küçükten büyüğe sıralanır, tekrar edenler bir kez alınır. Dosya adları açıyı iki ondalıkla tutar, bu yüzden açılar arasında en az 0.01° fark olmalı. Fluent 2024 R2'de bir listeyle denendi (1.99, 4.01, 6.11, 8.08; Ladson'ın deney açıları).",
        "en": 'Example: 1.3, 2.8, 6.8. Use a dot for decimals; separate angles with a space, ; or a comma and a space. Angles are sorted from smallest to largest and repeats are taken once. File names hold the angle to 2 decimals, so angles must be at least 0.01° apart. Tried in Fluent 2024 R2 with a list (1.99, 4.01, 6.11, 8.08; the test angles of Ladson).',
    },
    'sweep_list_empty': {
        "tr": 'Taramak istediğiniz açıları yazın (ör. 1.3, 2.8, 6.8).',
        "en": 'Enter the angles to sweep (e.g. 1.3, 2.8, 6.8).',
    },
    'sweep_csv': {
        "tr": 'Taramayı CSV olarak indir',
        "en": 'Download the sweep as CSV',
    },
    'jou_title': {
        "tr": 'Fluent journal',
        "en": 'Fluent journal',
    },
    'jou_note': {
        "tr": "Journal her açıda yalnızca {expr} named expression'ını değiştirip iterasyon koşar; her açı bir öncekinin çözümünden devam eder. Case'inizde yukarıdaki satırların kurulu olması (sınır koşulunuza göre pressure-far-field ya da velocity-inlet satırları), report file'larda yalnızca expression report'lar (ve moment) bulunması ve residual convergence checks'in kapalı olması gerekir. {expr} değerini ilk açıya (\"İlk açı\") ayarlayıp initialize edin ve en az bir iterasyonu kendiniz koşun (iterasyon 0'dan başlayan bir çalışmada Fluent report file'lar için \"Ok to overwrite?\" diye sorabilir ve journal bozulur). Açı başına {iterations} iterasyon üst sınırdır: case'te Convergence Conditions (Solution → Report Definitions) varsa Fluent koşul dolunca o açıyı erken bitirir ve journal sonraki açıya geçer. Cl/Cd, report file'larda her açının bloğundan okunur. Named expression düzenleme komutu, Cl/Cd expression'ları ve report file'lar Fluent 2024 R2'de (standalone, 2B) 3 açılı kısa bir taramayla (açı başına 50 iterasyon) ve 11 açılı uzun bir taramayla (−4…16°, en çok 2000 iterasyon, Convergence Conditions, velocity-inlet case) denendi; ikisi de soru sorulmadan bitti. Pressure-far-field case'iyle bir tarama da (M 0.3, 2…8°, dış sınırın tamamı far-field) soru sorulmadan bitti. Workbench içindeki Fluent'te denendi ve çalışmaz: her açı değişikliğinde \"Settings have changed\" diye sorar (\"current and future calculations\" seçilse de); journal standalone Fluent (Launcher) içindir. Journal Fluent'in üzerine yazma sorusunu kapatır; aynı adlı bir case dosyasının üzerine yazma henüz denenmedi.",
        "en": "At each angle the journal only changes the named expression {expr} and iterates; every angle continues from the previous solution. Your case needs the lines above (the pressure-far-field or the velocity-inlet lines, for your boundary condition), report files holding only expression reports (and the moment), and residual convergence checks off. Set {expr} to the first angle (\"First angle\"), initialise, and run at least one iteration yourself (a run starting at iteration 0 can make Fluent ask \"Ok to overwrite?\" for the report files and breaks the journal). {iterations} iterations per angle is an upper limit: if the case has Convergence Conditions (Solution → Report Definitions), Fluent ends the angle early when they are met and the journal goes on to the next angle. Cl/Cd are read from each angle's block in the report files. The named-expression edit command, the Cl/Cd expressions and the report files were tried in Fluent 2024 R2 (standalone, 2D) with a short 3-angle sweep (50 iterations each) and an 11-angle sweep (−4…16°, up to 2000 iterations, Convergence Conditions, velocity-inlet case); both ended without a question. A sweep with a pressure-far-field case (M 0.3, 2…8°, the whole outer boundary far-field) also ended without a question. Tried in Fluent inside Workbench, where it does not work: it asks \"Settings have changed\" at every angle change (even after \"current and future calculations\"); the journal is meant for standalone Fluent (Launcher). The journal turns off Fluent's overwrite question; overwriting a case file of the same name has not been tried yet.",
    },
    'jou_setup_title': {
        "tr": 'Case\'te olması gerekenler (named expression ve report definition)',
        "en": 'What the case needs (named expression and report definitions)',
    },
    'jou_setup_aoa': {
        "tr": 'Named expression {expr}: ilk açı, örn. {first} [deg]',
        "en": 'Named expression {expr}: the first angle, e.g. {first} [deg]',
    },
    'jou_setup_flow_x': {
        "tr": 'Pressure-far-field, X-Component of Flow Direction',
        "en": 'Pressure-far-field, X-Component of Flow Direction',
    },
    'jou_setup_flow_y': {
        "tr": 'Pressure-far-field, Y-Component of Flow Direction',
        "en": 'Pressure-far-field, Y-Component of Flow Direction',
    },
    'jou_setup_inlet_x': {
        "tr": 'ya da velocity-inlet (Components), X-Velocity',
        "en": 'or velocity-inlet (Components), X-Velocity',
    },
    'jou_setup_inlet_y': {
        "tr": 'ya da velocity-inlet (Components), Y-Velocity',
        "en": 'or velocity-inlet (Components), Y-Velocity',
    },
    'jou_setup_cl': {
        "tr": 'Report definition cl (expression)',
        "en": 'Report definition cl (expression)',
    },
    'jou_setup_cd': {
        "tr": 'Report definition cd (expression)',
        "en": 'Report definition cd (expression)',
    },
    'jou_setup_clconv': {
        "tr": "Report definition clconv (expression; report file'a eklemeyin, Convergence Conditions'ta cl yerine seçin)",
        "en": "Report definition clconv (expression; keep it out of the report files, pick it instead of cl in Convergence Conditions)",
    },
    'jou_setup_note': {
        "tr": "clconv = cl + 1: Fluent'in Convergence Conditions ölçütü görelidir; Cl ≈ 0 olan açıda (simetrik profilde 0°) hiç dolmaz ve açı iterasyon üst sınırına kadar koşar. cl + 1 değeri 1 civarında kaldığı için göreli değişimi Cl'nin mutlak değişimine eşit olur. Fluent 2024 R2'de denendi: 0°'de açı 366 iterasyonda kendisi durdu, Cl ve Cd 2000 iterasyonluk koşuyla aynı çıktı. Yoğunluk ve hız yukarıdaki serbest akış değerlerinden alındı ve alan c × 1 m. Fluent'in Reference Values bölümündeki yoğunluk ve hız farklıysa (ör. pressure-far-field'da Fluent referans hızı kendisi hesaplar) bu iki değeri Fluent'inkilerle değiştirin. Velocity-inlet satırlarındaki hız da aynı hızdır; bu satırlar uygulamadan kopyalanarak Fluent 2024 R2'de denendi ([m s^-1] birimi kabul edildi, sonuç elle yazılan [m/s] ile aynı). Duvar bölgesinin adı wall değilse Force(['...']) içini değiştirin.",
        "en": "clconv = cl + 1: Fluent's Convergence Conditions use a relative change; at an angle where Cl ≈ 0 (a symmetric profile at 0°) it is never met and the angle runs to the iteration limit. cl + 1 stays near 1, so its relative change equals the absolute change of Cl. Tried in Fluent 2024 R2: at 0° the angle stopped by itself after 366 iterations with the same Cl and Cd as a 2000-iteration run. Density and speed come from the free-stream values above and the area is c × 1 m. If the density and velocity in Fluent's Reference Values differ (e.g. Fluent computes the reference velocity itself for a pressure far field), replace these two numbers with Fluent's. The velocity-inlet lines use the same speed; they were tried in Fluent 2024 R2 by copying them from the app ([m s^-1] was accepted; same result as [m/s] typed by hand). If your wall zone is not called wall, change the name inside Force(['...']).",
    },
    'jou_expr': {
        "tr": 'Named expression adı',
        "en": 'Named expression name',
    },
    'jou_expr_help': {
        "tr": "Fluent'teki açı named expression'ının adı (varsayılan aoa). Harf, rakam ve _ içerebilir; rakamla başlayamaz.",
        "en": "Name of the angle named expression in Fluent (default aoa). Letters, digits and _; must not start with a digit.",
    },
    'jou_iter': {
        "tr": 'Açı başına iterasyon',
        "en": 'Iterations per angle',
    },
    'jou_save_every': {
        "tr": "Case & data: her kaç açıda bir",
        "en": 'Case & data: every how many angles',
    },
    'jou_save_every_help': {
        "tr": "1 = her açıdan sonra, 5 = her 5 açıda bir; son açı her zaman kaydedilir. 0 = yalnızca son açı. Kayıt başına yaklaşık 7–9 MB (50 bin hücre). Uzun süren açılarda 1 seçin. Tarama yarıda kalırsa: son kaydedilen case & data'yı açın ve journal'dan önce 1 iterasyonu elle koşun; Fluent her report file için \"Do you want to create new file?\" diye sorar (dosyada daha ileri iterasyonlar var), Yes deyin, kalan kısım <ad>_<iterasyon>.out dosyasına yazılır. Sonra burada ilk açıyı bir sonraki açı yapın, yeni journal indirip okutun. Polar aracına eski ve yeni report file'ı birlikte yükleyin. Fluent 2024 R2'de denendi (2026-11-25).",
        "en": 'Every k-th angle (1 = every angle, 5 = every 5 angles); the last angle is always saved. 0 = only the last angle. About 7–9 MB per save (50k cells). Use 1 when each angle takes long. If the sweep stops midway: read the last saved case & data and run one iteration by hand before the journal; Fluent asks "Do you want to create new file?" for every report file (it holds later iterations), answer Yes, and the rest goes to <name>_<iteration>.out. Then set the first angle here to the next angle, download a new journal and read it. Give the polar tool the old and the new report file together. Tried in Fluent 2024 R2 (2026-11-25).',
    },
    'jou_folder': {
        "tr": 'Kayıt klasörü',
        "en": 'Save folder',
    },
    'jou_folder_help': {
        "tr": "Tam yol, örn. C:/.../fluent; Türkçe karakter olmasın (ç, ş, ü...). Boşsa Fluent'in çalışma klasörü kullanılır.",
        "en": "Full path, e.g. C:/.../fluent; ASCII characters only. Empty = Fluent's working folder.",
    },
    'jou_download': {
        "tr": 'Fluent journal (.jou) indir',
        "en": 'Download the Fluent journal (.jou)',
    },
    'jou_error': {
        "tr": 'Journal üretilemedi: {msg}',
        "en": 'Could not build the journal: {msg}',
    },
    'warn_yplus_high': {
        "tr": "Transition SST için y⁺ ≈ 1 önerilir; y⁺ > 5'te geçiş öne kayabilir. Düz levha tahmini x = c içindir; en büyük y⁺ hücum kenarı yakınında ve hücum açısında emme tepesinde oluşur.",
        "en": "Transition SST wants y⁺ ≈ 1; above 5 transition can move forward. The flat-plate estimate is for x = c; the largest y⁺ occurs near the leading edge and at the suction peak at angle of attack.",
    },
    'warn_rarefied': {
        "tr": "Bu Mach ve Reynolds sayısı çok seyrek bir gaz veriyor (statik basınç {p:.3g} Pa, Knudsen sayısı {kn:.1e}). 1e-3'ün üzerinde gaz duvarda kaymaya başlar ve Fluent'in sürekli ortam (kaymasız) modeli geçerliliğini yitirir; girişleri kontrol edin.",
        "en": "This Mach and Reynolds number give a very thin gas (static pressure {p:.3g} Pa, Knudsen number {kn:.1e}). Above 1e-3 the gas starts to slip at the wall and Fluent's continuum (no-slip) model no longer holds; check the inputs.",
    },
    'warn_coverage_low': {
        "tr": "Inflation kalınlığı sınır tabakadan ince kalır (kapsama < 1). Düz levha tahmini emme tarafında gerçek kalınlıktan küçük olabilir; 1.5 ya da daha fazlası önerilir.",
        "en": "The inflation is thinner than the boundary layer (coverage < 1). The flat-plate estimate can be smaller than the real thickness on the suction side; 1.5 or more is advised.",
    },
    'warn_re_high': {
        "tr": "Re > 10⁹: sürtünme bağıntısı (Schlichting) bu aralık için tanımlı değil; y⁺ ve ilk hücre değerlerini kontrol edin.",
        "en": "Re > 10⁹: the skin-friction correlation (Schlichting) is not defined for this range; check the y⁺ and first-cell values.",
    },
    'fl_temp_props': {
        "tr": "{temp:g} °C için öneri (deniz seviyesi basıncı, ideal gaz ve Sutherland): yoğunluk ≈ {rho:.4f} kg/m³, viskozite ≈ {mu:.4e} Pa·s. Re ve Mach aynı duruma ait olsun diye bunları yukarıya girin.",
        "en": "Suggestion for {temp:g} °C (sea-level pressure, ideal gas and Sutherland): density ≈ {rho:.4f} kg/m³, viscosity ≈ {mu:.4e} Pa·s. Enter them above so Re and Mach belong to the same state.",
    },
    'fl_mach_warn': {
        "tr": "Mach = {m:.2f} > 0.3: sıkıştırılabilirlik etkileri önemlidir; Fluent'te yoğunluğu ideal gaz olarak tanımlayın. Dış akışta velocity-inlet yerine pressure-far-field (Mach ve yön bileşenleri) daha uygun olabilir.",
        "en": 'Mach = {m:.2f} > 0.3: compressibility matters; use ideal-gas density in Fluent. For external flow, pressure-far-field (Mach and direction components) may suit better than velocity-inlet.',
    },
    # ---- outline used as drawn (vortex generator, flap, kinked section)
    'as_is': {
        "tr": 'Dosyadaki çizgiyi olduğu gibi kullan (VG, flap, kırık profil)',
        "en": 'Use the outline as drawn (VG, flap, kinked section)',
    },
    'as_is_help': {
        "tr": "Normalde dosya x boyunca ilerleyen üst ve alt yüzeye ayrılır; geri giden noktalar atılır. Vorteks jeneratörü (dik ya da öne yatık duvarlı çıkıntı), flap ya da kırık profil için bu kutuyu işaretleyin: noktalar dosyadaki sırasıyla tek kapalı çizgi olarak kalır ve yalnızca hücum kenarında (en küçük x) ve firar kenarında (en büyük x) ikiye kesilir. Yalnızca inflation iş akışı kullanılabilir (ön eksen + iz ekseni, dikey bölme çizgisi yok).",
        "en": "Normally the file is split into an upper and a lower surface that advance in x, and points that go back are dropped. Tick this box for a vortex generator (a fin with vertical or forward-leaning walls), a flap or a kinked section: the points stay one closed outline in file order and are only cut in two at the leading edge (smallest x) and the trailing edge (largest x). Only the inflation workflow is available (front axis + wake axis, no vertical split lines).",
    },
    'asis_geom_info': {
        "tr": 'Çizgi dosyadaki gibi kullanılıyor: kanat duvarı iki kenardır (üst ve alt yol, hücum kenarından firar kenarına) ve yalnızca ön eksen ile iz ekseni çizilir. Kenar çubuğundaki bölme çizgisi seçimi bu modda kullanılmaz.',
        "en": 'The outline is used as drawn: the airfoil wall is two edges (upper and lower path, leading edge to trailing edge) and only the front axis and the wake axis are drawn. The split-line selection in the sidebar does not apply in this mode.',
    },
    'asis_no_mapped': {
        "tr": 'Dosyadaki çizgi olduğu gibi kullanıldığında mapped mesh yoktur: bloklar için dikey bölme çizgileri gerekir.',
        "en": 'Mapped meshing is not available for an outline used as drawn: its blocks need the vertical split lines.',
    },
    'asis_edges_note': {
        "tr": "Kanat kenarları (üst ve alt yol) bu modda tabloda yok: VG'nin duvarları ve köşeleri tek bir eleman dağılımına uymaz. Bu iki kenara Edge Sizing'i elle verin: hücum kenarında yaklaşık {ds_le}, firar kenarında {ds_te}; VG'nin ya da kırığın üzerinde ise eleman boyu en kısa duvarından birkaç kat küçük olsun (örneğin duvarı en az 5–10 elemana bölün). Sıradan bir profil için denenen örnek (NACA 4412, c = 1 m, Re 2×10⁶, Fluent 2024 R2): üst kenar 266, alt kenar 258 bölüm, tek yönlü Bias 10, küçük eleman hücum kenarında (hücum kenarında ≈1 mm, firar kenarında ≈10 mm).",
        "en": "The airfoil edges (upper and lower path) are not in the table in this mode: the walls and corners of a VG do not fit one element distribution. Give these two edges an Edge Sizing by hand: about {ds_le} at the leading edge and {ds_te} at the trailing edge, and on the VG or kink an element size several times smaller than its shortest wall (e.g. at least 5–10 elements per wall). Tried example for a plain section (NACA 4412, c = 1 m, Re 2×10⁶, Fluent 2024 R2): upper edge 266, lower edge 258 divisions, one-way bias 10, small end at the leading edge (≈1 mm there, ≈10 mm at the trailing edge).",
    },
    'af_upper': {"tr": 'Kanat üst yolu', "en": 'Airfoil upper path'},
    'af_lower': {"tr": 'Kanat alt yolu', "en": 'Airfoil lower path'},
}


# Turkish versions of the (English) error messages raised by the core modules.
ERRORS_TR = {
    'Temperature must be above absolute zero': 'Sıcaklık mutlak sıfırın üstünde olmalı',
    'Distance and viscosity ratio must be positive': 'Mesafe ve viskozite oranı pozitif olmalı',
    'Target turbulence intensity must be positive': 'İstenen türbülans yoğunluğu pozitif olmalı',
    'Angle step must be positive': 'Açı adımı pozitif olmalı',
    'Last angle must not be below the first one': 'Son açı ilk açıdan küçük olamaz',
    'Too many angles (more than 361)': 'Çok fazla açı (361’den fazla)',
    'Use a dot for decimals (1.5) and separate angles with a space, ; or a comma and a space': 'Ondalık için nokta kullanın (1.5); açıları boşluk, ; ya da virgül ve boşlukla ayırın ("1,3" gibi virgüllü sayı kabul edilmez)',
    'Angles must be numbers, separated by a space, ; or a comma': 'Açılar sayı olmalı; boşluk, ; ya da virgülle ayrılmalı',
    'Enter at least one angle': 'En az bir açı yazın',
    'Cell counts must be positive': 'Hücre sayıları pozitif olmalı',
    'The three meshes need different cell counts': 'Üç mesh farklı hücre sayılarına sahip olmalı',
    'No angle, Cl or Cd column in the report file': "Report file'da açı, Cl ya da Cd sütunu bulunamadı",
    'Coarse and medium values are equal: the order of convergence is undefined': 'Kaba ve orta mesh değerleri aynı: yakınsama mertebesi tanımsız',
    'The mesh file is only available for the C-grid domain': 'Mesh dosyası yalnızca C-Grid domain için üretilir',
    'Mesh topology error: an edge is shared by more than two cells': 'Mesh topoloji hatası: bir kenar ikiden fazla hücreye ait',
    'Angles must be between -180 and 180 degrees': 'Açılar −180 ile 180 derece arasında olmalı',
    'Two angles get the same file name: keep angles at least 0.01° apart': 'İki açı aynı dosya adını alıyor: açılar arasında en az 0.01° fark olsun',
    'Speed, chord, density and viscosity must be positive': 'Hız, veter, yoğunluk ve viskozite pozitif olmalı',
    'Reynolds number must be at least 1000': 'Reynolds sayısı en az 1000 olmalı',
    'Edge is shorter than the requested cell size': 'Kenar, istenen hücre boyundan kısa; hücre boylarını küçültün',
    'NACA 4-digit code must be 4 digits': 'NACA 4 haneli kod 4 rakamdan oluşmalı',
    'Thickness must be between 1% and 40%': 'Kalınlık %1 ile %40 arasında olmalı',
    'Cambered NACA 4-digit needs a camber position (2nd digit) > 0': "Kamburlu NACA 4 haneli profilde kamburluk konumu (2. hane) 0'dan büyük olmalı",
    'Symmetric NACA 4-digit has no camber position: the 2nd digit must be 0': 'Simetrik NACA 4 haneli profilde kamburluk konumu yoktur: 2. hane 0 olmalı',
    'Surface extends past the trailing edge (camber/thickness too large)': 'Yüzey firar kenarını aşıyor (kamburluk/kalınlık çok büyük)',
    'NACA 5-digit code must be 5 digits': 'NACA 5 haneli kod 5 rakamdan oluşmalı',
    'A 5-digit code starting with 6 is a NACA 6-series name (e.g. 64-012), not a 5-digit section': '6 ile başlayan 5 haneli kod bir NACA 6 serisi adıdır (ör. 64-012), 5 haneli profil değildir',
    'Unsupported NACA 5-digit camber position (only standard, non-reflexed series: 2nd-3rd digits 10, 20, 30, 40, 50)': 'Desteklenmeyen NACA 5 haneli kamburluk konumu (yalnızca standart, refleks olmayan seri: 2.-3. haneler 10, 20, 30, 40, 50)',
    'NACA code must have 4 or 5 digits': 'NACA kodu 4 veya 5 haneli olmalı',
    'File does not contain enough coordinate rows': 'Dosyada yeterli koordinat satırı yok',
    'Could not find the leading edge inside the point loop': 'Nokta dizisinde hücum kenarı bulunamadı',
    'Each surface needs at least 3 distinct points': 'Her yüzeyde en az 3 farklı nokta olmalı',
    'Invalid chord in file': 'Dosyadaki veter uzunluğu geçersiz',
    'Points are not in order along the surface (mixed-up rows or more than one element)': 'Noktalar yüzey boyunca sıralı değil (satırlar karışmış ya da dosyada birden fazla eleman var)',
    'Airfoil has no thickness': 'Profilin kalınlığı yok (üst ve alt yüzey aynı)',
    'Upper and lower surfaces cross each other': 'Üst ve alt yüzey birbirini kesiyor (çakışma binde bir veterden fazla; dosyadaki noktaları kontrol edin)',
    'Split location must be between 0.05c and 0.9c': 'Bölme konumu 0.05c ile 0.9c arasında olmalı',
    'Skewness must be between 0 and 1': 'Skewness 0 ile 1 arasında olmalı',
    'Orthogonal quality must be between 0 and 1': 'Orthogonal quality 0 ile 1 arasında olmalı',
    'Wake length must be at least 0.5c': 'İz uzunluğu en az 0.5c olmalı',
    'Inlet radius must be larger than the chord': 'Giriş yarıçapı veter uzunluğundan büyük olmalı',
    'Top/bottom boundaries must be at least 0.5c away from the airfoil': 'Üst/alt sınırlar kanattan en az 0.5c uzakta olmalı',
    'Inlet must be at least 0.5c upstream of the leading edge': 'Giriş, hücum kenarının en az 0.5c önünde olmalı',
    'The outline needs at least 6 distinct points': 'Çizgide en az 6 farklı nokta olmalı',
    'The outline crosses itself': 'Çizgi kendini kesiyor (dosyadaki nokta sırasını kontrol edin)',
    'The outline crosses the front axis (the horizontal line ahead of the leading edge)': 'Çizgi ön ekseni (hücum kenarının önündeki yatay çizgiyi) kesiyor',
    'The outline crosses the wake axis (the horizontal line behind the trailing edge)': 'Çizgi iz eksenini (firar kenarının arkasındaki yatay çizgiyi) kesiyor',
    'Iterations must be an integer of at least 1': 'İterasyon sayısı en az 1 olan bir tam sayı olmalı',
    'Save interval must be a whole number of 0 or more': 'Kayıt aralığı 0 ya da daha büyük bir tam sayı olmalı',
    'Expression name may only contain letters, digits and _ and must not start with a digit': 'Expression adı yalnızca harf, rakam ve _ içerebilir ve rakamla başlayamaz',
    'Wall zone name may only contain letters, digits and _ . : -': 'Duvar bölgesi adı yalnızca harf, rakam ve _ . : - içerebilir',
    'Density must be a positive number': 'Yoğunluk pozitif bir sayı olmalı',
    'Speed must be a positive number': 'Hız pozitif bir sayı olmalı',
    'Chord must be a positive number': 'Veter pozitif bir sayı olmalı',
    'Depth must be a positive number': 'Derinlik pozitif bir sayı olmalı',
    'File name prefix may only contain letters, digits and _ . -': 'Dosya adı öneki yalnızca harf, rakam ve _ . - içerebilir',
    'Mach number, Reynolds number and chord must be positive': 'Mach sayısı, Reynolds sayısı ve veter pozitif olmalı',
    'Not a Fluent report file: no header line with the column names': 'Fluent report file değil: sütun adlarını içeren başlık satırı yok',
    'The report file has no data rows': 'Report file\'da veri satırı yok',
    'Column not in the report file': 'Bu sütun report file\'da yok',
    'The report files do not have the same columns': "Report file'ların sütunları aynı değil (aynı report definition'dan olmalılar)",
    'Folder must not contain a double quote': 'Klasör yolunda çift tırnak olamaz',
    'Folder must contain only ASCII characters (Fluent may not handle others)': 'Klasör yolunda yalnızca ASCII karakterler olmalı (Fluent diğerlerini işleyemeyebilir)',
    'Angle step too small: two angles get the same file name': 'Açı adımı çok küçük: iki açı aynı dosya adını alıyor',
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
