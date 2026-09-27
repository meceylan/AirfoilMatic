import streamlit as st
import numpy as np
import plotly.graph_objects as go

def calculate_naca4(naca, c, n_points=100):
    m = int(naca[0]) / 100.0
    p = int(naca[1]) / 10.0
    t = int(naca[2:4]) / 100.0
    
    # 1. Matematiksel Bölme: X=0.3c'den ikiye ayırıyoruz
    beta_front = np.linspace(0, np.pi/2, n_points)
    xc_front = 0.3 * (1 - np.cos(beta_front))
    
    beta_rear = np.linspace(0, np.pi/2, n_points)
    xc_rear = 0.3 + 0.7 * np.sin(beta_rear)
    
    def get_coords(xc_arr):
        x = xc_arr * c
        # -0.1036 ile firar kenarı kusursuz kapatılıyor (Sliver Face / Kısa Kenar Çözümü)
        yt = 5 * t * c * (0.2969 * np.sqrt(xc_arr) - 0.1260 * xc_arr - 0.3516 * xc_arr**2 + 0.2843 * xc_arr**3 - 0.1036 * xc_arr**4)
        
        yc = np.zeros_like(xc_arr)
        dyc_dx = np.zeros_like(xc_arr)
        
        if p > 0:
            for i, val in enumerate(xc_arr):
                if val <= p:
                    yc[i] = c * (m / p**2) * (2 * p * val - val**2)
                    dyc_dx[i] = (m / p**2) * (2 * p - 2 * val)
                else:
                    yc[i] = c * (m / (1 - p)**2) * (1 - 2 * p + 2 * p * val - val**2)
                    dyc_dx[i] = (m / (1 - p)**2) * (2 * p - 2 * val)
                    
        theta = np.arctan(dyc_dx)
        xu = x - yt * np.sin(theta)
        yu = yc + yt * np.cos(theta)
        xl = x + yt * np.sin(theta)
        yl = yc - yt * np.cos(theta)
        return xu, yu, xl, yl

    # 4 Ayrı Dizi: Üst-Ön, Üst-Arka, Alt-Ön, Alt-Arka
    xu_f, yu_f, xl_f, yl_f = get_coords(xc_front)
    xu_r, yu_r, xl_r, yl_r = get_coords(xc_rear)
    
    return (xu_f, yu_f), (xu_r, yu_r), (xl_f, yl_f), (xl_r, yl_r)

def calculate_naca5(naca, c, n_points=100):
    L = int(naca[0])
    P = int(naca[1:3])
    T = int(naca[3:5])
    
    cl_opt = L * 0.15
    t = T / 100.0
    
    table = {
        10: (0.0580, 361.400),
        20: (0.1260, 39.060),
        30: (0.2025, 15.957),
        40: (0.2900, 6.643),
        50: (0.3910, 3.230)
    }
    
    if P not in table:
        raise ValueError("Desteklenmeyen NACA 5-digit kamburluk konumu. 2. ve 3. hane (P) 10, 20, 30, 40 veya 50 olmalıdır.")
        
    m, k1 = table[P]
    
    # 1. Matematiksel Bölme: X=0.3c'den ikiye ayırıyoruz
    beta_front = np.linspace(0, np.pi/2, n_points)
    xc_front = 0.3 * (1 - np.cos(beta_front))
    
    beta_rear = np.linspace(0, np.pi/2, n_points)
    xc_rear = 0.3 + 0.7 * np.sin(beta_rear)
    
    def get_coords(xc_arr):
        x = xc_arr * c
        # -0.1036 ile firar kenarı kusursuz kapatılıyor (Sliver Face / Kısa Kenar Çözümü)
        yt = 5 * t * c * (0.2969 * np.sqrt(xc_arr) - 0.1260 * xc_arr - 0.3516 * xc_arr**2 + 0.2843 * xc_arr**3 - 0.1036 * xc_arr**4)
        
        yc = np.zeros_like(xc_arr)
        dyc_dx = np.zeros_like(xc_arr)
        
        scale = cl_opt / 0.3 if cl_opt != 0 else 0.0
        
        for i, val in enumerate(xc_arr):
            if val <= m:
                yc[i] = scale * (k1 / 6.0) * (val**3 - 3 * m * val**2 + m**2 * (3 - m) * val) * c
                dyc_dx[i] = scale * (k1 / 6.0) * (3 * val**2 - 6 * m * val + m**2 * (3 - m))
            else:
                yc[i] = scale * (k1 * m**3 / 6.0) * (1 - val) * c
                dyc_dx[i] = scale * (-k1 * m**3 / 6.0)
                
        theta = np.arctan(dyc_dx)
        xu = x - yt * np.sin(theta)
        yu = yc + yt * np.cos(theta)
        xl = x + yt * np.sin(theta)
        yl = yc - yt * np.cos(theta)
        return xu, yu, xl, yl

    xu_f, yu_f, xl_f, yl_f = get_coords(xc_front)
    xu_r, yu_r, xl_r, yl_r = get_coords(xc_rear)
    
    return (xu_f, yu_f), (xu_r, yu_r), (xl_f, yl_f), (xl_r, yl_r)


