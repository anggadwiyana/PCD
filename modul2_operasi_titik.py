"""Modul 2: Operasi Titik (Point Operations)
===========================================
Modul ini menangani pemrosesan citra di mana nilai keluaran setiap piksel
hanya ditentukan oleh nilai intensitas piksel itu sendiri secara independen:
1. Modifikasi kecemerlangan (Brightness Modification)
2. Peningkatan kontras (Contrast Enhancement)
3. Negasi citra (Inversion / Negative)
4. Konversi warna True Color (RGB) ke Derajat Keabuan (Grayscale)
5. Pengambangan (Thresholding) biner tunggal dan ganda (band thresholding)

100% Native Python (Tanpa NumPy / Pillow / OpenCV / Matplotlib).
"""

import os
import sys
from typing import Tuple, Union

# Memastikan direktori modul ini terdaftar di sys.path
DIR_INI = os.path.dirname(os.path.abspath(__file__))
if DIR_INI not in sys.path:
    sys.path.insert(0, DIR_INI)

# Impor representasi matriks dari Modul 1
try:
    from modul1_representasi_citra import (
        CitraMatriks,
        buat_citra_sampel_gradien,
        buat_citra_sampel_warna,
        muat_bmp,
        simpan_bmp,
    )
except ImportError:
    from .modul1_representasi_citra import (
        CitraMatriks,
        buat_citra_sampel_gradien,
        buat_citra_sampel_warna,
        muat_bmp,
        simpan_bmp,
    )


def jepit(nilai: Union[int, float], batas_bawah: int = 0, batas_atas: int = 255) -> int:
    """Membatasi nilai intensitas agar berada dalam rentang valid [0, 255]."""
    return max(batas_bawah, min(batas_atas, round(nilai)))


# ---------------------------------------------------------------------------
# 1. Modifikasi Kecemerlangan (Brightness Modification)
# ---------------------------------------------------------------------------

def ubah_kecerahan(citra: CitraMatriks, nilai_offset: int) -> CitraMatriks:
    """Mengubah tingkat kecerahan citra dengan menambahkan nilai offset konstan C.
    
    Formula:
        Ko = clamp(Ki + C, 0, 255)
    
    Args:
        citra: Objek CitraMatriks sumber.
        nilai_offset: Nilai penambahan/pengurangan intensitas (positif = terang, negatif = gelap).
    
    Returns:
        CitraMatriks baru hasil penyesuaian kecerahan.
    """
    hasil = CitraMatriks(citra.lebar, citra.tinggi, citra.mode)
    for y in range(citra.tinggi):
        for x in range(citra.lebar):
            p = citra.get_pixel(x, y)
            if citra.mode == "GRAYSCALE":
                hasil.set_pixel(x, y, jepit(p + nilai_offset))
            else:
                r, g, b = p
                hasil.set_pixel(x, y, (
                    jepit(r + nilai_offset),
                    jepit(g + nilai_offset),
                    jepit(b + nilai_offset)
                ))
    return hasil


# ---------------------------------------------------------------------------
# 2. Peningkatan Kontras (Contrast Enhancement)
# ---------------------------------------------------------------------------

def tingkatkan_kontras(citra: CitraMatriks, faktor_gain: float, titik_poros: int = 128) -> CitraMatriks:
    """Meningkatkan atau meregangkan kontras citra terhadap titik poros tertentu.
    
    Formula:
        Ko = clamp(G * (Ki - P) + P, 0, 255)
    
    Args:
        citra: Objek CitraMatriks sumber.
        faktor_gain: Faktor pengali kontras (G > 1 meningkatkan kontras, G < 1 menurunkan kontras).
        titik_poros: Nilai referensi tengah (P), default 128 (titik tengah 8-bit).
    
    Returns:
        CitraMatriks baru hasil penyesuaian kontras.
    """
    hasil = CitraMatriks(citra.lebar, citra.tinggi, citra.mode)
    for y in range(citra.tinggi):
        for x in range(citra.lebar):
            p = citra.get_pixel(x, y)
            if citra.mode == "GRAYSCALE":
                baru = jepit(faktor_gain * (p - titik_poros) + titik_poros)
                hasil.set_pixel(x, y, baru)
            else:
                r, g, b = p
                hasil.set_pixel(x, y, (
                    jepit(faktor_gain * (r - titik_poros) + titik_poros),
                    jepit(faktor_gain * (g - titik_poros) + titik_poros),
                    jepit(faktor_gain * (b - titik_poros) + titik_poros)
                ))
    return hasil


