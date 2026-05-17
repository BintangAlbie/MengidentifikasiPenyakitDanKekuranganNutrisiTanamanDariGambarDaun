# Identifikasi Penyakit & Kekurangan Nutrisi Tanaman dari Gambar Daun

Aplikasi desktop berbasis **Python + PyQt5** dan **OpenCV** untuk mendeteksi penyakit serta kekurangan nutrisi tanaman melalui citra digital daun menggunakan teknik deteksi tepi (Canny, Sobel, Prewitt) dan konvolusi.

## Fitur

- Deteksi tepi Canny, Sobel, dan Prewitt
- Konvolusi kernel kustom
- Identifikasi penyakit berdasarkan kepadatan tepi, simetri, dan fitur morfologi daun
- Pencocokan dengan dataset referensi
- Rekomendasi penanganan otomatis

## Requirements

- Python 3.8+
- pip (Python package manager)

## Cara Setup

1. **Clone repositori**

```bash
git clone https://github.com/BintangAlbie/MengidentifikasiPenyakitDanKekuranganNutrisiTanamanDariGambarDaun.git
cd MengidentifikasiPenyakitDanKekuranganNutrisiTanamanDariGambarDaun
```

2. **Buat virtual environment (disarankan)**

```bash
python -m venv .venv
```

3. **Aktifkan virtual environment**

   - Windows:
   ```bash
   .venv\Scripts\activate
   ```
   - Linux / macOS:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**

```bash
pip install opencv-python numpy pandas PyQt5
```

5. **Siapkan dataset referensi**

Buat folder `dataset/` dan file `dataset/referensi_penyakit.csv` dengan format:

| nama_penyakit | kepadatan_tepi_rendah | kepadatan_tepi_tinggi | rekomendasi |
|--------------|----------------------|----------------------|-------------|

Setiap baris berisi nama penyakit, rentang kepadatan tepi (%), dan rekomendasi penanganan.

*(Folder `dataset/` otomatis diabaikan oleh .gitignore)*

## Menjalankan Aplikasi

**Via run.bat (Windows):**
```bash
run.bat
```

**Secara manual:**
```bash
python main.py
```

Aplikasi akan membuka jendela GUI. Klik **Load** untuk memilih gambar daun, lalu klik **Identifikasi** untuk mendiagnosis.

## Struktur Proyek

```
├── main.py               # GUI utama (PyQt5)
├── konvolusi.py          # Fungsi konvolusi manual
├── identifikasi.py       # Logika identifikasi penyakit
├── main.ui               # File layout Qt Designer
├── run.bat               # Script jalanin aplikasi (Windows)
├── .gitignore
└── README.md
```

## Teknologi

- Python
- PyQt5 (GUI)
- OpenCV (pengolahan citra)
- NumPy (komputasi numerik)
- Pandas (dataset referensi)
