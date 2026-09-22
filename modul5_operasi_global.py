"""Modul 5: Operasi Global (Global Operations)
============================================
Modul ini memproses citra dengan mempertimbangkan karakteristik statistik
keseluruhan piksel di seluruh area citra melalui histogram:
1. Perhitungan Histogram Citra (Frekuensi Kemunculan Derajat Keabuan).
2. Ekualisasi Histogram (Histogram Equalization) untuk meratakan kontras global.
3. Evaluasi Statistik Citra (Mean, Standar Deviasi Kontras, Min, Max).
4. Visualisasi Grafik Histogram Berbasis Teks/ASCII di Terminal (100% Native, tanpa Matplotlib).

100% Native Python (Pustaka standar Python: math, os).
"""

import math
import os
import sys
from typing import Dict, List, Tuple, Union

# Memastikan direktori modul ini terdaftar di sys.path
DIR_INI = os.path.dirname(os.path.abspath(__file__))
if DIR_INI not in sys.path:
    sys.path.insert(0, DIR_INI)

# Impor representasi matriks dari Modul 1
try:
    from modul1_representasi_citra import (
        CitraMatriks,
        buat_citra_sampel_warna,
        muat_bmp,
        simpan_bmp,
    )
except ImportError:
    from .modul1_representasi_citra import (
        CitraMatriks,
        buat_citra_sampel_warna,
        muat_bmp,
        simpan_bmp,
    )


# ---------------------------------------------------------------------------
# 1. Perhitungan Histogram
# ---------------------------------------------------------------------------

def hitung_histogram(citra: CitraMatriks) -> Dict[str, List[int]]:
    """Menghitung frekuensi kemunculan intensitas piksel [0..255].
    
    Returns:
        Dict berisi:
        - {'gray': [256 integer]} jika mode GRAYSCALE.
        - {'r': [...], 'g': [...], 'b': [...]} jika mode RGB.
    """
    if citra.mode == "GRAYSCALE":
        h_gray = [0] * 256
        for y in range(citra.tinggi):
            for x in range(citra.lebar):
                intensitas = citra.get_pixel(x, y)
                h_gray[intensitas] += 1
        return {"gray": h_gray}
    else:
        h_r = [0] * 256
        h_g = [0] * 256
        h_b = [0] * 256
        for y in range(citra.tinggi):
            for x in range(citra.lebar):
                r, g, b = citra.get_pixel(x, y)
                h_r[r] += 1
                h_g[g] += 1
                h_b[b] += 1
        return {"r": h_r, "g": h_g, "b": h_b}


# ---------------------------------------------------------------------------
# 2. Ekualisasi Histogram (Histogram Equalization)
# ---------------------------------------------------------------------------

def _bangun_tabel_ekualisasi(hist: List[int], total_piksel: int) -> List[int]:
    """Menghitung tabel penelusuran (Lookup Table / LUT) transformasi CDF."""
    # 1. Hitung Cumulative Distribution Function (CDF)
    cdf = [0] * 256
    kumulatif = 0
    for i in range(256):
        kumulatif += hist[i]
        cdf[i] = kumulatif

    # 2. Cari nilai CDF minimum yang bukan nol
    cdf_min = 0
    for val in cdf:
        if val > 0:
            cdf_min = val
            break

    # 3. Buat tabel pemetaan piksel
    # Formula standar: s_k = round( ((CDF(k) - CDF_min) / (total_piksel - CDF_min)) * 255 )
    lut = [0] * 256
    pembagi = total_piksel - cdf_min
    if pembagi <= 0:
        return list(range(256))

    for k in range(256):
        if cdf[k] == 0:
            lut[k] = 0
        else:
            nilai_baru = round(((cdf[k] - cdf_min) / pembagi) * 255)
            lut[k] = max(0, min(255, nilai_baru))

    return lut


