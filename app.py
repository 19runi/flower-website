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
    except Exception as e:
        st.error(f"❌ Model tidak ditemukan! Pastikan file 'model_bunga_densenet121.h5' ada di folder yang sama.")
        st.error(f"Detail error: {str(e)}")
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
            '🌻 Bunga matahari muda mengikuti pergerakan matahari (heliotropisme)',
            '🌻 Kepala bunga matahari terdiri dari ribuan bunga kecil (bunga majemuk)',
            '🌻 Bunga matahari adalah bunga nasional Ukraina'
        ]
    },
    'lotus': {
        'nama_latin': 'Nelumbo nucifera',
        'fakta': [
            '🪷 Teratai dapat bertahan hidup hingga 1.000 tahun dalam kondisi kering',
            '🪷 Bunga teratai suci dalam agama Buddha dan Hindu',
            '🪷 Meskipun tumbuh di air berlumpur, daun teratai tetap bersih (efek lotus)',
            '🪷 Biji teratai dapat berkecambah setelah 1.300 tahun'
        ]
    }
}

# ============================================
# 4. FUNGSI PREDIKSI
# ============================================
def preprocess_image(img_file):
    """Pra-proses gambar untuk prediksi"""
    try:
        # Load gambar
        img = Image.open(img_file)
        
        # Konversi ke RGB jika gambar grayscale atau RGBA
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize sesuai input model
        img = img.resize((224, 224))
        
        # Konversi ke array dan normalisasi
        img_array = np.array(img) / 255.0
        
        # Tambahkan batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array, img
        
    except Exception as e:
        st.error(f"Error dalam preprocessing gambar: {str(e)}")
        return None, None

def predict_flower(model, img_file):
    """Fungsi untuk memprediksi jenis bunga dari gambar"""
    try:
        # Pra-proses gambar
        img_array, original_img = preprocess_image(img_file)
        if img_array is None:
            return None, None, None
        
        # Prediksi
        with st.spinner('⏳ Menganalisis gambar dengan model...'):
            predictions = model.predict(img_array)
        
        # Dapatkan kelas dengan probabilitas tertinggi
        predicted_idx = np.argmax(predictions[0])
        predicted_class = class_names[predicted_idx]
        confidence = float(np.max(predictions[0]) * 100)
        
        # Hitung probabilitas semua kelas
        prob_dict = {}
        for i, name in enumerate(class_names):
            prob_dict[name] = float(predictions[0][i] * 100)
        
        return predicted_class, confidence, prob_dict, original_img
        
    except Exception as e:
        st.error(f"Error dalam prediksi: {str(e)}")
        return None, None, None, None

