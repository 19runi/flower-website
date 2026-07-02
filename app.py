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
        
        st.success(f"✅ **{nama.upper()}**")
        st.info(f"📊 {acc:.2f}%")
        
        st.write("Probabilitas:")
        for i, name in enumerate(class_names):
            st.progress(int(pred[0][i]*100)/100)
            st.write(f"{name}: {pred[0][i]*100:.1f}%")