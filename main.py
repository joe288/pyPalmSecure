import os
from pyPalmSecure import palmScan


if __name__ == "__main__":
    ordner_pfad = os.getcwd()

    for datei in os.listdir(ordner_pfad):
        if 'capture' in datei:
            bild_pfad = os.path.join(ordner_pfad, datei)
            os.remove(bild_pfad)

    ps = palmScan()

    ps.open()
    ps.start()
    ps.do_detect()
    ps.stop()