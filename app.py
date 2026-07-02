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
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #fce4ec 0%, #f3e5f5 100%);
    }
    .card {
        background: rgba(255,255,255,0.9);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
    }
    .title {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        background: linear-gradient(45deg, #ff6b6b, #ffa94d, #ffd93d, #6bcb77, #4d96ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .result-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 20px;
        padding: 25px;
        border-left: 6px solid #ff6b6b;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    .nama-bunga {
        font-size: 2.5em;
        font-weight: bold;
        color: #2d3436;
    }
    .akurasi {
        font-size: 2em;
        font-weight: bold;
        color: #00b894;
    }
    .deskripsi-card {
        background: linear-gradient(135deg, #dfe6e9, #b2bec3);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #6c5ce7;
    }
    .fakta-item {
        padding: 8px 0;
        font-size: 1.05em;
        border-bottom: 1px solid #eee;
    }
    .stProgress > div > div {
        background: linear-gradient(90deg, #00b894, #00cec9) !important;
        border-radius: 10px !important;
    }
    .upload-area {
        border: 3px dashed #dfe6e9;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        background: rgba(255,255,255,0.5);
    }
    .footer {
        text-align: center;
        color: #888;
        margin-top: 40px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown('<p class="title">🌸 Klasifikasi Jenis Bunga</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload gambar bunga untuk mengetahui jenisnya secara instan! 🚀</p>', unsafe_allow_html=True)

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
        return bunga_info['fakta']
    return None

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

class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']

with st.container():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        model = load_model()
        if model is None:
            st.error("❌ Gagal load model")
            st.stop()
        st.success("✅ Model berhasil dimuat!")

# ============ UPLOAD & PREDIKSI ============
st.markdown("---")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "📤 Upload gambar bunga", 
        type=['jpg', 'png', 'jpeg'],
        help="Upload gambar dengan format JPG, PNG, atau JPEG"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="📷 Gambar yang diupload", use_column_width=True)

with col_right:
    if uploaded:
        if st.button("🔍 Klasifikasi Sekarang!", use_container_width=True, type="primary"):
            with st.spinner("🧠 Menganalisis gambar..."):
                img_resized = img.resize((224, 224))
                x = np.array(img_resized) / 255.0
                x = np.expand_dims(x, axis=0)
                
                pred = model.predict(x)
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                acc = pred[0][idx] * 100
                
                # === HASIL ===
                st.markdown("---")
                st.markdown("### 📊 Hasil Klasifikasi")
                
                col_res1, col_res2 = st.columns([2, 1])
                with col_res1:
                    st.markdown(f'<p class="nama-bunga">🌺 {nama.upper()}</p>', unsafe_allow_html=True)
                with col_res2:
                    st.markdown(f'<p class="akurasi">{acc:.2f}%</p>', unsafe_allow_html=True)
                
                # === DESKRIPSI ===
                fakta_list = get_deskripsi_bunga(nama)
                if fakta_list:
                    st.markdown(f'<div class="deskripsi-card">', unsafe_allow_html=True)
                    st.markdown(f"**📖 Fakta Menarik tentang {nama.upper()}**")
                    for fakta in fakta_list:
                        st.markdown(f"- {fakta}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # === PROBABILITAS ===
                st.markdown("**📈 Probabilitas per Kelas:**")
                for i, name in enumerate(class_names):
                    prob = pred[0][i] * 100
                    col_bar, col_pct = st.columns([4, 1])
                    with col_bar:
                        st.progress(int(prob) / 100)
                    with col_pct:
                        st.write(f"{prob:.1f}%")

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🌸 Dibuat dengan ❤️ menggunakan TensorFlow & Streamlit • Model DenseNet121</p>
    <p>© 2026 Klasifikasi Bunga • 5 Jenis: Tulip, Lily, Orchid, Sunflower, Lotus</p>
</div>
""", unsafe_allow_html=True)
