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

# CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #ffe4e1 0%, #ffd1dc 50%, #ffb6c1 100%);
    }
    
    .css-1d391kg, .css-1lcbmhc, .stSidebar {
        display: none !important;
    }
    
    .stFileUploader > div > div {
        display: none !important;
    }
    
    .stFileUploader > div > div > div {
        display: none !important;
    }
    
    .stFileUploader > div > div > div > div {
        display: none !important;
    }
    
    .stFileUploader > div > div > div > small {
        display: none !important;
    }
    
    .stFileUploader > div > div > div > div > div {
        display: none !important;
    }
    
    .stFileUploader small {
        display: none !important;
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
    
    .stFileUploader > div > button > div {
        display: none !important;
    }
    
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

# ============ HEADER ============
st.markdown("""
<div class="header">
    <div style="font-size: 3.5rem; margin-bottom: 0.3rem; letter-spacing: 10px;">
        🌸 🌺 🌷 🌻 🪷
    </div>
    <h1>Klasifikasi Bunga</h1>
    <p>📸 Upload gambar untuk mengetahui jenis bunganya secara instan</p>
    <span class="badge">🤖 Didukung AI &nbsp;·&nbsp; 5 Jenis Bunga</span>
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
