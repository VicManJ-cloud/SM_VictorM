import serial

PORT = '/dev/ttyUSB0'
BAUDRATE = 115200

esp32 = serial.Serial(PORT, BAUDRATE, timeout=1)

while True:
    linea = esp32.readline().decode().strip()

    if linea:
        print(f'ADC = {linea}')
