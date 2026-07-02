import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re
import base64

# Konfigurasi halaman
st.set_page_config(
    page_title="Klasifikasi Bunga", 
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk desain yang lebih menarik
st.markdown("""
<style>
    /* Background dan styling utama */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: fadeInDown 0.8s ease;
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .upload-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 2rem;
    }
    
    .upload-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    /* Hasil prediksi styling */
    .result-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-top: 2rem;
        animation: fadeInUp 0.6s ease;
    }
    
    .result-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
    }
    
    .result-title.tulip {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
    }
    .result-title.lily {
        background: linear-gradient(135deg, #fda085, #f6d365);
        color: white;
    }
    .result-title.orchid {
        background: linear-gradient(135deg, #a8edea, #fed6e3);
        color: #2d3436;
    }
    .result-title.sunflower {
        background: linear-gradient(135deg, #f6d365, #fda085);
        color: white;
    }
    .result-title.lotus {
        background: linear-gradient(135deg, #e0c3fc, #8ec5fc);
        color: #2d3436;
    }
    
    .accuracy-badge {
        display: inline-block;
        background: linear-gradient(135deg, #00b894, #00cec9);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.2rem;
        margin: 0.5rem 0;
    }
    
    /* Deskripsi styling */
    .description-box {
        background: linear-gradient(135deg, #dfe6e9, #b2bec3);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #6c5ce7;
    }
    
    .fact-item {
        padding: 0.5rem;
        margin: 0.5rem 0;
        background: rgba(255,255,255,0.6);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .fact-item:hover {
        transform: translateX(10px);
        background: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Progress bar styling */
    .progress-container {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.2rem;
        font-weight: 500;
    }
    
    /* Custom progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        border-radius: 10px !important;
    }
    
    /* Upload button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border: none;
        border-radius: 50px;
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* File uploader styling */
    .uploaded-file {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: rgba(255,255,255,0.5);
        transition: all 0.3s ease;
    }
    
    .uploaded-file:hover {
        border-color: #764ba2;
        background: rgba(255,255,255,0.8);
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
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
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .result-title {
            font-size: 1.8rem;
        }
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# Header yang menarik
st.markdown("""
<div class="main-header">
    <h1>🌸 Klasifikasi Jenis Bunga</h1>
    <p>Upload gambar bunga dan temukan keindahan di balik setiap kelopaknya</p>
</div>
""", unsafe_allow_html=True)

# Definisi class names
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
        deskripsi = f"### 🌿 **{nama_bunga.upper()}** *({bunga_info['nama_latin']})*\n"
        for fakta in bunga_info['fakta']:
            deskripsi += f"\n{fakta}"
        return deskripsi
    return f"\n⚠️ Deskripsi untuk {nama_bunga} belum tersedia\n"
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

# Upload area dengan design yang menarik
st.markdown('<div class="upload-card">', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "📤 Pilih gambar bunga", 
    type=['jpg','png','jpeg'],
    help="Upload gambar dengan format JPG, PNG, atau JPEG"
)

if uploaded:
    img = Image.open(uploaded)
    
    # Tampilan gambar dengan styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(img, use_column_width=True, caption="📸 Gambar yang diupload")
    
    # Tombol klasifikasi dengan styling
    if st.button("🔍 Klasifikasikan Bunga!", use_container_width=True):
        img = img.resize((224,224))
        x = np.array(img) / 255.0
        x = np.expand_dims(x, axis=0)
        
        pred = model.predict(x)
        idx = np.argmax(pred[0])
        nama = class_names[idx]
        acc = pred[0][idx] * 100
        
        # Hasil prediksi
        st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
        
        # Title dengan warna sesuai kelas
        color_class = nama.lower()
        st.markdown(f"""
        <div class="result-title {color_class}">
            🌸 {nama.upper()}
        </div>
        """, unsafe_allow_html=True)
        
        # Accuracy badge
        st.markdown(f"""
        <div style="text-align: center;">
            <span class="accuracy-badge">🎯 Akurasi: {acc:.2f}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        # ============ TAMPILKAN DESKRIPSI ============
        deskripsi = get_deskripsi_bunga(nama)
        st.markdown(f"""
        <div class="description-box">
            {deskripsi}
        </div>
        """, unsafe_allow_html=True)
        # =============================================
        
        # Probabilitas per kelas
        st.markdown("### 📊 Probabilitas per Kelas")
        for i, name in enumerate(class_names):
            prob = pred[0][i] * 100
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-label">
                    <span>{name.capitalize()}</span>
                    <span>{prob:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(int(prob) / 100)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666; margin-top: 2rem;">
    <small>✨ Dibuat dengan ❤️ menggunakan Streamlit & TensorFlow</small>
</div>
""", unsafe_allow_html=True)
