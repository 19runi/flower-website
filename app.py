import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os

st.set_page_config(page_title="Klasifikasi Bunga", page_icon="🌸")

# ============================================
# 1. DATA BUNGA
# ============================================
class_names = ['tulip', 'lily', 'orchid', 'sunflower', 'lotus']

# ============================================
# 2. COBA LOAD MODEL (TANPA DOWNLOAD DULU)
# ============================================
@st.cache_resource
def load_model():
    try:
        model = tf.keras.models.load_model('model_bunga_densenet121.h5')
        return model
    except:
        return None

model = load_model()

# ============================================
# 3. TAMPILAN
# ============================================
st.title("🌸 Klasifikasi Jenis Bunga")

if model is None:
    st.warning("⚠️ Model belum tersedia. Silakan upload file model dulu.")
    st.info("📤 Upload file model_bunga_densenet121.h5 di bagian bawah")
    
    uploaded_model = st.file_uploader("Upload model (.h5)", type=['h5'])
    if uploaded_model is not None:
        with open("model_bunga_densenet121.h5", "wb") as f:
            f.write(uploaded_model.getbuffer())
        st.success("✅ Model berhasil diupload!")
        st.rerun()
    st.stop()

# Upload gambar
uploaded_file = st.file_uploader("📤 Upload gambar bunga", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Gambar yang diupload", use_column_width=True)
    
    if st.button("🔍 Klasifikasi!"):
        img_resized = img.resize((224, 224))
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = model.predict(img_array)
        predicted_idx = np.argmax(predictions[0])
        predicted_class = class_names[predicted_idx]
        confidence = np.max(predictions[0]) * 100
        
        st.success(f"✅ **Jenis Bunga**: {predicted_class.upper()}")
        st.info(f"📊 **Keyakinan**: {confidence:.2f}%")
        
        # Tampilkan semua probabilitas
        st.subheader("📈 Probabilitas per Kelas")
        for i, name in enumerate(class_names):
            prob = predictions[0][i] * 100
            st.progress(int(prob) / 100)
            st.write(f"{name.capitalize()}: {prob:.1f}%")