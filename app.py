import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

# ============ KONFIGURASI ============
st.set_page_config(
    page_title="FLOWER WEBSITE",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ CSS ============
st.markdown("""
<style>
    /* SEMBUNYIKAN DEFAULT */
    #MainMenu {display: none !important;}
    footer {display: none !important;}
    header {display: none !important;}
    .stFileUploader {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    .main > div {padding-top: 0 !important; padding-bottom: 0 !important;}
    
    /* BACKGROUND PINK SOFT */
    .stApp {
        background: linear-gradient(145deg, #fdf6f9 0%, #fce4ec 50%, #f8e8f5 100%);
    }
    
    /* HEADER */
    .header {
        text-align: center;
        padding: 35px 0 15px 0;
        margin-bottom: 25px;
    }
    .header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: 5px;
        margin: 0;
        background: linear-gradient(135deg, #f06292, #ab47bc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .header p {
        color: #b08a9a;
        font-size: 0.95rem;
        letter-spacing: 8px;
        font-weight: 600;
        margin: 0;
    }

    /* UPLOAD BOX - TANPA CARD */
    .upload-box {
        border: 2.5px dashed #e8c0d0;
        border-radius: 20px;
        padding: 45px 20px;
        text-align: center;
        background: rgba(255,255,255,0.25);
        transition: 0.3s;
        cursor: pointer;
        margin: 10px 0;
    }
    .upload-box:hover {
        border-color: #f06292;
        background: rgba(255,255,255,0.5);
    }
    .upload-box .icon { font-size: 3.5rem; display: block; }
    .upload-box .main { font-size: 1.1rem; font-weight: 700; color: #3d2a35; margin-top: 5px; }
    .upload-box .sub { color: #b08a9a; font-size: 0.8rem; }

    /* TOMBOL */
    .stButton > button {
        background: linear-gradient(135deg, #f06292, #ab47bc) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 14px !important;
        border-radius: 50px !important;
        border: none !important;
        width: 100% !important;
        letter-spacing: 2px;
        box-shadow: 0 8px 25px rgba(240,98,146,0.3) !important;
        transition: 0.3s !important;
        margin: 10px 0 !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(240,98,146,0.5) !important;
    }

    /* HASIL LANGSUNG */
    .result-box {
        background: rgba(255,255,255,0.5);
        border-radius: 16px;
        padding: 18px 22px;
        border-left: 5px solid #f06292;
        margin: 15px 0;
    }
    .result-name { font-size: 2.2rem; font-weight: 700; color: #2d1b26; }
    .result-acc { font-size: 1.8rem; font-weight: 700; color: #66bb6a; text-align: right; }

    .desc-box {
        background: rgba(255,255,255,0.4);
        border-radius: 14px;
        padding: 12px 18px;
        border-left: 4px solid #ab47bc;
        margin: 12px 0;
    }
    .desc-title { font-weight: 700; color: #6a1b4d; font-size: 0.9rem; }
    .desc-item { font-size: 0.85rem; color: #3d2a35; padding: 3px 0; border-bottom: 1px solid rgba(0,0,0,0.03); }
    .desc-item:last-child { border-bottom: none; }

    .stProgress > div > div {
        background: linear-gradient(90deg, #f06292, #ab47bc) !important;
        border-radius: 20px !important;
        height: 18px !important;
    }

    .footer {
        text-align: center;
        padding: 25px 0 15px 0;
        color: #c4aab6;
        font-size: 0.75rem;
        letter-spacing: 2px;
        border-top: 1px solid rgba(240,98,146,0.08);
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
<div class="header">
    <h1>🌸 FLOWER WEBSITE</h1>
    <p>IDENTIFIKASI 5 JENIS BUNGA</p>
</div>
""", unsafe_allow_html=True)

# ============ DATABASE ============
BUNGA = {
    'tulip': ['🌷 Simbol nasional Belanda', '🌷 3.000+ varietas', '🌷 Merah=cinta, Kuning=kegembiraan', '🌷 Fenomena "Tulip Mania"'],
    'lily': ['🌸 Bunga tertua (3.000 tahun SM)', '🌸 6 kelopak, lambang kemurnian', '🌸 Bunga dewi Hera', '🌸 Tumbuh hingga 2,5 meter'],
    'orchid': ['🌺 28.000+ spesies', '🌺 Ditemukan di semua benua', '🌺 3 juta biji per kapsul', '🌺 Hidup hingga 100 tahun'],
    'sunflower': ['🌻 Tumbuh hingga 3 meter', '🌻 Mengikuti pergerakan matahari', '🌻 Ribuan bunga kecil', '🌻 Bunga nasional Ukraina'],
    'lotus': ['🪷 Bertahan 1.000 tahun kering', '🪷 Bunga suci Buddha & Hindu', '🪷 Tumbuh di lumpur tetap bersih', '🪷 Biji berkecambah 1.300 tahun']
}
def get_fakta(n): return BUNGA.get(n.lower())

# ============ LOAD MODEL ============
@st.cache_resource
def load_model():
    path = 'model_bunga_densenet121.h5'
    fid = "12ZJi1HbkI8ian7fWM0K98ADi1tpMvU4y"
    if os.path.exists(path):
        try: return tf.keras.models.load_model(path)
        except: os.remove(path)
    with st.spinner('⏳ Download model...'):
        try:
            url = f'https://drive.google.com/uc?export=download&id={fid}'
            r = requests.get(url, stream=True)
            if 'confirm' in r.text:
                c = re.search(r'confirm=([^&]+)', r.text)
                if c:
                    url = f'https://drive.google.com/uc?export=download&confirm={c.group(1)}&id={fid}'
                    r = requests.get(url, stream=True)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            return tf.keras.models.load_model(path)
        except: return None

class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']
model = load_model()
if model is None:
    st.error("❌ Gagal memuat model")
    st.stop()

# ============ STATUS ============
st.markdown('<p style="text-align:center;color:#66bb6a;font-weight:600;font-size:0.85rem;">✅ Model siap digunakan</p>', unsafe_allow_html=True)

# ============ 2 KOLOM ============
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    # === UPLOAD ===
    uploaded = st.file_uploader("", type=['jpg','png','jpeg'], label_visibility="collapsed")
    
    if not uploaded:
        st.markdown("""
        <div class="upload-box">
            <span class="icon">🌸</span>
            <div class="main">Klik atau seret gambar</div>
            <div class="sub">JPG, PNG, JPEG • Max 200MB</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        img = Image.open(uploaded)
        st.image(img, caption="📷 Gambar yang diupload", use_column_width=True)

with col2:
    if uploaded:
        if st.button("🌺 KLASIFIKASI", type="primary", use_container_width=True):
            with st.spinner("Menganalisis..."):
                img_r = img.resize((224,224))
                x = np.array(img_r) / 255.0
                x = np.expand_dims(x, axis=0)
                
                pred = model.predict(x)
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                acc = pred[0][idx] * 100
                
                # HASIL
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                c1, c2 = st.columns([2,1])
                icon = {'tulip':'🌷','lily':'🌸','orchid':'🌺','sunflower':'🌻','lotus':'🪷'}.get(nama,'🌸')
                with c1: st.markdown(f'<div class="result-name">{icon} {nama.upper()}</div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="result-acc">{acc:.1f}%</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # FAKTA
                fakta = get_fakta(nama)
                if fakta:
                    st.markdown('<div class="desc-box">', unsafe_allow_html=True)
                    st.markdown('<div class="desc-title">📖 Fakta Menarik</div>', unsafe_allow_html=True)
                    for item in fakta:
                        st.markdown(f'<div class="desc-item">{item}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # PROBABILITAS
                st.markdown("📊 **Probabilitas**")
                for i, name in enumerate(class_names):
                    prob = pred[0][i] * 100
                    bc, pc = st.columns([4,1])
                    with bc: st.progress(int(prob) / 100)
                    with pc: st.markdown(f'<span style="font-weight:700;">{prob:.1f}%</span>', unsafe_allow_html=True)
                    st.caption(name.upper())
    else:
        st.markdown('<p style="text-align:center;color:#b08a9a;padding:50px 0;">🌸 Upload gambar untuk memulai</p>', unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("""
<div class="footer">
    🌸 FLOWER WEBSITE • Dibuat dengan ❤️ untuk UAS • Model DenseNet121
    <br>
    🌷 Tulip • 🌸 Lily • 🌺 Orchid • 🌻 Sunflower • 🪷 Lotus
</div>
""", unsafe_allow_html=True)