def process_custom_airfoil(file_content, c):
    lines = file_content.decode("utf-8").split('\n')
    coords = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            try:
                coords.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
    
    coords = np.array(coords) * c
    X, Y = coords[:, 0], coords[:, 1]
    
    # Evrensel Yüzey Ayırıcı (Hem Selig hem Lednicer formatları için)
    le_idx = np.argmin(X)
    te_idx = np.argmax(X)
    
    i1 = min(le_idx, te_idx)
    i2 = max(le_idx, te_idx)
    
    # Kanadı iki fiziksel yüzeye ayır
    part_a_X, part_a_Y = X[i1:i2+1], Y[i1:i2+1]
    part_b_X, part_b_Y = np.concatenate([X[i2:], X[:i1+1]]), np.concatenate([Y[i2:], Y[:i1+1]])
    
    # X'e göre sırala (Fermuar / Zigzag etkisini KESİN olarak önler)
    sort_a = np.argsort(part_a_X)
    part_a_X, part_a_Y = part_a_X[sort_a], part_a_Y[sort_a]
    
    sort_b = np.argsort(part_b_X)
    part_b_X, part_b_Y = part_b_X[sort_b], part_b_Y[sort_b]
    
    # Hangisi Üst, Hangisi Alt? (Y ortalamasına bak)
    if np.mean(part_a_Y) > np.mean(part_b_Y):
        Xu, Yu = part_a_X, part_a_Y
        Xl, Yl = part_b_X, part_b_Y
    else:
        Xu, Yu = part_b_X, part_b_Y
        Xl, Yl = part_a_X, part_a_Y
        
    # Aynı X değerlerini temizle (İnterpolasyon için şart)
    Xu, unq_u = np.unique(Xu, return_index=True); Yu = Yu[unq_u]
    Xl, unq_l = np.unique(Xl, return_index=True); Yl = Yl[unq_l]
    
    # 0.3c noktasını hesapla
    x_split = 0.3 * c
    y_split_u = np.interp(x_split, Xu, Yu)
    y_split_l = np.interp(x_split, Xl, Yl)
    
    # 4 Parçaya Böl ve 0.3c Noktasını Zorla Ekle
    xu_front = np.append(Xu[Xu < x_split], x_split)
    yu_front = np.append(Yu[Xu < x_split], y_split_u)
    
    xu_rear = np.insert(Xu[Xu > x_split], 0, x_split)
    yu_rear = np.insert(Yu[Xu > x_split], 0, y_split_u)
    
    xl_front = np.append(Xl[Xl < x_split], x_split)
    yl_front = np.append(Yl[Xl < x_split], y_split_l)
    
    xl_rear = np.insert(Xl[Xl > x_split], 0, x_split)
    yl_rear = np.insert(Yl[Xl > x_split], 0, y_split_l)
    
    return xu_front, yu_front, xu_rear, yu_rear, xl_front, yl_front, xl_rear, yl_rear, y_split_u, y_split_l

