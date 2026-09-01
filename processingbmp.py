import os
import struct
import matplotlib.pyplot as plt

IMG_DIR = "img"

def get_available_bmp():
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
        return []
    return [f for f in os.listdir(IMG_DIR) if f.lower().endswith('.bmp')]

def parse_bmp(filepath):
    with open(filepath, 'rb') as f:
        # File Header (14 bytes)
        bfType = f.read(2)
        if bfType != b'BM':
            raise ValueError("Bukan format berkas BMP valid (Header Magic != BM)")
        
        bfSize, bfReserved1, bfReserved2, bfOffBits = struct.unpack('<IHHI', f.read(12))
        
        # Info Header (DIB Header - minimal 40 bytes / BITMAPINFOHEADER)
        biSize = struct.unpack('<I', f.read(4))[0]
        if biSize < 40:
            raise ValueError(f"Ukuran DIB Header ({biSize} bytes) tidak didukung.")
            
        biWidth, biHeight, biPlanes, biBitCount, biCompression, biSizeImage, biXPelsPerMeter, biYPelsPerMeter, biClrUsed, biClrImportant = struct.unpack('<iiHHIIiiII', f.read(36))
        
        # Melewati sisa header jika biSize > 40
        if biSize > 40:
            f.read(biSize - 40)
            
        is_top_down = False
        if biHeight < 0:
            is_top_down = True
            height = -biHeight
        else:
            height = biHeight
        width = biWidth

        # Membaca Color Table / Palet (jika 8-bit)
        palette = []
        if biBitCount == 8:
            num_colors = biClrUsed if biClrUsed > 0 else 256
            for _ in range(num_colors):
                b, g, r, _ = struct.unpack('4B', f.read(4))
                palette.append((r, g, b))
                
        # Lompat ke posisi awal data piksel
        f.seek(bfOffBits)
        
        pixels = []
        if biBitCount == 8:
            row_padding = (4 - (width % 4)) % 4
            for _ in range(height):
                row = []
                for _ in range(width):
                    idx = ord(f.read(1))
                    if palette:
                        # Jika ada palet grayscale atau warna
                        color = palette[idx]
                        if color[0] == color[1] == color[2]:
                            row.append(color[0])  # Grayscale murni
                        else:
                            row.append(list(color))
                    else:
                        row.append(idx)
                if row_padding > 0:
                    f.read(row_padding)
                pixels.append(row)
        elif biBitCount == 24:
            row_padding = (4 - ((width * 3) % 4)) % 4
            for _ in range(height):
                row = []
                for _ in range(width):
                    b, g, r = struct.unpack('3B', f.read(3))
                    row.append([r, g, b])
                if row_padding > 0:
                    f.read(row_padding)
                pixels.append(row)
        else:
            raise ValueError(f"Bit depth {biBitCount}-bit belum didukung.")

        # BMP standar disusun bottom-up, jika bukan top-down maka perlu dibalik
        if not is_top_down:
            pixels.reverse()

        return {
            'width': width,
            'height': height,
            'bit_count': biBitCount,
            'pixels': pixels,
            'is_grayscale': (biBitCount == 8 and isinstance(pixels[0][0], int))
        }

# --- Perhitungan Histogram & Pengecekan ---

def compute_hist_manual(pixels, is_grayscale):
    if is_grayscale:
        hist = [0] * 256
        for row in pixels:
            for val in row:
                hist[val] += 1
        return {'gray': hist}
    else:
        hist_r = [0] * 256
        hist_g = [0] * 256
        hist_b = [0] * 256
        for row in pixels:
            for r, g, b in row:
                hist_r[r] += 1
                hist_g[g] += 1
                hist_b[b] += 1
        return {'r': hist_r, 'g': hist_g, 'b': hist_b}

def are_histograms_identical(hist1, hist2):
    if hist1.keys() != hist2.keys():
        return False
    for k in hist1:
        if hist1[k] != hist2[k]:
            return False
    return True

# --- Operasi Titik ---

