"""Paket Pengolahan Citra Digital (PCD) Native Python.
Terdiri dari:
- modul1_representasi_citra: Pembacaan & representasi matriks citra BMP native
- modul2_operasi_titik: Operasi titik (kecerahan, kontras, negasi, grayscale, thresholding)
- modul3_operasi_geometri: Operasi geometri (flipping, rotasi, cropping, scaling)
- modul4_operasi_bingkai: Operasi berbasis bingkai (blending, frame differencing, operasi logika biner)
- modul5_operasi_global: Operasi global (histogram, ekualisasi histogram, evaluasi statistik)
"""

import os
import sys

# Memastikan path direktori paket terdaftar
_DIR_INI = os.path.dirname(os.path.abspath(__file__))
if _DIR_INI not in sys.path:
    sys.path.insert(0, _DIR_INI)

from .modul1_representasi_citra import (
    CitraMatriks,
    muat_bmp,
    simpan_bmp,
    buat_citra_sampel_gradien,
    buat_citra_sampel_warna,
)

