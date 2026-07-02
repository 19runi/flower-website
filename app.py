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

# CSS dengan Background Pink Soft
st.markdown("""
<style>
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
        color: #4a1942;
        font-size: 2.8rem;
        margin: 0;
        font-weight: 700;
    }
    
    .header p {
        color: #6b3a5a;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Upload area */
    .upload-area {
        background: rgba(255, 255, 255, 0.7);
        padding: 3rem 2rem;
        border-radius: 20px;
        border: 2px dashed #ffb6c1;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(255, 182, 193, 0.2);
    }
    
    .upload-area:hover {
        background: rgba(255, 255, 255, 0.85);
        border-color: #e88a9e;
    }
    
    .upload-area .info-text {
        color: #6b3a5a;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        opacity: 0.7;
    }
    
    /* Tombol */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #e88a9e, #d4708a);
        color: white;
        font-weight: 600;
        padding: 0.8rem;
        border: none;
        border-radius: 15px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(232, 138, 158, 0.3);
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(232, 138, 158, 0.5);
        background: linear-gradient(135deg, #d4708a, #c05d78);
    }
    
    /* Upload label */
    .stFileUploader > div > button {
        background: #e88a9e !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
    }
    
    .stFileUploader > div > button:hover {
        background: #d4708a !important;
    }
    
    /* Image preview */
    .image-preview {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(255, 182, 193, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.5);
        margin: 1rem 0;
    }
    
    /* Result box */
    .result-box {
        background: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(255, 182, 193, 0.3);
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.5);
    }
    
    .result-box .name {
        font-size: 3rem;
        font-weight: bold;
        color: #4a1942;
        margin: 0.5rem 0;
    }
    
    .result-box .accuracy {
        font-size: 1.4rem;
        color: #c0392b;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.5);
        padding: 0.3rem 1.5rem;
        border-radius: 50px;
        display: inline-block;
    }
    
    /* Info card */
    .info-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(255, 182, 193, 0.2);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.5);
    }
    
    .info-card .title {
        color: #4a1942;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .info-card .latin {
        color: #6b3a5a;
        font-style: italic;
        font-size: 1rem;
        margin: 0;
    }
    
    .fact {
        padding: 0.7rem 0;
        border-bottom: 1px solid rgba(255, 182, 193, 0.3);
        display: flex;
        align-items: center;
        gap: 12px;
        color: #4a1942;
        font-size: 0.95rem;
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
        font-size: 0.95rem;
        color: #4a1942;
        font-weight: 500;
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
        color: #6b3a5a;
        font-size: 0.9rem;
        opacity: 0.7;
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
uploaded = st.file_uploader("", type=['jpg', 'png', 'jpeg'])

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

# ============ TAMPILKAN HASIL ============
if 'hasil' in st.session_state:
    hasil = st.session_state['hasil']
    nama = hasil['nama']
    akurasi = hasil['akurasi']
    prob = hasil['probabilitas']
    
    # Result card
    st.markdown(f"""
    <div class="result-box">
        <p style="color: #6b3a5a; font-size: 1rem; margin: 0;">Hasil Klasifikasi</p>
        <p class="name">{nama.upper()}</p>
        <p class="accuracy">✨ {akurasi:.1f}%</p>
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
        st.markdown(f"""
        <div class="progress-item">
            <div class="label">
                <span>{'🌸 ' + name.capitalize()}</span>
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
