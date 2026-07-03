import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

st.set_page_config(
    page_title="Identifikasi Bunga",
    layout="centered"
)

# ============ CSS ============
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(145deg, #faf0f5 0%, #fce4ec 50%, #f3e5f5 100%);
        font-family: 'Segoe UI', 'Quicksand', sans-serif;
    }
    
    .css-1d391kg, .css-1lcbmhc, .stSidebar, #MainMenu, header, footer {
        display: none !important;
    }
    
    .stFileUploader > div > button {
        font-family: 'Segoe UI', 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #e91e63, #c2185b) !important;
        color: white !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 0.8rem 2.5rem !important;
        font-size: 1.05rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 4px 15px rgba(233, 30, 99, 0.3) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }
    
    .stFileUploader > div > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(233, 30, 99, 0.4) !important;
        background: linear-gradient(135deg, #c2185b, #880e4f) !important;
    }
    
    .header {
        text-align: center;
        padding: 2.8rem 2rem 2.2rem 2rem;
        background: rgba(255, 255, 255, 0.85);
        border-radius: 30px;
        margin-bottom: 2.5rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 40px rgba(233, 30, 99, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.6);
        position: relative;
        overflow: hidden;
    }
    
    .header h1 {
        font-family: 'Playfair Display', 'Georgia', serif;
        font-size: 3.8rem;
        font-weight: 700;
        margin: 0.2rem 0;
        background: linear-gradient(135deg, #880e4f, #c2185b, #e91e63);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
        position: relative;
        z-index: 1;
        letter-spacing: 2px;
    }
    
    @keyframes shimmer {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    
    .header .subtitle {
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
        font-size: 1.15rem;
        font-weight: 500;
        color: #6a1b4d;
        margin: 0.8rem 0 0.5rem 0;
        opacity: 0.9;
        position: relative;
        z-index: 1;
        line-height: 1.8;
    }
    
    .result-box {
        background: linear-gradient(145deg, rgba(255,255,255,0.95), rgba(252,228,236,0.95));
        padding: 2.8rem 2.5rem;
        border-radius: 35px;
        text-align: center;
        box-shadow: 0 12px 50px rgba(233, 30, 99, 0.1);
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.8);
        animation: fadeInUp 0.7s ease;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.03); }
    }
    
    .result-box .label {
        font-family: 'Quicksand', sans-serif;
        color: #8b5a7a;
        font-size: 0.85rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 5px;
        text-transform: uppercase;
        opacity: 0.6;
        position: relative;
        z-index: 1;
    }
    
    .result-box .name {
        font-family: 'Playfair Display', 'Georgia', serif;
        font-size: 4.8rem;
        font-weight: 900;
        margin: 0.3rem 0 0.8rem 0;
        background: linear-gradient(135deg, #880e4f, #c2185b, #e91e63, #c2185b, #880e4f);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s linear infinite;
        letter-spacing: 3px;
        position: relative;
        z-index: 1;
    }
    
    .result-box .accuracy-wrapper {
        display: inline-block;
        background: linear-gradient(135deg, #e91e63, #c2185b);
        padding: 0.6rem 2.8rem;
        border-radius: 50px;
        box-shadow: 0 4px 25px rgba(233, 30, 99, 0.3);
        animation: pulse 2s ease-in-out infinite;
        position: relative;
        z-index: 1;
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
        background: linear-gradient(145deg, rgba(255,255,255,0.95), rgba(252,228,236,0.93));
        padding: 2rem;
        border-radius: 30px;
        box-shadow: 0 8px 40px rgba(233, 30, 99, 0.06);
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.6);
    }
    
    .info-card .title-wrapper {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 0.8rem;
    }
    
    .info-card .title {
        font-family: 'Playfair Display', 'Georgia', serif;
        color: #4a1942;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    .info-card .latin-wrapper {
        display: inline-block;
        background: linear-gradient(135deg, rgba(233,30,99,0.08), rgba(194,24,91,0.08));
        padding: 0.4rem 1.5rem;
        border-radius: 50px;
        margin: 0.5rem 0 1.2rem 0;
        border: 1px solid rgba(233,30,99,0.08);
    }
    
    .info-card .latin {
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
        color: #6b3a5a;
        font-style: italic;
        font-size: 1.05rem;
        margin: 0;
        font-weight: 600;
    }
    
    .fact {
        padding: 0.9rem 0.5rem;
        border-bottom: 1px solid rgba(233, 30, 99, 0.06);
        display: flex;
        align-items: center;
        gap: 16px;
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
        color: #4a1942;
        font-size: 0.95rem;
        font-weight: 500;
        transition: all 0.3s ease;
        padding-left: 0.8rem;
        border-radius: 12px;
    }
    
    .fact:hover {
        background: rgba(233, 30, 99, 0.04);
        padding-left: 1.2rem;
        transform: translateX(3px);
    }
    
    .fact:last-child {
        border-bottom: none;
    }
    
    .fact-icon {
        font-size: 1.5rem;
        min-width: 36px;
    }
    
    .prob-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.95), rgba(252,228,236,0.93));
        padding: 2rem;
        border-radius: 30px;
        box-shadow: 0 8px 40px rgba(233, 30, 99, 0.06);
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.6);
    }
    
    .prob-card .title-wrapper {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1.5rem;
    }
    
    .prob-card .title {
        font-family: 'Playfair Display', 'Georgia', serif;
        color: #4a1942;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    .prob-item {
        margin: 1rem 0;
        padding: 0.6rem 0.8rem;
        border-radius: 18px;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.4);
    }
    
    .prob-item:hover {
        background: rgba(255, 255, 255, 0.7);
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(233, 30, 99, 0.05);
    }
    
    .prob-item .label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #4a1942;
        margin-bottom: 0.4rem;
    }
    
    .prob-item .label .name {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .prob-item .label .percentage {
        font-size: 1.1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #e91e63, #c2185b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .prob-item .bar {
        background: rgba(233, 30, 99, 0.08);
        border-radius: 20px;
        height: 14px;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .prob-item .bar .fill {
        height: 100%;
        border-radius: 20px;
        transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .prob-item:nth-child(1) .fill { background: linear-gradient(90deg, #e91e63, #c2185b); }
    .prob-item:nth-child(2) .fill { background: linear-gradient(90deg, #f06292, #e91e63); }
    .prob-item:nth-child(3) .fill { background: linear-gradient(90deg, #ba68c8, #9c27b0); }
    .prob-item:nth-child(4) .fill { background: linear-gradient(90deg, #ffd54f, #ffb300); }
    .prob-item:nth-child(5) .fill { background: linear-gradient(90deg, #4dd0e1, #00acc1); }
    
    .stButton > button {
        width: 100%;
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        background: linear-gradient(135deg, #e91e63, #c2185b);
        color: white;
        padding: 0.9rem;
        border: none;
        border-radius: 50px;
        transition: all 0.4s ease;
        box-shadow: 0 4px 20px rgba(233, 30, 99, 0.25);
        margin-top: 1rem;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 35px rgba(233, 30, 99, 0.35);
        background: linear-gradient(135deg, #c2185b, #880e4f);
    }
    
    .footer {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
        color: #6b3a5a;
        font-size: 0.95rem;
        opacity: 0.6;
        font-weight: 500;
        letter-spacing: 0.5px;
        border-top: 1px solid rgba(233, 30, 99, 0.05);
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
<div class="header">
    <div class="emoji-row">🌸 🌺 🌷 🌻 🪷</div>
    <h1>Identifikasi Bunga</h1>
    <div class="subtitle">
        Unggah foto bunga dan dapatkan hasil identifikasi secara instan
    </div>
</div>
""", unsafe_allow_html=True)

# ============ DATABASE ============
BUNGA_DESKRIPSI = {
    'lily': {
        'nama_latin': 'Lilium',
        'fakta': [
            '🌸 Lily sudah ada sejak 3.000 tahun SM',
            '🌸 Memiliki 6 kelopak bunga',
            '🌸 Melambangkan kemurnian dan keanggunan',
            '🌸 Bunga dewi Hera dalam mitologi Yunani kuno'
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
            '🌻 Mengikuti pergerakan matahari (heliotropisme)',
            '🌻 Terdiri dari ribuan bunga kecil',
            '🌻 Bunga nasional Ukraina'
        ]
    },
    'tulip': {
        'nama_latin': 'Tulipa',
        'fakta': [
            '🌷 Tulip berasal dari Asia Tengah',
            '🌷 Ada lebih dari 3.000 varietas tulip',
            '🌷 Warna merah = cinta, kuning = kegembiraan',
            '🌷 Belanda pernah mengalami "Tulip Mania"'
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
    
    try:
        # Cek apakah model sudah ada
        if os.path.exists(model_path):
            st.info("📂 Memuat model dari lokal...")
            try:
                model = tf.keras.models.load_model(model_path, compile=False)
                st.success("✅ Model berhasil dimuat dari lokal!")
                return model
            except Exception as e:
                st.warning(f"⚠️ Gagal memuat model lokal: {str(e)}")
                os.remove(model_path)  # Hapus file corrupt
        
        # Download model dari Google Drive
        st.info("📥 Mengunduh model dari Google Drive...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Gunakan gdown untuk download
        url = f'https://drive.google.com/uc?id={file_id}'
        gdown.download(url, model_path, quiet=False)
        
        progress_bar.progress(100)
        status_text.text("✅ Download selesai!")
        
        # Load model
        st.info("🔄 Memuat model...")
        model = tf.keras.models.load_model(model_path, compile=False)
        st.success("✅ Model berhasil dimuat!")
        return model
        
    except Exception as e:
        st.error(f"❌ Gagal memuat model: {str(e)}")
        st.error("Pastikan file model tersedia dan koneksi internet stabil.")
        
        # Fallback: coba load dengan custom_objects
        try:
            custom_objects = {
                'Functional': tf.keras.models.Model,
                'Sequential': tf.keras.models.Sequential
            }
            model = tf.keras.models.load_model(model_path, compile=False, custom_objects=custom_objects)
            st.warning("⚠️ Model dimuat dengan custom_objects fallback.")
            return model
        except:
            return None

# Load model
with st.spinner("⏳ Sedang memuat model..."):
    model = load_model()

if model is None:
    st.error("❌ Gagal memuat model. Silakan restart aplikasi.")
    st.stop()

# ============ CLASS NAMES ============
# PERBAIKAN: Urutan class names sesuai dengan training model
# Model dilatih dengan urutan: lily, lotus, orchid, sunflower, tulip
class_names = ['lily', 'lotus', 'orchid', 'sunflower', 'tulip']

emoji_map = {
    'lily': '🌸',
    'lotus': '🪷',
    'orchid': '🌺',
    'sunflower': '🌻',
    'tulip': '🌷'
}

# ============ PREPROCESSING FUNCTION ============
def preprocess_image(img):
    """
    Preprocess gambar untuk DenseNet121
    Normalisasi yang benar untuk DenseNet121 di TensorFlow
    """
    try:
        # Resize ke 224x224
        img = img.resize((224, 224), Image.Resampling.LANCZOS)
        
        # Convert ke RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert ke array
        x = np.array(img, dtype=np.float32)
        
        # Normalisasi ke [0, 1] - standar untuk DenseNet121 di TensorFlow
        x = x / 255.0
        
        # Expand dims untuk batch
        x = np.expand_dims(x, axis=0)
        
        return x
        
    except Exception as e:
        st.error(f"❌ Error preprocessing: {str(e)}")
        return None

# ============ PREDICTION ============
def predict_flower(model, x):
    """
    Melakukan prediksi dengan confidence check
    """
    try:
        # Prediksi
        predictions = model.predict(x, verbose=0)
        
        # Pastikan output adalah probabilitas
        # Jika output masih logits, terapkan softmax
        prob = predictions[0]
        
        # Cek apakah sudah probabilitas (jumlah = 1)
        if np.sum(prob) > 1.1 or np.sum(prob) < 0.9:
            # Terapkan softmax jika belum
            prob = tf.nn.softmax(prob).numpy()
        
        # Ambil top prediction
        top_idx = np.argmax(prob)
        top_confidence = prob[top_idx] * 100
        
        return top_idx, top_confidence, prob
        
    except Exception as e:
        st.error(f"❌ Error prediction: {str(e)}")
        return None, None, None

# ============ UPLOAD ============
uploaded = st.file_uploader("", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

if uploaded:
    try:
        # Baca gambar
        img = Image.open(uploaded)
        
        # Tampilkan gambar
        st.image(img, use_column_width=True)
        
        # Tombol klasifikasi
        if st.button("🔍 Klasifikasikan!"):
            with st.spinner("⏳ Memproses gambar..."):
                # Preprocess
                x = preprocess_image(img)
                
                if x is not None:
                    # Prediksi
                    idx, akurasi, prob = predict_flower(model, x)
                    
                    if idx is not None:
                        nama = class_names[idx]
                        
                        # Validasi confidence
                        if akurasi < 50:
                            st.warning(f"⚠️ Akurasi rendah ({akurasi:.1f}%). Model tidak yakin dengan prediksi ini.")
                        
                        # Simpan hasil
                        st.session_state['hasil'] = {
                            'nama': nama,
                            'akurasi': akurasi,
                            'probabilitas': prob,
                            'idx': idx
                        }
                        
                        st.balloons()
                        
    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")

# ============ HASIL ============
if 'hasil' in st.session_state:
    hasil = st.session_state['hasil']
    nama = hasil['nama']
    akurasi = hasil['akurasi']
    prob = hasil['probabilitas']
    idx = hasil['idx']
    
    emoji = emoji_map.get(nama, '🌸')
    
    # Tampilkan hasil
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
    <div class="prob-card">
        <div class="title-wrapper">
            <span style="font-size:2rem;">📊</span>
            <p class="title">Probabilitas</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sort by probability
    sorted_indices = np.argsort(prob)[::-1]
    
    for i in sorted_indices:
        name = class_names[i]
        prob_value = prob[i] * 100
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
