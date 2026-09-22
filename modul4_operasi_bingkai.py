"""Modul 4: Operasi Berbasis Bingkai (Frame / Multi-Image Operations)
==================================================================
Modul ini memproses kombinasi piksel dari dua atau lebih citra pada koordinat
spasial yang bersesuaian (pixel-by-pixel multi-image operations):
1. Penggabungan Citra Berbobot (Image Blending / Overlay)
2. Deteksi Pergerakan (Motion Detection via Frame Differencing)
3. Operasi Logika Citra Biner (AND, OR, XOR, SUB, dan NOT)

100% Native Python (Tanpa ketergantungan library eksternal).
"""

import os
import sys
from typing import Optional, Tuple

# Memastikan direktori modul ini terdaftar di sys.path
DIR_INI = os.path.dirname(os.path.abspath(__file__))
if DIR_INI not in sys.path:
    sys.path.insert(0, DIR_INI)

# Impor representasi matriks dan operasi titik
try:
    from modul1_representasi_citra import (
        CitraMatriks,
        TipePiksel,
        buat_citra_sampel_gradien,
        muat_bmp,
        simpan_bmp,
    )
    from modul2_operasi_titik import konversi_keabuan, pengambangan_tunggal
except ImportError:
    from .modul1_representasi_citra import (
        CitraMatriks,
        TipePiksel,
        buat_citra_sampel_gradien,
        muat_bmp,
        simpan_bmp,
    )
    from .modul2_operasi_titik import konversi_keabuan, pengambangan_tunggal


def jepit(nilai: float, bawah: int = 0, atas: int = 255) -> int:
    """Membatasi nilai ke rentang [0, 255]."""
    return max(bawah, min(atas, round(nilai)))


def _selaraskan_kanvas(citra_a: CitraMatriks, citra_b: CitraMatriks):
    """Menghitung kanvas gabungan dan offset posisi agar citra yang lebih kecil
    dipusatkan (centered) di atas kanvas citra yang lebih besar.
    """
    w_kanvas = max(citra_a.lebar, citra_b.lebar)
    h_kanvas = max(citra_a.tinggi, citra_b.tinggi)

    offset_ax = (w_kanvas - citra_a.lebar) // 2
    offset_ay = (h_kanvas - citra_a.tinggi) // 2

    offset_bx = (w_kanvas - citra_b.lebar) // 2
    offset_by = (h_kanvas - citra_b.tinggi) // 2

    return w_kanvas, h_kanvas, offset_ax, offset_ay, offset_bx, offset_by


# ---------------------------------------------------------------------------
# 1. Penggabungan Citra (Image Blending)
# ---------------------------------------------------------------------------

def gabung_citra(
    citra_a: CitraMatriks,
    citra_b: CitraMatriks,
    bobot_a: float = 0.5
) -> CitraMatriks:
    """Menggabungkan (overlay) dua citra dengan bobot linier:
    
    Formula:
        C(x, y) = wa * A(x, y) + wb * B(x, y), di mana wb = 1.0 - wa
    
    Args:
        citra_a: Citra pertama (A).
        citra_b: Citra kedua (B).
        bobot_a: Proporsi kontribusi citra A [0.0 .. 1.0].
    
    Returns:
        CitraMatriks hasil perpaduan citra.
    """
    if not (0.0 <= bobot_a <= 1.0):
        raise ValueError("Nilai bobot_a harus berada di antara rentang 0.0 sampai 1.0.")

    bobot_b = 1.0 - bobot_a

    # Samakan mode jika berbeda (ke Grayscale)
    mode_target = "RGB" if (citra_a.mode == "RGB" or citra_b.mode == "RGB") else "GRAYSCALE"
    a = citra_a if citra_a.mode == mode_target else (
        citra_a if mode_target == "GRAYSCALE" else _rgb_kan(citra_a)
    )
    b = citra_b if citra_b.mode == mode_target else (
        citra_b if mode_target == "GRAYSCALE" else _rgb_kan(citra_b)
    )

    kw, kh, oax, oay, obx, oby = _selaraskan_kanvas(a, b)
    hasil = CitraMatriks(kw, kh, mode_target)

    for y in range(kh):
        for x in range(kw):
            # Cek keberadaan piksel citra A
            ax, ay = x - oax, y - oay
            piksel_a = a.get_pixel(ax, ay) if (0 <= ax < a.lebar and 0 <= ay < a.tinggi) else None

            # Cek keberadaan piksel citra B
            bx, by = x - obx, y - oby
            piksel_b = b.get_pixel(bx, by) if (0 <= bx < b.lebar and 0 <= by < b.tinggi) else None

            if piksel_a is not None and piksel_b is not None:
                # Koordinat bertumpuk: lakukan blending berbobot
                if mode_target == "GRAYSCALE":
                    campur = jepit(bobot_a * piksel_a + bobot_b * piksel_b)
                    hasil.set_pixel(x, y, campur)
                else:
                    hasil.set_pixel(x, y, (
                        jepit(bobot_a * piksel_a[0] + bobot_b * piksel_b[0]),
                        jepit(bobot_a * piksel_a[1] + bobot_b * piksel_b[1]),
                        jepit(bobot_a * piksel_a[2] + bobot_b * piksel_b[2])
                    ))
            elif piksel_a is not None:
                hasil.set_pixel(x, y, piksel_a)
            elif piksel_b is not None:
                hasil.set_pixel(x, y, piksel_b)

    return hasil


