import rclpy
from rclpy.node import Node
#se usa el mismo tipo de mensaje que se publica en led_blink
from std_msgs.msg import Int32
#se importa para teneret comunicacion con el esp32 por el serial
import serial

#Este es el nodo "traductor" entre ros y el hardware. Escucha el topico y 
#lo traduce para mandarlo por el puerto serial
class SerialBridge(Node):
    def __init__(self):
        #se registra con el nombre serial_bridge
        super().__init__('serial_bridge')
        
        #se suscribe al topico led_command, y debe coincidir con el tipo de mensaje
        # y el topico del publicador
        self.subscription_ = self.create_subscription(Int32, '/led_command', self.led_callback,10)
        #se abre el puerto serial, se asigna el baudrate
        self.serial_ = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

        self.get_logger().info('Esperando mensajes')

    #se ejecuta cada vez que llega un mensaje al topico
    def led_callback(self, msg):
        #si llega un 1, se manda el caracter a la esp32 como bytes para encender el led
        if msg.data == 1:
            self.serial_.write(b'1\n')
            self.get_logger().info('ROS 2 -> Serial: 1')
        #si llega un 0 se apaga el led
        elif msg.data == 0:
            self.serial_.write(b'0\n')
            self.get_logger().info('ROS 2 -> Serial: 0')


def main(args=None):
    #arranca contexto de ros
    rclpy.init(args=args)
    #crea la instacia del nodo
    node = SerialBridge()
    #se deja al nodo esperando mensajes del topico
    rclpy.spin(node)
    #se cierra el puerto para liberarlo
    node.serial_.close()
    #se cierra el nodo y el contexto
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
