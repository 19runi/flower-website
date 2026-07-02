import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re
import time

# Konfigurasi halaman
st.set_page_config(
    page_title="Klasifikasi Bunga",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Kustom untuk desain yang lebih baik
st.markdown("""
    <style>
    /* Animasi gradien untuk header */
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .main-header {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3.5rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0;
    }
    
    .main-header p {
        color: white;
        font-size: 1.2rem;
        opacity: 0.95;
        margin: 0.5rem 0 0 0;
    }
    
    /* Card untuk hasil prediksi */
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-5px);
    }
    
    .result-card .flower-name {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .result-card .confidence {
        font-size: 1.5rem;
        opacity: 0.95;
        margin: 0.5rem 0;
    }
    
    /* Card deskripsi */
    .deskripsi-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    
    .deskripsi-card .latin-name {
        color: #667eea;
        font-style: italic;
        font-size: 1.1rem;
        margin-top: 0.3rem;
    }
    
    .fact-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .fact-item:last-child {
        border-bottom: none;
    }
    
    .fact-icon {
        font-size: 1.5rem;
        min-width: 40px;
    }
    
    /* Upload area */
    .upload-area {
        border: 3px dashed #e0e0e0;
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        background: #fafafa;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #667eea;
        background: #f0f0ff;
    }
    
    /* Progress bar kustom */
    .custom-progress {
        margin: 0.5rem 0;
        padding: 0.3rem 0;
    }
    
    .custom-progress .label {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
        color: #555;
    }
    
    /* Sidebar styling */
    .sidebar-content {
        padding: 0.5rem;
    }
    
    .sidebar-content .info-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Tombol klasifikasi */
    .classify-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .classify-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Gambar preview */
    .image-preview {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Loading spinner */
    .loading-spinner {
        text-align: center;
        padding: 2rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        .result-card .flower-name {
            font-size: 2.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
    <div class="main-header">
        <h1>🌸 Klasifikasi Bunga</h1>
        <p>Upload gambar bunga dan temukan jenisnya dengan teknologi AI</p>
    </div>
""", unsafe_allow_html=True)

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 🌺 Tentang Aplikasi")
    st.markdown("""
    <div class="sidebar-content">
        <div class="info-box">
            <b>Aplikasi ini menggunakan</b><br>
            🤖 Deep Learning (DenseNet121)<br>
            📱 Streamlit Framework
        </div>
        <div class="info-box">
            <b>5 Jenis Bunga:</b><br>
            🌷 Tulip<br>
            🌸 Lily<br>
            🌺 Orchid<br>
            🌻 Sunflower<br>
            🪷 Lotus
        </div>
        <div class="info-box">
            <b>📊 Akurasi:</b><br>
            Model dilatih dengan 2500+ gambar
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("💡 **Tips:** Upload gambar dengan latar belakang bersih untuk hasil terbaik")

# ============ MAIN CONTENT ============
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Upload Gambar")
    
    # Upload area dengan styling
    uploaded = st.file_uploader(
        "Pilih gambar bunga",
        type=['jpg', 'png', 'jpeg'],
        help="Upload gambar dengan format JPG atau PNG"
    )
    
    if uploaded:
        img = Image.open(uploaded)
        st.markdown('<div class="image-preview">', unsafe_allow_html=True)
        st.image(img, use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tombol klasifikasi dengan styling
        if st.button("🔍 Klasifikasikan!", key="classify", use_container_width=True):
            with st.spinner("🧠 Menganalisis gambar..."):
                time.sleep(0.5)  # Efek loading
                
                # Preprocessing
                img_resized = img.resize((224, 224))
                x = np.array(img_resized) / 255.0
                x = np.expand_dims(x, axis=0)
                
                # Prediksi
                pred = model.predict(x)
                idx = np.argmax(pred[0])
                nama = class_names[idx]
                acc = pred[0][idx] * 100
                
                # Simpan hasil di session state
                st.session_state['prediction'] = {
                    'nama': nama,
                    'akurasi': acc,
                    'probabilitas': pred[0]
                }

with col2:
    # Hasil prediksi
    if 'prediction' in st.session_state:
        pred_data = st.session_state['prediction']
        nama = pred_data['nama']
        acc = pred_data['akurasi']
        prob = pred_data['probabilitas']
        
        # Card hasil
        st.markdown(f"""
        <div class="result-card">
            <p style="font-size:1rem; opacity:0.8; margin:0;">🎯 HASIL KLASIFIKASI</p>
            <p class="flower-name">{nama.upper()}</p>
            <p class="confidence">✨ {acc:.1f}% Akurasi</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Deskripsi bunga
        deskripsi = get_deskripsi_bunga(nama)
        st.markdown("### 📖 Informasi Bunga")
        
        # Parse dan tampilkan deskripsi dengan styling lebih baik
        lines = deskripsi.strip().split('\n')
        if len(lines) > 1:
            # Nama dan latin
            st.markdown(f"""
            <div class="deskripsi-card">
                <h3 style="margin:0; color:#333;">{lines[0].replace('**', '')}</h3>
                <p class="latin-name">{lines[0].split('(')[1].replace(')', '') if '(' in lines[0] else ''}</p>
            """, unsafe_allow_html=True)
            
            # Fakta-fakta
            for line in lines[2:]:
                if line.strip():
                    # Pisahkan ikon dan teks
                    if ' ' in line:
                        icon = line.split(' ')[0] if line.startswith(('🌷', '🌸', '🌺', '🌻', '🪷')) else '🌸'
                        text = line.replace(icon, '').strip()
                        st.markdown(f"""
                        <div class="fact-item">
                            <span class="fact-icon">{icon}</span>
                            <span>{text}</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Probabilitas per kelas
        st.markdown("### 📊 Probabilitas per Kelas")
        for i, name in enumerate(class_names):
            prob_value = prob[i] * 100
            # Warna gradien berdasarkan nilai
            color = f"hsl({int(prob_value * 0.8)}, 70%, 50%)"
            st.markdown(f"""
            <div class="custom-progress">
                <div class="label">
                    <span>{'🌸 ' + name.upper()}</span>
                    <span><b>{prob_value:.1f}%</b></span>
                </div>
                <div style="background:#f0f0f0; border-radius:10px; overflow:hidden; height:10px;">
                    <div style="width:{prob_value}%; height:100%; background:linear-gradient(90deg, #667eea, #764ba2); border-radius:10px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem 0;">
    <p>🌱 Dibuat dengan ❤️ menggunakan Streamlit & TensorFlow</p>
    <p style="font-size: 0.8rem;">© 2026 Klasifikasi Bunga AI</p>
</div>
""", unsafe_allow_html=True)

# ============ FUNGSI DESKRIPSI ============
# (Fungsi get_deskripsi_bunga dan BUNGA_DESKRIPSI sama seperti sebelumnya)
# NOTE: Pertahankan fungsi get_deskripsi_bunga dan dictionary BUNGA_DESKRIPSI dari kode asli

def get_deskripsi_bunga(nama_bunga):
    bunga_info = BUNGA_DESKRIPSI.get(nama_bunga.lower())
    if bunga_info:
        deskripsi = f"\n🌿 **{nama_bunga.upper()}** ({bunga_info['nama_latin']})\n"
        deskripsi += "─" * 55 + "\n"
        for fakta in bunga_info['fakta']:
            deskripsi += f"{fakta}\n"
        return deskripsi
    return f"\n⚠️ Deskripsi untuk {nama_bunga} belum tersedia\n"

# Dictionary BUNGA_DESKRIPSI (sama seperti kode asli)
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

# ============ FUNGSI LOAD MODEL ============
# (Sama seperti kode asli)
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

# Load model
model = load_model()
if model is None:
    st.error("❌ Gagal load model")
    st.stop()
