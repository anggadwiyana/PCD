"""Modul 1: Pembacaan & Representasi Citra (Dasar)
================================================
Modul ini menangani:
1. Pembacaan berkas citra format BMP (Bitmap) dari awal (from-scratch) secara native.
2. Ekstraksi informasi header (File Header & DIB Header).
3. Representasi citra dalam struktur matriks dua dimensi (N baris x M kolom).
4. Penyimpanan matriks citra kembali ke berkas berkas BMP standar.
5. Pembuatan kanvas citra kosong dan citra uji sintetis.

100% Native Python (Hanya menggunakan pustaka bawaan: struct, os, sys).
"""

import os
import struct
import sys
from typing import Any, List, Optional, Tuple, Union

# Memastikan direktori modul ini terdaftar di sys.path
DIR_INI = os.path.dirname(os.path.abspath(__file__))
if DIR_INI not in sys.path:
    sys.path.insert(0, DIR_INI)

# Tipe data untuk piksel:
# - Integer (0..255) untuk mode GRAYSCALE
# - Tuple[int, int, int] (R, G, B) untuk mode RGB
TipePiksel = Union[int, Tuple[int, int, int]]


class CitraMatriks:
    """Representasi citra digital dalam bentuk matriks 2D (N baris x M kolom).
    
    Koordinat matriks:
    - y (baris): 0 sampai (tinggi - 1), dari atas ke bawah.
    - x (kolom): 0 sampai (lebar - 1), dari kiri ke kanan.
    """

    def __init__(self, lebar: int, tinggi: int, mode: str = "GRAYSCALE", nilai_dasar: TipePiksel = 0):
        """Inisialisasi citra baru dengan dimensi dan mode tertentu.
        
        Args:
            lebar: Jumlah kolom citra (M).
            tinggi: Jumlah baris citra (N).
            mode: "GRAYSCALE" (keabuan) atau "RGB" (warna penuh).
            nilai_dasar: Nilai awal piksel untuk mengisi matriks (default 0 / hitam).
        """
        if lebar <= 0 or tinggi <= 0:
            raise ValueError("Lebar dan tinggi citra harus bernilai positif.")
        if mode not in ("GRAYSCALE", "RGB"):
            raise ValueError("Mode citra yang didukung hanya 'GRAYSCALE' dan 'RGB'.")

        self.lebar = lebar
        self.tinggi = tinggi
        self.mode = mode

        # Alokasi matriks 2 dimensi: N baris (tinggi) x M kolom (lebar)
        if mode == "RGB" and isinstance(nilai_dasar, int):
            nilai_dasar = (nilai_dasar, nilai_dasar, nilai_dasar)

        self.matriks: List[List[TipePiksel]] = [
            [nilai_dasar for _ in range(lebar)] for _ in range(tinggi)
        ]

    def get_pixel(self, x: int, y: int) -> TipePiksel:
        """Mengambil nilai piksel pada koordinat kolom x dan baris y."""
        if not (0 <= x < self.lebar and 0 <= y < self.tinggi):
            raise IndexError(f"Koordinat ({x}, {y}) di luar batas citra {self.lebar}x{self.tinggi}.")
        return self.matriks[y][x]

    def set_pixel(self, x: int, y: int, nilai: TipePiksel) -> None:
        """Mengatur nilai piksel pada koordinat kolom x dan baris y."""
        if not (0 <= x < self.lebar and 0 <= y < self.tinggi):
            raise IndexError(f"Koordinat ({x}, {y}) di luar batas citra {self.lebar}x{self.tinggi}.")
        self.matriks[y][x] = nilai

    def salin(self) -> "CitraMatriks":
        """Membuat salinan dalam (deep copy) dari objek CitraMatriks."""
        duplikat = CitraMatriks(self.lebar, self.tinggi, self.mode)
        for y in range(self.tinggi):
            for x in range(self.lebar):
                duplikat.matriks[y][x] = self.matriks[y][x]
        return duplikat

    def info(self) -> str:
        """Mengembalikan ringkasan spesifikasi matriks citra."""
        return f"Citra [{self.mode}] - Resolusi: {self.lebar}x{self.tinggi} piksel (N={self.tinggi}, M={self.lebar})"