def _rgb_kan(citra_gray: CitraMatriks) -> CitraMatriks:
    """Mengubah citra grayscale ke citra 3 kanal RGB identik."""
    hasil = CitraMatriks(citra_gray.lebar, citra_gray.tinggi, "RGB")
    for y in range(citra_gray.tinggi):
        for x in range(citra_gray.lebar):
            val = citra_gray.get_pixel(x, y)
            hasil.set_pixel(x, y, (val, val, val))
    return hasil


# ---------------------------------------------------------------------------
# 2. Deteksi Gerakan (Motion Detection via Frame Differencing)
# ---------------------------------------------------------------------------

def deteksi_gerakan(
    frame_awal: CitraMatriks,
    frame_lanjut: CitraMatriks,
    ambang_gerak: int = 30
) -> Tuple[CitraMatriks, CitraMatriks]:
    """Mendeteksi pergerakan objek antara dua frame berurutan menggunakan pengurangan citra.
    
    Formula:
        Selisih(x, y) = |Frame_Awal(x, y) - Frame_Lanjut(x, y)|
        Mask_Gerak(x, y) = 255 jika Selisih(x, y) >= ambang_gerak, selain itu 0.
    
    Returns:
        Tuple: (citra_selisih_absolut, citra_mask_biner_gerak).
    """
    # Operasi dilakukan pada representasi grayscale
    fa = frame_awal if frame_awal.mode == "GRAYSCALE" else konversi_keabuan(frame_awal)
    fl = frame_lanjut if frame_lanjut.mode == "GRAYSCALE" else konversi_keabuan(frame_lanjut)

    w = min(fa.lebar, fl.lebar)
    h = min(fa.tinggi, fl.tinggi)

    citra_selisih = CitraMatriks(w, h, "GRAYSCALE")
    citra_mask = CitraMatriks(w, h, "GRAYSCALE")

    for y in range(h):
        for x in range(w):
            p1 = fa.get_pixel(x, y)
            p2 = fl.get_pixel(x, y)
            diff = abs(int(p1) - int(p2))

            citra_selisih.set_pixel(x, y, diff)
            citra_mask.set_pixel(x, y, 255 if diff >= ambang_gerak else 0)

    return citra_selisih, citra_mask


# ---------------------------------------------------------------------------
# 3. Operasi Logika Citra (Logic Operations)
# ---------------------------------------------------------------------------

def _siapkan_biner(citra: CitraMatriks) -> CitraMatriks:
    """Memastikan citra berformat biner (GRAYSCALE dengan intensitas 0 atau 255)."""
    gray = citra if citra.mode == "GRAYSCALE" else konversi_keabuan(citra)
    # Jalankan thresholding pada nilai tengah 128
    return pengambangan_tunggal(gray, ambang=128)


def logika_and(citra_a: CitraMatriks, citra_b: CitraMatriks) -> CitraMatriks:
    """Operasi Logika AND: C(x, y) = A(x, y) AND B(x, y)."""
    ba = _siapkan_biner(citra_a)
    bb = _siapkan_biner(citra_b)
    kw, kh, oax, oay, obx, oby = _selaraskan_kanvas(ba, bb)
    hasil = CitraMatriks(kw, kh, "GRAYSCALE", nilai_dasar=0)

    for y in range(kh):
        for x in range(kw):
            ax, ay = x - oax, y - oay
            bx, by = x - obx, y - oby
            va = ba.get_pixel(ax, ay) if (0 <= ax < ba.lebar and 0 <= ay < ba.tinggi) else 0
            vb = bb.get_pixel(bx, by) if (0 <= bx < bb.lebar and 0 <= by < bb.tinggi) else 0
            # Bernilai 255 jika kedua piksel sama-sama 255
            hasil.set_pixel(x, y, 255 if (va > 0 and vb > 0) else 0)

    return hasil


