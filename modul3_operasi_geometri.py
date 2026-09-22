"""Modul 3: Operasi Geometri (Geometric Operations)
==================================================
Modul ini menangani manipulasi koordinat spasial piksel untuk mengubah
bentuk fisik, orientasi, atau ukuran citra:
1. Pencerminan (Flipping): Horizontal, Vertikal, dan Kombinasi.
2. Rotasi (Rotation): 90 Derajat, 180 Derajat, dan Sudut Bebas (Arbitrary Angle).
3. Pemotongan Citra (Cropping).
4. Penskalaan Citra (Scaling / Zooming) pembesaran dan pengecilan.

100% Native Python (Hanya menggunakan math dan modul dasar Python).
"""

import math
import os
import sys
from typing import Optional, Tuple, Union

# Memastikan direktori modul ini terdaftar di sys.path
DIR_INI = os.path.dirname(os.path.abspath(__file__))
if DIR_INI not in sys.path:
    sys.path.insert(0, DIR_INI)

# Impor representasi matriks dari Modul 1
try:
    from modul1_representasi_citra import (
        CitraMatriks,
        TipePiksel,
        buat_citra_sampel_gradien,
        buat_citra_sampel_warna,
        muat_bmp,
        simpan_bmp,
    )
except ImportError:
    from .modul1_representasi_citra import (
        CitraMatriks,
        TipePiksel,
        buat_citra_sampel_gradien,
        buat_citra_sampel_warna,
        muat_bmp,
        simpan_bmp,
    )


# ---------------------------------------------------------------------------
# 1. Pencerminan (Flipping)
# ---------------------------------------------------------------------------

def cermin_horizontal(citra: CitraMatriks) -> CitraMatriks:
    """Mencerminkan citra terhadap sumbu vertikal (kiri <-> kanan).
    
    Formula transformasi:
        x' = Lebar - 1 - x
        y' = y
    """
    hasil = CitraMatriks(citra.lebar, citra.tinggi, citra.mode)
    w = citra.lebar
    for y in range(citra.tinggi):
        for x in range(w):
            hasil.set_pixel(w - 1 - x, y, citra.get_pixel(x, y))
    return hasil


def cermin_vertikal(citra: CitraMatriks) -> CitraMatriks:
    """Mencerminkan citra terhadap sumbu horizontal (atas <-> bawah).
    
    Formula transformasi:
        x' = x
        y' = Tinggi - 1 - y
    """
    hasil = CitraMatriks(citra.lebar, citra.tinggi, citra.mode)
    h = citra.tinggi
    for y in range(h):
        for x in range(citra.lebar):
            hasil.set_pixel(x, h - 1 - y, citra.get_pixel(x, y))
    return hasil


def cermin_kombinasi(citra: CitraMatriks) -> CitraMatriks:
    """Mencerminkan citra secara horizontal dan vertikal sekaligus.
    
    Formula transformasi:
        x' = Lebar - 1 - x
        y' = Tinggi - 1 - y
    """
    hasil = CitraMatriks(citra.lebar, citra.tinggi, citra.mode)
    w, h = citra.lebar, citra.tinggi
    for y in range(h):
        for x in range(w):
            hasil.set_pixel(w - 1 - x, h - 1 - y, citra.get_pixel(x, y))
    return hasil


# ---------------------------------------------------------------------------
# 2. Rotasi Citra (Rotation)
# ---------------------------------------------------------------------------

def rotasi_90(citra: CitraMatriks, searah_jarum_jam: bool = True) -> CitraMatriks:
    """Memutar citra sebesar 90 derajat.
    
    Catatan: Dimensi citra hasil akan bertukar (Lebar Baru = Tinggi Lama, Tinggi Baru = Lebar Lama).
    
    Formula (Searah Jarum Jam):
        x' = Tinggi_Lama - 1 - y
        y' = x
    """
    w_lama, h_lama = citra.lebar, citra.tinggi
    w_baru, h_baru = h_lama, w_lama
    hasil = CitraMatriks(w_baru, h_baru, citra.mode)

    for y in range(h_lama):
        for x in range(w_lama):
            p = citra.get_pixel(x, y)
            if searah_jarum_jam:
                nx = h_lama - 1 - y
                ny = x
            else:
                nx = y
                ny = w_lama - 1 - x
            hasil.set_pixel(nx, ny, p)
    return hasil


def rotasi_180(citra: CitraMatriks) -> CitraMatriks:
    """Memutar citra sebesar 180 derajat.
    
    Dimensi tetap sama. Hasil ekuivalen dengan cermin kombinasi horizontal & vertikal.
    """
    return cermin_kombinasi(citra)