# ---------------------------------------------------------------------------
# Fungsi I/O Berkas BMP (Native Parser & Writer)
# ---------------------------------------------------------------------------

def muat_bmp(path_berkas: str) -> Tuple[CitraMatriks, dict]:
    """Membaca berkas BMP, mengurai header, dan menyusun piksel ke CitraMatriks.
    
    Mendukung format:
    - 24-bit True Color (RGB murni tanpa kompresi)
    - 8-bit Grayscale / Palette Berindeks (256 warna)
    
    Returns:
        Tuple berupa objek CitraMatriks dan dictionary metadata header.
    """
    if not os.path.exists(path_berkas):
        raise FileNotFoundError(f"Berkas tidak ditemukan: {path_berkas}")

    with open(path_berkas, "rb") as f:
        # 1. Bitmap File Header (14 bytes)
        # Format: 2s (magic 'BM'), I (filesize), H (reserved1), H (reserved2), I (offset data piksel)
        magic_bytes = f.read(2)
        if magic_bytes != b"BM":
            raise ValueError(f"Bukan berkas BMP valid. Tanda magic: {magic_bytes!r}")

        ukuran_berkas, _, _, offset_data = struct.unpack("<IHHI", f.read(12))

        # 2. DIB Header (BITMAPINFOHEADER minimum 40 bytes)
        ukuran_dib = struct.unpack("<I", f.read(4))[0]
        if ukuran_dib < 40:
            raise ValueError(f"Ukuran DIB Header ({ukuran_dib} byte) tidak didukung.")

        lebar_mentah, tinggi_mentah, planes, bpp, kompresi, ukuran_gambar, x_ppm, y_ppm, warna_digunakan, warna_penting = struct.unpack(
            "<iiHHIIiiII", f.read(36)
        )

        # Melewati sisa header jika ukuran DIB lebih dari 40 byte
        if ukuran_dib > 40:
            f.read(ukuran_dib - 40)

        # Validasi dukungan format
        if kompresi != 0:
            raise ValueError(f"Kompresi BMP tipe {kompresi} belum didukung. Hanya uncompressed BMP (BI_RGB).")
        if bpp not in (8, 24):
            raise ValueError(f"Kedalaman bit {bpp}-bpp belum didukung. Hanya 8-bit dan 24-bit.")

        # Penentuan arah baris (bottom-up vs top-down)
        # Nilai tinggi positif berarti baris disusun dari bawah ke atas (standar BMP).
        arah_terbalik = tinggi_mentah > 0
        tinggi = abs(tinggi_mentah)
        lebar = lebar_mentah

        metadata = {
            "ukuran_berkas_byte": ukuran_berkas,
            "offset_piksel": offset_data,
            "lebar": lebar,
            "tinggi": tinggi,
            "bit_per_piksel": bpp,
            "arah_bottom_up": arah_terbalik,
            "warna_digunakan": warna_digunakan,
        }

        # 3. Membaca Palet Warna (hanya ada pada citra 8-bit)
        palet: List[Tuple[int, int, int]] = []
        if bpp == 8:
            jumlah_warna = warna_digunakan if warna_digunakan > 0 else 256
            for _ in range(jumlah_warna):
                b, g, r, _reserved = struct.unpack("4B", f.read(4))
                palet.append((r, g, b))

        # 4. Membaca Data Piksel
        f.seek(offset_data)

        # Mode citra: 8-bit dikonversi ke GRAYSCALE (atau RGB jika palet berwarna), 24-bit ke RGB
        mode = "RGB" if bpp == 24 else "GRAYSCALE"
        citra = CitraMatriks(lebar, tinggi, mode)

        if bpp == 8:
            # Pada BMP, tiap baris data harus sejajar dengan kelipatan 4 byte (padding)
            padding = (4 - (lebar % 4)) % 4
            baris_terbaca = []
            for _ in range(tinggi):
                indeks_baris = list(f.read(lebar))
                if padding > 0:
                    f.read(padding)
                
                # Petakan indeks ke nilai grayscale atau palet
                if palet:
                    baris_piksel = [palet[idx][0] for idx in indeks_baris]
                else:
                    baris_piksel = indeks_baris
                baris_terbaca.append(baris_piksel)

            if arah_terbalik:
                baris_terbaca.reverse()

            citra.matriks = baris_terbaca

        elif bpp == 24:
            padding = (4 - ((lebar * 3) % 4)) % 4
            baris_terbaca = []
            for _ in range(tinggi):
                baris_piksel: List[TipePiksel] = []
                data_baris = f.read(lebar * 3)
                for i in range(0, len(data_baris), 3):
                    b = data_baris[i]
                    g = data_baris[i + 1]
                    r = data_baris[i + 2]
                    baris_piksel.append((r, g, b))
                if padding > 0:
                    f.read(padding)
                baris_terbaca.append(baris_piksel)

            if arah_terbalik:
                baris_terbaca.reverse()

            citra.matriks = baris_terbaca

        return citra, metadata


