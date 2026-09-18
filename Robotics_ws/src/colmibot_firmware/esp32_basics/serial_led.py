#se importa serial para comunicarse con el puerto serial y time
#para el sleep
import serial
import time
#El puerto y la velocidad que se usaran para la comunicacion
PORT = '/dev/ttyUSB0'
BAUDRATE = 115200
#Se abre el puerto, el timeout es el max de tiempo para cada lectura
esp32 = serial.Serial(PORT, BAUDRATE, timeout=1)
# se dejan correr 2 segundos
time.sleep(2)
#ciclo infinito
while True:
    #se espera hasta que se reciba algun dato
    dato = input("Escribe 1 para encender, 0 para apagar, q para salir: ")
    #se manda el 1 pero se manda como byte para encender
    if dato == '1':
        esp32.write(b'1\n')
    #se manda el 0 pero se manda como byte para apagar
    elif dato == '0':
        esp32.write(b'0\n')
    #se manda el q para detener el programa
    elif dato == 'q':
        break
#se cierra el puerto para liberarlo y pueda ser usado de nuevo
esp32.close()
