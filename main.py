import usb.core
import usb.util



# Alle USB-Geräte auflisten
devices = usb.core.find(find_all=True)

# Durch die gefundenen Geräte iterieren und Informationen ausgeben
for dev in devices:
    print(f"Gerät: {dev.idVendor:04x}:{dev.idProduct:04x}")
    print(f"  Hersteller: {usb.util.get_string(dev, dev.iManufacturer)}")
    print(f"  Produkt: {usb.util.get_string(dev, dev.iProduct)}")
    print(f"  Seriennummer: {usb.util.get_string(dev, dev.iSerialNumber)}")
    # print(f"  Konfiguration: {dev.bConfigurationValue}")
    print()


# Suche nach dem USB-Gerät
dev = usb.core.find(idVendor=0x04c5, idProduct=0x1084)

# Überprüfen, ob das Gerät gefunden wurde
if dev is None:
    raise ValueError("Gerät nicht gefunden")

# Setze die Konfiguration
dev.set_configuration()

# Beispiel: Lese Daten von einem Endpunkt
endpoint = dev[0][(0,0)][0]  # Ersetze dies durch den richtigen Endpunkt
data = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)

print("Gelesene Daten:", data)