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

# ============ CSS CUSTOM - ESTETIK BANGET ============
st.markdown("""
<style>
    /* RESET */
    .main > div { padding-top: 0; }
    .stApp { background: #faf0f5; }
    
    /* HAPUS UPLOAD DEFAULT */
    .stFileUploader > div > div > div > div {
        display: none !important;
    }
    .stFileUploader > div > div {
        padding: 0 !important;
    }
    .stFileUploader > div > div > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    .stFileUploader label {
        display: none !important;
    }
    
    /* HEADER - ELEGAN */
    .header {
        text-align: center;
        padding: 30px 0 10px 0;
    }
    .header .logo {
        font-size: 3.8em;
        font-weight: 900;
        letter-spacing: 6px;
        background: linear-gradient(135deg, #e91e63, #f06292, #ba68c8, #7e57c2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
        margin: 0;
        line-height: 1.2;
    }
    .header .sub {
        font-size: 1em;
        color: #7a4a6e;
        letter-spacing: 8px;
        font-weight: 400;
        margin-top: 0;
        opacity: 0.7;
    }
    .header .divider {
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, #e91e63, #ba68c8);
        margin: 15px auto 5px auto;
        border-radius: 10px;
    }
    
    /* CARD - GLASS ELEGAN */
    .glass {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 30px 32px;
        border: 1px solid rgba(255, 255, 255, 0.7);
        box-shadow: 0 15px 50px rgba(233, 30, 99, 0.08);
        transition: all 0.4s ease;
    }
    .glass:hover {
        box-shadow: 0 20px 60px rgba(233, 30, 99, 0.12);
        transform: translateY(-2px);
    }
    
    /* TITLE CARD */
    .card-title {
        font-size: 1.1em;
        font-weight: 700;
        color: #4a2a40;
        letter-spacing: 1px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .card-title span {
        font-size: 1.3em;
    }
    
    /* UPLOAD AREA - SATU, BERSIH, ESTETIK */
    .upload-area {
        border: 2px dashed #e8d5e0;
        border-radius: 24px;
        padding: 50px 20px;
        text-align: center;
        background: rgba(255, 255, 255, 0.3);
        transition: all 0.4s ease;
        cursor: pointer;
        position: relative;
    }
    .upload-area:hover {
        border-color: #e91e63;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(1.01);
    }
    .upload-area .icon {
        font-size: 4em;
        display: block;
        margin-bottom: 10px;
        opacity: 0.8;
    }
    .upload-area .main-text {
        font-size: 1.2em;
        font-weight: 600;
        color: #3d2a35;
    }
    .upload-area .sub-text {
        font-size: 0.85em;
        color: #aa8a9a;
        margin-top: 6px;
    }
    
    /* STATUS MODEL - MINIMALIS */
    .status {
        text-align: center;
        font-size: 0.85em;
        color: #66bb6a;
        font-weight: 500;
        padding: 6px 0 0 0;
        letter-spacing: 1px;
    }
    
    /* TOMBOL */
    .btn-pink {
        background: linear-gradient(135deg, #e91e63, #9c27b0) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1em !important;
        padding: 14px 30px !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 8px 30px rgba(233, 30, 99, 0.3) !important;
        transition: all 0.3s !important;
        width: 100% !important;
        letter-spacing: 2px;
    }
    .btn-pink:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 40px rgba(233, 30, 99, 0.45) !important;
    }
    
    /* HASIL */
    .result {
        background: linear-gradient(135deg, #fff5f8, #fce4ec);
        border-radius: 20px;
        padding: 22px 26px;
        border-left: 5px solid #e91e63;
        margin: 15px 0;
        animation: fadeUp 0.5s ease;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .result .name {
        font-size: 2.6em;
        font-weight: 900;
        color: #2d1b26;
    }
    .result .acc {
        font-size: 2.2em;
        font-weight: 900;
        color: #00b894;
        text-align: right;
    }
    
    /* DESKRIPSI */
    .desc-box {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 16px;
        padding: 18px 22px;
        border-left: 4px solid #ba68c8;
        margin: 15px 0;
    }
    .desc-box .title {
        font-weight: 700;
        color: #6a1b4d;
        margin-bottom: 6px;
        font-size: 0.95em;
    }
    .desc-box .item {
        padding: 4px 0;
        font-size: 0.92em;
        color: #3d2a35;
        border-bottom: 1px solid rgba(0,0,0,0.04);
    }
    .desc-box .item:last-child { border-bottom: none; }
    
    /* PROGRESS */
    .stProgress > div > div {
        background: linear-gradient(90deg, #e91e63, #ba68c8) !important;
        border-radius: 20px !important;
        height: 20px !important;
    }
    
    /* FOOTER - RINGKAS & ESTETIK */
    .footer {
        text-align: center;
        padding: 25px 0 15px 0;
        color: #bba0ae;
        font-size: 0.8em;
        letter-spacing: 2px;
        border-top: 1px solid rgba(233,30,99,0.06);
        margin-top: 20px;
    }
    .footer .love { color: #e91e63; }
    .footer .flowers { font-size: 1.4em; letter-spacing: 8px; opacity: 0.5; }
    
    /* INFO UPLOAD */
    .info-upload {
        font-size: 0.85em;
        color: #aa8a9a;
        padding: 8px 0 0 0;
        text-align: center;
    }
    
    /* RESPONSIF */
    @media (max-width: 768px) {
        .header .logo { font-size: 2.4em; letter-spacing: 3px; }
        .result .name { font-size: 1.8em; }
        .result .acc { font-size: 1.6em; }
        .glass { padding: 20px; }
        .upload-area { padding: 30px 15px; }
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
<div class="header">
    <div class="logo">FLOWER WEBSITE</div>
    <div class="sub">identifikasi 5 jenis bunga</div>
    <div class="divider"></div>
</div>
""", unsafe_allow_html=True)