st.set_page_config(page_title="AirfoilMatic v0.2 Beta", layout="wide")

st.title("AirfoilMatic V0.2 Beta: 2B CFD Domain Generator")

# --- 4. ARAYÜZ SADELEŞTİRMESİ ---
st.sidebar.header("AirfoilMatic V0.2 Beta")

data_source = st.sidebar.radio("Kanat Veri Kaynağı", ['NACA (4 veya 5 Haneli)', 'Özel Kanat (.dat / .txt)'])

naca_input = "0012"
custom_file = None
file_name_prefix = "domain"

if data_source == 'NACA (4 veya 5 Haneli)':
    naca_input = st.sidebar.text_input("NACA Kodu", value="0012", max_chars=5).strip()
    file_name_prefix = f"domain_naca{naca_input}"
else:
    custom_file = st.sidebar.file_uploader("Özel Kanat Dosyası Yükle (.dat, .txt)", type=["dat", "txt"])
    if custom_file:
        file_name_prefix = f"domain_{custom_file.name.split('.')[0]}"
    else:
        file_name_prefix = "domain_custom"

domain_type = st.sidebar.selectbox("Akış Alanı (Domain) Tipi", ['C-Grid (Standart)', 'Dikdörtgen (Rüzgar Tüneli)'])

chord_c = st.sidebar.number_input("Chord Uzunluğu (c) [m]", value=1.0, step=0.1, min_value=0.1)
R_inlet = st.sidebar.number_input("Giriş Yarıçapı/Uzaklığı (Rinlet) [m]", value=20.0, step=1.0, min_value=1.0)
L_wake = st.sidebar.number_input("İz Uzunluğu (Lwake) [m]", value=40.0, step=1.0, min_value=1.0)

# Sidebar Download Butonu (erişilebilirlik için ek konum)
sidebar_download_placeholder = st.sidebar.empty()

st.sidebar.warning("⚠️ Beta Sürümü (v0.2)\nBu araç 2B CFD ön işlemini hızlandırmak için tasarlanmıştır. Çıktıların analiz uygunluğunu (geometri, ağ yapısı vb.) Ansys ortamında mutlaka doğrulayın.")

# --- GEOMETRİ VE TOPOLOJİ HESAPLAMALARI ---
try:
    if data_source == 'NACA (4 veya 5 Haneli)':
        if len(naca_input) not in [4, 5] or not naca_input.isdigit():
            st.error("Lütfen geçerli 4 veya 5 haneli bir NACA kodu girin.")
            st.stop()
            
        if len(naca_input) == 4:
            (xu_f, yu_f), (xu_r, yu_r), (xl_f, yl_f), (xl_r, yl_r) = calculate_naca4(naca_input, chord_c, n_points=100)
        elif len(naca_input) == 5:
            (xu_f, yu_f), (xu_r, yu_r), (xl_f, yl_f), (xl_r, yl_r) = calculate_naca5(naca_input, chord_c, n_points=100)
            
        airfoil_label = f'NACA {naca_input}'
    else:
        if custom_file is None:
            st.info("Lütfen bir kanat dosyası yükleyin.")
            st.stop()
        xu_f, yu_f, xu_r, yu_r, xl_f, yl_f, xl_r, yl_r, y_split_u, y_split_l = process_custom_airfoil(custom_file.read(), chord_c)
        airfoil_label = 'Özel Kanat'
except Exception as e:
    st.error(f"Kanat geometrisi oluşturulurken bir hata oluştu: {e}")
    st.stop()