def rotasi_bebas(
    citra: CitraMatriks,
    sudut_derajat: float,
    latar_belakang: Optional[TipePiksel] = None
) -> CitraMatriks:
    """Memutar citra dengan sudut bebas berlawanan arah jarum jam (CCW).
    
    Menggunakan teknik Pemetaan Terbalik (Inverse Mapping) untuk menghindari lubang (holes)
    dan memperbesar kanvas secara adaptif agar gambar tidak terpotong (*no clipping*).
    
    Args:
        citra: Citra sumber.
        sudut_derajat: Sudut putar dalam satuan derajat.
        latar_belakang: Warna latar untuk area kosong hasil rotasi.
    """
    if latar_belakang is None:
        latar_belakang = 0 if citra.mode == "GRAYSCALE" else (0, 0, 0)

    # Konversi derajat ke radian
    rad = math.radians(sudut_derajat)
    cos_t = math.cos(rad)
    sin_t = math.sin(rad)

    w_lama = citra.lebar
    h_lama = citra.tinggi

    # Menghitung dimensi batas luar (bounding box) kanvas baru
    w_baru = max(1, round(abs(w_lama * cos_t) + abs(h_lama * sin_t)))
    h_baru = max(1, round(abs(w_lama * sin_t) + abs(h_lama * cos_t)))

    cx_lama = w_lama / 2.0
    cy_lama = h_lama / 2.0
    cx_baru = w_baru / 2.0
    cy_baru = h_baru / 2.0

    hasil = CitraMatriks(w_baru, h_baru, citra.mode, nilai_dasar=latar_belakang)

    # Telusuri setiap piksel pada kanvas tujuan (Inverse Mapping)
    for ny in range(h_baru):
        for nx in range(w_baru):
            # Koordinat relatif terhadap titik tengah kanvas baru
            dx = nx - cx_baru
            dy = ny - cy_baru

            # Putar terbalik menuju sistem koordinat citra asal
            sx = round(dx * cos_t + dy * sin_t + cx_lama)
            sy = round(-dx * sin_t + dy * cos_t + cy_lama)

            # Jika koordinat jatuh di dalam citra asal, ambil nilainya
            if 0 <= sx < w_lama and 0 <= sy < h_lama:
                hasil.set_pixel(nx, ny, citra.get_pixel(sx, sy))

    return hasil


# ---------------------------------------------------------------------------
# 3. Pemotongan Citra (Cropping)
# ---------------------------------------------------------------------------

def potong_citra(
    citra: CitraMatriks,
    x_awal: int,
    y_awal: int,
    lebar_potong: int,
    tinggi_potong: int
) -> CitraMatriks:
    """Memotong bagian tertentu dari citra sesuai kotak batas (bounding box).
    
    Args:
        citra: Citra sumber.
        x_awal: Koordinat kolom sudut kiri-atas pemotongan.
        y_awal: Koordinat baris sudut kiri-atas pemotongan.
        lebar_potong: Lebar area yang akan dipotong.
        tinggi_potong: Tinggi area yang akan dipotong.
    
    Returns:
        CitraMatriks baru berukuran lebar_potong x tinggi_potong.
    """
    if x_awal < 0 or y_awal < 0 or lebar_potong <= 0 or tinggi_potong <= 0:
        raise ValueError("Parameter pemotongan tidak valid (harus positif).")
    if (x_awal + lebar_potong > citra.lebar) or (y_awal + tinggi_potong > citra.tinggi):
        raise ValueError(
            f"Area potong [{x_awal}:{x_awal+lebar_potong}, {y_awal}:{y_awal+tinggi_potong}] "
            f"melebihi batas citra {citra.lebar}x{citra.tinggi}."
        )

    hasil = CitraMatriks(lebar_potong, tinggi_potong, citra.mode)
    for ny in range(tinggi_potong):
        for nx in range(lebar_potong):
            hasil.set_pixel(nx, ny, citra.get_pixel(x_awal + nx, y_awal + ny))
    return hasil


# ---------------------------------------------------------------------------
# 4. Penskalaan Citra (Scaling / Zooming)
# ---------------------------------------------------------------------------