# ---------------------------------------------------------------------------
# 3. Negasi Citra (Inversion / Negative)
# ---------------------------------------------------------------------------

def negasi_citra(citra: CitraMatriks) -> CitraMatriks:
    """Membalik nilai intensitas citra menghasilkan efek film negatif.
    
    Formula:
        Ko = 255 - Ki
    
    Args:
        citra: Objek CitraMatriks sumber.
    
    Returns:
        CitraMatriks baru dengan intensitas terbalik.
    """
    hasil = CitraMatriks(citra.lebar, citra.tinggi, citra.mode)
    for y in range(citra.tinggi):
        for x in range(citra.lebar):
            p = citra.get_pixel(x, y)
            if citra.mode == "GRAYSCALE":
                hasil.set_pixel(x, y, 255 - p)
            else:
                r, g, b = p
                hasil.set_pixel(x, y, (255 - r, 255 - g, 255 - b))
    return hasil


# ---------------------------------------------------------------------------
# 4. Konversi True Color (RGB) ke Grayscale
# ---------------------------------------------------------------------------

def konversi_keabuan(citra: CitraMatriks, metode: str = "luminance") -> CitraMatriks:
    """Mengonversi citra berwarna (RGB) ke citra derajat keabuan (GRAYSCALE).
    
    Metode yang didukung:
    - 'luminance': Pembobotan perseptual mata manusia (0.299*R + 0.587*G + 0.114*B).
    - 'average': Rata-rata aritmetika ketiga kanal ((R + G + B) / 3).
    
    Args:
        citra: Objek CitraMatriks sumber (bila sudah GRAYSCALE, akan diduplikasi).
        metode: 'luminance' atau 'average'.
    
    Returns:
        CitraMatriks dengan mode "GRAYSCALE".
    """
    if citra.mode == "GRAYSCALE":
        return citra.salin()

    hasil = CitraMatriks(citra.lebar, citra.tinggi, "GRAYSCALE")
    for y in range(citra.tinggi):
        for x in range(citra.lebar):
            r, g, b = citra.get_pixel(x, y)
            if metode == "luminance":
                abu = jepit(0.299 * r + 0.587 * g + 0.114 * b)
            elif metode == "average":
                abu = jepit((r + g + b) / 3.0)
            else:
                raise ValueError(f"Metode konversi '{metode}' tidak dikenal. Pilih 'luminance' atau 'average'.")
            hasil.set_pixel(x, y, abu)
    return hasil


# ---------------------------------------------------------------------------
# 5. Pengambangan (Thresholding)
# ---------------------------------------------------------------------------

def pengambangan_tunggal(citra: CitraMatriks, ambang: int = 128) -> CitraMatriks:
    """Binarisasi citra menggunakan satu nilai ambang (single thresholding).
    
    Formula:
        Ko = 255 jika Ki >= Ambang, selain itu 0.
    
    Args:
        citra: Objek CitraMatriks (jika RGB, otomatis dikonversi ke grayscale dulu).
        ambang: Nilai batas pemisah antara latar depan dan latar belakang [0..255].
    
    Returns:
        CitraMatriks biner (mode GRAYSCALE bernilai 0 atau 255).
    """
    citra_gray = citra if citra.mode == "GRAYSCALE" else konversi_keabuan(citra)
    hasil = CitraMatriks(citra_gray.lebar, citra_gray.tinggi, "GRAYSCALE")

    for y in range(citra_gray.tinggi):
        for x in range(citra_gray.lebar):
            intensitas = citra_gray.get_pixel(x, y)
            biner = 255 if intensitas >= ambang else 0
            hasil.set_pixel(x, y, biner)
    return hasil


def pengambangan_ganda(citra: CitraMatriks, ambang_bawah: int = 85, ambang_atas: int = 170) -> CitraMatriks:
    """Segmentasi citra menggunakan dua nilai ambang (band / double thresholding).
    
    Formula:
        Ko = 255 jika Ambang_Bawah <= Ki <= Ambang_Atas, selain itu 0.
    
    Args:
        citra: Objek CitraMatriks.
        ambang_bawah: Batas bawah rentang intensitas.
        ambang_atas: Batas atas rentang intensitas.
    
    Returns:
        CitraMatriks biner tersegmentasi (mode GRAYSCALE bernilai 0 atau 255).
    """
    citra_gray = citra if citra.mode == "GRAYSCALE" else konversi_keabuan(citra)
    hasil = CitraMatriks(citra_gray.lebar, citra_gray.tinggi, "GRAYSCALE")

    for y in range(citra_gray.tinggi):
        for x in range(citra_gray.lebar):
            intensitas = citra_gray.get_pixel(x, y)
            biner = 255 if (ambang_bawah <= intensitas <= ambang_atas) else 0
            hasil.set_pixel(x, y, biner)
    return hasil