def modify_brightness(pixels, is_grayscale, val):
    new_pixels = []
    for row in pixels:
        new_row = []
        for p in row:
            if is_grayscale:
                new_row.append(max(0, min(255, p + val)))
            else:
                new_row.append([
                    max(0, min(255, p[0] + val)),
                    max(0, min(255, p[1] + val)),
                    max(0, min(255, p[2] + val))
                ])
        new_pixels.append(new_row)
    return new_pixels, is_grayscale

def modify_contrast(pixels, is_grayscale, factor, pivot=128):
    new_pixels = []
    for row in pixels:
        new_row = []
        for p in row:
            if is_grayscale:
                v = int(factor * (p - pivot) + pivot)
                new_row.append(max(0, min(255, v)))
            else:
                r = int(factor * (p[0] - pivot) + pivot)
                g = int(factor * (p[1] - pivot) + pivot)
                b = int(factor * (p[2] - pivot) + pivot)
                new_row.append([
                    max(0, min(255, r)),
                    max(0, min(255, g)),
                    max(0, min(255, b))
                ])
        new_pixels.append(new_row)
    return new_pixels, is_grayscale

def modify_invert(pixels, is_grayscale):
    new_pixels = []
    for row in pixels:
        new_row = []
        for p in row:
            if is_grayscale:
                new_row.append(255 - p)
            else:
                new_row.append([255 - p[0], 255 - p[1], 255 - p[2]])
        new_pixels.append(new_row)
    return new_pixels, is_grayscale

def convert_color_space(pixels, is_grayscale):
    new_pixels = []
    if is_grayscale:
        # Grayscale ke RGB
        for row in pixels:
            new_row = []
            for p in row:
                new_row.append([p, p, p])
            new_pixels.append(new_row)
        return new_pixels, False
    else:
        # RGB ke Grayscale
        for row in pixels:
            new_row = []
            for p in row:
                gray = int(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2])
                new_row.append(max(0, min(255, gray)))
            new_pixels.append(new_row)
        return new_pixels, True

def modify_threshold(pixels, is_grayscale, thresh):
    if not is_grayscale:
        pixels, _ = convert_color_space(pixels, is_grayscale)
    new_pixels = []
    for row in pixels:
        new_row = []
        for p in row:
            new_row.append(255 if p >= thresh else 0)
        new_pixels.append(new_row)
    return new_pixels, True

# --- Visualisasi ---

def display_results(orig_pixels, orig_gray, trans_pixels, trans_gray, title_op):
    hist_orig = compute_hist_manual(orig_pixels, orig_gray)
    hist_trans = compute_hist_manual(trans_pixels, trans_gray)
    identical = are_histograms_identical(hist_orig, hist_trans)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # Tampilan Citra Asli
    if orig_gray:
        axes[0, 0].imshow(orig_pixels, cmap='gray', vmin=0, vmax=255)
    else:
        axes[0, 0].imshow(orig_pixels)
    axes[0, 0].set_title("Citra Asli")
    axes[0, 0].axis('off')

    # Tampilan Citra Transformasi
    if trans_gray:
        axes[0, 1].imshow(trans_pixels, cmap='gray', vmin=0, vmax=255)
    else:
        axes[0, 1].imshow(trans_pixels)
    axes[0, 1].set_title(f"Hasil: {title_op}")
    axes[0, 1].axis('off')

    # Histogram Asli
    if orig_gray:
        axes[1, 0].plot(hist_orig['gray'], color='black', label='Grayscale')
    else:
        axes[1, 0].plot(hist_orig['r'], color='red', label='Red')
        axes[1, 0].plot(hist_orig['g'], color='green', label='Green')
        axes[1, 0].plot(hist_orig['b'], color='blue', label='Blue')
    axes[1, 0].set_title("Histogram Citra Asli")
    axes[1, 0].set_xlim([0, 255])
    axes[1, 0].legend()
    axes[1, 0].grid(True, linestyle=':', alpha=0.6)

    # Histogram Transformasi
    if trans_gray:
        axes[1, 1].plot(hist_trans['gray'], color='black', label='Grayscale')
    else:
        axes[1, 1].plot(hist_trans['r'], color='red', label='Red')
        axes[1, 1].plot(hist_trans['g'], color='green', label='Green')
        axes[1, 1].plot(hist_trans['b'], color='blue', label='Blue')

    status_str = "IDENTIK (Citra Sama)" if identical else "TIDAK IDENTIK"
    axes[1, 1].set_title(f"Histogram Hasil [{status_str}]")
    axes[1, 1].set_xlim([0, 255])
    axes[1, 1].legend()
    axes[1, 1].grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.show()

