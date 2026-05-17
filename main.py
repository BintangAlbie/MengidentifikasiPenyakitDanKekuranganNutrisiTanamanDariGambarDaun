import sys
import os
import cv2
import numpy as np
import pandas as pd
from PyQt5 import QtCore, uic
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QFileDialog, QMessageBox
)
from konvolusi import fungsi_konvolusi
from identifikasi import identifikasi_penyakit

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
REF_CSV = os.path.join(DATASET_DIR, "referensi_penyakit.csv")

class ShowImage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image = None
        self.gray = None
        self.canny_result = None
        self.sobel_result = None
        self.prewitt_result = None
        self.csv_data = None

        self.initUI()
        self.loadReferenceCSV()

    def initUI(self):
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.ui")
        uic.loadUi(ui_path, self)
        self.loadBtn.clicked.connect(self.loadImage)
        self.identBtn.clicked.connect(self.identifikasi)

    def loadReferenceCSV(self):
        if os.path.exists(REF_CSV):
            try:
                self.csv_data = pd.read_csv(REF_CSV)
                self.statusLabel.setText(f"Reference CSV loaded: {len(self.csv_data)} diseases")
            except Exception as e:
                print(f"Reference CSV load failed: {e}")

    def loadImage(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Pilih Gambar Daun", "",
            "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        if fname:
            self.image = cv2.imread(fname)
            if self.image is not None:
                self.prosesSemua()
                filename = fname.replace("\\", "/").split("/")[-1]
                self.statusLabel.setText(f"Loaded: {filename} ({self.image.shape[1]}x{self.image.shape[0]}) - Edge detection selesai")
            else:
                QMessageBox.warning(self, "Error", "Gagal memuat gambar!")

    def prosesSemua(self):
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.displayImage(self.gray, self.origLabel)

        img = self.gray

        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        prewitt_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        prewitt_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])

        gx = fungsi_konvolusi(img, sobel_x)
        gy = fungsi_konvolusi(img, sobel_y)
        grad_sobel = np.sqrt(gx**2 + gy**2)
        grad_sobel = (grad_sobel / grad_sobel.max() * 255).astype(np.uint8)
        self.sobel_result = grad_sobel
        self.displayImage(grad_sobel, self.sobelLabel)

        gx = fungsi_konvolusi(img, prewitt_x)
        gy = fungsi_konvolusi(img, prewitt_y)
        grad_prewitt = np.sqrt(gx**2 + gy**2)
        grad_prewitt = (grad_prewitt / grad_prewitt.max() * 255).astype(np.uint8)
        self.prewitt_result = grad_prewitt
        self.displayImage(grad_prewitt, self.prewittLabel)

        gauss = (1.0 / 57) * np.array([
            [0, 1, 2, 1, 0], [1, 3, 5, 3, 1], [2, 5, 9, 5, 2],
            [1, 3, 5, 3, 1], [0, 1, 2, 1, 0]
        ])
        img_blur = fungsi_konvolusi(img, gauss)

        gx = fungsi_konvolusi(img_blur, sobel_x)
        gy = fungsi_konvolusi(img_blur, sobel_y)
        grad = np.sqrt(gx**2 + gy**2)
        theta = np.arctan2(gy, gx)
        grad = (grad / grad.max() * 255).astype(np.uint8)

        H, W = grad.shape
        Z = np.zeros((H, W), dtype=np.uint8)
        angle = theta * 180.0 / np.pi
        angle[angle < 0] += 180

        for i in range(1, H - 1):
            for j in range(1, W - 1):
                q = 255; r = 255
                if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                    q = grad[i, j + 1]; r = grad[i, j - 1]
                elif 22.5 <= angle[i, j] < 67.5:
                    q = grad[i + 1, j - 1]; r = grad[i - 1, j + 1]
                elif 67.5 <= angle[i, j] < 112.5:
                    q = grad[i + 1, j]; r = grad[i - 1, j]
                elif 112.5 <= angle[i, j] < 157.5:
                    q = grad[i - 1, j - 1]; r = grad[i + 1, j + 1]
                if (grad[i, j] >= q) and (grad[i, j] >= r):
                    Z[i, j] = grad[i, j]

        weak, strong = 100, 150
        res = np.zeros((H, W), dtype=np.uint8)
        for i in range(H):
            for j in range(W):
                if Z[i, j] >= strong: res[i, j] = 255
                elif Z[i, j] >= weak: res[i, j] = weak

        for i in range(1, H - 1):
            for j in range(1, W - 1):
                if res[i, j] == weak:
                    if ((res[i+1, j-1] == 255) or (res[i+1, j] == 255) or
                        (res[i+1, j+1] == 255) or (res[i, j-1] == 255) or
                        (res[i, j+1] == 255) or (res[i-1, j-1] == 255) or
                        (res[i-1, j] == 255) or (res[i-1, j+1] == 255)):
                        res[i, j] = 255
                    else:
                        res[i, j] = 0

        self.canny_result = res
        self.displayImage(res, self.cannyLabel)

    def identifikasi(self):
        if self.image is None:
            QMessageBox.warning(self, "Warning", "Load image terlebih dahulu!")
            return

        self.statusLabel.setText("Melakukan identifikasi...")
        QApplication.processEvents()

        hasil = identifikasi_penyakit(
            self.image, self.gray,
            self.canny_result, self.sobel_result, self.prewitt_result
        )

        if self.csv_data is not None:
            canny_edges = np.sum(self.canny_result > 0)
            total_pixels = self.canny_result.shape[0] * self.canny_result.shape[1]
            canny_density = canny_edges / total_pixels * 100

            matches = []
            for _, row in self.csv_data.iterrows():
                try:
                    low = float(row['kepadatan_tepi_rendah'])
                    high = float(row['kepadatan_tepi_tinggi'])
                    if low <= canny_density <= high:
                        matches.append(row['nama_penyakit'])
                except (ValueError, KeyError):
                    pass

            if matches:
                hasil += "\n" + "-" * 50 + "\n"
                hasil += "=== REFERENSI DATASET ===\n"
                hasil += "Berdasarkan kecocokan kepadatan tepi:\n"
                for m in matches[:5]:
                    hasil += f"  -> {m}\n"

                csv_match = self.csv_data[self.csv_data['nama_penyakit'].isin(matches[:3])]
                if len(csv_match) > 0:
                    hasil += "\nRekomendasi dari dataset:\n"
                    for _, row in csv_match.iterrows():
                        hasil += f"  [{row['nama_penyakit']}] {row['rekomendasi']}\n"

        self.identText.setText(hasil)
        self.statusLabel.setText("Identifikasi selesai")

    def displayImage(self, img, label):
        if len(img.shape) == 2:
            h, w = img.shape
            bytes_per_line = w
            qformat = QImage.Format_Grayscale8
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, _ = img.shape
            bytes_per_line = 3 * w
            qformat = QImage.Format_RGB888
        qimg = QImage(img.data, w, h, bytes_per_line, qformat)
        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(
            label.width() - 4, label.height() - 4,
            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ShowImage()
    window.show()
    sys.exit(app.exec_())
