import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

# ============ KONFIGURASI HALAMAN ============
st.set_page_config(
    page_title="Klasifikasi Bunga 🌸", 
    page_icon="🌸",
    layout="wide"
)

# ============ CSS CUSTOM ============
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #fce4ec 0%, #f3e5f5 50%, #e8f5e9 100%);
    }
    
    /* Card */
    .card {
        background: rgba(255,255,255,0.92);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.10);
        border: 1px solid rgba(255,255,255,0.3);
        margin: 15px 0;
    }
    
    /* Judul */
    .title {
        text-align: center;
        font-size: 3em;
        font-weight: 800;
        color: #2d3436;
        margin-bottom: 5px;
    }
    .title-highlight {
        background: linear-gradient(45deg, #e74c3c, #f39c12, #2ecc71, #3498db, #9b59b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.1em;
        margin-bottom: 25px;
    }
    
    /* Hasil */
    .result-name {
        font-size: 2.8em;
        font-weight: 800;
        color: #2d3436;
        padding: 10px 0;
    }
    .result-accuracy {
        font-size: 2.5em;
        font-weight: 800;
        color: #00b894;
        text-align: right;
    }
    
    /* Deskripsi */
    .deskripsi-box {
        background: linear-gradient(135deg, #dfe6e9, #f5f6fa);
        border-radius: 15px;
        padding: 20px 25px;
        border-left: 6px solid #6c5ce7;
        margin: 15px 0;
    }
    .deskripsi-title {
        font-size: 1.2em;
        font-weight: 700;
        color: #2d3436;
        margin-bottom: 10px;
    }
    .fakta-item {
        padding: 6px 0;
        font-size: 1em;
        color: #2d3436;
        border-bottom: 1px solid #e0e0e0;
    }
    .fakta-item:last-child {
        border-bottom: none;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #999;
        margin-top: 40px;
        padding: 20px;
        font-size: 0.85em;
    }
    
    /* Upload area */
    .upload-area {
        border: 2px dashed #bdc3c7;
        border-radius: 15px;
        padding: 40px 20px;
        text-align: center;
        background: rgba(255,255,255,0.5);
    }
    
    /* Tombol */
    .stButton > button {
        background: linear-gradient(135deg, #6c5ce7, #a29bfe) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1em !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        border: none !important;
        transition: all 0.3s !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        border-radius: 10px !important;
        height: 20px !important;
    }
    .progress-label {
        font-size: 0.9em;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown('<h1 class="title">🌸 <span class="title-highlight">Klasifikasi Jenis Bunga</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">📸 Upload gambar bunga dan dapatkan hasil instan dengan kecerdasan buatan!</p>', unsafe_allow_html=True)

# ============ DATABASE DESKRIPSI BUNGA ============
BUNGA_DESKRIPSI = {
    'tulip': {
        'nama_latin': 'Tulipa',
        'fakta': [
            '🌷 Tulip berasal dari Asia Tengah dan menjadi simbol nasional Belanda',
            '🌷 Ada lebih dari 3.000 varietas tulip yang terdaftar secara resmi',
            '🌷 Warna tulip: merah = cinta, kuning = kegembiraan, putih = maaf',
            '🌷 Pada abad ke-17, Belanda mengalami "Tulip Mania"'
        ]
    },
    'lily': {
        'nama_latin': 'Lilium',
        'fakta': [
            '🌸 Lily adalah salah satu bunga tertua (3.000 tahun SM)',
            '🌸 Bunga lily memiliki 6 kelopak dan melambangkan kemurnian',
            '🌸 Di Yunani kuno, lily adalah bunga dewi Hera',
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

def get_fakta_bunga(nama_bunga):
    info = BUNGA_DESKRIPSI.get(nama_bunga.lower())
    return info['fakta'] if info else None

# ============ LOAD MODEL ============
@st.cache_resource
def load_model():
    model_path = 'model_bunga_densenet121.h5'
    file_id = "12ZJi1HbkI8ian7fWM0K98ADi1tpMvU4y"
    
    # Cek di local dulu
    if os.path.exists(model_path):
        try:
            return tf.keras.models.load_model(model_path)
        except:
            os.remove(model_path)
    
    # Download dari Drive
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
        except Exception as e:
            st.error(f"Gagal download model: {e}")
            return None

class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']

# Load model
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        model = load_model()
        if model is None:
            st.error("❌ Gagal memuat model. Silakan coba lagi.")
            st.stop()
        st.success("✅ Model berhasil dimuat!")

st.markdown("---")

# ============ UPLOAD & PREDIKSI ============
col_kiri, col_kanan = st.columns([1, 1], gap="large")

with col_kiri:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Gambar")
    
    uploaded = st.file_uploader(
        "Pilih gambar bunga",
        type=['jpg', 'png', 'jpeg'],
        help="Format yang didukung: JPG, PNG, JPEG"
    )
    
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="🖼️ Gambar yang diupload", use_column_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_kanan:
    if uploaded:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Klasifikasi")
        
        if st.button("🚀 Klasifikasi Sekarang", type="primary", use_container_width=True):
            with st.spinner("🧠 Menganalisis gambar..."):
                # Preprocess
                img_resized = img.resize((224, 224))
                x = np.array(img_resized) / 255.0
                x = np.expand_dims(x, axis=0)
                
                # Prediksi
                pred = model.predict(x)
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                akurasi = pred[0][idx] * 100
                
                # === TAMPILAN HASIL ===
                st.markdown("---")
                st.markdown("### ✅ Hasil Klasifikasi")
                
                # Nama & Akurasi
                col_nama, col_akurasi = st.columns([2, 1])
                with col_nama:
                    st.markdown(f'<p class="result-name">🌺 {nama.upper()}</p>', unsafe_allow_html=True)
                with col_akurasi:
                    st.markdown(f'<p class="result-accuracy">{akurasi:.2f}%</p>', unsafe_allow_html=True)
                
                # === DESKRIPSI ===
                fakta = get_fakta_bunga(nama)
                if fakta:
                    st.markdown('<div class="deskripsi-box">', unsafe_allow_html=True)
                    st.markdown(f'<p class="deskripsi-title">📖 Fakta Menarik tentang {nama.upper()}</p>', unsafe_allow_html=True)
                    for item in fakta:
                        st.markdown(f'<p class="fakta-item">{item}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # === PROBABILITAS ===
                st.markdown("### 📊 Probabilitas per Kelas")
                for i, name in enumerate(class_names):
                    prob = pred[0][i] * 100
                    
                    col_bar, col_pct = st.columns([4, 1])
                    with col_bar:
                        st.progress(int(prob) / 100)
                    with col_pct:
                        st.markdown(f'<span style="font-weight:600;color:#2d3436;">{prob:.1f}%</span>', unsafe_allow_html=True)
                    st.markdown(f'<span style="font-size:0.85em;color:#666;">{name.upper()}</span>', unsafe_allow_html=True)
                    st.markdown("")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🌸 Dibuat dengan ❤️ menggunakan TensorFlow & Streamlit • Model DenseNet121</p>
    <p>Klasifikasi 5 jenis bunga: Tulip, Lily, Orchid, Sunflower, Lotus</p>
</div>
""", unsafe_allow_html=True)
