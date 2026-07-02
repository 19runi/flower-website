import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re
import io

st.set_page_config(
    page_title="Klasifikasi Bunga",
    page_icon="🌸",
    layout="centered"
)

# CSS (Saya singkatkan, gunakan CSS Anda yang sudah ada)
st.markdown("""
<style>
    /* ... CSS Anda yang sudah ada ... */
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
<div class="header">
    <h1>🌸 Klasifikasi Bunga</h1>
    <p>Upload gambar untuk mengetahui jenis bunganya</p>
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
            # Load dengan custom_objects untuk kompatibilitas
            model = tf.keras.models.load_model(model_path, compile=False)
            st.success("✅ Model berhasil dimuat dari lokal!")
            return model
        except Exception as e:
            st.warning(f"⚠️ Gagal load model lokal: {str(e)}")
            os.remove(model_path)  # Hapus file corrupt
    
    # Download model dari Google Drive
    with st.spinner('⏳ Mengunduh model (sekitar 30MB)...'):
        try:
            url = f'https://drive.google.com/uc?export=download&id={file_id}'
            session = requests.Session()
            response = session.get(url, stream=True)
            
            # Handle Google Drive confirmation
            if 'confirm' in response.text:
                confirm = re.search(r'confirm=([^&]+)', response.text)
                if confirm:
                    url = f'https://drive.google.com/uc?export=download&confirm={confirm.group(1)}&id={file_id}'
                    response = session.get(url, stream=True)
            
            # Download file
            total_size = 0
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            st.success(f"✅ Model berhasil diunduh! ({total_size/1024/1024:.1f} MB)")
            
            # Load model
            model = tf.keras.models.load_model(model_path, compile=False)
            return model
            
        except Exception as e:
            st.error(f"❌ Gagal download/load model: {str(e)}")
            return None

# Load model
model = load_model()
if model is None:
    st.error("❌ Gagal memuat model. Silakan coba lagi nanti.")
    st.stop()

# Class names dan emoji
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
    Preprocess gambar untuk DenseNet121
    """
    try:
        # Resize ke 224x224 (ukuran input DenseNet)
        img = img.resize((224, 224), Image.Resampling.LANCZOS)
        
        # Convert ke RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert ke array
        x = np.array(img, dtype=np.float32)
        
        # Normalisasi untuk DenseNet (ImageNet preprocessing)
        # DenseNet dilatih dengan normalisasi [0,1] dan kemudian mean subtraction
        x = x / 255.0
        
        # Preprocessing sesuai DenseNet (mean subtraction)
        # Mean ImageNet: [0.485, 0.456, 0.406]
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        x = (x - mean) / std
        
        # Add batch dimension
        x = np.expand_dims(x, axis=0)
        
        return x
        
    except Exception as e:
        st.error(f"❌ Error preprocessing: {str(e)}")
        return None

# ============ PREDICTION ============
def predict_image(img):
    """
    Melakukan prediksi pada gambar
    """
    try:
        # Preprocess
        x = preprocess_image(img)
        if x is None:
            return None
        
        # Predict
        predictions = model.predict(x, verbose=0)
        
        # Ambil hasil
        idx = np.argmax(predictions[0])
        nama = class_names[idx]
        akurasi = predictions[0][idx] * 100
        
        return {
            'nama': nama,
            'akurasi': akurasi,
            'probabilitas': predictions[0],
            'all_predictions': predictions
        }
        
    except Exception as e:
        st.error(f"❌ Error prediksi: {str(e)}")
        return None

# ============ UPLOAD SECTION ============
st.markdown("""
<div class="upload-area">
    <p class="main-text">📸 Upload Gambar Bunga</p>
    <p class="sub-text">Pilih gambar dari perangkat Anda</p>
    <p class="info-text">200MB per file • JPG, PNG</p>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

if uploaded:
    try:
        # Baca gambar
        img = Image.open(uploaded)
        
        # Tampilkan preview
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(img, use_column_width=True)
        
        # Button prediksi
        if st.button("🔍 Klasifikasikan!", use_container_width=True):
            with st.spinner("⏳ Menganalisis gambar..."):
                # Lakukan prediksi
                result = predict_image(img)
                
                if result:
                    # Simpan hasil di session state
                    st.session_state['hasil'] = result
                    st.rerun()
                    
    except Exception as e:
        st.error(f"❌ Error membaca gambar: {str(e)}")

# ============ HASIL PREDIKSI ============
if 'hasil' in st.session_state:
    hasil = st.session_state['hasil']
    nama = hasil['nama']
    akurasi = hasil['akurasi']
    prob = hasil['probabilitas']
    emoji = emoji_map.get(nama, '🌸')
    
    # Tampilkan hasil utama
    st.markdown(f"""
    <div class="result-box">
        <p class="label">✨ Hasil Klasifikasi</p>
        <p class="name">{emoji} {nama.upper()}</p>
        <div class="accuracy-wrapper">
            <p class="accuracy">🎯 {akurasi:.1f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Informasi bunga
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
    
    # Probabilitas semua kelas
    st.markdown("""
    <div class="prob-card">
        <div class="title-wrapper">
            <span style="font-size:2rem;">📊</span>
            <p class="title">Probabilitas per Kelas</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Urutkan dari probabilitas tertinggi
    sorted_indices = np.argsort(prob)[::-1]
    
    for idx in sorted_indices:
        name = class_names[idx]
        prob_value = prob[idx] * 100
        emoji_icon = emoji_map.get(name, '🌸')
        
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
    
    st.markdown('</div>', unsafe_HTML=True)
    
    # Button untuk reset
    if st.button("🔄 Coba Gambar Lain", use_container_width=True):
        del st.session_state['hasil']
        st.rerun()

# ============ FOOTER ============
st.markdown("""
<div class="footer">
    🌸 Dibuat dengan ❤️ untuk pecinta bunga 🌸
</div>
""", unsafe_allow_html=True)
