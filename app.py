import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

# ============ KONFIGURASI ============
st.set_page_config(
    page_title="🌺 FLOWER WEBSITE",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ CSS ============
st.markdown("""
<style>
    /* Reset */
    .main > div { padding-top: 0; }
    
    /* Background */
    .stApp {
        background: linear-gradient(160deg, #fce4ec 0%, #f8e8f5 40%, #f3e5f5 70%, #e8eaf6 100%);
        min-height: 100vh;
    }
    
    /* Header */
    .header {
        text-align: center;
        padding: 20px 0 5px 0;
    }
    .header h1 {
        font-size: 4.2em;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(135deg, #e91e63, #ff6f00, #f9a825, #2e7d32, #0d47a1, #6a1b9a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 5px;
    }
    .header .sub {
        font-size: 1.15em;
        color: #6a1b4d;
        font-weight: 500;
        opacity: 0.8;
        letter-spacing: 4px;
        margin-top: 0;
    }
    .header .flowers-deco {
        font-size: 2em;
        opacity: 0.4;
        margin: 5px 0;
        letter-spacing: 12px;
    }
    
    /* Glass Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.82);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 28px;
        padding: 28px 32px;
        box-shadow: 0 10px 40px rgba(233, 30, 99, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin: 10px 0;
        transition: transform 0.3s;
    }
    .glass-card:hover {
        transform: translateY(-2px);
    }
    
    /* Section Title */
    .section-title {
        font-size: 1.3em;
        font-weight: 700;
        color: #2d3436;
        margin-bottom: 18px;
    }
    
    /* Upload Area - SATU AJA */
    .upload-area {
        border: 3px dashed #e91e63;
        border-radius: 20px;
        padding: 45px 25px;
        text-align: center;
        background: rgba(255,255,255,0.35);
        transition: all 0.4s ease;
        cursor: pointer;
    }
    .upload-area:hover {
        background: rgba(255,255,255,0.65);
        border-color: #9c27b0;
        transform: scale(1.01);
    }
    .upload-icon { font-size: 4em; display: block; margin-bottom: 8px; }
    .upload-text { font-size: 1.25em; font-weight: 700; color: #2d3436; }
    .upload-sub { color: #999; font-size: 0.9em; margin-top: 6px; }
    
    /* Tombol */
    .btn-classify {
        background: linear-gradient(135deg, #e91e63, #9c27b0) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.15em !important;
        padding: 15px 35px !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 8px 30px rgba(233, 30, 99, 0.35) !important;
        transition: all 0.3s !important;
        width: 100% !important;
        letter-spacing: 2px;
    }
    .btn-classify:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 40px rgba(233, 30, 99, 0.5) !important;
    }
    
    /* Hasil */
    .result-box {
        background: linear-gradient(135deg, #ffffff, #fce4ec);
        border-radius: 18px;
        padding: 20px 25px;
        border-left: 6px solid #e91e63;
        margin: 15px 0;
        animation: fadeIn 0.5s ease;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .result-name {
        font-size: 3em;
        font-weight: 900;
        color: #2d3436;
    }
    .result-accuracy {
        font-size: 2.4em;
        font-weight: 900;
        background: linear-gradient(135deg, #00b894, #00cec9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: right;
    }
    
    /* Deskripsi */
    .deskripsi-box {
        background: linear-gradient(135deg, #fdf2f8, #fce4ec);
        border-radius: 16px;
        padding: 18px 22px;
        border-left: 5px solid #e91e63;
        margin: 15px 0;
    }
    .deskripsi-title {
        font-weight: 700;
        color: #880e4f;
        margin-bottom: 8px;
    }
    .fakta-item {
        padding: 5px 0;
        font-size: 0.95em;
        color: #2d3436;
        border-bottom: 1px solid rgba(233,30,99,0.08);
    }
    .fakta-item:last-child { border-bottom: none; }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #e91e63, #9c27b0) !important;
        border-radius: 12px !important;
        height: 22px !important;
    }
    
    /* Status Model - Minimalis di card */
    .model-status {
        text-align: center;
        font-size: 0.9em;
        color: #00b894;
        font-weight: 600;
        padding: 2px 0;
    }
    
    /* Footer Ringkas */
    .footer {
        text-align: center;
        padding: 25px 0 10px 0;
        color: #aaa;
        font-size: 0.85em;
        border-top: 1px solid rgba(233,30,99,0.08);
        margin-top: 20px;
    }
    .footer .love { color: #e91e63; }
    
    /* Responsif */
    @media (max-width: 768px) {
        .header h1 { font-size: 2.5em; }
        .result-name { font-size: 2em; }
        .result-accuracy { font-size: 1.8em; }
        .glass-card { padding: 18px; }
        .upload-area { padding: 30px 15px; }
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
<div class="header">
    <h1>🌺 FLOWER WEBSITE</h1>
    <p class="sub">✨ Identifikasi 5 Jenis Bunga dengan AI</p>
    <div class="flowers-deco">🌸 🌷 🌻 🌺 🪷</div>
</div>
""", unsafe_allow_html=True)

# ============ DATABASE ============
BUNGA_DESKRIPSI = {
    'tulip': {
        'nama_latin': 'Tulipa',
        'fakta': [
            '🌷 Tulip berasal dari Asia Tengah, simbol nasional Belanda',
            '🌷 Lebih dari 3.000 varietas tulip terdaftar secara resmi',
            '🌷 Merah = cinta, kuning = kegembiraan, putih = maaf',
            '🌷 Abad ke-17: Belanda mengalami "Tulip Mania"'
        ]
    },
    'lily': {
        'nama_latin': 'Lilium',
        'fakta': [
            '🌸 Lily salah satu bunga tertua (3.000 tahun SM)',
            '🌸 Memiliki 6 kelopak, melambangkan kemurnian',
            '🌸 Dalam mitologi Yunani, bunga dewi Hera',
            '🌸 Beberapa spesies bisa tumbuh hingga 2,5 meter'
        ]
    },
    'orchid': {
        'nama_latin': 'Orchidaceae',
        'fakta': [
            '🌺 Lebih dari 28.000 spesies anggrek di dunia',
            '🌺 Ditemukan di semua benua kecuali Antartika',
            '🌺 Satu kapsul berisi hingga 3 juta biji',
            '🌺 Beberapa spesies bisa hidup hingga 100 tahun'
        ]
    },
    'sunflower': {
        'nama_latin': 'Helianthus annuus',
        'fakta': [
            '🌻 Bisa tumbuh hingga 3 meter lebih',
            '🌻 Bunga muda mengikuti pergerakan matahari',
            '🌻 Kepala bunga terdiri dari ribuan bunga kecil',
            '🌻 Bunga nasional Ukraina'
        ]
    },
    'lotus': {
        'nama_latin': 'Nelumbo nucifera',
        'fakta': [
            '🪷 Bisa bertahan 1.000 tahun dalam kondisi kering',
            '🪷 Bunga suci dalam agama Buddha dan Hindu',
            '🪷 Tumbuh di air berlumpur tapi tetap bersih',
            '🪷 Biji bisa berkecambah setelah 1.300 tahun'
        ]
    }
}

def get_fakta(nama):
    info = BUNGA_DESKRIPSI.get(nama.lower())
    return info['fakta'] if info else None

# ============ LOAD MODEL ============
@st.cache_resource
def load_model():
    model_path = 'model_bunga_densenet121.h5'
    file_id = "12ZJi1HbkI8ian7fWM0K98ADi1tpMvU4y"
    
    if os.path.exists(model_path):
        try:
            return tf.keras.models.load_model(model_path)
        except:
            os.remove(model_path)
    
    with st.spinner('⏳ Download model 30MB...'):
        try:
            url = f'https://drive.google.com/uc?export=download&id={file_id}'
            r = requests.get(url, stream=True)
            if 'confirm' in r.text:
                confirm = re.search(r'confirm=([^&]+)', r.text)
                if confirm:
                    url = f'https://drive.google.com/uc?export=download&confirm={confirm.group(1)}&id={file_id}'
                    r = requests.get(url, stream=True)
            with open(model_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return tf.keras.models.load_model(model_path)
        except:
            return None

class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']

model = load_model()
if model is None:
    st.error("❌ Gagal memuat model. Refresh halaman.")
    st.stop()

# ============ 2 KOLOM ============
col_kiri, col_kanan = st.columns([1, 1], gap="large")

with col_kiri:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📸 Upload Gambar</p>')
    
    # Status model di dalam card
    st.markdown('<p class="model-status">✅ Model siap digunakan</p>', unsafe_allow_html=True)
    
    # Upload - SATU AREA
    uploaded = st.file_uploader(
        "",
        type=['jpg', 'png', 'jpeg'],
        label_visibility="collapsed"
    )
    
    if not uploaded:
        st.markdown("""
        <div class="upload-area">
            <span class="upload-icon">🌸</span>
            <div class="upload-text">Klik atau seret gambar ke sini</div>
            <div class="upload-sub">Format: JPG, PNG, JPEG • Maks 200MB</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        img = Image.open(uploaded)
        st.image(img, caption="🖼️ Gambar yang diupload", use_column_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_kanan:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🔍 Hasil Klasifikasi</p>')
    
    if uploaded:
        if st.button("🌸 KLASIFIKASI SEKARANG", type="primary", use_container_width=True):
            with st.spinner("🧠 Menganalisis..."):
                img_resized = img.resize((224, 224))
                x = np.array(img_resized) / 255.0
                x = np.expand_dims(x, axis=0)
                
                pred = model.predict(x)
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                akurasi = pred[0][idx] * 100
                
                # Hasil
                st.markdown("---")
                col_nama, col_akurasi = st.columns([2, 1])
                with col_nama:
                    icon_map = {'tulip':'🌷','lily':'🌸','orchid':'🌺','sunflower':'🌻','lotus':'🪷'}
                    st.markdown(f'<p class="result-name">{icon_map.get(nama, "🌸")} {nama.upper()}</p>', unsafe_allow_html=True)
                with col_akurasi:
                    st.markdown(f'<p class="result-accuracy">{akurasi:.2f}%</p>', unsafe_allow_html=True)
                
                # Deskripsi
                fakta = get_fakta(nama)
                if fakta:
                    st.markdown('<div class="deskripsi-box">', unsafe_allow_html=True)
                    st.markdown(f'<p class="deskripsi-title">📖 Fakta Menarik</p>', unsafe_allow_html=True)
                    for item in fakta:
                        st.markdown(f'<p class="fakta-item">{item}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Probabilitas
                st.markdown("📊 **Probabilitas per Kelas**")
                for i, name in enumerate(class_names):
                    prob = pred[0][i] * 100
                    col_bar, col_pct = st.columns([4, 1])
                    with col_bar:
                        st.progress(int(prob) / 100)
                    with col_pct:
                        st.markdown(f'<span style="font-weight:700;">{prob:.1f}%</span>', unsafe_allow_html=True)
                    st.caption(name.upper())
    else:
        st.info("👆 Upload gambar terlebih dahulu")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============ FOOTER RINGKAS ============
st.markdown("""
<div class="footer">
    🌺 <b>FLOWER WEBSITE</b> • Dibuat dengan <span class="love">❤️</span> untuk UAS • Model DenseNet121
    <br>
    🌷 Tulip &nbsp;·&nbsp; 🌸 Lily &nbsp;·&nbsp; 🌺 Orchid &nbsp;·&nbsp; 🌻 Sunflower &nbsp;·&nbsp; 🪷 Lotus
</div>
""", unsafe_allow_html=True)
