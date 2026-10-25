# Changelog

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
