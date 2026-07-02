import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

st.set_page_config(page_title="Klasifikasi Bunga", page_icon="🌸")

# ============ CUSTOM CSS UNTUK DESAIN ============
st.markdown("""
<style>
    /* Styling utama */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .header-container h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .header-container p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Card styling */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #f0f0f0;
    }
    
    /* Upload area styling */
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        background: #f0f2ff;
        border-color: #764ba2;
    }
    
    /* Result card */
    .result-card {
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin-top: 1rem;
    }
    
    .flower-name {
        font-size: 2rem;
        font-weight: 700;
        color: #2d3436;
        margin: 0;
    }
    
    .accuracy {
        font-size: 1.2rem;
        color: #00b894;
        font-weight: 600;
    }
    
    /* Description styling */
    .desc-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .fact-item {
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-radius: 6px;
        background: white;
        border-left: 3px solid #667eea;
    }
    
    /* Progress bar container */
    .prob-item {
        margin: 0.5rem 0;
        padding: 0.3rem;
        border-radius: 6px;
        background: #f8f9fa;
    }
    
    .prob-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.2rem;
    }
    
    /* Custom progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-weight: 600;
        padding: 0.6rem 2rem;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Image styling */
    .stImage {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Success/Info boxes */
    .stAlert {
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
<div class="header-container">
    <h1>🌸 Klasifikasi Jenis Bunga</h1>
    <p>Upload gambar bunga untuk mengetahui jenisnya!</p>
</div>
""", unsafe_allow_html=True)

class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']

# ============ DATABASE DESKRIPSI BUNGA ============
BUNGA_DESKRIPSI = {
    'tulip': {
        'nama_latin': 'Tulipa',
        'fakta': [
            '🌷 Tulip berasal dari Asia Tengah dan menjadi simbol nasional Belanda',
            '🌷 Ada lebih dari 3.000 varietas tulip yang terdaftar secara resmi',
            '🌷 Warna tulip memiliki makna: merah melambangkan cinta, kuning melambangkan kegembiraan',
            '🌷 Pada abad ke-17, Belanda mengalami "Tulip Mania"'
        ]
    },
    'lily': {
        'nama_latin': 'Lilium',
        'fakta': [
            '🌸 Lily adalah salah satu bunga tertua, sudah ada sejak 3.000 tahun SM',
            '🌸 Bunga lily memiliki 6 kelopak dan melambangkan kemurnian',
            '🌸 Di Yunani kuno, lily adalah bunga dewi Hera',
            '🌸 Beberapa spesies lily dapat tumbuh hingga 2,5 meter'
        ]
    },
    'orchid': {
        'nama_latin': 'Orchidaceae',
        'fakta': [
            '🌺 Anggrek memiliki lebih dari 28.000 spesies',
            '🌺 Anggrek dapat ditemukan di setiap benua kecuali Antartika',
            '🌺 Satu kapsul anggrek dapat berisi hingga 3 juta biji',
            '🌺 Beberapa spesies anggrek dapat hidup hingga 100 tahun'
        ]
    },
    'sunflower': {
        'nama_latin': 'Helianthus annuus',
        'fakta': [
            '🌻 Bunga matahari dapat tumbuh hingga 3 meter lebih',
            '🌻 Bunga matahari muda mengikuti pergerakan matahari',
            '🌻 Kepala bunga matahari terdiri dari ribuan bunga kecil',
            '🌻 Bunga matahari adalah bunga nasional Ukraina'
        ]
    },
    'lotus': {
        'nama_latin': 'Nelumbo nucifera',
        'fakta': [
            '🪷 Teratai dapat bertahan hidup hingga 1.000 tahun dalam kondisi kering',
            '🪷 Bunga teratai suci dalam agama Buddha dan Hindu',
            '🪷 Meskipun tumbuh di air berlumpur, teratai tetap bersih',
            '🪷 Biji teratai dapat berkecambah setelah 1.300 tahun'
        ]
    }
}

def get_deskripsi_bunga(nama_bunga):
    bunga_info = BUNGA_DESKRIPSI.get(nama_bunga.lower())
    if bunga_info:
        deskripsi = f"### 🌿 **{nama_bunga.upper()}** *({bunga_info['nama_latin']})*\n\n"
        for fakta in bunga_info['fakta']:
            deskripsi += f"<div class='fact-item'>{fakta}</div>\n"
        return deskripsi
    return f"⚠️ Deskripsi untuk {nama_bunga} belum tersedia"
# ===================================================

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

# ============ UPLOAD AREA ============
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="upload-area">', unsafe_allow_html=True)

uploaded = st.file_uploader("📤 Pilih gambar bunga", type=['jpg','png','jpeg'])

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded:
    img = Image.open(uploaded)
    st.image(img, use_column_width=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    if st.button("🔍 Klasifikasikan!"):
        img = img.resize((224,224))
        x = np.array(img) / 255.0
        x = np.expand_dims(x, axis=0)
        
        pred = model.predict(x)
        idx = np.argmax(pred[0])
        nama = class_names[idx]
        acc = pred[0][idx] * 100
        
        # ============ HASIL PREDIKSI ============
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="flower-name">🌸 {nama.upper()}</span>
            <span class="accuracy">🎯 {acc:.2f}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        # ============ DESKRIPSI ============
        st.markdown('<div class="desc-box">', unsafe_allow_html=True)
        deskripsi = get_deskripsi_bunga(nama)
        st.markdown(deskripsi, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ============ PROBABILITAS ============
        st.markdown("### 📊 Probabilitas per Kelas")
        for i, name in enumerate(class_names):
            prob = pred[0][i] * 100
            st.markdown(f"""
            <div class="prob-item">
                <div class="prob-label">
                    <span>{name.capitalize()}</span>
                    <span>{prob:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(int(prob) / 100)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("""
<div style="text-align: center; padding: 2rem 0 0 0; color: #888; font-size: 0.9rem;">
    ✨ Dibuat dengan Streamlit & TensorFlow
</div>
""", unsafe_allow_html=True)