def ekualisasi_histogram(citra: CitraMatriks) -> CitraMatriks:
    """Meratakan distribusi derajat keabuan citra menggunakan Ekualisasi Histogram.
    
    Tujuan:
        Meningkatkan kontras global, khususnya pada citra yang terlalu gelap,
        terlalu terang, atau memiliki kontras rendah (distribusi warna menyempit).
    
    Args:
        citra: Objek CitraMatriks (mendukung GRAYSCALE dan RGB).
    
    Returns:
        CitraMatriks baru dengan histogram yang terdistribusi merata.
    """
    total_piksel = citra.lebar * citra.tinggi
    hist_data = hitung_histogram(citra)
    hasil = CitraMatriks(citra.lebar, citra.tinggi, citra.mode)

    if citra.mode == "GRAYSCALE":
        lut = _bangun_tabel_ekualisasi(hist_data["gray"], total_piksel)
        for y in range(citra.tinggi):
            for x in range(citra.lebar):
                lama = citra.get_pixel(x, y)
                hasil.set_pixel(x, y, lut[lama])
    else:
        lut_r = _bangun_tabel_ekualisasi(hist_data["r"], total_piksel)
        lut_g = _bangun_tabel_ekualisasi(hist_data["g"], total_piksel)
        lut_b = _bangun_tabel_ekualisasi(hist_data["b"], total_piksel)
        for y in range(citra.tinggi):
            for x in range(citra.lebar):
                r, g, b = citra.get_pixel(x, y)
                hasil.set_pixel(x, y, (lut_r[r], lut_g[g], lut_b[b]))

    return hasil


# ---------------------------------------------------------------------------
# 3. Evaluasi Statistik Citra
# ---------------------------------------------------------------------------

def evaluasi_statistik(citra: CitraMatriks) -> Dict[str, float]:
    """Menghitung metrik statistik intensitas piksel (Rata-rata, Standar Deviasi, Min, Max).
    
    Standar deviasi merupakan indikator objektif kontras citra:
    semakin tinggi standar deviasi, semakin tinggi kontras citra.
    """
    total_piksel = citra.lebar * citra.tinggi
    if citra.mode == "GRAYSCALE":
        nilai_list = [citra.get_pixel(x, y) for y in range(citra.tinggi) for x in range(citra.lebar)]
    else:
        # Konversi ke intensitas ekuivalen untuk statistik RGB
        nilai_list = [
            round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2])
            for y in range(citra.tinggi)
            for x in range(citra.lebar)
            for p in [citra.get_pixel(x, y)]
        ]

    rata_rata = sum(nilai_list) / total_piksel
    variansi = sum((v - rata_rata) ** 2 for v in nilai_list) / total_piksel
    standar_deviasi = math.sqrt(variansi)

    return {
        "rata_rata_intensitas": round(rata_rata, 2),
        "standar_deviasi_kontras": round(standar_deviasi, 2),
        "intensitas_min": min(nilai_list),
        "intensitas_max": max(nilai_list),
    }


# ---------------------------------------------------------------------------
# 4. Visualisasi Grafik Histogram ASCII (100% Native Terminal Display)
# ---------------------------------------------------------------------------

