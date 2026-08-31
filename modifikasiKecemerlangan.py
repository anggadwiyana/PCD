import cv2
import numpy as np
import matplotlib.pyplot as plt

image = cv2.imread('citra_input.jpg')
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

C = int(input("Masukkan nilai konstanta C (positif untuk menerangkan, negatif untuk menggelapkan): "))

# Ko = Ki + C
image_bright = np.clip(image_rgb.astype(np.int16) + C, 0, 255).astype(np.uint8)

# Konfigurasi figur untuk menampilkan gambar dan histogram
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Tampilkan Citra Asli
axs[0, 0].imshow(image_rgb)
axs[0, 0].set_title('Citra Asli')
axs[0, 0].axis('off')

# Tampilkan Citra Hasil Modifikasi
axs[0, 1].imshow(image_bright)
axs[0, 1].set_title(f'Citra Modifikasi Kecemerlangan (C={C})')
axs[0, 1].axis('off')

# Buat Histogram Citra Asli (Kanal R, G, B)
colors = ('r', 'g', 'b')
for i, color in enumerate(colors):
    hist = cv2.calcHist([image_rgb], [i], None, [256], [0, 256])
    axs[1, 0].plot(hist, color=color)
axs[1, 0].set_title('Histogram Citra Asli')
axs[1, 0].set_xlim([0, 256])

# Buat Histogram Citra Modifikasi (Kanal R, G, B)
for i, color in enumerate(colors):
    hist_bright = cv2.calcHist([image_bright], [i], None, [256], [0, 256])
    axs[1, 1].plot(hist_bright, color=color)
axs[1, 1].set_title('Histogram Citra Modifikasi')
axs[1, 1].set_xlim([0, 256])

plt.tight_layout()
plt.show()