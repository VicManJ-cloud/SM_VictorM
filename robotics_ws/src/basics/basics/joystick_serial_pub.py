import rclpy
from rclpy.node import Node
#Point tiene los campos x, y, z, se usan x e y para los dos ejes
#del joystick
from geometry_msgs.msg import Point
#libreria para leer el puerto serie de la esp32
import serial


#este nodo lee los dos valores que manda la esp32 y los publica en un
#topico, no manda nada a turtlesim, solo reparte el dato crudo
class JoystickSerialPublisher(Node):
    def __init__(self):
        #se registra el nodo con el nombre joystick_serial_pub
        super().__init__('joystick_serial_pub')

        #se crea el publicador sobre el topico /joystick_raw, el raw es
        #para dejar claro que son valores del ADC y no velocidades
        self.publisher_ = self.create_publisher(Point, '/joystick_raw', 10)

        #se abre el puerto serie con el mismo baudrate del sketch
        self.serial_ = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

        #el temporizador revisa el puerto cada 10 ms, mas seguido de lo
        #que manda la esp32, asi no se acumula retraso
        self.timer_ = self.create_timer(0.01, self.read_serial)
        self.get_logger().info('ESP32 conectada, leyendo joystick')

    def read_serial(self):
        #in_waiting dice cuantos bytes hay esperando en el buffer
        if self.serial_.in_waiting > 0:
            #se lee hasta el salto de linea y se limpia
            linea = self.serial_.readline().decode().strip()

            #la linea viene como "1890,1828", split la parte en dos
            partes = linea.split(',')

            #se verifica que hayan llegado los dos valores y que sean
            #numeros, al arrancar el buffer puede traer lineas cortadas
            if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit():
                msg = Point()
                #float porque los campos de Point son de tipo double
                msg.x = float(partes[0])
                msg.y = float(partes[1])
                self.publisher_.publish(msg)

def main(args=None):
    #arranca el contexto de ROS 2
    rclpy.init(args=args)
    #se crea la instancia del nodo
    node = JoystickSerialPublisher()
    #spin deja el nodo corriendo atendiendo el temporizador
    rclpy.spin(node)
    #se cierra el puerto para liberarlo
    node.serial_.close()
    #se libera el nodo y se cierra el contexto
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()