#Libreria para comunicarse con el puerto serial
import serial
#cosntantes para el puerto y el baudrate
PORT = '/dev/ttyUSB0'
BAUDRATE = 115200
#se abre el puerto, el timeout en segundos es lo maximo que espera una lectura
esp32 = serial.Serial(PORT, BAUDRATE, timeout=1)
#ciclo infinito
while True:
    #readline lee bytes hasta el salto de linea
    #decode pasa a texto
    #strip quita el salto de linea y espacios dejando solo digitos
    linea = esp32.readline().decode().strip()
    
    #Si la cadena cumple el timeoit sin que llegue nada, readline regresa
    #una cadena vacia.  Evita imprimir lineas en blanco
    if linea:
        print(f'ADC = {linea}')
