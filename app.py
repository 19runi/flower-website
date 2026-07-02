# ============================================
# WEBSITE KLASIFIKASI BUNGA DENGAN STREAMLIT
# ============================================

import streamlit as st
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os

# ============================================
# 1. SETUP HALAMAN
# ============================================
st.set_page_config(
    page_title="Klasifikasi Bunga",
    page_icon="🌸",
    layout="centered"
)

# ============================================
# 2. LOAD MODEL
# ============================================
@st.cache_resource
def load_model():
    """Memuat model yang sudah dilatih"""
    try:
        model = tf.keras.models.load_model('model_bunga_densenet121.h5')
        return model
    except:
        st.error("❌ Model tidak ditemukan! Pastikan file 'model_bunga_densenet121.h5' ada di folder yang sama.")
        return None

# ============================================
# 3. DATA BUNGA
# ============================================
class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']

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

# ============================================
# 4. FUNGSI PREDIKSI
# ============================================
def predict_flower(model, img_file):
    """Fungsi untuk memprediksi jenis bunga dari gambar"""
    # Load dan resize gambar
    img = Image.open(img_file)
    img = img.resize((224, 224))
    
    # Konversi ke array
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Prediksi
    predictions = model.predict(img_array)
    predicted_idx = np.argmax(predictions)
    predicted_class = class_names[predicted_idx]
    confidence = np.max(predictions) * 100
    
    # Probabilitas semua kelas
    prob_dict = {}
    for i, name in enumerate(class_names):
        prob_dict[name] = predictions[0][i] * 100
    
    return predicted_class, confidence, prob_dict

# ============================================
# 5. TAMPILAN WEBSITE
# ============================================
def main():
    # Header
    st.title("🌸 Klasifikasi Jenis Bunga")
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
    <p style='font-size: 16px;'>
    Upload gambar bunga dan sistem akan mengidentifikasi jenisnya dengan teknologi <b>Deep Learning</b>!
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load model
    model = load_model()
    if model is None:
        st.stop()
    
    # Upload file
    uploaded_file = st.file_uploader(
        "📤 Pilih gambar bunga...",
        type=['jpg', 'jpeg', 'png'],
        help="Upload gambar bunga yang ingin diklasifikasi"
    )
    
    if uploaded_file is not None:
        # Buat columns untuk layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Tampilkan gambar
            st.image(uploaded_file, caption="📷 Gambar yang diupload", use_column_width=True)
        
        with col2:
            # Tombol prediksi
            if st.button("🔍 Klasifikasi!", type="primary", use_container_width=True):
                with st.spinner("⏳ Menganalisis gambar..."):
                    # Lakukan prediksi
                    predicted_class, confidence, prob_dict = predict_flower(model, uploaded_file)
                    
                    # Tampilkan hasil
                    st.success(f"✅ **Jenis Bunga**: {predicted_class.upper()}")
                    st.info(f"📊 **Tingkat Keyakinan**: {confidence:.2f}%")
        
        # Tampilkan detail setelah prediksi
        if 'predicted_class' in locals():
            st.markdown("---")
            
            # ========== FAKTA MENARIK ==========
            st.subheader("📖 Fakta Menarik")
            bunga_info = BUNGA_DESKRIPSI.get(predicted_class)
            if bunga_info:
                st.markdown(f"**Nama Latin:** _{bunga_info['nama_latin']}_")
                for fakta in bunga_info['fakta']:
                    st.write(fakta)
            
            # ========== PROBABILITAS ==========
            st.subheader("📈 Probabilitas per Kelas")
            
            # Buat progress bar untuk setiap kelas
            for name, prob in prob_dict.items():
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.write(f"{name.capitalize()}")
                with col2:
                    # Progress bar
                    st.progress(int(prob) / 100)
                with col3:
                    st.write(f"{prob:.1f}%")
    
    # ========== FOOTER ==========
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
    <p>Made with ❤️ menggunakan DenseNet121 Transfer Learning</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 6. RUN APLIKASI
# ============================================
if __name__ == "__main__":
    main()
