import usb.core
import usb.util
import random
import time
import numpy as np
import cv2

class palmScan:
    dev:usb.core.Device
    mask:bytearray
    scan_first:bool 

    def __init__(self):
        scan_first= True

    def __bulk_send(self, endpoint, buf):
        final = 0
        offset = 0
        while True:
            # Erstelle einen Teil des Puffers (maximal 16384 Bytes)
            data = buf[offset:offset + 16384]
            if not data:  # Wenn der Puffer leer ist, beende die Schleife
                break
            
            # tx = ctypes.c_int(0)  # Anzahl der gesendeten Bytes
            res = self.dev.write(endpoint & 0x7f, data, 0)
            
            if res < 0:
                print("QUsbDevice: failed write")
                # self.handle_libusb_res(res)
                return -1
            
            if res != len(data):
                print("QUsbDevice: failed to write all the data")
                return -1
            
            final += res
            offset += res
            
            if offset >= len(buf):  # Wenn der Offset das Ende des Puffers erreicht hat, beende die Schleife
                break
        
        return final

    def __bulk_receive(self, endpoint, length):
        final = bytearray()
        while length > 0:
            chunk_size = min(16384, length)
            try:
                data = self.dev.read(endpoint | 0x80, chunk_size)
                final.extend(data[:chunk_size])
                length -= chunk_size
            except usb.core.USBError as e:
                print("QUsbDevice: failed write")
                return bytearray()
        return final

    def __bufToImage(self, buf, w, h):
        res = np.zeros((h, w), dtype=np.uint8)

        for y in range(h):
            for x in range(w):
                res[y, x] = buf[y * w + x]
        return res

    def __captureLarge(self):
        res = []
        print("Capture lage!")
        data = self.dev.ctrl_transfer(0xc0, 0x4e, 0, 0, 3)           #returns 4e0100
        data = self.dev.ctrl_transfer(0xc0, 0x4e, 1, 0, 3)           #returns 4e0100
        data = self.dev.ctrl_transfer(0xc0, 0x4e, 2, 0, 3)           #returns 4e0100
        data = self.dev.ctrl_transfer(0xc0, 0x4e, 3, 0, 3)           #returns 4e0100
        data = self.dev.ctrl_transfer(0xc0, 0x46, 0x5d0, 0, 3)       #returns 460100
        data = self.dev.ctrl_transfer(0xc0, 0x47, 0x10, 0, 3)        #returns 470100
        data = self.dev.ctrl_transfer(0xc0, 0x49, 0x100, 0, 3)       #returns 490100
        data = self.dev.ctrl_transfer(0xc0, 0x4a, 0x78, 240, 5)      #returns 4a01005802 - image size related?
        data = self.dev.ctrl_transfer(0xc0, 0x46, 0xc8, 3, 3)        #returns 460100
        data = self.dev.ctrl_transfer(0xc0, 0x47, 0x10, 3, 3)        #returns 470100
        data = self.dev.ctrl_transfer(0xc0, 0x49, 0x100, 3, 3)       #returns 490100
        data = self.dev.ctrl_transfer(0xc0, 0x42, 0x100, 2, 3)       #returns 420100
        data = self.dev.ctrl_transfer(0xc0, 0x43, 0, 0, 3)           #returns 430100       take picture
        data = self.dev.ctrl_transfer(0xc0, 0x4a, 0, 480, 5)         #returns 4a0100b004 - image height?
        
        print("Capture 1")
        data = self.dev.ctrl_transfer(0xc0, 0x44, 0, 0, 6)           #returns 440100b00400
        dat = self.__bulk_receive(2,307200)                            #vein data, 640x480
        for i in range(240 * 640):
            dat[i + 120 * 640] ^= self.mask[i]
        res.append(self.__bufToImage(dat, 640, 480))

        # print("Capture 2")
        # data = self.dev.ctrl_transfer(0xc0, 0x44, 0, 1, 6)           #returns 440100b00400
        # dat = self.__bulk_receive(2,307200)                            #normal picture
        # res.append(self.__bufToImage(dat, 640, 480))

        # print("Capture 3")
        # data = self.dev.ctrl_transfer(0xc0, 0x4d, 0x78, 240, 5)      #returns 4d01005802
        # data = self.dev.ctrl_transfer(0xc0, 0x44, 3, 2, 6)           #returns 440100580200
        # dat = self.__bulk_receive(2,153600)                            #"4 dots"

        res.append(self.__bufToImage(dat, 640, 240))

        #back to scan mode
        data = self.dev.ctrl_transfer(0xc0, 0x27, 7, 1, 8)           #returns 2707000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 8, 1, 8)           #returns 2708000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0, 1, 6)           #returns 270000280000
        self.scan_first = True
        
        return res

    def __captureSmall(self):
        res = []
        print("Capture small!")

        data = self.dev.ctrl_transfer(0xc0, 0x4e, 0, 0, 3)           #returns 4e0100
        data = self.dev.ctrl_transfer(0xc0, 0x4e, 1, 0, 3)           #returns 4e0100
        data = self.dev.ctrl_transfer(0xc0, 0x4e, 2, 0, 3)           #returns 4e0100
        data = self.dev.ctrl_transfer(0xc0, 0x4e, 3, 0, 3)           #returns 4e0100
        data = self.dev.ctrl_transfer(0xc0, 0x46, 0x7b7, 2, 3)       #returns 460100
        data = self.dev.ctrl_transfer(0xc0, 0x47, 0x10, 2, 3)        #returns 470100
        data = self.dev.ctrl_transfer(0xc0, 0x49, 0x100, 2, 3)       #returns 490100
        data = self.dev.ctrl_transfer(0xc0, 0x4c, 0xc0, 96, 5)       #returns 4c0100f000 - image height?
        data = self.dev.ctrl_transfer(0xc0, 0x46, 0xc8, 3, 3)        #returns 460100
        data = self.dev.ctrl_transfer(0xc0, 0x47, 0x10, 3, 3)        #returns 470100
        data = self.dev.ctrl_transfer(0xc0, 0x49, 0x100, 3, 3)       #returns 490100
        data = self.dev.ctrl_transfer(0xc0, 0x42, 0, 258, 3)         #returns 420100
        data = self.dev.ctrl_transfer(0xc0, 0x43, 0, 0, 3)           #returns 430100
        data = self.dev.ctrl_transfer(0xc0, 0x4c, 0xc0, 96, 5)       #returns 4c0100f000 - image height?
        data = self.dev.ctrl_transfer(0xc0, 0x44, 2, 0, 6)           #returns 440100f00000

        print("Capture 4")
        dat = self.__bulk_receive(2,61440)                             #vein data
        for i in range(96 * 640):
            dat[i] ^= self.mask[i]
        res.append(self.__bufToImage(dat, 640, 96))
        
        print("Capture 5")
        data = self.dev.ctrl_transfer(0xc0, 0x44, 2, 1, 6)           #returns 440100f00000
        dat = self.__bulk_receive(2,61440)                             #normal picture
        res.append(self.__bufToImage(dat, 640, 96))

        print("Capture 6")
        data = self.dev.ctrl_transfer(0xc0, 0x4d, 0x78, 240, 5)      #returns 4d01005802
        data = self.dev.ctrl_transfer(0xc0, 0x44, 3, 2, 6)           #returns 440100580200
        dat = self.__bulk_receive(2,153600)                            #"4 dots"
        res.append(self.__bufToImage(dat, 640, 240))

        #back to scan mode
        data = self.dev.ctrl_transfer(0xc0, 0x27, 7, 1, 8)           #returns 2707000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 8, 1, 8)           #returns 2708000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0, 1, 6)           #returns 270000280000
        self.scan_first = True
        
        return res
    
    def scanUSBDevices(self):
        devices = usb.core.find(find_all=True)

        # Durch die gefundenen Geräte iterieren und Informationen ausgeben
        for dev in devices:
            print(f"Gerät: {dev.idVendor:04x}:{dev.idProduct:04x}")
            print(f"  Hersteller: {usb.util.get_string(dev, dev.iManufacturer)}")
            print(f"  Produkt: {usb.util.get_string(dev, dev.iProduct)}")
            print(f"  Seriennummer: {usb.util.get_string(dev, dev.iSerialNumber)}")
            # print(f"  Konfiguration: {dev.bConfigurationValue}")
            print()

    def deviceName(self):
        if self.dev is None:
            return ""

        bytes_name = self.dev.ctrl_transfer(0xc0, 0x28, 0, 21, 21).tobytes()
        
        # cut off zero termination
        null_byte_index = bytes_name.find(b'\x00')
        if null_byte_index != -1:
            bytes_name = bytes_name[:null_byte_index]
    
        return bytes_name.decode('latin-1')

    def open(self):
        # init random mask
        random.seed(int(time.time() * 1000) % 1000)
        self.mask = bytearray(random.getrandbits(8) for _ in range(307200))

        # seach USB-Device
        
        self.dev = usb.core.find(idVendor=0x04c5, idProduct=0x1084)
        print(type(self.dev))
        if self.dev is None:
            raise ValueError("no device found")

        # set Config
        self.dev.set_configuration()

        data = self.dev.ctrl_transfer(0xc0, 0xa0, 0, 0, 3) #returns a000cb
        data = self.dev.ctrl_transfer(0xc0, 0x29, 0, 0, 4) #returns 29000300 (probably means "flag value is 3")
        data = self.dev.ctrl_transfer(0xc0, 0x66, 0, 0, 3) #returns 660000
        data = self.dev.ctrl_transfer(0xc0, 0xa3, 0, 0, 4) #returns a392cd01
        
        device_name = self.deviceName()
        print("PalmSecure: Connected to device ", device_name)
            
        data = self.dev.ctrl_transfer(0xc0, 0x29, 1, 4, 4) #returns 29010400 (probably means "flag value is 4")
        
        # We initialize device's random generator with this method, it seems
        key = self.dev.ctrl_transfer(0xc0, 0x35, random.randint(0, 0xffff), random.randint(0, 0xffff), 18 ) #returns 3500 + encryption key
        self.dev.ctrl_transfer(0xc0, 0x36, 0, 0, 3)
        
        # "encrypt" mask and send it
        mask2 = (key[2:10] * 80) + (key[10:18] * 80)
        mask2 = mask2 * 240
        # XOR mask2 and mask
        for i in range(307200):
            mask2[i] ^= self.mask[i]

        res = self.__bulk_send(0x01, mask2)
        print(f"PalmSecure: Wrote {res} bytes to device (should be 307200)")

        if res == -1:
            print("false")

        data = self.dev.ctrl_transfer(0xc0, 0x29, 1, 0, 4)       #returns 29010400 (probably means something)
        data = self.dev.ctrl_transfer(0xc0, 0xf6, 9, 0, 168)     #returns a400000002000000d0051000b7071000d7a3703d0ad7fd3fd7a3703d0ad7a33f6666666666565e401c041000f80410003108ac1c5a640040367689eaad81ad3f713d0ad7a3605540e80210004b031000f0a7c64b378901404faf94658863b53f52b81e85eb314e400e0210003e021000fed478e9263102406002b7eee6a9be3fae47e17a144e4540740110008c011000cff753e3a59b024024624a24d1cbc43f0ad7a3703d0a3e40
        data = self.dev.ctrl_transfer(0xc0, 0xf6, 8, 0, 152)     #returns 94000000010000000000000000000040000000000000324000000000000084400000000000007e40fa7e6abc7493783f0038b1e02533833fccc5bd1f468d54bf00001ae91ded883f00ac11642c67ed3f4ba5ca32f867b0bfc42951a36f36793f34fe9ffa4662f43fe3d40ddaa64bd53f9b186be9afb2d9bf693754c7b3e55240aee258d2929a67bf504164df91a63dbf953ead43900be9bf
        data = self.dev.ctrl_transfer(0xc0, 0xf6, 7, 0, 302)     #returns 3401000001000000040000000000000061e849533fe226c0190e2d82fc2827c00000000000000000094155c358418b3f60805047ad44513fd6fd521d45ffef3f7eb6d422de042740cdccd212dc4a27c00000000000000000433ed92b619f7b3f0f25c8d5ce9661bf3816387acbffef3f29a96ce37edc26c072cc748eef102740000000000000000082f2c7d86e53933f9a4c9416e67b8a3f77fc4916dbfdef3fac1796de70ed2640e428b29c3ce02640000000000000000033f14bd221639f3ffd970612085827bf5f59a39326fcef3f020004004201f0004201ef004301f5004801f20000000000d2a12dffc12342400901b700f800a6007b01b6008c01a5000a012e01fa003e0180012a0191013b01bff27cd4352453402901d7001d01cb005b01d6006701ca002a010e011f01

        # switch off all lights?
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0, 0, 6)       #returns 270000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x05, 0, 8)    #returns 2705000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x06, 0, 8)    #returns 2706000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x07, 0, 8)    #returns 2707000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x08, 0, 8)    #returns 2708000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x09, 0, 8)    #returns 2709000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x0a, 0, 8)    #returns 270a000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x0b, 0, 8)    #returns 270b000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x0c, 0, 8)    #returns 270c000000000000
        print("PalmSecure: init done")
        return True

    def start(self):
        # switch on light
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x07, 1, 8)    #returns 2707000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x08, 1, 8)    #returns 2708000000000000
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x00, 1, 6)    #returns 270000280000
        self.scan_first = True

    def stop(self):
        # stop light?
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x07, 0, 8)    #returns ?
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x08, 0, 8)    #returns ?
        data = self.dev.ctrl_transfer(0xc0, 0x27, 0x00, 0, 6)    #returns ?
        data = self.dev.ctrl_transfer(0xc0, 0x45, 0, 0, 3)       #returns 450100
        
    def do_detect(self):
        self.scan_first
        ok = False
        val1 = self.dev.ctrl_transfer(0xc0, 0x4d, 0x78, 240, 5)      #returns 4d01005802
        
        while ok == False:
            val2 = self.dev.ctrl_transfer(0xc0, 0x58, 0xffce if self.scan_first else 0, 0xf0f, 56)    #returns 5801000000000808080808090809090808080809080908090808090807080808080808080808080909080908080908080808080808080800
            self.scan_first = False
            # print(f"CHECK [{' '.join(format(byte, '02x') for byte in val1)}] [{' '.join(format(byte, '02x') for byte in val2)}]")

            d = [0] * 4
            for i in range(4):
                d[i] = val2[2 + i] 

            print(f"DIST VALUE={d[0], d[1], d[2], d[3]}")

            if all(40 < wert < 50 for wert in d):
                ok = True

            if ok:
                list_of_images = self.__captureLarge()  
                # list_of_images = captureSmall()
                cv2.imwrite("capture_1.png", list_of_images[0])
                # cv2.imwrite("capture_2.png", list_of_images[1])
                # cv2.imwrite("capture_3.png", list_of_images[2])
                return list_of_images[0]