def main():
    files = get_available_bmp()
    if not files:
        print(f"Folder '{IMG_DIR}' kosong atau tidak ada file .bmp.")
        print(f"Silakan letakkan file .bmp pada folder '{IMG_DIR}'.")
        return

    print("=== DAFTAR BERKAS BMP TERSEDIA ===")
    for idx, name in enumerate(files, 1):
        print(f"[{idx}] {name}")

    while True:
        try:
            choice = int(input("\nPilih nomor gambar (0 untuk keluar): "))
            if choice == 0:
                print("Program selesai.")
                return
            if 1 <= choice <= len(files):
                selected = os.path.join(IMG_DIR, files[choice - 1])
                break
            print("Pilihan tidak valid.")
        except ValueError:
            print("Masukkan angka!")

    try:
        bmp_data = parse_bmp(selected)
    except Exception as e:
        print(f"Gagal mem-parsing file BMP: {e}")
        return

    print(f"\nBerhasil membaca {selected}")
    print(f"Ukuran: {bmp_data['width']}x{bmp_data['height']} | Kedalaman: {bmp_data['bit_count']}-bit | Mode: {'Grayscale' if bmp_data['is_grayscale'] else 'RGB'}")

    orig_pix = bmp_data['pixels']
    orig_gray = bmp_data['is_grayscale']

    while True:
        print("\n=== MENU OPERASI TITIK (MANUAL BMP) ===")
        print("[1] Tampilkan Histogram Citra Asli")
        print("[2] Modifikasi Brightness")
        print("[3] Tingkatkan / Ubah Kontras")
        print("[4] Negasi / Inversi Citra")
        print("[5] Konversi Ruang Warna (RGB <-> Grayscale)")
        print("[6] Thresholding (Pengambangan)")
        print("[0] Keluar")

        try:
            op = int(input("Pilih operasi: "))
        except ValueError:
            print("Masukkan angka!")
            continue

        if op == 0:
            print("Keluar dari program.")
            break
        elif op == 1:
            display_results(orig_pix, orig_gray, orig_pix, orig_gray, "Citra Asli (No Change)")
        elif op == 2:
            val = int(input("Masukkan nilai brightness (-255 s.d. 255): "))
            res_pix, res_gray = modify_brightness(orig_pix, orig_gray, val)
            display_results(orig_pix, orig_gray, res_pix, res_gray, f"Brightness ({val:+d})")
        elif op == 3:
            factor = float(input("Masukkan faktor kontras (misal 1.5): "))
            res_pix, res_gray = modify_contrast(orig_pix, orig_gray, factor)
            display_results(orig_pix, orig_gray, res_pix, res_gray, f"Kontras (x{factor})")
        elif op == 4:
            res_pix, res_gray = modify_invert(orig_pix, orig_gray)
            display_results(orig_pix, orig_gray, res_pix, res_gray, "Negasi (Inversi)")
        elif op == 5:
            res_pix, res_gray = convert_color_space(orig_pix, orig_gray)
            target = "RGB" if orig_gray else "Grayscale"
            display_results(orig_pix, orig_gray, res_pix, res_gray, f"Konversi ke {target}")
        elif op == 6:
            thresh = int(input("Masukkan nilai threshold (0-255): "))
            res_pix, res_gray = modify_threshold(orig_pix, orig_gray, thresh)
            display_results(orig_pix, orig_gray, res_pix, res_gray, f"Thresholding (T={thresh})")
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()