# ---------------------------------------------------------------------------
# Blok Demonstrasi Mandiri
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print(" DEMONSTRASI MODUL 2: OPERASI TITIK (POINT OPERATIONS)")
    print("=" * 60)

    folder_output = os.path.join(DIR_INI, "hasil")
    os.makedirs(folder_output, exist_ok=True)

    # 1. Siapkan Citra Sumber
    citra_uji_gray = buat_citra_sampel_gradien(100, 60)
    citra_uji_rgb = buat_citra_sampel_warna(100, 60)

    print(f"\n[Citra Uji]")
    print(f"  - Grayscale: {citra_uji_gray.info()}")
    print(f"  - RGB Warna: {citra_uji_rgb.info()}")

    # 2. Uji Operasi Brightness
    print("\n[1] Menjalankan Modifikasi Kecerahan (Brightness +40 dan -40)...")
    terang = ubah_kecerahan(citra_uji_gray, 40)
    gelap = ubah_kecerahan(citra_uji_gray, -40)
    simpan_bmp(terang, os.path.join(folder_output, "titik_brightness_terang.bmp"))
    simpan_bmp(gelap, os.path.join(folder_output, "titik_brightness_gelap.bmp"))
    print(f"    Piksel (50, 30) Asli: {citra_uji_gray.get_pixel(50, 30)} -> Terang: {terang.get_pixel(50, 30)}, Gelap: {gelap.get_pixel(50, 30)}")

    # 3. Uji Operasi Kontras
    print("\n[2] Menjalankan Peningkatan Kontras (Gain = 1.8)...")
    kontras = tingkatkan_kontras(citra_uji_gray, faktor_gain=1.8, titik_poros=128)
    simpan_bmp(kontras, os.path.join(folder_output, "titik_kontras_tinggi.bmp"))
    print(f"    Piksel (20, 20) Asli: {citra_uji_gray.get_pixel(20, 20)} -> Kontras: {kontras.get_pixel(20, 20)}")

    # 4. Uji Negasi
    print("\n[3] Menjalankan Negasi Citra...")
    negatif = negasi_citra(citra_uji_gray)
    simpan_bmp(negatif, os.path.join(folder_output, "titik_negasi.bmp"))
    print(f"    Piksel (50, 30) Asli: {citra_uji_gray.get_pixel(50, 30)} -> Negasi: {negatif.get_pixel(50, 30)}")

    # 5. Uji Konversi True Color ke Grayscale
    print("\n[4] Menjalankan Konversi Warna RGB ke Grayscale (Luminance & Average)...")
    abu_luminance = konversi_keabuan(citra_uji_rgb, metode="luminance")
    abu_average = konversi_keabuan(citra_uji_rgb, metode="average")
    simpan_bmp(abu_luminance, os.path.join(folder_output, "titik_grayscale_luminance.bmp"))
    simpan_bmp(abu_average, os.path.join(folder_output, "titik_grayscale_average.bmp"))
    piksel_warna = citra_uji_rgb.get_pixel(30, 10)
    print(f"    Piksel RGB Asli: {piksel_warna} -> Luminance: {abu_luminance.get_pixel(30, 10)}, Average: {abu_average.get_pixel(30, 10)}")

    # 6. Uji Thresholding (Tunggal & Ganda)
    print("\n[5] Menjalankan Pengambangan (Thresholding Tunggal & Ganda)...")
    biner_tunggal = pengambangan_tunggal(citra_uji_gray, ambang=128)
    biner_ganda = pengambangan_ganda(citra_uji_gray, ambang_bawah=80, ambang_atas=180)
    simpan_bmp(biner_tunggal, os.path.join(folder_output, "titik_threshold_tunggal.bmp"))
    simpan_bmp(biner_ganda, os.path.join(folder_output, "titik_threshold_ganda.bmp"))
    print(f"    Threshold Tunggal Ambang 128 -> Nilai unik hasil: {sorted(list(set(biner_tunggal.matriks[0])))}")
    print(f"    Threshold Ganda [80..180] -> Nilai unik hasil: {sorted(list(set(biner_ganda.matriks[0])))}")

    print("\n[V] Sukses: Seluruh fungsi operasi titik berjalan 100% lancar dan berkas hasil tersimpan!")

