import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

# ============ KONFIGURASI HALAMAN ============
st.set_page_config(
    page_title="🌸 FlowerAI - Klasifikasi Bunga",
    page_icon="🌸",
    layout="wide"
)

# ============ CSS CUSTOM ============
st.markdown("""
<style>
    /* Hapus padding default */
    .main > div {
        padding-top: 0;
    }
    
    /* Background pink soft gradien */
    .stApp {
        background: linear-gradient(160deg, #fce4ec 0%, #f8e8f5 30%, #f3e5f5 60%, #e8eaf6 100%);
    }
    
    /* Header utama */
    .header {
        text-align: center;
        padding: 30px 0 10px 0;
    }
    .header h1 {
        font-size: 3.8em;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(135deg, #e91e63, #9c27b0, #3f51b5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .header p {
        font-size: 1.2em;
        color: #6a1b4d;
        margin-top: 5px;
        font-weight: 500;
        opacity: 0.85;
    }
    
    /* Card utama dengan efek glass */
    .glass-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 30px 35px;
        box-shadow: 
            0 10px 40px rgba(233, 30, 99, 0.15),
            0 2px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.6);
        transition: transform 0.3s ease;
        margin: 10px 0;
    }
    .glass-card:hover {
        transform: translateY(-3px);
    }
    
    /* Upload area - lebih menarik */
    .upload-area {
        border: 3px dashed #e91e63;
        border-radius: 20px;
        padding: 50px 30px;
        text-align: center;
        background: rgba(255, 255, 255, 0.5);
        transition: all 0.4s ease;
        cursor: pointer;
    }
    .upload-area:hover {
        background: rgba(255, 255, 255, 0.8);
        border-color: #9c27b0;
        transform: scale(1.01);
        box-shadow: 0 8px 30px rgba(233, 30, 99, 0.15);
    }
    .upload-icon {
        font-size: 4em;
        margin-bottom: 10px;
    }
    .upload-text {
        font-size: 1.3em;
        font-weight: 600;
        color: #2d3436;
    }
    .upload-sub {
        color: #888;
        font-size: 0.95em;
        margin-top: 8px;
    }
    
    /* Tombol klasifikasi */
    .btn-classify {
        background: linear-gradient(135deg, #e91e63, #9c27b0) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.2em !important;
        padding: 14px 40px !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(233, 30, 99, 0.35) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        letter-spacing: 0.5px;
    }
    .btn-classify:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(233, 30, 99, 0.5) !important;
    }
    
    /* Hasil */
    .result-box {
        background: linear-gradient(135deg, #ffffff, #f8f0ff);
        border-radius: 20px;
        padding: 25px 30px;
        border-left: 6px solid #e91e63;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin: 15px 0;
    }
    .result-name {
        font-size: 3em;
        font-weight: 900;
        color: #2d3436;
        padding: 10px 0;
    }
    .result-accuracy {
        font-size: 2.5em;
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
        padding: 20px 25px;
        border-left: 5px solid #e91e63;
        margin: 15px 0;
    }
    .deskripsi-title {
        font-size: 1.1em;
        font-weight: 700;
        color: #880e4f;
        margin-bottom: 10px;
    }
    .fakta-item {
        padding: 7px 0;
        font-size: 1em;
        color: #2d3436;
        border-bottom: 1px solid rgba(233, 30, 99, 0.1);
    }
    .fakta-item:last-child {
        border-bottom: none;
    }
    .fakta-item .emoji {
        margin-right: 10px;
    }
    
    /* Progress bar custom */
    .stProgress > div > div {
        background: linear-gradient(90deg, #e91e63, #9c27b0, #3f51b5) !important;
        border-radius: 12px !important;
        height: 22px !important;
    }
    .prob-label {
        display: flex;
        justify-content: space-between;
        font-weight: 600;
        color: #2d3436;
        padding: 2px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px 0 10px 0;
        color: #888;
        font-size: 0.85em;
        opacity: 0.7;
    }
    .footer span {
        margin: 0 10px;
    }
    
    /* Status model - minimalis */
    .model-status {
        text-align: center;
        padding: 5px 0;
        font-size: 0.9em;
        color: #00b894;
        font-weight: 500;
    }
    
    /* Responsif */
    @media (max-width: 768px) {
        .header h1 { font-size: 2.2em; }
        .result-name { font-size: 2em; }
        .result-accuracy { font-size: 1.8em; }
        .glass-card { padding: 20px; }
        .upload-area { padding: 30px 15px; }
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
<div class="header">
    <h1>🌸 FlowerAI</h1>
    <p>✨ Identifikasi 5 Jenis Bunga dengan Kecerdasan Buatan</p>
</div>
""", unsafe_allow_html=True)

