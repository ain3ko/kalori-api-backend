# main.py

# 1. Import library yang kita butuhkan
from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
from PIL import Image
import io
from typing import List, Dict, Any

# 2. Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="API Deteksi Kalori Makanan",
    description="API ini menerima gambar makanan dan mengembalikan hasil deteksi beserta estimasi kalori.",
    version="0.1.0",
)

# 3. Muat Model YOLO saat aplikasi dimulai
# Model dimuat di sini (di luar fungsi endpoint) agar hanya dimuat sekali
# saat aplikasi pertama kali berjalan. Ini membuat respons API jauh lebih cepat.
try:
    model = YOLO("best.pt")
    print("Model AI berhasil dimuat.")
except Exception as e:
    print(f"Error memuat model: {e}")
    model = None

# 4. Data Kalori Makanan
# Kamus ini berisi informasi kalori per 100 gram.
data_kalori = {
    'Ayam Goreng': {'kalori_per_100g': 245},
    'Ikan Goreng': {'kalori_per_100g': 198},
    'Mie Goreng': {'kalori_per_100g': 150},
    'Nasi Goreng': {'kalori_per_100g': 170},
    'Nasi Putih': {'kalori_per_100g': 130},
    'Rendang Sapi': {'kalori_per_100g': 195},
    'Tahu Goreng': {'kalori_per_100g': 115},
    'TelurGoreng': {'kalori_per_100g': 190},
    'Tempe Goreng': {'kalori_per_100g': 192},
    'Terong Balado': {'kalori_per_100g': 90},
    'Tumis Kangkung': {'kalori_per_100g': 45},
}

# 5. Definisikan endpoint utama (Root Endpoint) - tidak ada perubahan
@app.get("/")
def read_root() -> Dict[str, str]:
    """Endpoint utama yang memberikan pesan selamat datang."""
    return {"message": "Selamat datang di API Deteksi Kalori! Endpoint untuk prediksi ada di /predict/"}


# 6. Definisikan endpoint untuk prediksi (Prediction Endpoint) - LOGIKA BARU
@app.post("/predict/")
async def create_upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Menerima sebuah file gambar, memprosesnya dengan model YOLOv8,
    dan mengembalikan hasil deteksi beserta estimasi kalori dalam format JSON.
    """
    if not model:
        return {"error": "Model tidak berhasil dimuat, tidak dapat melakukan prediksi."}
    
    # Baca data gambar dari file yang diunggah
    image_bytes = await file.read()
    
    # Buka gambar menggunakan PIL (Python Imaging Library)
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        return {"error": f"File yang diunggah bukan format gambar yang valid: {e}"}

    # Lakukan prediksi dengan model
    results = model.predict(image, conf=0.4)
    result = results[0]

    # Siapkan list untuk menampung hasil deteksi
    detections = []
    total_kalori = 0

    # Loop melalui setiap objek yang terdeteksi
    for box in result.boxes:
        class_id = int(box.cls[0])
        nama_kelas = model.names[class_id]
        confidence = float(box.conf[0])
        
        # Cari info kalori
        kalori_info = data_kalori.get(nama_kelas, {}).get('kalori_per_100g')
        if kalori_info:
            total_kalori += kalori_info

        # Tambahkan hasil deteksi ke dalam list
        detections.append({
            "label": nama_kelas,
            "confidence": round(confidence, 2),
            "kalori_per_100g": kalori_info
        })
        
    # Siapkan respons akhir dalam format JSON
    response = {
        "sukses": True,
        "deteksi": detections,
        "total_estimasi_kalori": total_kalori
    }
    
    return response