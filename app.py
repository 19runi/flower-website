import numpy as np
from google.colab import files
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
import tensorflow as tf

# Dictionary deskripsi bunga
bunga_deskripsi = {
    'lily': {
        'nama_ilmiah': 'Lilium',
        'deskripsi': 'Bunga Lily adalah simbol kemurnian dan keanggunan. Bunga ini memiliki kelopak yang besar dan harum yang mekar di musim panas. Lily tersedia dalam berbagai warna seperti putih, kuning, merah muda, dan oranye. Dalam budaya Tiongkok, Lily dipercaya membawa keberuntungan dan kebahagiaan.',
        'fakta': '🌺 Fakta menarik: Beberapa spesies Lily dapat tumbuh hingga ketinggian 2 meter!'
    },
    'lotus': {
        'nama_ilmiah': 'Nelumbo nucifera',
        'deskripsi': 'Teratai atau Lotus adalah bunga sakral yang tumbuh di air. Bunga ini melambangkan kesucian, kebangkitan spiritual, dan kelahiran kembali dalam berbagai budaya Asia. Lotus memiliki kemampuan unik untuk mekar sempurna di atas air meskipun akarnya tertanam di lumpur.',
        'fakta': '🌺 Fakta menarik: Biji Lotus dapat bertahan hidup hingga 1.300 tahun dan masih bisa tumbuh!'
    },
    'rose': {
        'nama_ilmiah': 'Rosa',
        'deskripsi': 'Mawar adalah ratunya bunga, melambangkan cinta dan romansa. Bunga ini memiliki duri di batangnya sebagai mekanisme pertahanan alami. Mawar tersedia dalam ribuan varietas dan warna, masing-masing dengan makna simbolis yang berbeda.',
        'fakta': '🌺 Fakta menarik: Mawar tertua di dunia berusia 1.000 tahun dan masih tumbuh di Katedral Hildesheim, Jerman!'
    },
    'tulip': {
        'nama_ilmiah': 'Tulipa',
        'deskripsi': 'Tulip adalah bunga musim semi yang berasal dari Asia Tengah. Bunga ini terkenal dengan bentuk cangkirnya yang sempurna dan warna-warna cerah. Tulip menjadi simbol ekonomi saat "Tulip Mania" melanda Belanda pada abad ke-17.',
        'fakta': '🌺 Fakta menarik: Ada lebih dari 3.000 varietas Tulip yang tercatat di dunia!'
    },
    'sunflower': {
        'nama_ilmiah': 'Helianthus annuus',
        'deskripsi': 'Bunga Matahari adalah bunga yang selalu menghadap ke arah matahari (heliotropisme). Bunga ini melambangkan kebahagiaan, kesetiaan, dan umur panjang. Bijinya kaya akan nutrisi dan sering dijadikan camilan sehat.',
        'fakta': '🌺 Fakta menarik: Bunga Matahari dapat tumbuh setinggi 3 meter dan memiliki 1.000-2.000 biji dalam satu kepala bunga!'
    },
    'orchid': {
        'nama_ilmiah': 'Orchidaceae',
        'deskripsi': 'Anggrek adalah salah satu keluarga bunga terbesar di dunia dengan lebih dari 25.000 spesies. Bunga ini melambangkan keindahan, kekuatan, dan kemewahan. Anggrek memiliki kemampuan adaptasi yang luar biasa dan dapat tumbuh di berbagai habitat.',
        'fakta': '🌺 Fakta menarik: Anggrek Vanilla adalah satu-satunya anggrek yang menghasilkan buah yang dapat dimakan!'
    },
    'daisy': {
        'nama_ilmiah': 'Bellis perennis',
        'deskripsi': 'Bunga Aster atau Daisy adalah bunga sederhana yang melambangkan kepolosan dan kesucian. Bunga ini memiliki kelopak putih dengan pusat kuning cerah. Daisy sering digunakan dalam permainan "love me, love me not" dan merupakan simbol persahabatan.',
        'fakta': '🌺 Fakta menarik: Bunga Daisy sebenarnya adalah gabungan dari dua bunga: bunga cakram di tengah dan bunga sinar di tepi!'
    },
    'jasmine': {
        'nama_ilmiah': 'Jasminum',
        'deskripsi': 'Melati adalah bunga yang sangat harum dan melambangkan keanggunan, kemurnian, dan kerendahan hati. Bunga ini sering digunakan dalam ritual pernikahan dan keagamaan di berbagai budaya. Minyak melati digunakan dalam industri parfum dan aromaterapi.',
        'fakta': '🌺 Fakta menarik: Bunga Melati mekar di malam hari dan mengeluarkan aroma yang paling kuat pada waktu itu!'
    }
}

def tampilkan_deskripsi_bunga(nama_bunga):
    """
    Menampilkan deskripsi lengkap tentang bunga yang diprediksi
    """
    nama_bunga_lower = nama_bunga.lower()
    
    # Cari deskripsi berdasarkan kata kunci
    for key, value in bunga_deskripsi.items():
        if key in nama_bunga_lower or nama_bunga_lower in key:
            print("\n" + "="*60)
            print(f"📖 DESKRIPSI BUNGA {nama_bunga.upper()}")
            print("="*60)
            print(f"Nama Ilmiah: {value['nama_ilmiah']}")
            print(f"\n{value['deskripsi']}")
            print(f"\n{value['fakta']}")
            print("="*60 + "\n")
            return
    
    # Jika tidak ditemukan dalam dictionary
    print("\n" + "="*60)
    print(f"📖 TENTANG BUNGA {nama_bunga.upper()}")
    print("="*60)
    print(f"{nama_bunga} adalah bunga yang indah dengan keunikan tersendiri. ")
    print("Setiap bunga memiliki keindahan dan makna yang berbeda dalam berbagai budaya.")
    print("="*60 + "\n")

def prediksi_bunga():
    # Mengunggah gambar
    uploaded = files.upload()

    for fn in uploaded.keys():
        path = fn
        # Memuat gambar dan mengubah ukurannya sesuai input model
        img = image.load_img(path, target_size=(224, 224))

        # Menampilkan gambar yang diunggah
        plt.figure(figsize=(6, 6))
        plt.imshow(img)
        plt.axis('off')
        plt.title('Gambar Bunga yang Diunggah')
        plt.show()

        # Preprocessing gambar
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0  # Normalisasi

        # Melakukan prediksi
        predictions = model.predict(x)
        score = tf.nn.softmax(predictions[0])

        # Mendapatkan index kelas dengan probabilitas tertinggi
        predicted_class_idx = np.argmax(predictions)
        predicted_class = class_names[predicted_class_idx]
        akurasi = np.max(predictions) * 100

        # Menampilkan hasil prediksi
        print("\n" + "="*60)
        print("🌼 HASIL ANALISIS BUNGA 🌼")
        print("="*60)
        print(f"🌸 Nama Bunga: **{predicted_class.upper()}**")
        print(f"📊 Tingkat Akurasi: {akurasi:.2f}%")
        print("="*60)

        # Menampilkan deskripsi bunga
        tampilkan_deskripsi_bunga(predicted_class)

        # Menampilkan top 3 prediksi
        print("\n🏆 3 Prediksi Teratas:")
        top_indices = np.argsort(predictions[0])[-3:][::-1]
        for i, idx in enumerate(top_indices, 1):
            print(f"   {i}. {class_names[idx]}: {predictions[0][idx]*100:.2f}%")

# Jalankan fungsi ini untuk mengetes sistem
prediksi_bunga()
