import os
import sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

IMG_DIR = "img"

def get_available_images():
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
        return []
    valid_exts = ('.bmp', '.png', '.jpg', '.jpeg', '.webp', '.tiff')
    return [f for f in os.listdir(IMG_DIR) if f.lower().endswith(valid_exts)]

def load_image(filepath):
    img = Image.open(filepath)
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    return np.array(img, dtype=np.uint8)

def compute_histogram(img_array):
    if img_array.ndim == 2:
        hist, _ = np.histogram(img_array, bins=256, range=(0, 256))
        return {'gray': hist}
    elif img_array.ndim == 3:
        hist_r, _ = np.histogram(img_array[:, :, 0], bins=256, range=(0, 256))
        hist_g, _ = np.histogram(img_array[:, :, 1], bins=256, range=(0, 256))
        hist_b, _ = np.histogram(img_array[:, :, 2], bins=256, range=(0, 256))
        return {'r': hist_r, 'g': hist_g, 'b': hist_b}

def are_histograms_identical(hist1, hist2):
    if set(hist1.keys()) != set(hist2.keys()):
        return False
    for k in hist1:
        if not np.array_equal(hist1[k], hist2[k]):
            return False
    return True

# --- Operasi Titik ---

def adjust_brightness(img_array, value):
    img_int = img_array.astype(np.int16) + value
    return np.clip(img_int, 0, 255).astype(np.uint8)

def adjust_contrast(img_array, factor, pivot=128):
    img_float = factor * (img_array.astype(np.float32) - pivot) + pivot
    return np.clip(img_float, 0, 255).astype(np.uint8)

def invert_image(img_array):
    return (255 - img_array).astype(np.uint8)

def convert_color(img_array):
    if img_array.ndim == 3:
        # RGB ke Grayscale (bobot luminance standar)
        gray = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
        return np.clip(gray, 0, 255).astype(np.uint8)
    else:
        # Grayscale ke RGB (3-kanal identik)
        return np.stack([img_array] * 3, axis=-1)

def apply_threshold(img_array, threshold_val):
    if img_array.ndim == 3:
        gray = convert_color(img_array)
    else:
        gray = img_array
    return np.where(gray >= threshold_val, 255, 0).astype(np.uint8)

# --- Visualisasi ---

def display_comparison(original, transformed, title_operation):
    hist_orig = compute_histogram(original)
    hist_trans = compute_histogram(transformed)
    identical = are_histograms_identical(hist_orig, hist_trans)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # Tampilan Citra Asli
    if original.ndim == 2:
        axes[0, 0].imshow(original, cmap='gray', vmin=0, vmax=255)
    else:
        axes[0, 0].imshow(original)
    axes[0, 0].set_title("Citra Asli")
    axes[0, 0].axis('off')

    # Tampilan Citra Transformasi
    if transformed.ndim == 2:
        axes[0, 1].imshow(transformed, cmap='gray', vmin=0, vmax=255)
    else:
        axes[0, 1].imshow(transformed)
    axes[0, 1].set_title(f"Hasil: {title_operation}")
    axes[0, 1].axis('off')

    # Plot Histogram Asli
    if 'gray' in hist_orig:
        axes[1, 0].plot(hist_orig['gray'], color='black', label='Grayscale')
    else:
        axes[1, 0].plot(hist_orig['r'], color='red', label='Red')
        axes[1, 0].plot(hist_orig['g'], color='green', label='Green')
        axes[1, 0].plot(hist_orig['b'], color='blue', label='Blue')
    axes[1, 0].set_title("Histogram Citra Asli")
    axes[1, 0].set_xlim([0, 255])
    axes[1, 0].legend()
    axes[1, 0].grid(True, linestyle=':', alpha=0.6)

    # Plot Histogram Transformasi
    if 'gray' in hist_trans:
        axes[1, 1].plot(hist_trans['gray'], color='black', label='Grayscale')
    else:
        axes[1, 1].plot(hist_trans['r'], color='red', label='Red')
        axes[1, 1].plot(hist_trans['g'], color='green', label='Green')
        axes[1, 1].plot(hist_trans['b'], color='blue', label='Blue')
    
    status_text = "IDENTIK (Citra Sama)" if identical else "TIDAK IDENTIK"
    axes[1, 1].set_title(f"Histogram Hasil [{status_text}]")
    axes[1, 1].set_xlim([0, 255])
    axes[1, 1].legend()
    axes[1, 1].grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.show()

def main():
    images = get_available_images()
    if not images:
        print(f"Folder '{IMG_DIR}' kosong atau tidak ditemukan file citra yang didukung.")
        print(f"Silakan letakkan file gambar di dalam folder '{IMG_DIR}'.")
        return

    print("=== DAFTAR GAMBAR TERSEDIA ===")
    for idx, img_name in enumerate(images, 1):
        print(f"[{idx}] {img_name}")

    while True:
        try:
            choice = int(input("\nPilih nomor gambar (0 untuk keluar): "))
            if choice == 0:
                print("Program selesai.")
                return
            if 1 <= choice <= len(images):
                selected_file = os.path.join(IMG_DIR, images[choice - 1])
                break
            print("Pilihan tidak valid.")
        except ValueError:
            print("Masukkan angka!")

    original_img = load_image(selected_file)
    print(f"\nMemuat: {selected_file} | Resolusi: {original_img.shape[1]}x{original_img.shape[0]} | Saluran: {'Grayscale' if original_img.ndim == 2 else 'RGB'}")

    while True:
        print("\n=== MENU OPERASI TITIK ===")
        print("[1] Tampilkan Histogram Citra Asli Saja")
        print("[2] Modifikasi Brightness")
        print("[3] Tingkatkan / Ubah Kontras")
        print("[4] Negasi / Inversi Citra")
        print("[5] Konversi Ruang Warna (RGB <-> Grayscale)")
        print("[6] Thresholding (Pengambangan)")
        print("[0] Keluar")

        try:
            op = int(input("Pilih operasi: "))
        except ValueError:
            print("Masukkan angka pilihan yang benar.")
            continue

        if op == 0:
            print("Keluar dari program.")
            break
        elif op == 1:
            display_comparison(original_img, original_img, "Citra Asli (No Change)")
        elif op == 2:
            val = int(input("Masukkan nilai pergeseran brightness (-255 s.d. 255): "))
            res = adjust_brightness(original_img, val)
            display_comparison(original_img, res, f"Brightness ({val:+d})")
        elif op == 3:
            factor = float(input("Masukkan faktor kontras (misal 1.5 untuk meningkatkan, 0.5 untuk menurunkan): "))
            res = adjust_contrast(original_img, factor)
            display_comparison(original_img, res, f"Kontras (x{factor})")
        elif op == 4:
            res = invert_image(original_img)
            display_comparison(original_img, res, "Negasi (Inversi)")
        elif op == 5:
            res = convert_color(original_img)
            target = "Grayscale" if original_img.ndim == 3 else "RGB"
            display_comparison(original_img, res, f"Konversi ke {target}")
        elif op == 6:
            thresh = int(input("Masukkan nilai ambang batas threshold (0-255): "))
            res = apply_threshold(original_img, thresh)
            display_comparison(original_img, res, f"Thresholding (T={thresh})")
        else:
            print("Opsi tidak dikenali.")

if __name__ == "__main__":
    main()
