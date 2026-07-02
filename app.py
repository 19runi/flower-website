import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

st.set_page_config(
    page_title="Identifikasi Bunga",
    page_icon="🌸",
    layout="centered"
)

# CSS 
st.markdown("""
<style>
    /* Background utama dengan gradien yang lebih halus */
    .stApp {
        background: linear-gradient(145deg, #faf0f5 0%, #fce4ec 50%, #f3e5f5 100%);
        font-family: 'Segoe UI', 'Quicksand', sans-serif;
    }
    
    /* Menyembunyikan elemen default Streamlit */
    .css-1d391kg, .css-1lcbmhc, .stSidebar, #MainMenu, header, footer {
        display: none !important;
    }
    
    /* Custom upload button */
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
    
    /* Header utama - lebih elegan */
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
    
    .header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(233, 30, 99, 0.03), transparent 70%);
        pointer-events: none;
    }
    
    .header .emoji-row {
        font-size: 3.2rem;
        letter-spacing: 15px;
        margin-bottom: 0.8rem;
        animation: float 3s ease-in-out infinite;
        position: relative;
        z-index: 1;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
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
    
    .header .flower-tags {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        margin: 1rem 0 0.5rem 0;
        position: relative;
        z-index: 1;
    }
    
    .header .flower-tag {
        display: inline-block;
        font-family: 'Quicksand', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 0.4rem 1.2rem;
        border-radius: 50px;
        background: linear-gradient(135deg, #fce4ec, #f8bbd0);
        color: #880e4f;
        border: 1px solid rgba(233, 30, 99, 0.1);
        transition: all 0.3s ease;
    }
    
    .header .flower-tag:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(233, 30, 99, 0.15);
        background: linear-gradient(135deg, #f8bbd0, #f48fb1);
    }
    
    /* Upload area - lebih modern */
    .upload-area {
        background: rgba(255, 255, 255, 0.92);
        padding: 3.5rem 2rem;
        border-radius: 30px;
        border: 2.5px dashed #e91e63;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 40px rgba(233, 30, 99, 0.06);
        transition: all 0.4s ease;
        margin-bottom: 0rem;
        position: relative;
    }
    
    .upload-area:hover {
        background: rgba(255, 255, 255, 0.97);
        border-color: #c2185b;
        transform: translateY(-5px);
        box-shadow: 0 12px 50px rgba(233, 30, 99, 0.12);
    }
    
    .upload-area .upload-icon {
        font-size: 4rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .upload-area .main-text {
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #4a1942;
        margin: 0.5rem 0 0.3rem 0;
    }
    
    .upload-area .sub-text {
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
        font-size: 1rem;
        color: #6b3a5a;
        margin: 0.3rem 0;
        font-weight: 400;
        opacity: 0.7;
    }
    
    .upload-area .info-text {
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
        font-size: 0.85rem;
        color: #8b5a7a;
        margin-top: 0.5rem;
        font-weight: 400;
        opacity: 0.6;
    }
    
    /* Result box - lebih elegan */
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
    
    .result-box::before {
        content: '';
        position: absolute;
        top: -30%;
        right: -30%;
        width: 60%;
        height: 60%;
        background: radial-gradient(circle, rgba(233, 30, 99, 0.05), transparent 70%);
        border-radius: 50%;
        pointer-events: none;
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
    
    /* Info cards - lebih rapi */
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
    
    .info-card .title-icon {
        font-size: 2rem;
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
    
    /* Probability bars - lebih modern */
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
    
    .prob-card .title-icon {
        font-size: 2rem;
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
    
    .prob-item .bar .fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmerBar 2s infinite;
    }
    
    @keyframes shimmerBar {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .prob-item:nth-child(1) .fill { background: linear-gradient(90deg, #e91e63, #c2185b); }
    .prob-item:nth-child(2) .fill { background: linear-gradient(90deg, #f06292, #e91e63); }
    .prob-item:nth-child(3) .fill { background: linear-gradient(90deg, #ba68c8, #9c27b0); }
    .prob-item:nth-child(4) .fill { background: linear-gradient(90deg, #ffd54f, #ffb300); }
    .prob-item:nth-child(5) .fill { background: linear-gradient(90deg, #4dd0e1, #00acc1); }
    
    .image-preview {
        border-radius: 25px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(233, 30, 99, 0.08);
        border: 3px solid rgba(255, 255, 255, 0.8);
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }
    
    .image-preview:hover {
        transform: scale(1.01);
        box-shadow: 0 15px 50px rgba(233, 30, 99, 0.12);
    }
    
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
    <h1>🌸 Identifikasi Bunga 🌸</h1>
    <div class="subtitle">
        ✨ Upload foto bunga dan dapatkan hasil identifikasi instan! ✨
    </div>
    <div class="subtitle" style="font-size: 0.95rem; opacity: 0.7; margin-top: 0.3rem;">
    </div>
    <div class="flower-tags">
        <span class="flower-tag">🌷 Tulip</span>
        <span class="flower-tag">🌸 Lily</span>
        <span class="flower-tag">🌺 Orchid</span>
        <span class="flower-tag">🌻 Sunflower</span>
        <span class="flower-tag">🪷 Lotus</span>
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
    
    if os.path.exists(model_path):
        try:
            # Coba load dengan custom_objects jika ada
            return tf.keras.models.load_model(model_path, compile=False)
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
        return tf.keras.models.load_model(model_path, compile=False)

model = load_model()
if model is None:
    st.error("❌ Gagal load model")
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
    Preprocess gambar dengan cara yang lebih robust
    """
    # Resize ke 224x224
    img = img.resize((224, 224), Image.Resampling.LANCZOS)
    
    # Convert ke RGB jika perlu
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert ke array
    x = np.array(img, dtype=np.float32)
    
    # Normalisasi yang benar (sesuai dengan training)
    # Biasanya model DenseNet menggunakan normalisasi [0,1] atau [-1,1]
    # Coba kedua cara
    x = x / 255.0  # Normalisasi [0,1]
    
    # Alternatif: jika model dilatih dengan preprocessing lain
    # x = (x - 0.5) / 0.5  # Normalisasi [-1,1]
    
    # Expand dims
    x = np.expand_dims(x, axis=0)
    
    return x

# ============ PREDICTION WITH ENSEMBLE ============
def predict_with_ensemble(model, x, num_augmentations=3):
    """
    Melakukan prediksi dengan augmentasi untuk hasil lebih robust
    """
    predictions = []
    
    # Prediksi original
    pred_original = model.predict(x, verbose=0)
    predictions.append(pred_original)
    
    # Prediksi dengan sedikit augmentasi
    for _ in range(num_augmentations - 1):
        # Tambahkan noise kecil
        noise = np.random.normal(0, 0.01, x.shape).astype(np.float32)
        x_noise = x + noise
        x_noise = np.clip(x_noise, 0, 1)
        pred_noise = model.predict(x_noise, verbose=0)
        predictions.append(pred_noise)
    
    # Rata-rata prediksi
    avg_pred = np.mean(predictions, axis=0)
    return avg_pred

# ============ UPLOAD ============
uploaded = st.file_uploader("", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

if uploaded:
    img = Image.open(uploaded)
    st.image(img, use_column_width=True)
    
    if st.button("🔍 Klasifikasikan!"):
        with st.spinner("⏳ Memproses..."):
            try:
                # Preprocess
                x = preprocess_image(img)
                
                # Prediksi dengan ensemble
                pred = predict_with_ensemble(model, x)
                
                # Ambil hasil
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                akurasi = pred[0][idx] * 100
                
                # Validasi: jika akurasi terlalu rendah, beri peringatan
                if akurasi < 50:
                    st.warning(f"⚠️ Akurasi rendah ({akurasi:.1f}%). Model tidak yakin dengan prediksi ini.")
                
                st.session_state['hasil'] = {
                    'nama': nama,
                    'akurasi': akurasi,
                    'probabilitas': pred[0]
                }
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

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

st.markdown("""
<div class="footer">
    🌸 Selamat mencoba! 🌸
</div>
""", unsafe_allow_html=True)
