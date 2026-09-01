# Panduan Penggunaan Program Pengolahan Citra Digital (PCD)

Dokumen ini berisi panduan lengkap untuk menggunakan dua program pengolahan citra digital berbasis Python: **`processinglib.py`** dan **`processingbmp.py`**.

---

## 📋 Fitur Utama

kedua skrip menyediakan fitur-fitur pengolahan citra sebagai berikut:

1. **Visualisasi Histogram**:
   * **1 Garis Grafik (Hitam)**: Untuk citra jenis Grayscale (8-bit).
   * **3 Garis Grafik (Merah, Hijau, Biru)**: Untuk citra jenis True Color / RGB (24-bit).
   * **Deteksi Citra Identik**: Otomatis mengecek dan menampilkan status apakah histogram citra hasil transformasi identik dengan citra asli.
2. **Operasi Titik (Point Operations)**:
   * **Modifikasi Kecerahan (Brightness)**: Menambah/mengurangi nilai kecerahan piksel.
   * **Peningkatkan Kontras**: Mengubah rentang kontras citra dengan faktor pengali.
   * **Negasi / Inversi Citra**: Mengubah piksel citra menjadi warna kebalikannya.
   * **Konversi Ruang Warna**: Mengubah citra dari RGB ke Grayscale atau Grayscale ke RGB.
   * **Pengambangan (Thresholding)**: Mengubah citra menjadi citra biner (hitam-putih mutlak) berdasarkan nilai ambang $T$.
3. **Navigasi CLI Interaktif**: Memilih gambar dan jenis operasi titik melalui menu berbasis angka yang sederhana.

---

## 🛠️ Persiapan Sebelum Menjalankan

### 1. Struktur Folder
Pastikan direktori proyek Anda memiliki struktur seperti berikut:
```text
Tugas 2/
├── img/                       <-- Letakkan berkas gambar uji di sini
│   ├── contoh_gambar.jpg
│   └── contoh_gambar.bmp
├── processinglib.py
└── processingbmp.py
```

### 2. Berkas Citra Uji
Letakkan file citra yang ingin diuji ke dalam folder **`img/`**.
* **`processinglib.py`**: Mendukung format `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`, `.tiff`.
* **`processingbmp.py`**: Khusus format `.bmp` (8-bit Grayscale & 24-bit RGB).

### 3. Requirement Library
Jalankan perintah berikut di terminal untuk menginstal dependensi yang dibutuhkan:
```bash
pip install numpy matplotlib pillow
```

---

## 🚀 Cara Menjalankan Program

### 1. Menggunakan `processinglib.py` (Berbasis Library)

Program ini memanfaatkan library modern (`Pillow`, `NumPy`, `Matplotlib`) untuk pemrosesan citra dengan cepat dan mendukung berbagai format berkas gambar.

**Perintah Terminal:**
```bash
python processinglib.py
```

---

### 2. Menggunakan `processingbmp.py` (Manual BMP Parser)

Program ini dibangun secara eksplisit untuk membaca struktur berkas BMP biner (header & data piksel) secara manual menggunakan modul bawaan Python `struct` tanpa bantuan library pengolah gambar.

**Perintah Terminal:**
```bash
python processingbmp.py
```

---

## 🎮 Alur Navigasi Program

Saat program dijalankan, ikuti langkah-langkah navigasi interaktif berikut:

### Langkah 1: Pilih Gambar
Program akan menampilkan daftar berkas gambar yang tersedia di folder `img/`:
```text
=== DAFTAR GAMBAR TERSEDIA ===
[1] citra_input.jpg
[2] citra_input_rgb.bmp

Pilih nomor gambar (0 untuk keluar): 1
```

### Langkah 2: Pilih Operasi Titik
Setelah gambar dimuat, menu operasi titik akan ditampilkan:
```text
=== MENU OPERASI TITIK ===
[1] Tampilkan Histogram Citra Asli Saja
[2] Modifikasi Brightness
[3] Tingkatkan / Ubah Kontras
[4] Negasi / Inversi Citra
[5] Konversi Ruang Warna (RGB <-> Grayscale)
[6] Thresholding (Pengambangan)
[0] Keluar

Pilih operasi: 2
```

### Langkah 3: Masukkan Parameter (Jika Memilih Operasi 2, 3, atau 6)
* **Brightness**: Masukkan nilai pergeseran intensitas (-255 s.d. 255), contoh: `50` (terang) atau `-40` (gelap).
* **Kontras**: Masukkan faktor pengali (misal: `1.5` untuk meningkatkan kontras, `0.7` untuk menurunkan).
* **Thresholding**: Masukkan nilai ambang batas $T$ (0-255), contoh: `128`.

---

## 📊 Hasil Visualisasi (Matplotlib)

Setelah operasi dipilih, jendela grafik akan menampilkan **4 panel visualisasi**:

| Panel Kiri Atas | Panel Kanan Atas |
| :---: | :---: |
| Tampilan **Citra Asli** | Tampilan **Hasil Transformasi** |

| Panel Kiri Bawah | Panel Kanan Bawah |
| :---: | :---: |
| Grafik **Histogram Citra Asli** | Grafik **Histogram Hasil Transformasi** <br> *(Disertai Status `IDENTIK (Citra Sama)` / `TIDAK IDENTIK`)* |

> **Catatan Pengeluaran**: Tutup jendela visualisasi Matplotlib untuk kembali ke menu CLI interaktif.