def logika_or(citra_a: CitraMatriks, citra_b: CitraMatriks) -> CitraMatriks:
    """Operasi Logika OR: C(x, y) = A(x, y) OR B(x, y)."""
    ba = _siapkan_biner(citra_a)
    bb = _siapkan_biner(citra_b)
    kw, kh, oax, oay, obx, oby = _selaraskan_kanvas(ba, bb)
    hasil = CitraMatriks(kw, kh, "GRAYSCALE", nilai_dasar=0)

    for y in range(kh):
        for x in range(kw):
            ax, ay = x - oax, y - oay
            bx, by = x - obx, y - oby
            va = ba.get_pixel(ax, ay) if (0 <= ax < ba.lebar and 0 <= ay < ba.tinggi) else 0
            vb = bb.get_pixel(bx, by) if (0 <= bx < bb.lebar and 0 <= by < bb.tinggi) else 0
            hasil.set_pixel(x, y, 255 if (va > 0 or vb > 0) else 0)

    return hasil


def logika_xor(citra_a: CitraMatriks, citra_b: CitraMatriks) -> CitraMatriks:
    """Operasi Logika XOR: C(x, y) = A(x, y) XOR B(x, y)."""
    ba = _siapkan_biner(citra_a)
    bb = _siapkan_biner(citra_b)
    kw, kh, oax, oay, obx, oby = _selaraskan_kanvas(ba, bb)
    hasil = CitraMatriks(kw, kh, "GRAYSCALE", nilai_dasar=0)

    for y in range(kh):
        for x in range(kw):
            ax, ay = x - oax, y - oay
            bx, by = x - obx, y - oby
            va = ba.get_pixel(ax, ay) if (0 <= ax < ba.lebar and 0 <= ay < ba.tinggi) else 0
            vb = bb.get_pixel(bx, by) if (0 <= bx < bb.lebar and 0 <= by < bb.tinggi) else 0
            # Bernilai 255 jika salah satu aktif, tapi bukan keduanya
            hasil.set_pixel(x, y, 255 if ((va > 0) ^ (vb > 0)) else 0)

    return hasil


def logika_sub(citra_a: CitraMatriks, citra_b: CitraMatriks) -> CitraMatriks:
    """Operasi Pengurangan Logika Biner: Menghapus area citra B dari citra A.
    
    Formula:
        C(x, y) = 255 jika A(x, y) == 255 dan B(x, y) == 0, selain itu 0.
    """
    ba = _siapkan_biner(citra_a)
    bb = _siapkan_biner(citra_b)
    kw, kh, oax, oay, obx, oby = _selaraskan_kanvas(ba, bb)
    hasil = CitraMatriks(kw, kh, "GRAYSCALE", nilai_dasar=0)

    for y in range(kh):
        for x in range(kw):
            ax, ay = x - oax, y - oay
            bx, by = x - obx, y - oby
            va = ba.get_pixel(ax, ay) if (0 <= ax < ba.lebar and 0 <= ay < ba.tinggi) else 0
            vb = bb.get_pixel(bx, by) if (0 <= bx < bb.lebar and 0 <= by < bb.tinggi) else 0
            hasil.set_pixel(x, y, 255 if (va > 0 and vb == 0) else 0)

    return hasil


def logika_not(citra: CitraMatriks) -> CitraMatriks:
    """Operasi Logika NOT: Pembalikan citra biner (255 - A)."""
    b = _siapkan_biner(citra)
    hasil = CitraMatriks(b.lebar, b.tinggi, "GRAYSCALE")
    for y in range(b.tinggi):
        for x in range(b.lebar):
            hasil.set_pixel(x, y, 255 - b.get_pixel(x, y))
    return hasil


# ---------------------------------------------------------------------------
# Generator Bentuk Geometris Uji Biner
# ---------------------------------------------------------------------------

