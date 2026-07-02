import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os

# ============================================
# SETUP HALAMAN
# ============================================
st.set_page_config(
    page_title="Klasifikasi Bunga",
    page_icon="🌸",
    layout="centered"
)

st.title("🌸 Klasifikasi Jenis Bunga")
st.write("Upload gambar bunga untuk mengetahui jenisnya!")

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
            '🌷 Warna merah melambangkan cinta, kuning melambangkan kegembiraan',
            '🌷 Pada abad ke-17, Belanda mengalami "Tulip Mania"'
        ]
    },
    'lily': {
        'nama_latin': 'Lilium',
        'fakta': [
            '🌸 Lily adalah bunga tertua, sudah ada sejak 3.000 tahun SM',
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
            '🌺 Satu kapsul anggrek berisi hingga 3 juta biji',
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
            '🪷 Teratai dapat bertahan hidup hingga 1.000 tahun kering',
            '🪷 Bunga teratai suci dalam agama Buddha dan Hindu',
            '🪷 Meskipun tumbuh di air berlumpur, teratai tetap bersih',
            '🪷 Biji teratai dapat berkecambah setelah 1.300 tahun'
        ]
    }
}

# ============================================
# LOAD MODEL
# ============================================
@st.cache_resource
def load_model():
    model_path = 'model_bunga_densenet121.h5'
    
    # Cek apakah model ada
    if not os.path.exists(model_path):
        return None
    
    try:
        model = tf.keras.models.load_model(model_path)
        return model
    except:
        return None

model = load_model()

# ============================================
# UPLOAD MODEL (JIKA BELUM ADA)
# ============================================
if model is None:
    st.warning("⚠️ Model belum tersedia. Silakan upload file model.")
    st.info("📤 Upload file **model_bunga_densenet121.h5** dari komputer kamu.")
    
    uploaded_model = st.file_uploader("Upload model (.h5)", type=['h5'])
    if uploaded_model is not None:
        with open("model_bunga_densenet121.h5", "wb") as f:
            f.write(uploaded_model.getbuffer())
        st.success("✅ Model berhasil diupload!")
        st.rerun()
    st.stop()

# ============================================
# PREDIKSI
# ============================================
uploaded_file = st.file_uploader("📤 Upload gambar bunga", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        img = Image.open(uploaded_file)
        st.image(img, caption="📷 Gambar yang diupload", use_column_width=True)
    
    with col2:
        if st.button("🔍 Klasifikasi!", type="primary", use_container_width=True):
            with st.spinner("⏳ Menganalisis gambar..."):
                # Preprocessing
                img_resized = img.resize((224, 224))
                img_array = np.array(img_resized) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                
                # Prediksi
                predictions = model.predict(img_array)
                predicted_idx = np.argmax(predictions[0])
                predicted_class = class_names[predicted_idx]
                confidence = np.max(predictions[0]) * 100
                
                # Hasil
                st.success(f"✅ **Jenis Bunga**: {predicted_class.upper()}")
                st.info(f"📊 **Keyakinan**: {confidence:.2f}%")
    
    if 'predicted_class' in locals():
        st.markdown("---")
        
        # Fakta
        st.subheader("📖 Fakta Menarik")
        bunga_info = BUNGA_DESKRIPSI.get(predicted_class)
        if bunga_info:
            st.markdown(f"**Nama Latin:** _{bunga_info['nama_latin']}_")
            for fakta in bunga_info['fakta']:
                st.write(fakta)
        
        # Probabilitas
        st.subheader("📈 Probabilitas per Kelas")
        for i, name in enumerate(class_names):
            prob = predictions[0][i] * 100
            col1, col2 = st.columns([2, 3])
            with col1:
                st.write(f"{name.capitalize()}")
            with col2:
                st.progress(int(prob) / 100)
                st.write(f"{prob:.1f}%")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("Made with ❤️ menggunakan DenseNet121")