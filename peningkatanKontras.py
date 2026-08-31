import cv2
import numpy as np
import matplotlib.pyplot as plt

image = cv2.imread('citra_input.jpg')
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

G = float(input("Masukkan koefisien penguatan kontras (G), misal 1.5: "))
P = int(input("Masukkan pusat pengontrasan (P), misal 128: "))

# Ko = G(Ki - P) + P
image_float = image_rgb.astype(np.float32)
image_contrast = G * (image_float - P) + P

image_contrast = np.clip(image_contrast, 0, 255).astype(np.uint8)

# Konfigurasi figur untuk menampilkan gambar dan histogram
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Tampilkan Citra Asli
axs[0, 0].imshow(image_rgb)
axs[0, 0].set_title('Citra Asli')
axs[0, 0].axis('off')

# Tampilkan Citra Hasil Modifikasi Kontras
axs[0, 1].imshow(image_contrast)
axs[0, 1].set_title(f'Citra Kontras (G={G}, P={P})')
axs[0, 1].axis('off')

# Histogram Citra Asli
colors = ('r', 'g', 'b')
for i, color in enumerate(colors):
    hist = cv2.calcHist([image_rgb], [i], None, [256], [0, 256])
    axs[1, 0].plot(hist, color=color)
axs[1, 0].set_title('Histogram Citra Asli')
axs[1, 0].set_xlim([0, 256])

# Histogram Citra Hasil Modifikasi Kontras
for i, color in enumerate(colors):
    hist_contrast = cv2.calcHist([image_contrast], [i], None, [256], [0, 256])
    axs[1, 1].plot(hist_contrast, color=color)
axs[1, 1].set_title('Histogram Citra Modifikasi Kontras')
axs[1, 1].set_xlim([0, 256])

plt.tight_layout()
plt.show()