# ============ DATABASE ============
BUNGA_DESKRIPSI = {
    'tulip': {
        'nama_latin': 'Tulipa',
        'fakta': [
            '🌷 Simbol nasional Belanda, berasal dari Asia Tengah',
            '🌷 3.000+ varietas terdaftar secara resmi',
            '🌷 Merah = cinta, kuning = kegembiraan, putih = maaf',
            '🌷 Abad ke-17: fenomena "Tulip Mania" di Belanda'
        ]
    },
    'lily': {
        'nama_latin': 'Lilium',
        'fakta': [
            '🌸 Salah satu bunga tertua (3.000 tahun SM)',
            '🌸 6 kelopak, melambangkan kemurnian',
            '🌸 Bunga dewi Hera dalam mitologi Yunani',
            '🌸 Beberapa spesies tumbuh hingga 2,5 meter'
        ]
    },
    'orchid': {
        'nama_latin': 'Orchidaceae',
        'fakta': [
            '🌺 28.000+ spesies di seluruh dunia',
            '🌺 Ditemukan di semua benua kecuali Antartika',
            '🌺 Satu kapsul berisi hingga 3 juta biji',
            '🌺 Beberapa spesies hidup hingga 100 tahun'
        ]
    },
    'sunflower': {
        'nama_latin': 'Helianthus annuus',
        'fakta': [
            '🌻 Bisa tumbuh hingga 3 meter lebih',
            '🌻 Bunga muda mengikuti pergerakan matahari',
            '🌻 Kepala bunga = ribuan bunga kecil',
            '🌻 Bunga nasional Ukraina'
        ]
    },
    'lotus': {
        'nama_latin': 'Nelumbo nucifera',
        'fakta': [
            '🪷 Bertahan 1.000 tahun dalam kondisi kering',
            '🪷 Bunga suci dalam agama Buddha & Hindu',
            '🪷 Tumbuh di lumpur tapi tetap bersih',
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
    
    with st.spinner('⏳ Mengunduh model...'):
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
    st.error("❌ Gagal memuat model.")
    st.stop()

# ============ 2 KOLOM ============
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><span>📸</span> Upload Gambar</div>')
    
    # Status model - minimalis
    st.markdown('<div class="status">✓ Model siap digunakan</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    
    # UPLOAD - SATU AREA, BERSIH
    uploaded = st.file_uploader(
        "",
        type=['jpg', 'png', 'jpeg'],
        label_visibility="collapsed"
    )
    
    if not uploaded:
        st.markdown("""
        <div class="upload-area">
            <span class="icon">🌸</span>
            <div class="main-text">Klik atau seret gambar</div>
            <div class="sub-text">JPG, PNG, JPEG • Maks 200MB</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        img = Image.open(uploaded)
        st.image(img, caption="📷 Gambar yang diupload", use_column_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="card-title"><span>🔍</span> Hasil Klasifikasi</div>')
    
    if uploaded:
        if st.button("🌸 KLASIFIKASI", type="primary", use_container_width=True):
            with st.spinner("Menganalisis..."):
                img_resized = img.resize((224, 224))
                x = np.array(img_resized) / 255.0
                x = np.expand_dims(x, axis=0)
                
                pred = model.predict(x)
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                akurasi = pred[0][idx] * 100
                
                # HASIL
                st.markdown('<div class="result">', unsafe_allow_html=True)
                col_n, col_a = st.columns([2, 1])
                icon_map = {'tulip':'🌷','lily':'🌸','orchid':'🌺','sunflower':'🌻','lotus':'🪷'}
                with col_n:
                    st.markdown(f'<div class="name">{icon_map.get(nama, "🌸")} {nama.upper()}</div>', unsafe_allow_html=True)
                with col_a:
                    st.markdown(f'<div class="acc">{akurasi:.2f}%</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # DESKRIPSI
                fakta = get_fakta(nama)
                if fakta:
                    st.markdown('<div class="desc-box">', unsafe_allow_html=True)
                    st.markdown('<div class="title">📖 Fakta Menarik</div>', unsafe_allow_html=True)
                    for item in fakta:
                        st.markdown(f'<div class="item">{item}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # PROBABILITAS
                st.markdown("📊 **Probabilitas**")
                for i, name in enumerate(class_names):
                    prob = pred[0][i] * 100
                    cb, cp = st.columns([4, 1])
                    with cb:
                        st.progress(int(prob) / 100)
                    with cp:
                        st.markdown(f'<span style="font-weight:600;">{prob:.1f}%</span>', unsafe_allow_html=True)
                    st.caption(name.upper())
    else:
        st.markdown('<div style="padding:30px 0;text-align:center;color:#bba0ae;">🌸 Upload gambar<br>untuk memulai</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("""
<div class="footer">
    <div class="flowers">🌸 🌷 🌻 🌺 🪷</div>
    FLOWER WEBSITE • Dibuat dengan <span class="love">♥</span> untuk UAS
    <br>
    Model DenseNet121 • TensorFlow • Streamlit
</div>
""", unsafe_allow_html=True)
