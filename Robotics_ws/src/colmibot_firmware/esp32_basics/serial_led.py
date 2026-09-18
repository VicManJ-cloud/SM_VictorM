import serial
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 115200

esp32 = serial.Serial(PORT, BAUDRATE, timeout=1)

time.sleep(2)

while True:

    dato = input("Escribe 1 para encender, 0 para apagar, q para salir: ")

    if dato == '1':
        esp32.write(b'1\n')

    elif dato == '0':
        esp32.write(b'0\n')

    elif dato == 'q':
        break

esp32.close()
