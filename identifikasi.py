import numpy as np
import cv2

def identifikasi_penyakit(original, gray, canny, sobel, prewitt):
    h, w = gray.shape
    total_pixels = h * w

    canny_edges = np.sum(canny > 0)
    sobel_edges = np.sum(sobel > 0)
    prewitt_edges = np.sum(prewitt > 0)

    canny_density = canny_edges / total_pixels * 100
    sobel_density = sobel_edges / total_pixels * 100
    prewitt_density = prewitt_edges / total_pixels * 100

    contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    num_contours = len(contours)

    if num_contours > 0:
        areas = [cv2.contourArea(c) for c in contours]
        perimeters = [cv2.arcLength(c, True) for c in contours]
        avg_area = np.mean(areas)
        total_area = np.sum(areas)
        avg_perimeter = np.mean(perimeters)
        leaf_coverage = total_area / total_pixels * 100
    else:
        avg_area = 0
        total_area = 0
        avg_perimeter = 0
        leaf_coverage = 0

    mid = w // 2
    left_half = canny[:, :mid]
    right_half = canny[:, mid:2*mid]

    if right_half.shape[1] > left_half.shape[1]:
        right_half = right_half[:, :left_half.shape[1]]
    elif left_half.shape[1] > right_half.shape[1]:
        left_half = left_half[:, :right_half.shape[1]]

    left_edges = np.sum(left_half > 0)
    right_edges = np.sum(right_half > 0)

    if left_edges + right_edges > 0:
        symmetry = 100 - abs(left_edges - right_edges) / max(left_edges, right_edges) * 100
    else:
        symmetry = 100

    grid_size = 4
    grid_h = h // grid_size
    grid_w = w // grid_size
    grid_densities = []

    for i in range(grid_size):
        for j in range(grid_size):
            grid_region = canny[i*grid_h:(i+1)*grid_h, j*grid_w:(j+1)*grid_w]
            if grid_region.size > 0:
                grid_density = np.sum(grid_region > 0) / grid_region.size * 100
                grid_densities.append(grid_density)

    edge_uniformity = np.std(grid_densities) if grid_densities else 0

    mean_intensity = np.mean(gray)

    result = []

    result.append("[METRIK]")
    result.append(f"  Canny density   : {canny_density:.2f}%")
    result.append(f"  Sobel density   : {sobel_density:.2f}%")
    result.append(f"  Prewitt density : {prewitt_density:.2f}%")
    result.append(f"  Kontur          : {num_contours}")
    result.append(f"  Rata luas kontur: {avg_area:.2f} px")
    result.append(f"  Luas daun       : {total_area:.2f} px ({leaf_coverage:.1f}%)")
    result.append(f"  Simetri         : {symmetry:.1f}%")
    result.append(f"  Uniformitas     : {edge_uniformity:.2f}")
    result.append(f"  Intensitas      : {mean_intensity:.1f}")
    result.append("")

    findings = []

    if canny_density > 25:
        findings.append("Kepadatan tepi sangat tinggi -> kemungkinan infeksi penyakit (bercak daun)")
    elif canny_density > 15:
        findings.append("Kepadatan tepi tinggi -> kemungkinan serangan hama atau infeksi jamur")
    elif canny_density > 10:
        findings.append("Kepadatan tepi di atas normal -> kemungkinan stres tanaman")
    else:
        findings.append("Kepadatan tepi normal -> daun dalam kondisi baik")

    if mean_intensity > 200:
        findings.append("Daun sangat terang -> indikasi klorosis (kekurangan klorofil)")
    elif mean_intensity > 180:
        findings.append("Daun cerah -> kemungkinan kekurangan Nitrogen")
    elif mean_intensity < 50:
        findings.append("Daun sangat gelap -> kemungkinan kekurangan Fosfor")
    elif mean_intensity < 80:
        findings.append("Daun gelap -> kemungkinan kelebihan Nitrogen atau kekurangan Kalium")

    if symmetry < 50:
        findings.append("Daun tidak simetris -> malformasi akibat hama atau penyakit")
    elif symmetry < 75:
        findings.append("Daun kurang simetris -> kemungkinan defisiensi nutrisi")

    if num_contours > 20:
        findings.append(f"Banyak kontur ({num_contours}) -> bercak penyakit atau lubang pada daun")
    elif num_contours <= 3 and leaf_coverage > 40:
        findings.append("Daun utuh dengan sedikit kontur -> daun sehat")
    elif num_contours > 10 and avg_area < 50:
        findings.append("Kontur kecil dan banyak -> indikasi bercak penyakit (bakteri/jamur)")

    if leaf_coverage < 10:
        findings.append("Daun sangat kecil/rusak -> daun mengering atau mati")
    elif leaf_coverage > 60:
        findings.append("Daun lebar dan sehat -> tanaman subur")

    edge_ratio_sobel = sobel_density / (canny_density + 0.001)
    edge_ratio_prewitt = prewitt_density / (canny_density + 0.001)
    if edge_ratio_sobel > 2.5 and edge_ratio_prewitt > 2.5:
        findings.append("Tekstur bergaris dominan -> pola tulang daun (vein) prominent")

    if not findings:
        findings.append("Tidak ditemukan indikasi penyakit yang signifikan")

    result.append("[DIAGNOSA]")
    for f in findings:
        result.append(f"  - {f}")

    result.append("")

    reco = []
    if canny_density > 15:
        reco.append("- Lakukan pemeriksaan lanjutan dengan mikroskop")
        reco.append("- Semprotkan fungisida organik jika indikasi jamur")
    if mean_intensity > 180:
        reco.append("- Berikan pupuk Nitrogen sesuai dosis")
        reco.append("- Periksa pH tanah dan pastikan drainase baik")
    elif mean_intensity < 60:
        reco.append("- Berikan pupuk Fosfor dan Kalium")
        reco.append("- Pastikan pencahayaan cukup untuk fotosintesis")
    if symmetry < 60:
        reco.append("- Periksa keberadaan hama pada batang dan daun")
    if num_contours > 15:
        reco.append("- Pangkas daun yang terinfeksi untuk mencegah penyebaran")
    if not reco:
        reco.append("- Tanaman tampak sehat, lanjutkan perawatan rutin")
        reco.append("- Pertahankan pola pemupukan dan penyiraman")

    result.append("[REKOMENDASI]")
    for r in reco:
        result.append(f"  {r}")

    return "\n".join(result)
