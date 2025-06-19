# Menggunakan base image Python versi 3.11 yang ringan
FROM python:3.11-slim

# Menetapkan direktori kerja di dalam kontainer
WORKDIR /app

# Menyalin file requirements terlebih dahulu untuk caching yang efisien
COPY requirements.txt .

# Menginstal semua library yang dibutuhkan
# --no-cache-dir untuk menjaga ukuran image tetap kecil
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin semua sisa file proyek (main.py, best.pt, dll) ke dalam direktori kerja
COPY . .

# Memberitahu Docker bahwa kontainer akan berjalan pada port 10000
EXPOSE 10000

# Perintah yang akan dijalankan saat kontainer dimulai
# Menjalankan server Uvicorn agar bisa diakses dari luar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]