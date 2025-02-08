import os
import cv2
import time
from pyPalmSecure import palmScan
import roi
import preProcess
import postProcess
import filters

ps = palmScan()

def startCapture():
    ps.open()
    ps.start()

def stopCapture():
    ps.stop()

def caputure():
    return ps.do_detect()

def removeAllImages(ordner_pfad, tag):
    for datei in os.listdir(ordner_pfad):
        if (tag in datei) and (('.jpg' in datei) or ('.png' in datei)):
            bild_pfad = os.path.join(ordner_pfad, datei)
            os.remove(bild_pfad)

if __name__ == "__main__":
    ordner_pfad = os.getcwd()
    
    # removeAllCaptures(ordner_pfad,'capture')
    removeAllImages(os.path.join(ordner_pfad,"processdImages"),'')
    
    startCapture()
    image = caputure()
    stopCapture()
    
    start_time = time.time()
    
    if not "image" in locals():
        picture = os.path.join(ordner_pfad,"capture_1.png")
        image = cv2.imread(picture, cv2.IMREAD_GRAYSCALE)

    image = roi.main(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","roi.jpg"),image)
    image = preProcess.main(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","preProcess.jpg"),image)
    image = postProcess.skel(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","postProcess.jpg"),image)
    image = filters.main(postProcess.invert(image))
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","filter.jpg"),image)

    end_time = time.time()

    # Laufzeit berechnen
    laufzeit = end_time - start_time
    print(f"Laufzeit: {laufzeit} Sekunden")