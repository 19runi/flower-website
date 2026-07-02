import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests
import re

# ============================================
# SETUP HALAMAN
# ============================================
st.set_page_config(
    page_title="Klasifikasi Bunga",
    page_icon="🌸",
    layout="centered"
)

st.title("🌸 Klasifikasi Jenis Bunga")
st.markdown("Upload gambar bunga dan sistem akan mengidentifikasi jenisnya!")

# ============================================
# DATA BUNGA
# ============================================
class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']

BUNGA_DESKRIPSI = {
    'tulip': {
        'nama_latin': 'Tulipa',
        'fakta': [
            '🌷 Tulip berasal dari Asia Tengah dan menjadi simbol nasional Belanda',
            '🌷 Ada lebih dari 3.000 varietas tulip',
            '🌷 Warna merah melambangkan cinta, kuning melambangkan kegembiraan'
        ]
    },
    'lily': {
        'nama_latin': 'Lilium',
        'fakta': [
            '🌸 Lily adalah bunga tertua, sudah ada sejak 3.000 tahun SM',
            '🌸 Bunga lily memiliki 6 kelopak dan melambangkan kemurnian',
            '🌸 Beberapa spesies lily dapat tumbuh hingga 2,5 meter'
        ]
    },
    'orchid': {
        'nama_latin': 'Orchidaceae',
        'fakta': [
            '🌺 Anggrek memiliki lebih dari 28.000 spesies',
            '🌺 Anggrek dapat ditemukan di setiap benua kecuali Antartika',
            '🌺 Beberapa spesies anggrek dapat hidup hingga 100 tahun'
        ]
    },
    'sunflower': {
        'nama_latin': 'Helianthus annuus',
        'fakta': [
            '🌻 Bunga matahari dapat tumbuh hingga 3 meter lebih',
            '🌻 Bunga matahari muda mengikuti pergerakan matahari',
            '🌻 Bunga matahari adalah bunga nasional Ukraina'
        ]
    },
    'lotus': {
        'nama_latin': 'Nelumbo nucifera',
        'fakta': [
            '🪷 Teratai dapat bertahan hidup hingga 1.000 tahun dalam kondisi kering',
            '🪷 Bunga teratai suci dalam agama Buddha dan Hindu',
            '🪷 Biji teratai dapat berkecambah setelah 1.300 tahun'
        ]
    }
}

# ============================================
# LOAD MODEL DARI GOOGLE DRIVE
# ============================================
@st.cache_resource
def load_model():
    model_path = 'model_bunga_densenet121.h5'
    file_id = "12ZJi1HbkI8ian7fWM0K98ADi1tpMvU4y"
    
    if os.path.exists(model_path):
        try:
            model = tf.keras.models.load_model(model_path)
            return model
        except:
            os.remove(model_path)
    
    with st.spinner('⏳ Mengunduh model (30 MB)...'):
        try:
            url = f'https://drive.google.com/uc?export=download&id={file_id}'
            response = requests.get(url, stream=True)
            
            if 'confirm' in response.text:
                confirm = re.search(r'confirm=([^&]+)', response.text)
                if confirm:
                    url = f'https://drive.google.com/uc?export=download&confirm={confirm.group(1)}&id={file_id}'
                    response = requests.get(url, stream=True)
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if os.path.getsize(model_path) < 1000000:
                os.remove(model_path)
                st.error('❌ File model corrupt!')
                return None
            
            st.success('✅ Model berhasil diunduh!')
            model = tf.keras.models.load_model(model_path)
            return model
            
        except Exception as e:
            st.error(f'❌ Gagal download: {str(e)}')
            return None

# ============================================
# MAIN APP
# ============================================
model = load_model()

if model is None:
    st.warning("⚠️ Gagal memuat model. Pastikan file model ada di Google Drive.")
    st.stop()

uploaded_file = st.file_uploader("📤 Upload gambar bunga", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        img = Image.open(uploaded_file)
        st.image(img, caption="📷 Gambar yang diupload", use_column_width=True)
    
    with col2:
        if st.button("🔍 Klasifikasi!", type="primary", use_container_width=True):
            with st.spinner("⏳ Menganalisis..."):
                img_resized = img.resize((224, 224))
                img_array = np.array(img_resized) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                
                predictions = model.predict(img_array)
                predicted_idx = np.argmax(predictions[0])
                predicted_class = class_names[predicted_idx]
                confidence = np.max(predictions[0]) * 100
                
                st.success(f"✅ **Jenis Bunga**: {predicted_class.upper()}")
                st.info(f"📊 **Keyakinan**: {confidence:.2f}%")
    
    if 'predicted_class' in locals():
        st.markdown("---")
        
        st.subheader("📖 Fakta Menarik")
        bunga_info = BUNGA_DESKRIPSI.get(predicted_class)
        if bunga_info:
            st.markdown(f"**Nama Latin:** _{bunga_info['nama_latin']}_")
            for fakta in bunga_info['fakta']:
                st.write(fakta)
        
        st.subheader("📈 Probabilitas per Kelas")
        for i, name in enumerate(class_names):
            prob = predictions[0][i] * 100
            st.progress(int(prob) / 100)
            st.write(f"{name.capitalize()}: {prob:.1f}%")

st.markdown("---")
st.markdown("Made with ❤️ menggunakan DenseNet121")
