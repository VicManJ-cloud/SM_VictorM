import rclpy
from rclpy.node import Node
#en este caso se usa int 32 por que se ocupa un numero entero
from std_msgs.msg import Int32
#libreria para leer del puerto serial
import serial

#Este nodo lee lo que manda la esp32 y lo publica en un topico
#es el complemento del bridge, este va de hardware a ros
class AnalogSerialPublisher(Node):
    def __init__(self):
        #se registra con el nombre de analog_serial_pub
        super().__init__('analog_serial_pub')

        #se crea el nodo publicador sobre el topico /analog
        self.publisher_ = self.create_publisher(Int32,'/analog', 10)
        #se abre el puerto serial con el mismo baudrate que el ino
        self.serial_ = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        #el temporizador revisa el puerto cada .01s
        self.timer_ = self.create_timer(0.01, self.read_serial)
        self.get_logger().info('ESP32 conectada')

    def read_serial(self):
        #in_waiting dice cuantos bytes hay esperando en el buffer, sino hay nada, no hace nada
        #y espera al sig ciclo
        if self.serial_.in_waiting > 0:
            #lee hasta el sig salto de linea, se pasa a texto y se quitan el salto y los espacios
            linea = self.serial_.readline().decode().strip()
            
            #si es digito entra entra
            if linea.isdigit():
                #se convierte el texto a entero y se manda el mensaje
                valor = int(linea)
                msg = Int32()
                msg.data = valor
                self.publisher_.publish(msg)

def main(args=None):
    #arranca contexto de ros
    rclpy.init(args=args)
    #se crea instancia de nodo
    node = AnalogSerialPublisher()
    #se inicia spin con el temporizador
    rclpy.spin(node)
    #se cierra el puerto para su liberacion
    node.serial_.close()
    #se libera el nodo y se destruye, se cierra contexto
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
