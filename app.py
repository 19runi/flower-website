import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

st.set_page_config(page_title="Klasifikasi Bunga", page_icon="🌸")

st.title("🌸 Klasifikasi Jenis Bunga")
st.write("Upload gambar bunga untuk mengetahui jenisnya!")

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
        deskripsi = f"\n🌿 **{nama_bunga.upper()}** ({bunga_info['nama_latin']})\n"
        deskripsi += "─" * 55 + "\n"
        for fakta in bunga_info['fakta']:
            deskripsi += f"{fakta}\n"
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

uploaded = st.file_uploader("Upload gambar bunga", type=['jpg','png','jpeg'])
if uploaded:
    img = Image.open(uploaded)
    st.image(img, use_column_width=True)
    
    if st.button("Klasifikasi!"):
        img = img.resize((224,224))
        x = np.array(img) / 255.0
        x = np.expand_dims(x, axis=0)
        
        pred = model.predict(x)
        idx = np.argmax(pred[0])
        nama = class_names[idx]
        acc = pred[0][idx] * 100
        
        # Hasil prediksi
        st.success(f"✅ **{nama.upper()}**")
        st.info(f"📊 {acc:.2f}%")
        
        # ============ TAMPILKAN DESKRIPSI ============
        deskripsi = get_deskripsi_bunga(nama)
        st.markdown(deskripsi)
        # =============================================
        
        # Probabilitas per kelas
        st.write("**Probabilitas per Kelas:**")
        for i, name in enumerate(class_names):
            prob = pred[0][i] * 100
            st.progress(int(prob) / 100)
            st.write(f"{name}: {prob:.1f}%")
