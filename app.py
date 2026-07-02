import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import gdown
import os

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
    
    url = f'https://drive.google.com/uc?id={FILE_ID}'
    
    # Cek apakah model sudah ada
    if not os.path.exists(model_path):
        with st.spinner('⏳ Mengunduh model dari Google Drive...'):
            try:
                gdown.download(url, model_path, quiet=False)
                st.success('✅ Model berhasil diunduh!')
            except Exception as e:
                st.error(f'❌ Gagal mengunduh model: {e}')
                return None
    
    # Load model
    try:
        model = tf.keras.models.load_model(model_path)
        return model
    except Exception as e:
        st.error(f'❌ Gagal memuat model: {e}')
        return None

# ... (sisa kode sama seperti sebelumnya)