# ============ DATABASE DESKRIPSI ============
BUNGA_DESKRIPSI = {
    'tulip': {
        'nama_latin': 'Tulipa',
        'fakta': [
            '🌷 Tulip berasal dari Asia Tengah dan menjadi simbol nasional Belanda',
            '🌷 Ada lebih dari 3.000 varietas tulip yang terdaftar secara resmi',
            '🌷 Warna tulip: merah = cinta, kuning = kegembiraan, putih = maaf',
            '🌷 Pada abad ke-17, Belanda mengalami fenomena "Tulip Mania"'
        ]
    },
    'lily': {
        'nama_latin': 'Lilium',
        'fakta': [
            '🌸 Lily adalah salah satu bunga tertua (3.000 tahun SM)',
            '🌸 Bunga lily memiliki 6 kelopak dan melambangkan kemurnian',
            '🌸 Dalam mitologi Yunani, lily adalah bunga dewi Hera',
            '🌸 Beberapa spesies lily dapat tumbuh hingga 2,5 meter'
        ]
    },
    'orchid': {
        'nama_latin': 'Orchidaceae',
        'fakta': [
            '🌺 Anggrek memiliki lebih dari 28.000 spesies di dunia',
            '🌺 Anggrek ditemukan di semua benua kecuali Antartika',
            '🌺 Satu kapsul anggrek berisi hingga 3 juta biji',
            '🌺 Beberapa spesies anggrek bisa hidup hingga 100 tahun'
        ]
    },
    'sunflower': {
        'nama_latin': 'Helianthus annuus',
        'fakta': [
            '🌻 Bunga matahari bisa tumbuh hingga 3 meter lebih',
            '🌻 Bunga muda mengikuti pergerakan matahari (heliotropisme)',
            '🌻 Kepala bunga terdiri dari ribuan bunga kecil',
            '🌻 Bunga matahari adalah bunga nasional Ukraina'
        ]
    },
    'lotus': {
        'nama_latin': 'Nelumbo nucifera',
        'fakta': [
            '🪷 Teratai bisa bertahan 1.000 tahun dalam kondisi kering',
            '🪷 Bunga teratai suci dalam agama Buddha dan Hindu',
            '🪷 Meskipun tumbuh di air berlumpur, teratai tetap bersih',
            '🪷 Biji teratai bisa berkecambah setelah 1.300 tahun'
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
    
    with st.spinner('⏳ Mengunduh model (30MB)...'):
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

# Status model minimal
model = load_model()
if model is None:
    st.error("❌ Gagal memuat model. Silakan refresh.")
    st.stop()
st.markdown('<p class="model-status">✅ Model siap digunakan</p>', unsafe_allow_html=True)

# ============ 2 KOLOM UTAMA ============
col_kiri, col_kanan = st.columns([1, 1], gap="large")

with col_kiri:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🌸 Upload Gambar Bunga")
    
    # Upload area yang menarik
    uploaded = st.file_uploader(
        "",
        type=['jpg', 'png', 'jpeg'],
        label_visibility="collapsed",
        accept_multiple_files=False
    )
    
    # Tampilkan custom upload area jika belum upload
    if not uploaded:
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">📸</div>
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
    st.markdown("### 🔍 Hasil Klasifikasi")
    st.markdown('<p style="color:#888;font-size:0.95em;">Upload gambar lalu klik tombol di bawah</p>', unsafe_allow_html=True)
    
    if uploaded:
        if st.button("🚀 Klasifikasi Sekarang", type="primary", use_container_width=True):
            with st.spinner("🧠 Menganalisis gambar..."):
                img_resized = img.resize((224, 224))
                x = np.array(img_resized) / 255.0
                x = np.expand_dims(x, axis=0)
                
                pred = model.predict(x)
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                akurasi = pred[0][idx] * 100
                
                # === HASIL ===
                st.markdown("---")
                col_nama, col_akurasi = st.columns([2, 1])
                with col_nama:
                    st.markdown(f'<p class="result-name">🌸 {nama.upper()}</p>', unsafe_allow_html=True)
                with col_akurasi:
                    st.markdown(f'<p class="result-accuracy">{akurasi:.2f}%</p>', unsafe_allow_html=True)
                
                # === DESKRIPSI ===
                fakta = get_fakta(nama)
                if fakta:
                    st.markdown('<div class="deskripsi-box">', unsafe_allow_html=True)
                    st.markdown(f'<p class="deskripsi-title">📖 Fakta Menarik</p>', unsafe_allow_html=True)
                    for item in fakta:
                        st.markdown(f'<p class="fakta-item">{item}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # === PROBABILITAS ===
                st.markdown("### 📊 Probabilitas")
                for i, name in enumerate(class_names):
                    prob = pred[0][i] * 100
                    col_bar, col_pct = st.columns([4, 1])
                    with col_bar:
                        st.progress(int(prob) / 100)
                    with col_pct:
                        st.markdown(f'<span style="font-weight:700;color:#2d3436;">{prob:.1f}%</span>', unsafe_allow_html=True)
                    st.caption(name.upper())
    else:
        st.info("👆 Silakan upload gambar terlebih dahulu")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("""
<div class="footer">
    🌸 <b>FlowerAI</b> • Dibuat dengan ❤️ menggunakan TensorFlow & Streamlit • Model DenseNet121
    <br>
    <span>🌷 Tulip</span> <span>🌸 Lily</span> <span>🌺 Orchid</span> <span>🌻 Sunflower</span> <span>🪷 Lotus</span>
</div>
""", unsafe_allow_html=True)