# 2. Dikey Çizgilerin Milimetrik Teması (X=0.3c tam noktaları)
x_up_03 = xu_f[-1]    
y_up_03 = yu_f[-1]    
x_low_03 = xl_f[-1]   
y_low_03 = yl_f[-1]   

# Firar kenarı tam noktaları (TE)
x_te_up = xu_r[-1]
y_te_up = yu_r[-1]
x_te_low = xl_r[-1]
y_te_low = yl_r[-1]

# NaN Kayıp Çizgi Kurtarma (Safe Val) Algoritması
def safe_val(val, fallback_arr):
    if val is None or np.isnan(val):
        valid_vals = fallback_arr[~np.isnan(fallback_arr)]
        return valid_vals[-1] if len(valid_vals) > 0 else 0.0
    return val

y_up_03 = safe_val(y_up_03, yu_f)
y_low_03 = safe_val(y_low_03, yl_f)
y_te_up = safe_val(y_te_up, yu_r)
y_te_low = safe_val(y_te_low, yl_r)

# Hücum kenarı noktası
x_le = xu_f[0]
y_le = safe_val(yu_f[0], yu_f)

domain_groups = []
split_lines = []

X_exit = chord_c + L_wake

if domain_type == 'C-Grid (Standart)':
    # Dış Sınırlar (Outer Boundaries)
    # C-Arc (İnlet)
    theta_arc = np.linspace(np.pi/2, 3*np.pi/2, 100)
    x_arc = R_inlet * np.cos(theta_arc)
    y_arc = R_inlet * np.sin(theta_arc)

    # Üst Sınır
    x_top = np.linspace(0, X_exit, 50)
    y_top = np.ones(50) * R_inlet

    # Alt Sınır
    x_bot = np.linspace(0, X_exit, 50)
    y_bot = -np.ones(50) * R_inlet

    # Çıkış (Outlet)
    y_outlet = np.linspace(R_inlet, -R_inlet, 50)
    x_outlet = np.ones(50) * X_exit

    domain_groups.extend([
        {"name": "C-Arc (İnlet)", "x": x_arc, "y": y_arc},
        {"name": "Üst Sınır", "x": x_top, "y": y_top},
        {"name": "Alt Sınır", "x": x_bot, "y": y_bot},
        {"name": "Çıkış (Outlet)", "x": x_outlet, "y": y_outlet}
    ])
    
    # İç Bölme Çizgileri
    # Ön Yatay Eksen (LE'den İnlet'e)
    x_front_split = np.linspace(-R_inlet, x_le, 50)
    y_front_split = np.ones(50) * y_le
else:
    # Dikdörtgen (Rüzgar Tüneli) Domain
    # Sol Sınır (İnlet)
    y_inlet = np.linspace(R_inlet, -R_inlet, 50)
    x_inlet = -np.ones(50) * R_inlet
    
    # Üst Sınır
    x_top = np.linspace(-R_inlet, X_exit, 50)
    y_top = np.ones(50) * R_inlet
    
    # Alt Sınır
    x_bot = np.linspace(-R_inlet, X_exit, 50)
    y_bot = -np.ones(50) * R_inlet
    
    # Çıkış (Outlet)
    y_outlet = np.linspace(R_inlet, -R_inlet, 50)
    x_outlet = np.ones(50) * X_exit
    
    domain_groups.extend([
        {"name": "Sol Sınır (İnlet)", "x": x_inlet, "y": y_inlet},
        {"name": "Üst Sınır", "x": x_top, "y": y_top},
        {"name": "Alt Sınır", "x": x_bot, "y": y_bot},
        {"name": "Çıkış (Outlet)", "x": x_outlet, "y": y_outlet}
    ])
    
    # İç Bölme Çizgileri
    # Ön Yatay Eksen (LE'den İnlet'e)
    x_front_split = np.linspace(-R_inlet, x_le, 50)
    y_front_split = np.ones(50) * y_le