def tampilkan_histogram_ascii(hist: List[int], judul: str = "HISTOGRAM", tinggi_grafik: int = 10, jumlah_bin: int = 32) -> None:
    """Menggambar grafik histogram langsung pada layar terminal teks menggunakan karakter ASCII/Unicode.
    
    Args:
        hist: List frekuensi [0..255].
        judul: Label judul grafik.
        tinggi_grafik: Ketinggian bar visual dalam jumlah baris.
        jumlah_bin: Jumlah interval pengelompokan tingkat keabuan (default 32 bin).
    """
    bin_size = 256 // jumlah_bin
    kelompok = [0] * jumlah_bin
    for i in range(256):
        b = min(jumlah_bin - 1, i // bin_size)
        kelompok[b] += hist[i]

    puncak = max(kelompok) if max(kelompok) > 0 else 1

    print(f"\n--- {judul} (Puncak: {puncak} piksel) ---")
    # Gambar baris grafik dari atas ke bawah
    for baris in range(tinggi_grafik, 0, -1):
        ambang_garis = (baris / tinggi_grafik) * puncak
        karakter_baris = []
        for jml in kelompok:
            if jml >= ambang_garis:
                karakter_baris.append("#")
            else:
                karakter_baris.append(" ")
        print(f"{int(ambang_garis):5d} | " + "".join(karakter_baris))

    # Garis alas dan sumbu X
    print("      +" + "-" * jumlah_bin)
    print("      0" + " " * (jumlah_bin - 6) + "255 (Tingkat Keabuan)")


# ---------------------------------------------------------------------------
# Generator Citra Kontras Rendah untuk Uji Ekualisasi
# ---------------------------------------------------------------------------

def _buat_citra_kontras_rendah(lebar: int = 100, tinggi: int = 80) -> CitraMatriks:
    """Membuat citra sintetis dengan intensitas yang terkumpul di rentang sempit [90..130]."""
    citra = CitraMatriks(lebar, tinggi, "GRAYSCALE")
    for y in range(tinggi):
        for x in range(lebar):
            # Gradien sempit di sekitar nilai 110
            offset = int(math.sin(x / 10.0) * 15 + math.cos(y / 10.0) * 15)
            nilai = max(80, min(140, 110 + offset))
            citra.set_pixel(x, y, nilai)
    return citra


# ---------------------------------------------------------------------------
# Blok Demonstrasi Mandiri
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print(" DEMONSTRASI MODUL 5: OPERASI GLOBAL (EKUALISASI HISTOGRAM)")
    print("=" * 60)

    folder_output = os.path.join(DIR_INI, "hasil")
    os.makedirs(folder_output, exist_ok=True)

    # 1. Siapkan Citra Kontras Rendah
    print("\n[1] Membuat Citra Uji Berkualitas Kontras Rendah (Piksel Terkumpul di [80..140])...")
    citra_asli = _buat_citra_kontras_rendah(120, 80)
    path_asli = os.path.join(folder_output, "global_sebelum_ekualisasi.bmp")
    simpan_bmp(citra_asli, path_asli)

    # Statistik sebelum ekualisasi
    stat_asli = evaluasi_statistik(citra_asli)
    print("    Statistik Citra Asli:")
    for k, v in stat_asli.items():
        print(f"      - {k}: {v}")

    # Cetak Histogram Asli
    hist_asli = hitung_histogram(citra_asli)["gray"]
    tampilkan_histogram_ascii(hist_asli, judul="HISTOGRAM SEBELUM EKUALISASI", tinggi_grafik=8)

    # 2. Jalankan Ekualisasi Histogram
    print("\n[2] Menjalankan Ekualisasi Histogram...")
    citra_ekual = ekualisasi_histogram(citra_asli)
    path_ekual = os.path.join(folder_output, "global_sesudah_ekualisasi.bmp")
    simpan_bmp(citra_ekual, path_ekual)

    # Statistik sesudah ekualisasi
    stat_ekual = evaluasi_statistik(citra_ekual)
    print("    Statistik Citra Sesudah Ekualisasi:")
    for k, v in stat_ekual.items():
        print(f"      - {k}: {v}")

    # Cetak Histogram Sesudah Ekualisasi
    hist_ekual = hitung_histogram(citra_ekual)["gray"]
    tampilkan_histogram_ascii(hist_ekual, judul="HISTOGRAM SESUDAH EKUALISASI", tinggi_grafik=8)

    # Peningkatan kontras terbukti dengan naiknya rentang dan standar deviasi
    print("\n[3] Analisis Perubahan:")
    print(f"    - Rentang Intensitas: [{stat_asli['intensitas_min']}..{stat_asli['intensitas_max']}] -> [{stat_ekual['intensitas_min']}..{stat_ekual['intensitas_max']}]")
    print(f"    - Standar Deviasi Kontras: {stat_asli['standar_deviasi_kontras']} -> {stat_ekual['standar_deviasi_kontras']} (Meningkat signifikan)")

    print(f"\n[V] Sukses: Berkas BMP hasil tersimpan di {folder_output}!")

