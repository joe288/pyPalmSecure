# https://stackoverflow.com/questions/17195325/palm-veins-enhancement-with-opencv

import cv2
import numpy as np

# Konstanten
THRESHOLD = 180
BRIGHT = 1.8  # Beispielwert, anpassen nach Bedarf
DARK = 0.0    # Beispielwert, anpassen nach Bedarf

# Hauptfunktion
def main(img):
    # Algorithmus anwenden
    float_gray = img.astype(np.float32) / 255.0
    blur = cv2.GaussianBlur(float_gray, (0, 0), 10)
    num = float_gray - blur
    blur = cv2.GaussianBlur(num * num, (0, 0), 20)
    den = np.power(blur, 0.5)
    enhanced = num / den
    enhanced = cv2.normalize(enhanced, None, 0.0, 255.0, cv2.NORM_MINMAX)
    enhanced = enhanced.astype(np.uint8)

    # Tiefpassfilter
    gaussian = cv2.GaussianBlur(enhanced, (0, 0), 3)

    # Hochpassfilter auf das berechnete Tiefpassbild
    laplace = cv2.Laplacian(gaussian, cv2.CV_32F, ksize=19)
    lapmin, lapmax = laplace.min(), laplace.max()
    scale = 127 / max(-lapmin, lapmax)
    laplace = cv2.convertScaleAbs(laplace, alpha=scale, beta=128)

    # Schwellenwertbildung zur Erstellung einer Venenmaske
    _, mask = cv2.threshold(laplace, THRESHOLD, 255, cv2.THRESH_BINARY)

    # Maske mit morphologischer Öffnung reinigen
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

    # Nachbarbereiche mit morphologischer Schließung verbinden
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))

    # Maske für eine sanftere Verbesserung verwischen
    mask = cv2.GaussianBlur(mask, (15, 15), 0)

    # Bild ebenfalls ein wenig verwischen, um Rauschen zu entfernen
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # Die Maske wird verwendet, um die Venen zu verstärken
    result = enhanced.copy()
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            coeff = (1.0 - (mask[i, j] / 255.0)) * BRIGHT + (1 - DARK)
            new_pixel = coeff * enhanced[i, j]
            result[i, j] = min(255, new_pixel)

    return result

if __name__ == "__main__":
     cv2.imwrite("preProcess.jpg",main(cv2.imread("capture_1.png", cv2.IMREAD_GRAYSCALE)))
