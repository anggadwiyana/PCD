"""Menu Utama / Runner Pengolahan Citra Digital (PCD)
=====================================================
Program utama untuk menjalankan seluruh modul PCD secara terpadu atau mandiri:
- Modul 1: Pembacaan & Representasi Citra BMP
- Modul 2: Operasi Titik (Brightness, Kontras, Negasi, Grayscale, Thresholding)
- Modul 3: Operasi Geometri (Flip, Rotasi, Crop, Scaling)
- Modul 4: Operasi Bingkai (Blending, Motion Detection, Operasi Logika)
- Modul 5: Operasi Global (Histogram, Ekualisasi Histogram, Statistik)

100% Native Python tanpa dependensi eksternal.
"""

import os
import sys

# Memastikan direktori PCD ini terdaftar dalam sys.path
DIR_INI = os.path.dirname(os.path.abspath(__file__))
if DIR_INI not in sys.path:
    sys.path.insert(0, DIR_INI)

import modul1_representasi_citra as m1
import modul2_operasi_titik as m2
import modul3_operasi_geometri as m3
import modul4_operasi_bingkai as m4
import modul5_operasi_global as m5


def jalankan_modul(nomor: int) -> None:
    modul_map = {
        1: ("Modul 1: Representasi & Pembacaan BMP", m1),
        2: ("Modul 2: Operasi Titik", m2),
        3: ("Modul 3: Operasi Geometri", m3),
        4: ("Modul 4: Operasi Berbasis Bingkai", m4),
        5: ("Modul 5: Operasi Global & Histogram", m5),
    }

    if nomor not in modul_map:
        print(f"[!] Nomor modul {nomor} tidak valid.")
        return

    nama, modul = modul_map[nomor]
    print("\n" + "=" * 65)
    print(f"  MENJALANKAN DEMONSTRASI: {nama}")
    print("=" * 65)

    folder_hasil = os.path.join(DIR_INI, "hasil")
    os.makedirs(folder_hasil, exist_ok=True)

    if nomor == 1:
        # Modul 1
        citra_gray = m1.buat_citra_sampel_gradien(120, 80)
        p_gray = os.path.join(folder_hasil, "sampel_grayscale.bmp")
        m1.simpan_bmp(citra_gray, p_gray)
        citra_read, meta = m1.muat_bmp(p_gray)
        citra_rgb = m1.buat_citra_sampel_warna(120, 80)
        p_rgb = os.path.join(folder_hasil, "sampel_warna.bmp")
        m1.simpan_bmp(citra_rgb, p_rgb)
        print("  -> Modul 1 berhasil dijalankan. Citra disimpan di folder 'hasil/'.")

    elif nomor == 2:
        # Modul 2
        citra_g = m1.buat_citra_sampel_gradien(100, 60)
        citra_c = m1.buat_citra_sampel_warna(100, 60)
        m1.simpan_bmp(m2.ubah_kecerahan(citra_g, 40), os.path.join(folder_hasil, "titik_brightness_terang.bmp"))
        m1.simpan_bmp(m2.ubah_kecerahan(citra_g, -40), os.path.join(folder_hasil, "titik_brightness_gelap.bmp"))
        m1.simpan_bmp(m2.tingkatkan_kontras(citra_g, 1.8), os.path.join(folder_hasil, "titik_kontras_tinggi.bmp"))
        m1.simpan_bmp(m2.negasi_citra(citra_g), os.path.join(folder_hasil, "titik_negasi.bmp"))
        m1.simpan_bmp(m2.konversi_keabuan(citra_c, "luminance"), os.path.join(folder_hasil, "titik_grayscale_luminance.bmp"))
        m1.simpan_bmp(m2.pengambangan_tunggal(citra_g, 128), os.path.join(folder_hasil, "titik_threshold_tunggal.bmp"))
        m1.simpan_bmp(m2.pengambangan_ganda(citra_g, 80, 180), os.path.join(folder_hasil, "titik_threshold_ganda.bmp"))
        print("  -> Modul 2 berhasil dijalankan. Citra disimpan di folder 'hasil/'.")

    elif nomor == 3:
        # Modul 3
        citra_g = m1.buat_citra_sampel_gradien(100, 60)
        m1.simpan_bmp(m3.cermin_horizontal(citra_g), os.path.join(folder_hasil, "geometri_flip_horizontal.bmp"))
        m1.simpan_bmp(m3.cermin_vertikal(citra_g), os.path.join(folder_hasil, "geometri_flip_vertikal.bmp"))
        m1.simpan_bmp(m3.cermin_kombinasi(citra_g), os.path.join(folder_hasil, "geometri_flip_kombinasi.bmp"))
        m1.simpan_bmp(m3.rotasi_90(citra_g), os.path.join(folder_hasil, "geometri_rotasi_90.bmp"))
        m1.simpan_bmp(m3.rotasi_180(citra_g), os.path.join(folder_hasil, "geometri_rotasi_180.bmp"))
        m1.simpan_bmp(m3.rotasi_bebas(citra_g, 35), os.path.join(folder_hasil, "geometri_rotasi_35_bebas.bmp"))
        m1.simpan_bmp(m3.potong_citra(citra_g, 25, 15, 50, 30), os.path.join(folder_hasil, "geometri_crop.bmp"))
        m1.simpan_bmp(m3.skala_citra(citra_g, 1.5, 1.5), os.path.join(folder_hasil, "geometri_skala_besar.bmp"))
        m1.simpan_bmp(m3.skala_citra(citra_g, 0.5, 0.5), os.path.join(folder_hasil, "geometri_skala_kecil.bmp"))
        print("  -> Modul 3 berhasil dijalankan. Citra disimpan di folder 'hasil/'.")

    elif nomor == 4:
        # Modul 4
        c_grad = m1.buat_citra_sampel_gradien(100, 100)
        c_ling = m4._buat_citra_lingkaran(100, 100, 35)
        c_kotak = m4._buat_citra_persegi(100, 100, 60)
        m1.simpan_bmp(m4.gabung_citra(c_grad, c_ling, 0.6), os.path.join(folder_hasil, "bingkai_blending.bmp"))
        m1.simpan_bmp(m4.logika_and(c_ling, c_kotak), os.path.join(folder_hasil, "bingkai_logika_and.bmp"))
        m1.simpan_bmp(m4.logika_or(c_ling, c_kotak), os.path.join(folder_hasil, "bingkai_logika_or.bmp"))
        m1.simpan_bmp(m4.logika_xor(c_ling, c_kotak), os.path.join(folder_hasil, "bingkai_logika_xor.bmp"))
        m1.simpan_bmp(m4.logika_sub(c_ling, c_kotak), os.path.join(folder_hasil, "bingkai_logika_sub.bmp"))
        m1.simpan_bmp(m4.logika_not(c_ling), os.path.join(folder_hasil, "bingkai_logika_not.bmp"))
        print("  -> Modul 4 berhasil dijalankan. Citra disimpan di folder 'hasil/'.")

    elif nomor == 5:
        # Modul 5
        c_kontras = m5._buat_citra_kontras_rendah(120, 80)
        p_asli = os.path.join(folder_hasil, "global_sebelum_ekualisasi.bmp")
        p_ekual = os.path.join(folder_hasil, "global_sesudah_ekualisasi.bmp")
        m1.simpan_bmp(c_kontras, p_asli)
        c_hasil = m5.ekualisasi_histogram(c_kontras)
        m1.simpan_bmp(c_hasil, p_ekual)
        stat = m5.evaluasi_statistik(c_hasil)
        print(f"  -> Ekualisasi selesai. Rata-rata: {stat['rata_rata_intensitas']}, StdDev: {stat['standar_deviasi_kontras']}")
        print("  -> Modul 5 berhasil dijalankan. Citra disimpan di folder 'hasil/'.")


