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

# ============ HILANGKAN SEMUA ELEMEN DEFAULT STREAMLIT ============
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stFileUploader {visibility: hidden !important; height: 0 !important; padding: 0 !important; margin: 0 !important;}
            .stFileUploader > div {display: none !important;}
            div[data-testid="stToolbar"] {display: none !important;}
            .main > div {padding-top: 0rem; padding-bottom: 0rem;}
            .stApp {background: #fdf6f9;}
            .stProgress > div > div {background: linear-gradient(90deg, #f06292, #ab47bc) !important; border-radius: 20px !important; height: 20px !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ============ CSS PINK SOFT ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap');
    
    html, body, .stApp {
        font-family: 'Quicksand', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(160deg, #fdf6f9 0%, #fce4ec 35%, #f8e8f5 65%, #f3e5f5 100%);
    }

    .header {
        text-align: center;
        padding: 25px 0 15px 0;
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(244, 143, 177, 0.1);
        margin-bottom: 20px;
        border-radius: 0 0 30px 30px;
    }
    .header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: 5px;
        margin: 0;
        background: linear-gradient(135deg, #f06292, #ec407a, #ab47bc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .header p {
        color: #b08a9a;
        font-size: 0.95rem;
        letter-spacing: 6px;
        font-weight: 600;
        margin-top: -2px;
        opacity: 0.8;
    }

    .card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 28px;
        padding: 28px 30px;
        box-shadow: 0 15px 50px rgba(233, 30, 99, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.7);
        transition: all 0.3s ease;
        height: 100%;
    }
    .card:hover {
        box-shadow: 0 20px 60px rgba(233, 30, 99, 0.12);
        transform: translateY(-2px);
    }

    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #4a2a40;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
        border-bottom: 2px solid #f8bbd0;
        padding-bottom: 12px;
    }

    /* UPLOAD BOX - SATU AREA */
    .upload-box {
        border: 2.5px dashed #f8bbd0;
        border-radius: 24px;
        padding: 50px 20px;
        text-align: center;
        background: rgba(255, 255, 255, 0.3);
        transition: all 0.4s ease;
        cursor: pointer;
    }
    .upload-box:hover {
        border-color: #f06292;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(1.01);
        box-shadow: 0 8px 30px rgba(240, 98, 146, 0.1);
    }
    .upload-box .icon { font-size: 4rem; display: block; margin-bottom: 8px; }
    .upload-box .main { font-weight: 700; font-size: 1.2rem; color: #3d2a35; }
    .upload-box .sub { color: #b08a9a; font-size: 0.85rem; margin-top: 5px; }

    .status {
        text-align: center;
        font-size: 0.8rem;
        color: #81c784;
        font-weight: 600;
        padding: 6px 0;
        background: rgba(129, 199, 132, 0.08);
        border-radius: 50px;
        margin-bottom: 18px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #f06292, #ab47bc) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 14px 20px !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(240, 98, 146, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        letter-spacing: 2px;
        font-family: 'Quicksand', sans-serif !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 40px rgba(240, 98, 146, 0.45) !important;
    }

    .result-card {
        background: linear-gradient(135deg, #fff5f8, #fce4ec);
        border-radius: 18px;
        padding: 20px 25px;
        border-left: 6px solid #f06292;
        margin: 15px 0;
        animation: fadeUp 0.5s ease;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .result-name { font-size: 2.6rem; font-weight: 700; color: #2d1b26; }
    .result-acc { font-size: 2rem; font-weight: 700; color: #81c784; text-align: right; }

    .desc-box {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        padding: 15px 20px;
        border-left: 4px solid #ab47bc;
        margin: 15px 0;
    }
    .desc-title { font-weight: 700; color: #6a1b4d; margin-bottom: 5px; font-size: 0.95rem; }
    .desc-item { padding: 4px 0; font-size: 0.9rem; color: #3d2a35; border-bottom: 1px solid rgba(0,0,0,0.03); }
    .desc-item:last-child { border-bottom: none; }

    .footer {
        text-align: center;
        padding: 25px 0 15px 0;
        color: #c4aab6;
        font-size: 0.8rem;
        letter-spacing: 2px;
        border-top: 1px solid rgba(240, 98, 146, 0.08);
        margin-top: 20px;
    }
    .footer .love { color: #f06292; }
    .footer span { margin: 0 6px; }

    @media (max-width: 768px) {
        .header h1 { font-size: 2.2rem; }
        .result-name { font-size: 1.8rem; }
        .result-acc { font-size: 1.5rem; }
        .card { padding: 18px; }
        .upload-box { padding: 30px 15px; }
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
<div class="header">
    <h1>🌸 FLOWER WEBSITE</h1>
    <p>Identifikasi 5 Jenis Bunga</p>
</div>
""", unsafe_allow_html=True)

# ============ DATABASE ============
BUNGA_DESKRIPSI = {
    'tulip': {'fakta': ['🌷 Simbol nasional Belanda', '🌷 3.000+ varietas', '🌷 Merah = cinta, Kuning = kegembiraan', '🌷 Fenomena "Tulip Mania" abad 17']},
    'lily': {'fakta': ['🌸 Bunga tertua (3.000 tahun SM)', '🌸 6 kelopak, lambang kemurnian', '🌸 Bunga dewi Hera', '🌸 Tumbuh hingga 2,5 meter']},
    'orchid': {'fakta': ['🌺 28.000+ spesies', '🌺 Ditemukan di semua benua kecuali Antartika', '🌺 3 juta biji per kapsul', '🌺 Hidup hingga 100 tahun']},
    'sunflower': {'fakta': ['🌻 Tumbuh hingga 3 meter', '🌻 Mengikuti pergerakan matahari', '🌻 Ribuan bunga kecil dalam 1 kepala', '🌻 Bunga nasional Ukraina']},
    'lotus': {'fakta': ['🪷 Bertahan 1.000 tahun kering', '🪷 Bunga suci Buddha & Hindu', '🪷 Tumbuh di lumpur tapi tetap bersih', '🪷 Biji berkecambah setelah 1.300 tahun']}
}
def get_fakta(n): return BUNGA_DESKRIPSI.get(n.lower(), {}).get('fakta')

# ============ LOAD MODEL ============
@st.cache_resource
def load_model():
    path = 'model_bunga_densenet121.h5'
    fid = "12ZJi1HbkI8ian7fWM0K98ADi1tpMvU4y"
    if os.path.exists(path):
        try: return tf.keras.models.load_model(path)
        except: os.remove(path)
    with st.spinner('⏳ Mengunduh Model...'):
        try:
            url = f'https://drive.google.com/uc?export=download&id={fid}'
            r = requests.get(url, stream=True)
            if 'confirm' in r.text:
                c = re.search(r'confirm=([^&]+)', r.text)
                if c: url = f'https://drive.google.com/uc?export=download&confirm={c.group(1)}&id={fid}'; r = requests.get(url, stream=True)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            return tf.keras.models.load_model(path)
        except: return None

class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']
model = load_model()
if model is None:
    st.error("❌ Gagal memuat model.")
    st.stop()

# ============ 2 KOLOM ============
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📸 Upload Gambar</div>')
    st.markdown('<div class="status">✅ Model siap digunakan</div>')
    
    # ============ UPLOAD - HANYA 1 AREA ============
    uploaded = st.file_uploader("", type=['jpg','png','jpeg'], label_visibility="collapsed")
    
    if not uploaded:
        st.markdown("""
        <div class="upload-box">
            <span class="icon">🌸</span>
            <div class="main">Klik atau seret gambar</div>
            <div class="sub">JPG, PNG, JPEG • Maks 200MB</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        img = Image.open(uploaded)
        st.image(img, caption="📷 Gambar yang diupload", use_column_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔍 Hasil Klasifikasi</div>')
    
    if uploaded:
        if st.button("🌸 KLASIFIKASI SEKARANG", type="primary", use_container_width=True):
            with st.spinner("Menganalisis..."):
                img_r = img.resize((224,224))
                x = np.array(img_r) / 255.0
                x = np.expand_dims(x, axis=0)
                
                pred = model.predict(x)
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                acc = pred[0][idx] * 100
                
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([2,1])
                icon = {'tulip':'🌷','lily':'🌸','orchid':'🌺','sunflower':'🌻','lotus':'🪷'}.get(nama, '🌸')
                with c1: st.markdown(f'<div class="result-name">{icon} {nama.upper()}</div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="result-acc">{acc:.2f}%</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                fakta = get_fakta(nama)
                if fakta:
                    st.markdown('<div class="desc-box">', unsafe_allow_html=True)
                    st.markdown('<div class="desc-title">📖 Fakta Menarik</div>', unsafe_allow_html=True)
                    for item in fakta: st.markdown(f'<div class="desc-item">{item}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("📊 **Probabilitas**")
                for i, name in enumerate(class_names):
                    prob = pred[0][i] * 100
                    bc, pc = st.columns([4,1])
                    with bc: st.progress(int(prob) / 100)
                    with pc: st.markdown(f'<span style="font-weight:700;">{prob:.1f}%</span>', unsafe_allow_html=True)
                    st.caption(name.upper())
    else:
        st.markdown('<div style="padding:50px 0;text-align:center;color:#b08a9a;">🌸 Upload gambar<br>untuk memulai</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("""
<div class="footer">
    🌸 <b>FLOWER WEBSITE</b> <span>·</span> Dibuat dengan <span class="love">♥</span> untuk UAS <span>·</span> Model DenseNet121
    <br>
    <span>🌷 Tulip</span> <span>🌸 Lily</span> <span>🌺 Orchid</span> <span>🌻 Sunflower</span> <span>🪷 Lotus</span>
</div>
""", unsafe_allow_html=True)