def display_prediction_result(predicted_class, confidence, prob_dict):
    """Menampilkan hasil prediksi dengan styling yang lebih baik"""
    
    # Tentukan warna berdasarkan confidence
    if confidence >= 80:
        status_color = "green"
        status_emoji = "🎉"
    elif confidence >= 60:
        status_color = "orange"
        status_emoji = "😊"
    else:
        status_color = "red"
        status_emoji = "🤔"
    
    # ========== HASIL PREDIKSI ==========
    st.markdown("---")
    st.subheader("🎯 Hasil Klasifikasi")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f"""
        <div style='
            background-color: #e8f5e9; 
            padding: 20px; 
            border-radius: 10px;
            border-left: 5px solid #4caf50;
        '>
            <h3 style='margin:0;'>{status_emoji} {predicted_class.upper()}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Tingkat Keyakinan", f"{confidence:.2f}%", 
                 delta="High" if confidence >= 80 else "Medium" if confidence >= 60 else "Low")
    
    # ========== FAKTA MENARIK ==========
    st.markdown("---")
    st.subheader("📖 Fakta Menarik")
    
    bunga_info = BUNGA_DESKRIPSI.get(predicted_class)
    if bunga_info:
        st.markdown(f"**Nama Latin:** _{bunga_info['nama_latin']}_")
        for fakta in bunga_info['fakta']:
            st.write(fakta)
    
    # ========== PROBABILITAS ==========
    st.markdown("---")
    st.subheader("📊 Distribusi Probabilitas per Kelas")
    
    # Urutkan probabilitas dari tertinggi ke terendah
    sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
    
    # Tampilkan progress bar untuk setiap kelas
    for name, prob in sorted_probs:
        col1, col2, col3 = st.columns([1.5, 3, 1])
        with col1:
            # Tandai yang merupakan prediksi utama
            if name == predicted_class:
                st.markdown(f"**👉 {name.capitalize()}**")
            else:
                st.write(f"{name.capitalize()}")
        
        with col2:
            # Progress bar dengan warna berbeda
            if name == predicted_class:
                st.progress(int(prob) / 100, text=f"{prob:.1f}%")
            else:
                st.progress(int(prob) / 100)
        
        with col3:
            st.write(f"{prob:.1f}%")

# ============================================
# 5. TAMPILAN WEBSITE
# ============================================
def main():
    # ========== HEADER ==========
    st.title("🌸 Klasifikasi Jenis Bunga")
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; 
        border-radius: 10px; 
        margin-bottom: 20px;
        color: white;
    '>
        <p style='font-size: 16px; margin: 0;'>
        📱 Upload gambar bunga dan sistem akan mengidentifikasi jenisnya 
        menggunakan teknologi <b>Deep Learning</b>!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== LOAD MODEL ==========
    model = load_model()
    if model is None:
        st.stop()
    
    # ========== UPLOAD FILE ==========
    uploaded_file = st.file_uploader(
        "📤 Pilih gambar bunga...",
        type=['jpg', 'jpeg', 'png'],
        help="Upload gambar bunga yang ingin diklasifikasi (format: JPG, JPEG, PNG)"
    )
    
    # ========== SESSION STATE ==========
    # Inisialisasi session state untuk menyimpan hasil prediksi
    if 'prediction_done' not in st.session_state:
        st.session_state.prediction_done = False
        st.session_state.predicted_class = None
        st.session_state.confidence = None
        st.session_state.prob_dict = None
        st.session_state.original_img = None
    
    # ========== PROSES GAMBAR ==========
    if uploaded_file is not None:
        # Tampilkan gambar yang diupload
        col1, col2 = st.columns([1, 1])
        
        with col1:
            img_display = Image.open(uploaded_file)
            st.image(img_display, caption="📷 Gambar yang diupload", use_column_width=True)
        
        with col2:
            # Tombol prediksi dengan callback
            if st.button("🔍 Klasifikasi!", type="primary", use_container_width=True):
                # Reset state
                st.session_state.prediction_done = False
                
                # Lakukan prediksi
                predicted_class, confidence, prob_dict, original_img = predict_flower(
                    model, uploaded_file
                )
                
                if predicted_class is not None:
                    # Simpan ke session state
                    st.session_state.prediction_done = True
                    st.session_state.predicted_class = predicted_class
                    st.session_state.confidence = confidence
                    st.session_state.prob_dict = prob_dict
                    st.session_state.original_img = original_img
                    st.rerun()
        
        # ========== TAMPILKAN HASIL ==========
        if st.session_state.prediction_done:
            display_prediction_result(
                st.session_state.predicted_class,
                st.session_state.confidence,
                st.session_state.prob_dict
            )
            
            # Tombol reset untuk prediksi baru
            if st.button("🔄 Reset dan Prediksi Ulang", use_container_width=True):
                st.session_state.prediction_done = False
                st.session_state.predicted_class = None
                st.session_state.confidence = None
                st.session_state.prob_dict = None
                st.rerun()
    
    else:
        # Tampilkan informasi jika belum upload gambar
        st.info("📌 Silakan upload gambar bunga terlebih dahulu untuk memulai klasifikasi.")
        
        # Tampilkan contoh bunga yang bisa diklasifikasi
        st.markdown("""
        <div style='
            background-color: #f0f2f6; 
            padding: 15px; 
            border-radius: 10px;
            margin-top: 20px;
        '>
            <p style='margin: 0; text-align: center;'>
            🌸 Jenis bunga yang dapat diklasifikasi: 
            <b>Tulip</b>, <b>Lily</b>, <b>Orchid</b>, <b>Sunflower</b>, dan <b>Lotus</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ========== FOOTER ==========
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
    <p>Made with ❤️ using DenseNet121 Transfer Learning</p>
    <p style='font-size: 12px;'>Versi 2.0 - Perbaikan Logika</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 6. RUN APLIKASI
# ============================================
if __name__ == "__main__":
    main()
