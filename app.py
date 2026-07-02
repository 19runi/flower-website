import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re
import tempfile

st.set_page_config(
    page_title="Klasifikasi Bunga",
    page_icon="🌸",
    layout="centered"
)

# CSS dengan font yang lebih indah
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,700&family=Quicksand:wght@300;400;500;600;700&family=Dancing+Script:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #ffe4e1 0%, #ffd1dc 50%, #ffb6c1 100%);
    }
    
    /* HIDE SIDEBAR */
    .css-1d391kg, .css-1lcbmhc, .stSidebar {
        display: none !important;
    }
    
    /* PERBAIKAN: Styling untuk uploader tanpa menyembunyikan elemen */
    .stFileUploader {
        margin: 0 !important;
    }
    
    .stFileUploader > div {
        display: block !important;
    }
    
    .stFileUploader > div > div {
        display: block !important;
        position: relative !important;
    }
    
    .stFileUploader > div > div > div {
        display: block !important;
    }
    
    .stFileUploader > div > button {
        display: inline-block !important;
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #e88a9e, #d4708a) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.7rem 2rem !important;
        font-size: 1rem !important;
        margin: 0.5rem 0 !important;
    }
    
    .stFileUploader > div > button:hover {
        transform: scale(1.05) !important;
    }
    
    /* HEADER YANG DIPERBAIKI - Lebih indah */
    .header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, rgba(255,255,255,0.85), rgba(255,240,245,0.85));
        border-radius: 30px;
        margin-bottom: 2rem;
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px rgba(255, 182, 193, 0.25);
        border: 2px solid rgba(255, 255, 255, 0.5);
        position: relative;
        overflow: hidden;
    }
    
    /* Efek dekoratif header */
    .header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(232,138,158,0.1), transparent 60%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .header-content {
        position: relative;
        z-index: 1;
    }
    
    .header .icon-deco {
        font-size: 3.5rem;
        display: block;
        margin-bottom: 0.3rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .header h1 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 900 !important;
        font-size: 3.8rem !important;
        margin: 0.2rem 0 !important;
        background: linear-gradient(135deg, #4a1942, #8b3a6a, #c05d78, #8b3a6a);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4s ease-in-out infinite;
        letter-spacing: 4px;
        text-shadow: none;
        position: relative;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .header .subtitle {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        color: #6b3a5a !important;
        margin: 0.5rem 0 0 0 !important;
        letter-spacing: 3px;
        opacity: 0.8;
        position: relative;
        display: inline-block;
        padding: 0 1rem;
    }
    
    .header .subtitle::before,
    .header .subtitle::after {
        content: '🌸';
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1rem;
        opacity: 0.5;
    }
    
    .header .subtitle::before {
        left: -1.5rem;
    }
    
    .header .subtitle::after {
        right: -1.5rem;
    }
    
    .header .deco-line {
        width: 100px;
        height: 3px;
        margin: 0.8rem auto 0;
        background: linear-gradient(90deg, transparent, #e88a9e, #d4708a, #e88a9e, transparent);
        border-radius: 5px;
    }
    
    /* UPLOAD AREA */
    .upload-area {
        background: rgba(255, 255, 255, 0.9);
        padding: 3rem 2rem;
        border-radius: 25px;
        border: 3px dashed #e88a9e;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(255, 182, 193, 0.25);
        transition: all 0.3s ease;
        margin-bottom: 0rem;
    }
    
    .upload-area:hover {
        background: rgba(255, 255, 255, 0.95);
        border-color: #d4708a;
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(255, 182, 193, 0.35);
    }
    
    .upload-area .main-text {
        font-family: 'Quicksand', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #4a1942;
        margin: 0;
    }
    
    .upload-area .sub-text {
        font-family: 'Quicksand', sans-serif;
        font-size: 1rem;
        color: #6b3a5a;
        margin: 0.5rem 0;
        font-weight: 400;
        opacity: 0.8;
    }
    
    .upload-area .info-text {
        font-family: 'Quicksand', sans-serif;
        font-size: 0.9rem;
        color: #8b5a7a;
        margin-top: 0.5rem;
        font-weight: 400;
        opacity: 0.7;
    }
    
    .stButton > button {
        width: 100%;
        font-family: 'Quicksand', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        background: linear-gradient(135deg, #e88a9e, #d4708a);
        color: white;
        padding: 0.8rem;
        border: none;
        border-radius: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(232, 138, 158, 0.3);
        margin-top: 1rem;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(232, 138, 158, 0.5);
        background: linear-gradient(135deg, #d4708a, #c05d78);
    }
    
    .image-preview {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(255, 182, 193, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.6);
        margin: 1.5rem 0;
    }
    
    .result-box {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,240,245,0.95));
        padding: 2.5rem 2rem;
        border-radius: 30px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(255, 182, 193, 0.4);
        margin: 1.5rem 0;
        border: 2px solid rgba(255, 255, 255, 0.6);
        animation: fadeInUp 0.6s ease;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    .result-box .label {
        font-family: 'Quicksand', sans-serif;
        color: #8b5a7a;
        font-size: 0.9rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 4px;
        text-transform: uppercase;
        opacity: 0.7;
    }
    
    .result-box .name {
        font-family: 'Playfair Display', serif;
        font-size: 4.5rem;
        font-weight: 900;
        margin: 0.3rem 0;
        background: linear-gradient(135deg, #4a1942, #8b3a6a, #4a1942);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s linear infinite;
        letter-spacing: 3px;
    }
    
    .result-box .accuracy-wrapper {
        display: inline-block;
        background: linear-gradient(135deg, #e88a9e, #d4708a);
        padding: 0.5rem 2.5rem;
        border-radius: 50px;
        box-shadow: 0 4px 20px rgba(232, 138, 158, 0.4);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .result-box .accuracy {
        font-family: 'Quicksand', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        letter-spacing: 2px;
        margin: 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,248,250,0.95));
        padding: 1.8rem;
        border-radius: 25px;
        box-shadow: 0 8px 32px rgba(255, 182, 193, 0.25);
        margin: 1.2rem 0;
        border: 2px solid rgba(255, 255, 255, 0.6);
    }
    
    .info-card .title-wrapper {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.5rem;
    }
    
    .info-card .title {
        font-family: 'Playfair Display', serif;
        color: #4a1942;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
    }
    
    .info-card .latin-wrapper {
        display: inline-block;
        background: linear-gradient(135deg, rgba(232,138,158,0.15), rgba(212,112,138,0.15));
        padding: 0.3rem 1.2rem;
        border-radius: 50px;
        margin: 0.5rem 0 1rem 0;
        border: 1px solid rgba(232,138,158,0.2);
    }
    
    .info-card .latin {
        font-family: 'Quicksand', sans-serif;
        color: #6b3a5a;
        font-style: italic;
        font-size: 1rem;
        margin: 0;
        font-weight: 600;
    }
    
    .fact {
        padding: 0.8rem 0;
        border-bottom: 1px solid rgba(255, 182, 193, 0.2);
        display: flex;
        align-items: center;
        gap: 14px;
        font-family: 'Quicksand', sans-serif;
        color: #4a1942;
        font-size: 0.95rem;
        font-weight: 500;
        transition: all 0.3s ease;
        padding-left: 0.5rem;
        border-radius: 10px;
    }
    
    .fact:hover {
        background: rgba(232, 138, 158, 0.05);
        padding-left: 1rem;
    }
    
    .fact:last-child {
        border-bottom: none;
    }
    
    .fact-icon {
        font-size: 1.4rem;
        min-width: 35px;
    }
    
    .fact-number {
        display: inline-block;
        background: linear-gradient(135deg, #e88a9e, #d4708a);
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        text-align: center;
        font-size: 0.7rem;
        font-weight: 700;
        line-height: 24px;
        margin-right: 5px;
    }
    
    .prob-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,248,250,0.95));
        padding: 1.8rem;
        border-radius: 25px;
        box-shadow: 0 8px 32px rgba(255, 182, 193, 0.25);
        margin: 1.2rem 0;
        border: 2px solid rgba(255, 255, 255, 0.6);
    }
    
    .prob-card .title-wrapper {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.2rem;
    }
    
    .prob-card .title {
        font-family: 'Playfair Display', serif;
        color: #4a1942;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
    }
    
    .prob-item {
        margin: 0.9rem 0;
        padding: 0.5rem 0.8rem;
        border-radius: 15px;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.3);
    }
    
    .prob-item:hover {
        background: rgba(255, 255, 255, 0.6);
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(255, 182, 193, 0.1);
    }
    
    .prob-item .label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Quicksand', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #4a1942;
        margin-bottom: 0.3rem;
    }
    
    .prob-item .label .name {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .prob-item .label .percentage {
        font-size: 1.1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #e88a9e, #d4708a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .prob-item .bar {
        background: rgba(255, 182, 193, 0.2);
        border-radius: 12px;
        height: 12px;
        overflow: hidden;
    }
    
    .prob-item .bar .fill {
        height: 100%;
        border-radius: 12px;
        transition: width 1.2s ease;
    }
    
    .prob-item:nth-child(1) .fill { background: linear-gradient(90deg, #e88a9e, #d4708a); }
    .prob-item:nth-child(2) .fill { background: linear-gradient(90deg, #f7a1b5, #e88a9e); }
    .prob-item:nth-child(3) .fill { background: linear-gradient(90deg, #d4a0c5, #b880a8); }
    .prob-item:nth-child(4) .fill { background: linear-gradient(90deg, #f5c542, #f0b830); }
    .prob-item:nth-child(5) .fill { background: linear-gradient(90deg, #9bc4d4, #7ab0c4); }
    
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        font-family: 'Quicksand', sans-serif;
        color: #6b3a5a;
        font-size: 1rem;
        opacity: 0.7;
        font-weight: 500;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER YANG DIPERBAIKI ============
st.markdown("""
<div class="header">
    <div class="header-content">
        <span class="icon-deco">🌸</span>
        <h1>Klasifikasi Bunga</h1>
        <p class="subtitle">Upload gambar untuk mengetahui jenis bunganya</p>
        <div class="deco-line"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============ DATABASE ============
BUNGA_DESKRIPSI = {
    'tulip': {
        'nama_latin': 'Tulipa',
        'fakta': [
            '🌷 Tulip berasal dari Asia Tengah',
            '🌷 Ada lebih dari 3.000 varietas tulip',
            '🌷 Warna merah = cinta, kuning = kegembiraan',
            '🌷 Belanda pernah mengalami "Tulip Mania"'
        ]
    },
    'lily': {
        'nama_latin': 'Lilium',
        'fakta': [
            '🌸 Lily sudah ada sejak 3.000 tahun SM',
            '🌸 Memiliki 6 kelopak bunga',
            '🌸 Melambangkan kemurnian',
            '🌸 Bunga dewi Hera di Yunani kuno'
        ]
    },
    'orchid': {
        'nama_latin': 'Orchidaceae',
        'fakta': [
            '🌺 Memiliki 28.000+ spesies',
            '🌺 Ditemukan di semua benua kecuali Antartika',
            '🌺 Satu kapsul berisi 3 juta biji',
            '🌺 Bisa hidup hingga 100 tahun'
        ]
    },
    'sunflower': {
        'nama_latin': 'Helianthus annuus',
        'fakta': [
            '🌻 Bisa tumbuh hingga 3 meter',
            '🌻 Mengikuti pergerakan matahari',
            '🌻 Terdiri dari ribuan bunga kecil',
            '🌻 Bunga nasional Ukraina'
        ]
    },
    'lotus': {
        'nama_latin': 'Nelumbo nucifera',
        'fakta': [
            '🪷 Bisa hidup 1.000 tahun dalam kondisi kering',
            '🪷 Suci dalam agama Buddha dan Hindu',
            '🪷 Tetap bersih meski di air berlumpur',
            '🪷 Biji bisa berkecambah setelah 1.300 tahun'
        ]
    }
}

def get_deskripsi(nama):
    return BUNGA_DESKRIPSI.get(nama.lower())

# ============ LOAD MODEL ============
@st.cache_resource
def load_model():
    model_path = 'model_bunga_densenet121.h5'
    file_id = "12ZJi1HbkI8ian7fWM0K98ADi1tpMvU4y"
    
    # Coba load model yang sudah ada
    if os.path.exists(model_path):
        try:
            st.info("📂 Memuat model dari cache...")
            model = tf.keras.models.load_model(model_path, compile=False)
            st.success("✅ Model berhasil dimuat!")
            return model
        except Exception as e:
            st.warning(f"⚠️ Gagal load model: {str(e)}")
            os.remove(model_path)
            st.info("🔄 Mengunduh ulang model...")
    
    # Download model dari Google Drive
    try:
        with st.spinner('⏳ Mengunduh model (sekitar 30MB)...'):
            url = f'https://drive.google.com/uc?export=download&id={file_id}'
            session = requests.Session()
            response = session.get(url, stream=True)
            
            # Handle Google Drive confirmation
            if 'confirm' in response.text:
                confirm = re.search(r'confirm=([^&]+)', response.text)
                if confirm:
                    url = f'https://drive.google.com/uc?export=download&confirm={confirm.group(1)}&id={file_id}'
                    response = session.get(url, stream=True)
            
            # Simpan model
            total_size = int(response.headers.get('content-length', 0))
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            st.success('✅ Model berhasil diunduh!')
            
            # Load model
            model = tf.keras.models.load_model(model_path, compile=False)
            return model
            
    except Exception as e:
        st.error(f"❌ Gagal mengunduh model: {str(e)}")
        return None

# Load model
model = load_model()
if model is None:
    st.error("❌ Gagal load model. Silakan coba lagi nanti.")
    st.stop()

class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']

emoji_map = {
    'tulip': '🌷',
    'lily': '🌸',
    'orchid': '🌺',
    'sunflower': '🌻',
    'lotus': '🪷'
}

# ============ PREPROCESSING FUNCTION ============
def preprocess_image(img):
    """
    Preprocess gambar untuk model DenseNet121
    """
    try:
        # Resize ke 224x224 (ukuran input DenseNet121)
        img = img.resize((224, 224), Image.Resampling.LANCZOS)
        
        # Convert ke RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert ke array dan normalisasi
        x = np.array(img, dtype=np.float32)
        
        # Normalisasi ke [0,1] untuk DenseNet
        x = x / 255.0
        
        # Tambahkan batch dimension
        x = np.expand_dims(x, axis=0)
        
        return x
        
    except Exception as e:
        st.error(f"❌ Error preprocessing: {str(e)}")
        return None

# ============ PREDICTION ============
def predict_image(model, x):
    """
    Melakukan prediksi dengan model
    """
    try:
        # Prediksi
        pred = model.predict(x, verbose=0)
        return pred
    except Exception as e:
        st.error(f"❌ Error prediksi: {str(e)}")
        return None

# ============ UPLOAD ============
st.markdown("""
<div class="upload-area">
    <p class="main-text">📸 Upload Gambar Bunga</p>
    <p class="sub-text">Pilih gambar dari perangkat Anda</p>
    <p class="info-text">200MB per file • JPG, PNG</p>
</div>
""", unsafe_allow_html=True)

# File uploader dengan label yang benar
uploaded = st.file_uploader(
    "Pilih gambar bunga", 
    type=['jpg', 'png', 'jpeg'],
    label_visibility="visible"
)

if uploaded is not None:
    # Tampilkan info file
    st.info(f"📁 File: {uploaded.name} ({uploaded.size/1024:.1f} KB)")
    
    # Buka gambar
    img = Image.open(uploaded)
    st.image(img, caption=f"📸 {uploaded.name}", use_column_width=True)
    
    # Tombol klasifikasi
    if st.button("🔍 Klasifikasikan!", type="primary"):
        with st.spinner("⏳ Memproses gambar..."):
            try:
                # Preprocess
                x = preprocess_image(img)
                if x is None:
                    st.stop()
                
                # Prediksi
                pred = predict_image(model, x)
                if pred is None:
                    st.stop()
                
                # Ambil hasil
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                akurasi = pred[0][idx] * 100
                
                # Validasi akurasi
                if akurasi < 50:
                    st.warning(f"⚠️ Akurasi rendah ({akurasi:.1f}%). Model tidak yakin dengan prediksi ini.")
                elif akurasi > 90:
                    st.balloons()
                    st.success(f"🎉 Akurasi sangat tinggi! ({akurasi:.1f}%)")
                
                # Simpan hasil
                st.session_state['hasil'] = {
                    'nama': nama,
                    'akurasi': akurasi,
                    'probabilitas': pred[0]
                }
                
                # Force refresh
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.error("Silakan coba upload gambar lain.")

# ============ HASIL ============
if 'hasil' in st.session_state:
    hasil = st.session_state['hasil']
    nama = hasil['nama']
    akurasi = hasil['akurasi']
    prob = hasil['probabilitas']
    
    emoji = emoji_map.get(nama, '🌸')
    
    st.markdown(f"""
    <div class="result-box">
        <p class="label">✨ Hasil Klasifikasi</p>
        <p class="name">{emoji} {nama.upper()}</p>
        <div class="accuracy-wrapper">
            <p class="accuracy">🎯 {akurasi:.1f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    info = get_deskripsi(nama)
    if info:
        st.markdown(f"""
        <div class="info-card">
            <div class="title-wrapper">
                <span style="font-size:2rem;">📖</span>
                <p class="title">Informasi Bunga</p>
            </div>
            <div class="latin-wrapper">
                <p class="latin"><span style="font-style:normal;opacity:0.6;">Nama Latin:</span> {info['nama_latin']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        for i, fact in enumerate(info['fakta'], 1):
            icon = fact.split()[0] if ' ' in fact else '🌸'
            text = fact.replace(icon, '').strip()
            st.markdown(f"""
            <div class="fact">
                <span class="fact-icon">{icon}</span>
                <span><span class="fact-number">{i}</span> {text}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Probabilitas
    st.markdown("""
    <div class="prob-card">
        <div class="title-wrapper">
            <span style="font-size:2rem;">📊</span>
            <p class="title">Probabilitas</p>
        </div>
    """, unsafe_allow_html=True)
    
    sorted_indices = np.argsort(prob)[::-1]
    
    for idx in sorted_indices:
        name = class_names[idx]
        prob_value = prob[idx] * 100
        emoji_icon = emoji_map.get(name, '🌸')
        
        # Highlight prediksi utama
        if name == nama:
            st.markdown(f"""
            <div class="prob-item" style="background: rgba(232,138,158,0.1); border: 2px solid #e88a9e;">
                <div class="label">
                    <span class="name">
                        <span>{emoji_icon}</span>
                        <span><strong>{name.capitalize()} ✨</strong></span>
                    </span>
                    <span class="percentage">{prob_value:.1f}%</span>
                </div>
                <div class="bar">
                    <div class="fill" style="width: {prob_value}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="prob-item">
                <div class="label">
                    <span class="name">
                        <span>{emoji_icon}</span>
                        <span>{name.capitalize()}</span>
                    </span>
                    <span class="percentage">{prob_value:.1f}%</span>
                </div>
                <div class="bar">
                    <div class="fill" style="width: {prob_value}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tombol reset
    if st.button("🔄 Reset"):
        del st.session_state['hasil']
        st.rerun()

st.markdown("""
<div class="footer">
    🌸 Selamat mencoba! 🌸
</div>
""", unsafe_allow_html=True)