def main():
    while True:
        print("\n" + "=" * 65)
        print(" SISTEM PENGOLAHAN CITRA DIGITAL (PCD) NATIVE PYTHON")
        print("=" * 65)
        print(" [1] Jalankan Modul 1 (Pembacaan, Header & Representasi Citra BMP)")
        print(" [2] Jalankan Modul 2 (Operasi Titik: Brightness, Kontras, Negasi, Threshold)")
        print(" [3] Jalankan Modul 3 (Operasi Geometri: Flip, Rotasi, Crop, Zoom)")
        print(" [4] Jalankan Modul 4 (Operasi Bingkai: Blending, Diff, Logika Biner)")
        print(" [5] Jalankan Modul 5 (Operasi Global: Histogram & Ekualisasi Kontras)")
        print(" [6] Jalankan SEMUA Modul Sekaligus (1 sampai 5)")
        print(" [0] Keluar")
        print("-" * 65)

        try:
            pilihan = input("Pilih menu (0-6): ").strip()
            if pilihan == "0":
                print("Terima kasih. Program selesai.")
                break
            elif pilihan == "6":
                for i in range(1, 6):
                    jalankan_modul(i)
                print("\n[V] Semua demonstrasi modul 1 s.d. 5 telah selesai dijalankan!")
            elif pilihan in ("1", "2", "3", "4", "5"):
                jalankan_modul(int(pilihan))
            else:
                print("[!] Pilihan tidak valid, silakan masukkan angka antara 0 - 6.")
        except (KeyboardInterrupt, EOFError):
            print("\nProgram dihentikan.")
            break


if __name__ == "__main__":
    main()