# Küt Firar Kenarı (Blunt TE) Orta Noktası
x_te_mid = (x_te_up + x_te_low) / 2.0
y_te_mid = (y_te_up + y_te_low) / 2.0

# Arka İz Eksen (TE'den Outlet'e) - Y ekseninin tam ortasından başlar
x_wake_split = np.linspace(x_te_mid, X_exit, 50)
y_wake_split = np.ones(50) * y_te_mid 

# X=0.3c Dikey Bölmeleri
x_split_up_03 = np.ones(50) * x_up_03
y_split_up_03 = np.linspace(y_up_03, R_inlet, 50)

x_split_low_03 = np.ones(50) * x_low_03
y_split_low_03 = np.linspace(y_low_03, -R_inlet, 50)

# Gerçek Firar Kenarı (Real TE) Dikey Bölmeleri
x_split_up_te = np.ones(50) * x_te_up
y_split_up_te = np.linspace(y_te_up, R_inlet, 50)

x_split_low_te = np.ones(50) * x_te_low
y_split_low_te = np.linspace(y_te_low, -R_inlet, 50)

split_lines.extend([
    {"name": "Ön Yatay Eksen", "x": x_front_split, "y": y_front_split},
    {"name": "Arka İz Eksen", "x": x_wake_split, "y": y_wake_split},
    {"name": "Üst Ön Dikey (X=0.3c)", "x": x_split_up_03, "y": y_split_up_03},
    {"name": "Alt Ön Dikey (X=0.3c)", "x": x_split_low_03, "y": y_split_low_03},
    {"name": "Üst Arka Dikey (X=TE)", "x": x_split_up_te, "y": y_split_up_te},
    {"name": "Alt Arka Dikey (X=TE)", "x": x_split_low_te, "y": y_split_low_te}
])

# Küt Firar Kenarı (Blunt TE) Kapatma
te_y_ust = y_te_up
te_y_alt = y_te_low

# Eğer uçlar açıksa (fark >= 0.001) dikey çizgi ile bağla
if abs(te_y_ust - te_y_alt) >= 0.001:
    x_blunt_te = np.linspace(x_te_up, x_te_low, 50)
    y_blunt_te = np.linspace(te_y_ust, te_y_alt, 50)
    split_lines.append({"name": "Küt Firar Kenarı Kapatma", "x": x_blunt_te, "y": y_blunt_te})

# --- 5. GÖRSELLEŞTİRME (PLOTLY) ---

# 4. Plotly Çizim Döngüsü (Fill=ToSelf için)
x_plot = np.concatenate([xu_f, xu_r, xl_r[::-1], xl_f[::-1]])
y_plot = np.concatenate([yu_f, yu_r, yl_r[::-1], yl_f[::-1]])

def add_airfoil_to_fig(fig_obj):
    # Çizgileri 4 ayrı parça olarak (saçaklanmayı önlemek için) düz siyah renk ile çiziyoruz
    fig_obj.add_trace(go.Scatter(x=xu_f, y=yu_f, mode='lines', line=dict(color='black', width=2), showlegend=False))
    fig_obj.add_trace(go.Scatter(x=xu_r, y=yu_r, mode='lines', line=dict(color='black', width=2), showlegend=False))
    fig_obj.add_trace(go.Scatter(x=xl_f, y=yl_f, mode='lines', line=dict(color='black', width=2), showlegend=False))
    fig_obj.add_trace(go.Scatter(x=xl_r, y=yl_r, mode='lines', line=dict(color='black', width=2), showlegend=False))
    
    # Tüm kapalı poligonu şeffaf kenar çizgisiyle ('rgba(0,0,0,0)') içi dolu (fill='toself') şekilde atıyoruz
    # Böylece fill işlemi saçağa neden olmadan sorunsuzca dolguyu yapıyor.
    fig_obj.add_trace(go.Scatter(
        x=x_plot, 
        y=y_plot, 
        fill='toself', 
        fillcolor='black', 
        line=dict(color='rgba(0,0,0,0)', width=0),
        name=airfoil_label
    ))