def _buat_citra_lingkaran(lebar: int = 100, tinggi: int = 100, radius: int = 35) -> CitraMatriks:
    """Membuat citra biner berupa lingkaran putih di tengah."""
    citra = CitraMatriks(lebar, tinggi, "GRAYSCALE", nilai_dasar=0)
    cx, cy = lebar // 2, tinggi // 2
    r_kuadrat = radius * radius
    for y in range(tinggi):
        for x in range(lebar):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r_kuadrat:
                citra.set_pixel(x, y, 255)
    return citra


def _buat_citra_persegi(lebar: int = 100, tinggi: int = 100, ukuran_kotak: int = 60) -> CitraMatriks:
    """Membuat citra biner berupa persegi putih di tengah."""
    citra = CitraMatriks(lebar, tinggi, "GRAYSCALE", nilai_dasar=0)
    cx, cy = lebar // 2, tinggi // 2
    setengah = ukuran_kotak // 2
    for y in range(cy - setengah, cy + setengah):
        for x in range(cx - setengah, cx + setengah):
            citra.set_pixel(x, y, 255)
    return citra


# ---------------------------------------------------------------------------
# Blok Demonstrasi Mandiri
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print(" DEMONSTRASI MODUL 4: OPERASI BERBASIS BINGKAI (FRAME / MULTI-IMAGE)")
    print("=" * 60)

    folder_output = os.path.join(DIR_INI, "hasil")
    os.makedirs(folder_output, exist_ok=True)

    # 1. Uji Penggabungan (Blending)
    print("\n[1] Menjalankan Penggabungan Citra (Image Blending bobot 0.6 & 0.4)...")
    img_gradien = buat_citra_sampel_gradien(100, 100)
    img_lingkaran = _buat_citra_lingkaran(100, 100, radius=35)
    hasil_blend = gabung_citra(img_gradien, img_lingkaran, bobot_a=0.6)
    simpan_bmp(hasil_blend, os.path.join(folder_output, "bingkai_blending.bmp"))
    print(f"    -> Hasil blending disimpan: {hasil_blend.info()}")

    # 2. Uji Deteksi Gerakan (Motion Detection)
    print("\n[2] Menjalankan Deteksi Gerakan (Frame Differencing)...")
    # Frame 1: Objek di posisi X=35
    frame1 = CitraMatriks(100, 100, "GRAYSCALE", nilai_dasar=40)
    for y in range(40, 60):
        for x in range(25, 45):
            frame1.set_pixel(x, y, 220)

    # Frame 2: Objek bergerak ke kanan (posisi X=55)
    frame2 = CitraMatriks(100, 100, "GRAYSCALE", nilai_dasar=40)
    for y in range(40, 60):
        for x in range(45, 65):
            frame2.set_pixel(x, y, 220)

    diff, mask = deteksi_gerakan(frame1, frame2, ambang_gerak=30)
    simpan_bmp(diff, os.path.join(folder_output, "bingkai_gerak_diff.bmp"))
    simpan_bmp(mask, os.path.join(folder_output, "bingkai_gerak_mask.bmp"))
    print("    -> Hasil frame differencing dan mask gerak berhasil disimpan.")

    # 3. Uji Operasi Logika (AND, OR, XOR, SUB, NOT)
    print("\n[3] Menjalankan Operasi Logika Citra (Lingkaran dan Persegi)...")
    kotak = _buat_citra_persegi(100, 100, 60)
    lingkaran = _buat_citra_lingkaran(100, 100, 35)

    c_and = logika_and(lingkaran, kotak)
    c_or  = logika_or(lingkaran, kotak)
    c_xor = logika_xor(lingkaran, kotak)
    c_sub = logika_sub(lingkaran, kotak)
    c_not = logika_not(lingkaran)

    simpan_bmp(c_and, os.path.join(folder_output, "bingkai_logika_and.bmp"))
    simpan_bmp(c_or,  os.path.join(folder_output, "bingkai_logika_or.bmp"))
    simpan_bmp(c_xor, os.path.join(folder_output, "bingkai_logika_xor.bmp"))
    simpan_bmp(c_sub, os.path.join(folder_output, "bingkai_logika_sub.bmp"))
    simpan_bmp(c_not, os.path.join(folder_output, "bingkai_logika_not.bmp"))

    print("    -> Logika AND, OR, XOR, SUB, dan NOT berhasil diproses dan disimpan.")
    print("\n[V] Sukses: Seluruh operasi multi-citra/bingkai berjalan dengan sempurna!")