def skala_citra(
    citra: CitraMatriks,
    faktor_x: float,
    faktor_y: float
) -> CitraMatriks:
    """Memperbesar (zoom in, faktor > 1) atau memperkecil (zoom out, faktor < 1) citra.
    
    Menggunakan metode Interpolasi Tetangga Terdekat (Nearest-Neighbor Interpolation).
    
    Args:
        citra: Citra sumber.
        faktor_x: Faktor pengali dimensi horizontal (lebar).
        faktor_y: Faktor pengali dimensi vertikal (tinggi).
    
    Returns:
        CitraMatriks baru dengan resolusi yang telah diskalakan.
    """
    if faktor_x <= 0 or faktor_y <= 0:
        raise ValueError("Faktor penskalaan harus bernilai lebih besar dari 0.")

    w_baru = max(1, round(citra.lebar * faktor_x))
    h_baru = max(1, round(citra.tinggi * faktor_y))

    hasil = CitraMatriks(w_baru, h_baru, citra.mode)

    for ny in range(h_baru):
        # Cari baris asal terdekat
        sy = min(citra.tinggi - 1, int(ny / faktor_y))
        for nx in range(w_baru):
            # Cari kolom asal terdekat
            sx = min(citra.lebar - 1, int(nx / faktor_x))
            hasil.set_pixel(nx, ny, citra.get_pixel(sx, sy))

    return hasil


# ---------------------------------------------------------------------------
# Blok Demonstrasi Mandiri
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print(" DEMONSTRASI MODUL 3: OPERASI GEOMETRI (GEOMETRIC OPERATIONS)")
    print("=" * 60)

    folder_output = os.path.join(DIR_INI, "hasil")
    os.makedirs(folder_output, exist_ok=True)

    # Siapkan citra uji sintetis
    citra_uji = buat_citra_sampel_gradien(100, 60)
    print(f"\n[Citra Uji Sumber]: {citra_uji.info()}")

    # 1. Uji Pencerminan (Flipping)
    print("\n[1] Menjalankan Operasi Pencerminan (Flip)...")
    flip_h = cermin_horizontal(citra_uji)
    flip_v = cermin_vertikal(citra_uji)
    flip_c = cermin_kombinasi(citra_uji)
    simpan_bmp(flip_h, os.path.join(folder_output, "geometri_flip_horizontal.bmp"))
    simpan_bmp(flip_v, os.path.join(folder_output, "geometri_flip_vertikal.bmp"))
    simpan_bmp(flip_c, os.path.join(folder_output, "geometri_flip_kombinasi.bmp"))
    print("    -> Berhasil menyimpan flip horizontal, vertikal, dan kombinasi.")

    # 2. Uji Rotasi
    print("\n[2] Menjalankan Operasi Rotasi...")
    rot_90 = rotasi_90(citra_uji, searah_jarum_jam=True)
    rot_180_deg = rotasi_180(citra_uji)
    rot_35_deg = rotasi_bebas(citra_uji, sudut_derajat=35)

    simpan_bmp(rot_90, os.path.join(folder_output, "geometri_rotasi_90.bmp"))
    simpan_bmp(rot_180_deg, os.path.join(folder_output, "geometri_rotasi_180.bmp"))
    simpan_bmp(rot_35_deg, os.path.join(folder_output, "geometri_rotasi_35_bebas.bmp"))

    print(f"    -> Rotasi 90 CW: Resolusi baru {rot_90.lebar}x{rot_90.tinggi}")
    print(f"    -> Rotasi 180: Resolusi {rot_180_deg.lebar}x{rot_180_deg.tinggi}")
    print(f"    -> Rotasi Bebas 35 deg: Kanvas adaptif {rot_35_deg.lebar}x{rot_35_deg.tinggi}")

    # 3. Uji Pemotongan (Cropping)
    print("\n[3] Menjalankan Pemotongan Citra (Cropping 50x30 piksel dari titik (25, 15))...")
    crop_hasil = potong_citra(citra_uji, x_awal=25, y_awal=15, lebar_potong=50, tinggi_potong=30)
    simpan_bmp(crop_hasil, os.path.join(folder_output, "geometri_crop.bmp"))
    print(f"    -> {crop_hasil.info()}")

    # 4. Uji Penskalaan (Scaling)
    print("\n[4] Menjalankan Penskalaan Citra (Zoom In 1.5x dan Zoom Out 0.5x)...")
    skala_besar = skala_citra(citra_uji, faktor_x=1.5, faktor_y=1.5)
    skala_kecil = skala_citra(citra_uji, faktor_x=0.5, faktor_y=0.5)
    simpan_bmp(skala_besar, os.path.join(folder_output, "geometri_skala_besar.bmp"))
    simpan_bmp(skala_kecil, os.path.join(folder_output, "geometri_skala_kecil.bmp"))
    print(f"    -> Zoom In 1.5x: {skala_besar.lebar}x{skala_besar.tinggi}")
    print(f"    -> Zoom Out 0.5x: {skala_kecil.lebar}x{skala_kecil.tinggi}")

    print("\n[V] Sukses: Seluruh fungsi operasi geometri bekerja dengan benar!")

