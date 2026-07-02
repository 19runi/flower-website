import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

st.set_page_config(
    page_title="Klasifikasi Bunga",
    page_icon="🌸",
    layout="centered"
)

# CSS dengan Font dan Efek Menarik
st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Quicksand:wght@400;600;700&display=swap');
    
    /* Background pink soft */
    .stApp {
        background: linear-gradient(135deg, #ffe4e1 0%, #ffd1dc 50%, #ffb6c1 100%);
    }
    
    /* Hilangkan sidebar */
    .css-1d391kg, .css-1lcbmhc {
        display: none;
    }
    
    .stSidebar {
        display: none;
    }
    
    /* Header */
    .header {
        text-align: center;
        padding: 2.5rem 1.5rem;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 20px;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(255, 182, 193, 0.2);
    }
    
    .header h1 {
        font-family: 'Playfair Display', serif;
        color: #4a1942;
        font-size: 3.2rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 2px 2px 8px rgba(255, 182, 193, 0.3);
        letter-spacing: 2px;
    }
    
    .header p {
        font-family: 'Quicksand', sans-serif;
        color: #6b3a5a;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    /* Upload area */
    .upload-area {
        background: rgba(255, 255, 255, 0.85);
        padding: 3rem 2rem;
        border-radius: 25px;
        border: 3px dashed #e88a9e;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(255, 182, 193, 0.25);
        transition: all 0.3s ease;
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
    
    /* Tombol */
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
    
    /* Upload label */
    .stFileUploader > div > button {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        background: #e88a9e !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div > button:hover {
        background: #d4708a !important;
        transform: scale(1.02);
    }
    
    /* Image preview */
    .image-preview {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(255, 182, 193, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.6);
        margin: 1.5rem 0;
    }
    
    /* ============ RESULT BOX YANG LEBIH MENARIK ============ */
    .result-box {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,240,245,0.95));
        padding: 2.5rem 2rem;
        border-radius: 30px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(255, 182, 193, 0.4), 
                    inset 0 1px 0 rgba(255,255,255,0.8);
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.6);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease;
    }
    
    /* Efek dekoratif di belakang */
    .result-box::before {
        content: '🌸';
        position: absolute;
        font-size: 8rem;
        opacity: 0.05;
        top: -20px;
        right: -20px;
        transform: rotate(15deg);
    }
    
    .result-box::after {
        content: '🌺';
        position: absolute;
        font-size: 6rem;
        opacity: 0.05;
        bottom: -20px;
        left: -20px;
        transform: rotate(-10deg);
    }
    
    /* Animasi muncul */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
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
        position: relative;
        z-index: 1;
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
        position: relative;
        z-index: 1;
        text-shadow: none;
        letter-spacing: 3px;
    }
    
    .result-box .accuracy-wrapper {
        display: inline-block;
        background: linear-gradient(135deg, #e88a9e, #d4708a);
        padding: 0.5rem 2.5rem;
        border-radius: 50px;
        box-shadow: 0 4px 20px rgba(232, 138, 158, 0.4);
        position: relative;
        z-index: 1;
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
    
    .result-box .accuracy-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    
    /* Emoji confetti effect */
    .result-box .confetti {
        position: absolute;
        font-size: 1.5rem;
        opacity: 0.2;
        z-index: 0;
    }
    
    /* Info card */
    .info-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 25px;
        box-shadow: 0 8px 32px rgba(255, 182, 193, 0.2);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.5);
    }
    
    .info-card .title {
        font-family: 'Playfair Display', serif;
        color: #4a1942;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .info-card .latin {
        font-family: 'Quicksand', sans-serif;
        color: #6b3a5a;
        font-style: italic;
        font-size: 1rem;
        margin: 0;
        font-weight: 400;
    }
    
    .fact {
        padding: 0.7rem 0;
        border-bottom: 1px solid rgba(255, 182, 193, 0.3);
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: 'Quicksand', sans-serif;
        color: #4a1942;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    .fact:last-child {
        border-bottom: none;
    }
    
    .fact-icon {
        font-size: 1.3rem;
        min-width: 35px;
    }
    
    /* Progress bar */
    .progress-item {
        margin: 0.7rem 0;
    }
    
    .progress-item .label {
        display: flex;
        justify-content: space-between;
        font-family: 'Quicksand', sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        color: #4a1942;
    }
    
    .progress-item .bar {
        background: rgba(255, 182, 193, 0.3);
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
        margin-top: 4px;
    }
    
    .progress-item .bar .fill {
        height: 100%;
        background: linear-gradient(90deg, #e88a9e, #d4708a);
        border-radius: 10px;
        transition: width 0.8s ease;
    }
    
    /* Loading */
    .stSpinner > div {
        border-color: #e88a9e !important;
    }
    
    /* Footer */
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

# ============ HEADER ============
st.markdown("""
<div class="header">
    <h1>🌸 Klasifikasi Bunga</h1>
    <p>Upload gambar untuk mengetahui jenis bunganya</p>
</div>
""", unsafe_allow_html=True)

# ============ DATABASE DESKRIPSI ============
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
    
    if os.path.exists(model_path):
        try:
            return tf.keras.models.load_model(model_path)
        except:
            os.remove(model_path)
    
    with st.spinner('⏳ Mengunduh model...'):
        url = f'https://drive.google.com/uc?export=download&id={file_id}'
        r = requests.get(url, stream=True)
        
        if 'confirm' in r.text:
            confirm = re.search(r'confirm=([^&]+)', r.text)
            if confirm:
                url = f'https://drive.google.com/uc?export=download&confirm={confirm.group(1)}&id={file_id}'
                r = requests.get(url, stream=True)
        
        with open(model_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        st.success('✅ Model siap!')
        return tf.keras.models.load_model(model_path)

model = load_model()
if model is None:
    st.error("❌ Gagal load model")
    st.stop()

class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']

# ============ UPLOAD AREA ============
st.markdown("""
<div class="upload-area">
    <p class="main-text">📸 Upload Gambar Bunga</p>
    <p class="sub-text">Pilih gambar dari perangkat Anda</p>
    <p class="info-text">200MB per file • JPG, PNG</p>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

if uploaded:
    img = Image.open(uploaded)
    st.markdown('<div class="image-preview">', unsafe_allow_html=True)
    st.image(img, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🔍 Klasifikasikan!"):
        with st.spinner("⏳ Memproses..."):
            img_resized = img.resize((224, 224))
            x = np.array(img_resized) / 255.0
            x = np.expand_dims(x, axis=0)
            
            pred = model.predict(x)
            idx = np.argmax(pred[0])
            nama = class_names[idx]
            akurasi = pred[0][idx] * 100
            
            st.session_state['hasil'] = {
                'nama': nama,
                'akurasi': akurasi,
                'probabilitas': pred[0]
            }

# ============ TAMPILKAN HASIL DENGAN EFEK MENARIK ============
if 'hasil' in st.session_state:
    hasil = st.session_state['hasil']
    nama = hasil['nama']
    akurasi = hasil['akurasi']
    prob = hasil['probabilitas']
    
    # Pilih emoji berdasarkan bunga
    emoji_map = {
        'tulip': '🌷',
        'lily': '🌸',
        'orchid': '🌺',
        'sunflower': '🌻',
        'lotus': '🪷'
    }
    emoji = emoji_map.get(nama, '🌸')
    
    # Result card dengan efek menarik
    st.markdown(f"""
    <div class="result-box">
        <div class="confetti" style="top:10%; left:5%;">✨</div>
        <div class="confetti" style="top:20%; right:8%;">🌟</div>
        <div class="confetti" style="bottom:15%; left:10%;">💫</div>
        <div class="confetti" style="bottom:25%; right:5%;">⭐</div>
        <p class="label">✨ Hasil Klasifikasi</p>
        <p class="name">{emoji} {nama.upper()}</p>
        <div class="accuracy-wrapper">
            <p class="accuracy">
                <span class="accuracy-icon">🎯</span>
                {akurasi:.1f}%
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Deskripsi
    info = get_deskripsi(nama)
    if info:
        st.markdown("""
        <div class="info-card">
            <div class="title">📖 Informasi Bunga</div>
            <p class="latin">Nama Latin: {}</p>
        """.format(info['nama_latin']), unsafe_allow_html=True)
        
        for fact in info['fakta']:
            icon = fact.split()[0] if ' ' in fact else '🌸'
            text = fact.replace(icon, '').strip()
            st.markdown(f"""
            <div class="fact">
                <span class="fact-icon">{icon}</span>
                <span>{text}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Probabilitas
    st.markdown("""
    <div class="info-card">
        <div class="title">📊 Probabilitas</div>
    """, unsafe_allow_html=True)
    
    for i, name in enumerate(class_names):
        prob_value = prob[i] * 100
        emoji_icon = emoji_map.get(name, '🌸')
        st.markdown(f"""
        <div class="progress-item">
            <div class="label">
                <span>{emoji_icon} {name.capitalize()}</span>
                <span>{prob_value:.1f}%</span>
            </div>
            <div class="bar">
                <div class="fill" style="width: {prob_value}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("""
<div class="footer">
    🌸 Selamat mencoba! 🌸
</div>
""", unsafe_allow_html=True)