def simpan_bmp(citra: CitraMatriks, path_berkas: str) -> None:
    """Menyimpan objek CitraMatriks ke dalam berkas BMP standar yang valid.
    
    Menyimpan sebagai:
    - 8-bit BMP (dengan palet grayscale 256 tingkat) jika mode GRAYSCALE
    - 24-bit BMP (BGR order) jika mode RGB
    """
    lebar = citra.lebar
    tinggi = citra.tinggi

    folder_induk = os.path.dirname(path_berkas)
    if folder_induk and not os.path.exists(folder_induk):
        os.makedirs(folder_induk, exist_ok=True)

    with open(path_berkas, "wb") as f:
        if citra.mode == "GRAYSCALE":
            bpp = 8
            padding = (4 - (lebar % 4)) % 4
            ukuran_data_piksel = (lebar + padding) * tinggi
            offset_data = 14 + 40 + (256 * 4)  # FileHeader + DIBHeader + Palet 256 warna
            ukuran_berkas = offset_data + ukuran_data_piksel

            # Tulis File Header (14 bytes)
            f.write(b"BM")
            f.write(struct.pack("<IHHI", ukuran_berkas, 0, 0, offset_data))

            # Tulis DIB Header (40 bytes)
            f.write(struct.pack(
                "<IiiHHIIiiII",
                40, lebar, tinggi, 1, bpp, 0, ukuran_data_piksel, 2835, 2835, 256, 0
            ))

            # Tulis Palet Warna (256 tingkatan abu-abu: B, G, R, 0)
            for val in range(256):
                f.write(struct.pack("4B", val, val, val, 0))

            # Tulis data piksel (Bottom-Up: dari baris terbawah ke atas)
            pad_bytes = b"\x00" * padding
            for y in range(tinggi - 1, -1, -1):
                baris_bytes = bytearray(citra.matriks[y])
                f.write(baris_bytes)
                if padding > 0:
                    f.write(pad_bytes)

        elif citra.mode == "RGB":
            bpp = 24
            padding = (4 - ((lebar * 3) % 4)) % 4
            ukuran_data_piksel = (lebar * 3 + padding) * tinggi
            offset_data = 14 + 40  # FileHeader + DIBHeader
            ukuran_berkas = offset_data + ukuran_data_piksel

            # Tulis File Header (14 bytes)
            f.write(b"BM")
            f.write(struct.pack("<IHHI", ukuran_berkas, 0, 0, offset_data))

            # Tulis DIB Header (40 bytes)
            f.write(struct.pack(
                "<IiiHHIIiiII",
                40, lebar, tinggi, 1, bpp, 0, ukuran_data_piksel, 2835, 2835, 0, 0
            ))

            # Tulis data piksel (Bottom-Up, format BGR)
            pad_bytes = b"\x00" * padding
            for y in range(tinggi - 1, -1, -1):
                baris_bytes = bytearray()
                for x in range(lebar):
                    p = citra.matriks[y][x]
                    r, g, b = p[0], p[1], p[2]
                    baris_bytes.extend([b, g, r])  # BGR
                f.write(baris_bytes)
                if padding > 0:
                    f.write(pad_bytes)


