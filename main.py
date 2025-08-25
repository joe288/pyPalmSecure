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
    if os.path.exists(ordner_pfad):
        for datei in os.listdir(ordner_pfad):
            if (tag in datei) and (('.jpg' in datei) or ('.png' in datei)):
                bild_pfad = os.path.join(ordner_pfad, datei)
                os.remove(bild_pfad)

def createImageFolder(ordner_pfad, tag):
    if not os.path.exists(ordner_pfad):
        os.mkdir(tag)

def process(image):
    image = roi.main(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","roi.jpg"),image)
    image = preProcess.main(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","preProcess.jpg"),image)
    image = postProcess.skel(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","postProcess.jpg"),image)
    return  filters.main(postProcess.invert(image))
    
if __name__ == "__main__":
    ordner_pfad = os.getcwd()
    removeAllImages(os.path.join(ordner_pfad,"processdImages"),'')
    createImageFolder(os.path.join(ordner_pfad,"processdImages"),'processdImages')

    try:
        startCapture()
        image = caputure()
        stopCapture()
    except:
        print("no device found, switch to simulation")
    
    start_time = time.time()
    
    if not "image" in locals():
        picture = os.path.join(ordner_pfad,"capture_1.png")
        image = cv2.imread(picture, cv2.IMREAD_GRAYSCALE)
    else:
         cv2.imwrite( os.path.join(ordner_pfad,"processdImages","capture.jpg"),image)

    image = process(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","filter.jpg"),image)

    end_time = time.time()

    # Laufzeit berechnen
    laufzeit = end_time - start_time
    print(f"Laufzeit: {laufzeit} Sekunden")