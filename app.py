import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import requests

# ============================================
# SETUP HALAMAN
# ============================================
st.set_page_config(
    page_title="Klasifikasi Bunga",
    page_icon="🌸",
    layout="centered"
)

# ============================================
# DOWNLOAD MODEL DARI GOOGLE DRIVE
# ============================================
@st.cache_resource
def load_model():
    """Download model dari Google Drive"""
    model_path = 'model_bunga_densenet121.h5'
    
    # FILE ID DARI GOOGLE DRIVE KAMU
    FILE_ID = "12ZJi1HbkI8ian7fWM0K98ADi1tpMvU4y"
    
    # URL download langsung (pakai export=download)
    url = f'https://drive.google.com/uc?export=download&id={FILE_ID}'
    
    # Cek apakah model sudah ada
    if not os.path.exists(model_path):
        with st.spinner('⏳ Mengunduh model dari Google Drive (sekitar 30 MB)...'):
            try:
                # Download pakai requests (lebih stabil dari gdown)
                response = requests.get(url, stream=True)
                
                # Cek apakah ada konfirmasi virus (Google Drive kadang minta konfirmasi)
                if "Virus scan warning" in response.text or "quota" in response.text:
                    # Ambil link konfirmasi
                    import re
                    confirm = re.search(r'confirm=([^&]+)', response.text)
                    if confirm:
                        confirm_token = confirm.group(1)
                        url = f'https://drive.google.com/uc?export=download&confirm={confirm_token}&id={FILE_ID}'
                        response = requests.get(url, stream=True)
                
                # Simpan file
                with open(model_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Cek ukuran file (minimal 1 MB)
                if os.path.getsize(model_path) < 1024 * 1024:
                    os.remove(model_path)
                    st.error('❌ File model corrupt atau tidak valid!')
                    return None
                    
                st.success('✅ Model berhasil diunduh!')
            except Exception as e:
                st.error(f'❌ Gagal mengunduh model: {str(e)}')
                return None
    else:
        # Cek ukuran file yang sudah ada
        if os.path.getsize(model_path) < 1024 * 1024:
            os.remove(model_path)
            st.warning('⚠️ File model corrupt, mengunduh ulang...')
            return load_model()  # Rekursif download ulang
    
    # Load model
    try:
        model = tf.keras.models.load_model(model_path)
        return model
    except Exception as e:
        st.error(f'❌ Gagal memuat model: {str(e)}')
        return None

# ============================================
# DATA BUNGA
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
# FUNGSI PREDIKSI
# ============================================
def predict_flower(model, img_file):
    """Fungsi untuk memprediksi jenis bunga"""
    img = Image.open(img_file)
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    predictions = model.predict(img_array)
    predicted_idx = np.argmax(predictions[0])
    predicted_class = class_names[predicted_idx]
    confidence = np.max(predictions[0]) * 100
    
    prob_dict = {}
    for i, name in enumerate(class_names):
        prob_dict[name] = predictions[0][i] * 100
    
    return predicted_class, confidence, prob_dict

# ============================================
# TAMPILAN WEBSITE
# ============================================
def main():
    # Header
    st.title("🌸 Klasifikasi Jenis Bunga")
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
    <p>Upload gambar bunga dan sistem akan mengidentifikasi jenisnya!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load model
    model = load_model()
    if model is None:
        st.stop()
    
    # Upload file
    uploaded_file = st.file_uploader(
        "📤 Pilih gambar bunga...",
        type=['jpg', 'jpeg', 'png']
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption="📷 Gambar yang diupload", use_column_width=True)
        
        with col2:
            if st.button("🔍 Klasifikasi!", type="primary", use_container_width=True):
                with st.spinner("⏳ Menganalisis gambar..."):
                    predicted_class, confidence, prob_dict = predict_flower(model, uploaded_file)
                    
                    st.success(f"✅ **Jenis Bunga**: {predicted_class.upper()}")
                    st.info(f"📊 **Keyakinan**: {confidence:.2f}%")
        
        if 'predicted_class' in locals():
            st.markdown("---")
            
            # Fakta Menarik
            st.subheader("📖 Fakta Menarik")
            bunga_info = BUNGA_DESKRIPSI.get(predicted_class)
            if bunga_info:
                st.markdown(f"**Nama Latin:** _{bunga_info['nama_latin']}_")
                for fakta in bunga_info['fakta']:
                    st.write(fakta)
            
            # Probabilitas
            st.subheader("📈 Probabilitas per Kelas")
            for name, prob in prob_dict.items():
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.write(f"{name.capitalize()}")
                with col2:
                    st.progress(int(prob) / 100)
                    st.write(f"{prob:.1f}%")
    
    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ menggunakan DenseNet121")

if __name__ == "__main__":
    main()