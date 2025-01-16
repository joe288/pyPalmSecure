import usb.core
import usb.util
import random
import time

dev:usb.core.Device

def bulk_send( endpoint, buf):
        final = 0
        offset = 0
        while True:
            # Erstelle einen Teil des Puffers (maximal 16384 Bytes)
            data = buf[offset:offset + 16384]
            if not data:  # Wenn der Puffer leer ist, beende die Schleife
                break
            
            # tx = ctypes.c_int(0)  # Anzahl der gesendeten Bytes
            res = dev.write(endpoint & 0x7f, data, 0)
            
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

def scanUSBDevices():
    devices = usb.core.find(find_all=True)

    # Durch die gefundenen Geräte iterieren und Informationen ausgeben
    for dev in devices:
        print(f"Gerät: {dev.idVendor:04x}:{dev.idProduct:04x}")
        print(f"  Hersteller: {usb.util.get_string(dev, dev.iManufacturer)}")
        print(f"  Produkt: {usb.util.get_string(dev, dev.iProduct)}")
        print(f"  Seriennummer: {usb.util.get_string(dev, dev.iSerialNumber)}")
        # print(f"  Konfiguration: {dev.bConfigurationValue}")
        print()

def deviceName():
    if dev is None:
        return ""

    bytes_name = dev.ctrl_transfer(0xc0, 0x28, 0, 21, 21).tobytes()
    
    # cut off zero termination
    null_byte_index = bytes_name.find(b'\x00')
    if null_byte_index != -1:
        bytes_name = bytes_name[:null_byte_index]
  
    return bytes_name.decode('latin-1')

def open():
    # init random mask
    random.seed(int(time.time() * 1000) % 1000)
    mask = bytearray(random.getrandbits(8) for _ in range(307200))

    # Suche nach dem USB-Gerät
    global dev 
    dev = usb.core.find(idVendor=0x04c5, idProduct=0x1084)
    print(type(dev))
    # Überprüfen, ob das Gerät gefunden wurde
    if dev is None:
        raise ValueError("Gerät nicht gefunden")

    # Setze die Konfiguration
    dev.set_configuration()

    data = dev.ctrl_transfer(0xc0, 0xa0, 0, 0, 3)
    print("Gelesene Daten:", ' '.join(format(byte, '02x') for byte in data))
    data = dev.ctrl_transfer(0xc0, 0x29, 0, 0, 4)
    print("Gelesene Daten:", ' '.join(format(byte, '02x') for byte in data))
    data = dev.ctrl_transfer(0xc0, 0x66, 0, 0, 3)
    print("Gelesene Daten:", ' '.join(format(byte, '02x') for byte in data))
    data = dev.ctrl_transfer(0xc0, 0xa3, 0, 0, 4)
    print("Gelesene Daten:", ' '.join(format(byte, '02x') for byte in data))
    
    device_name = deviceName()
    print("PalmSecure: Connected to device ", device_name)
        
    data = dev.ctrl_transfer(0xc0, 0x29, 1, 4, 4)
    print("Gelesene Daten:", ' '.join(format(byte, '02x') for byte in data))
    
    # We initialize device's random generator with this method, it seems
    rand1 = random.randint(0, 0xffff)
    rand2 = random.randint(0, 0xffff)
    key = dev.ctrl_transfer(0xc0, 0x35, rand1, rand2, 18 )
    dev.ctrl_transfer(0xc0, 0x36, 0, 0, 3)
    
    # "encrypt" mask and send it
    mask2 = (key[2:10] * 80) + (key[10:18] * 80)
    mask2 = mask2 * 240
    # XOR mask2 and mask
    for i in range(307200):
        mask2[i] ^= mask[i]


    res = bulk_send(0x01, mask2)
    print(f"PalmSecure: Wrote {res} bytes to device (should be 307200)")

    if res == -1:
        print("false")

    data = dev.ctrl_transfer(0xc0, 0x29, 1, 0, 4)   #returns 29010400 (probably means something)
    data = dev.ctrl_transfer(0xc0, 0xf6, 9, 0, 168) #returns a400000002000000d0051000b7071000d7a3703d0ad7fd3fd7a3703d0ad7a33f6666666666565e401c041000f80410003108ac1c5a640040367689eaad81ad3f713d0ad7a3605540e80210004b031000f0a7c64b378901404faf94658863b53f52b81e85eb314e400e0210003e021000fed478e9263102406002b7eee6a9be3fae47e17a144e4540740110008c011000cff753e3a59b024024624a24d1cbc43f0ad7a3703d0a3e40
    data = dev.ctrl_transfer(0xc0, 0xf6, 8, 0, 152) #returns 94000000010000000000000000000040000000000000324000000000000084400000000000007e40fa7e6abc7493783f0038b1e02533833fccc5bd1f468d54bf00001ae91ded883f00ac11642c67ed3f4ba5ca32f867b0bfc42951a36f36793f34fe9ffa4662f43fe3d40ddaa64bd53f9b186be9afb2d9bf693754c7b3e55240aee258d2929a67bf504164df91a63dbf953ead43900be9bf
    data = dev.ctrl_transfer(0xc0, 0xf6, 7, 0, 302) #returns 3401000001000000040000000000000061e849533fe226c0190e2d82fc2827c00000000000000000094155c358418b3f60805047ad44513fd6fd521d45ffef3f7eb6d422de042740cdccd212dc4a27c00000000000000000433ed92b619f7b3f0f25c8d5ce9661bf3816387acbffef3f29a96ce37edc26c072cc748eef102740000000000000000082f2c7d86e53933f9a4c9416e67b8a3f77fc4916dbfdef3fac1796de70ed2640e428b29c3ce02640000000000000000033f14bd221639f3ffd970612085827bf5f59a39326fcef3f020004004201f0004201ef004301f5004801f20000000000d2a12dffc12342400901b700f800a6007b01b6008c01a5000a012e01fa003e0180012a0191013b01bff27cd4352453402901d7001d01cb005b01d6006701ca002a010e011f01

    # switch off all lights?
    data = dev.ctrl_transfer(0xc0, 0x27, 0, 0, 6)    #returns 270000000000
    data = dev.ctrl_transfer(0xc0, 0x27, 0x05, 0, 8) #returns 2705000000000000
    data = dev.ctrl_transfer(0xc0, 0x27, 0x06, 0, 8) #returns 2706000000000000
    data = dev.ctrl_transfer(0xc0, 0x27, 0x07, 0, 8) #returns 2707000000000000
    data = dev.ctrl_transfer(0xc0, 0x27, 0x08, 0, 8) #returns 2708000000000000
    data = dev.ctrl_transfer(0xc0, 0x27, 0x09, 0, 8) #returns 2709000000000000
    data = dev.ctrl_transfer(0xc0, 0x27, 0x0a, 0, 8) #returns 270a000000000000
    data = dev.ctrl_transfer(0xc0, 0x27, 0x0b, 0, 8) #returns 270b000000000000
    data = dev.ctrl_transfer(0xc0, 0x27, 0x0c, 0, 8) #returns 270c000000000000
    
def start():
    True

if __name__ == "__main__":
    open()
    start()