# --- Grafik 1: Yakın Çekim Kanat Profili (Zoom-In) ---
st.subheader("🔎 Yakın Çekim: Kanat Profili ve Kesme (Split) Noktaları")
fig_zoom = go.Figure()

# Sadece iç bölmeler (Gri ve Kesik Çizgi formatında)
for grp in split_lines:
    fig_zoom.add_trace(go.Scatter(x=grp['x'], y=grp['y'], mode='lines', name=grp['name'], line=dict(color='gray', width=1, dash='dash')))

# Airfoil Poligonu (Saçaklanma Düzeltmesiyle)
add_airfoil_to_fig(fig_zoom)

fig_zoom.update_layout(
    xaxis_title="X Koordinatı [m]",
    yaxis_title="Y Koordinatı [m]",
    xaxis=dict(range=[-0.1*chord_c, 1.1*chord_c]),
    yaxis=dict(scaleanchor="x", scaleratio=1, range=[-0.5*chord_c, 0.5*chord_c]),
    showlegend=True,
    height=500,
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_zoom, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': True})


# --- Grafik 2: Tam Akış Alanı (Domain) Topolojisi ---
st.subheader("🌐 Uzak Çekim: CFD Akış Alanı Sınırları")
fig_full = go.Figure()

# Dış Sınırlar
for grp in domain_groups:
    fig_full.add_trace(go.Scatter(x=grp['x'], y=grp['y'], mode='lines', name=grp['name'], line=dict(color='deepskyblue', width=2)))

# İç Bölmeler
for grp in split_lines:
    fig_full.add_trace(go.Scatter(x=grp['x'], y=grp['y'], mode='lines', name=grp['name'], line=dict(color='gray', width=1, dash='dash')))

# Airfoil Poligonu (Saçaklanma Düzeltmesiyle)
add_airfoil_to_fig(fig_full)

fig_full.update_layout(
    xaxis_title="X Koordinatı [m]",
    yaxis_title="Y Koordinatı [m]",
    yaxis=dict(scaleanchor="x", scaleratio=1), 
    showlegend=True,
    height=700,
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_full, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': True})

# --- 3. ANSYS TXT EXPORT GÜNCELLEMESİ ---
def generate_ansys_txt():
    lines = []
    
    def add_points(group_num, x_arr, y_arr):
        for i, (px, py) in enumerate(zip(x_arr, y_arr)):
            lines.append(f"{group_num}\t{i+1}\t{px:.6f}\t{py:.6f}\t0.000000")

    # Kanat yüzeyi ilk 4 grup olarak basılıyor
    add_points(1, xu_f, yu_f) # Grup 1: Üst-Ön
    add_points(2, xu_r, yu_r) # Grup 2: Üst-Arka
    add_points(3, xl_f, yl_f) # Grup 3: Alt-Ön
    add_points(4, xl_r, yl_r) # Grup 4: Alt-Arka
    
    # Dış Sınırlar bu 4 grubun peşine ekleniyor
    grp_idx = 5
    for grp in domain_groups:
        add_points(grp_idx, grp['x'], grp['y'])
        grp_idx += 1
        
    # İç Bölme Çizgileri peşinden ekleniyor
    for grp in split_lines:
        add_points(grp_idx, grp['x'], grp['y'])
        grp_idx += 1
        
    return "\n".join(lines)

try:
    txt_data = generate_ansys_txt()

    st.download_button(
        label="⬇️ Ansys TXT İndir",
        data=txt_data,
        file_name=f"{file_name_prefix}.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_main"
    )

    sidebar_download_placeholder.download_button(
        label="⬇️ Ansys TXT İndir",
        data=txt_data,
        file_name=f"{file_name_prefix}.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_sidebar"
    )
except Exception as e:
    st.error(f"Dışa aktarma verisi oluşturulurken hata: {e}")