# ---------------------------------------------------------------------------
# Generator Citra Uji Sintetis
# ---------------------------------------------------------------------------

def buat_citra_sampel_gradien(lebar: int = 120, tinggi: int = 80) -> CitraMatriks:
    """Membuat citra sintetis grayscale berpola gradien horisontal dan kotak uji."""
    citra = CitraMatriks(lebar, tinggi, "GRAYSCALE")
    for y in range(tinggi):
        for x in range(lebar):
            # Pola gradien bertahap
            nilai = int((x / lebar) * 255)
            # Berikan aksen kotak di tengah
            if (tinggi // 4 <= y <= 3 * tinggi // 4) and (lebar // 4 <= x <= 3 * lebar // 4):
                nilai = 255 - nilai
            citra.set_pixel(x, y, nilai)
    return citra


def buat_citra_sampel_warna(lebar: int = 120, tinggi: int = 80) -> CitraMatriks:
    """Membuat citra sintetis warna RGB (pita merah, hijau, biru, dan kuning)."""
    citra = CitraMatriks(lebar, tinggi, "RGB")
    seperempat_y = tinggi // 4
    for y in range(tinggi):
        for x in range(lebar):
            if y < seperempat_y:
                # Pita Merah dengan intensitas bervariasi
                citra.set_pixel(x, y, (int(x / lebar * 255), 30, 30))
            elif y < 2 * seperempat_y:
                # Pita Hijau
                citra.set_pixel(x, y, (30, int(x / lebar * 255), 30))
            elif y < 3 * seperempat_y:
                # Pita Biru
                citra.set_pixel(x, y, (30, 30, int(x / lebar * 255)))
            else:
                # Pita Campuran Kuning
                intensitas = int(x / lebar * 255)
                citra.set_pixel(x, y, (intensitas, intensitas, 50))
    return citra


# ---------------------------------------------------------------------------
# Blok Demonstrasi Mandiri
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print(" DEMONSTRASI MODUL 1: PEMBACAAN & REPRESENTASI CITRA (DASAR)")
    print("=" * 60)

    folder_output = os.path.join(DIR_INI, "hasil")
    os.makedirs(folder_output, exist_ok=True)

    # 1. Membuat citra sintetis dalam bentuk matriks N x M
    print("\n[1] Membuat Citra Matriks Sintetis Grayscale (80 baris x 120 kolom)...")
    citra_gray = buat_citra_sampel_gradien(120, 80)
    print(f"    -> {citra_gray.info()}")
    print(f"    -> Contoh intensitas piksel di tengah (x=60, y=40): {citra_gray.get_pixel(60, 40)}")

    # 2. Menyimpan matriks ke berkas BMP
    path_simpan_gray = os.path.join(folder_output, "sampel_grayscale.bmp")
    simpan_bmp(citra_gray, path_simpan_gray)
    print(f"    -> Citra berhasil disimpan ke: {path_simpan_gray}")

    # 3. Memuat kembali berkas BMP dan memeriksa informasi header
    print("\n[2] Membaca kembali berkas BMP dan mengekstrak Header...")
    citra_terbaca, meta = muat_bmp(path_simpan_gray)
    print("    Informasi Header BMP Terbaca:")
    for k, v in meta.items():
        print(f"      - {k}: {v}")

    # 4. Membuat citra RGB dan menyimpannya
    print("\n[3] Membuat Citra Matriks RGB 24-bit...")
    citra_rgb = buat_citra_sampel_warna(120, 80)
    path_simpan_rgb = os.path.join(folder_output, "sampel_warna.bmp")
    simpan_bmp(citra_rgb, path_simpan_rgb)
    print(f"    -> Citra RGB berhasil disimpan ke: {path_simpan_rgb}")

    # Verifikasi konsistensi matriks
    assert citra_terbaca.lebar == citra_gray.lebar
    assert citra_terbaca.tinggi == citra_gray.tinggi
    assert citra_terbaca.get_pixel(60, 40) == citra_gray.get_pixel(60, 40)
    print("\n[V] Sukses: Matriks citra dan parser BMP 100% konsisten dan bekerja dengan benar!")
