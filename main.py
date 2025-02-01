import os
import cv2
from pyPalmSecure import palmScan
import roi
import preProcess
import postProcess
import filters

ps = palmScan()

def caputure():
    ps.open()
    ps.start()
    ps.do_detect()
    ps.stop()

def removeAllImages(ordner_pfad, tag):
    for datei in os.listdir(ordner_pfad):
        if (tag in datei) and (('.jpg' in datei) or ('.png' in datei)):
            bild_pfad = os.path.join(ordner_pfad, datei)
            os.remove(bild_pfad)

if __name__ == "__main__":
    ordner_pfad = os.getcwd()
    
    # removeAllCaptures(ordner_pfad,'capture')
    removeAllImages(os.path.join(ordner_pfad,"processdImages"),'')
    # caputure()
    
    picture = os.path.join(ordner_pfad,"capture_1.png")
    image = cv2.imread(picture, cv2.IMREAD_GRAYSCALE)
    image = roi.main(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","roi.jpg"),image)
    image = preProcess.main(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","preProcess.jpg"),image)
    image = postProcess.skel(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","postProcess.jpg"),image)
    image = filters.main(image)
    cv2.imwrite( os.path.join(ordner_pfad,"processdImages","filter.jpg"),image)