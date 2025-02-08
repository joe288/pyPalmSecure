# https://stackoverflow.com/questions/17195325/palm-veins-enhancement-with-opencv

import cv2
import numpy as np

# Konstanten
THRESHOLD = 140
BRIGHT = 1.10  # Beispielwert, anpassen nach Bedarf
DARK = 0.6    # Beispielwert, anpassen nach Bedarf

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
    import tkinter as tk
    from PIL import Image, ImageTk
     # Funktion zum Erstellen der GUI
    def create_window(path):
        # Hauptfenster erstellen
        root = tk.Tk()
        root.title("Bildanzeige mit Schieberegler")

        # Bild laden
        original_image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

        # Funktion, die beim Bewegen des Schiebereglers aufgerufen wird
        def on_slider1_change(value):
            global THRESHOLD
            # Den Wert des Schiebereglers in eine Ganzzahl umwandeln
            THRESHOLD = int(value)
            # Bild skalieren
            processd_image = main(original_image)
            photo = ImageTk.PhotoImage(image=Image.fromarray(processd_image))

            # Bild im Label aktualisieren
            label.config(image=photo)
            label.image = photo  # Referenz speichern, um Garbage Collection zu vermeiden

        # Funktion, die beim Bewegen des Schiebereglers aufgerufen wird
        def on_slider2_change(value):
            global BRIGHT
            # Den Wert des Schiebereglers in eine Ganzzahl umwandeln
            BRIGHT = float(value)/10
            # Bild skalieren
            processd_image = main(original_image)
            photo = ImageTk.PhotoImage(image=Image.fromarray(processd_image))

            # Bild im Label aktualisieren
            label.config(image=photo)
            label.image = photo  # Referenz speichern, um Garbage Collection zu vermeiden

        # Funktion, die beim Bewegen des Schiebereglers aufgerufen wird
        def on_slider3_change(value):
            global DARK
            # Den Wert des Schiebereglers in eine Ganzzahl umwandeln
            DARK = float(value)/10
            # Bild skalieren
            processd_image = main(original_image)
            photo = ImageTk.PhotoImage(image=Image.fromarray(processd_image))

            # Bild im Label aktualisieren
            label.config(image=photo)
            label.image = photo  # Referenz speichern, um Garbage Collection zu vermeiden

        # Label erstellen, um das Bild anzuzeigen
        label = tk.Label(root)
        label.pack()

        # Beschriftung für den Schieberegler
        threshold_label = tk.Label(root, text="Threshold")
        threshold_label.pack()

        # Schieberegler erstellen
        slider1 = tk.Scale(root, from_=1, to=200, orient=tk.HORIZONTAL, command=on_slider1_change)
        slider1.pack()

         # Beschriftung für den Schieberegler
        bright_label = tk.Label(root, text="BRIGHT")
        bright_label.pack()

        # Schieberegler erstellen
        slider2 = tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, command=on_slider2_change)
        slider2.pack()

         # Beschriftung für den Schieberegler
        dark_label = tk.Label(root, text="DARK")
        dark_label.pack()

        # Schieberegler erstellen
        slider3 = tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, command=on_slider3_change)
        slider3.pack()

        # Initiales Bild anzeigen
        on_slider1_change(slider2.get())

        # Fenster starten
        root.mainloop()

    # Funktion aufrufen
    # create_window("capture_1.png")
    create_window("processdImages\\roi.jpg")
    #  cv2.imwrite("preProcess.jpg",main(cv2.imread("capture_1.png", cv2.IMREAD_GRAYSCALE)))
    # cv2.imwrite("preProcess.jpg",main(cv2.imread("processdImages\\roi.jpg", cv2.IMREAD_GRAYSCALE)))
