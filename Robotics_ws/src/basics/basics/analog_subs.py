import rclpy
from rclpy.node import Node
#tipo de mensaje es el mismo que publica analog_serial_pub
from std_msgs.msg import Int32

#este nodo escucha el topico e imprime el valor
class AnalogSubscriber(Node):
    def __init__(self):
        #se inicia con el nombre de analog_subscriber
        super().__init__('analog_subscriber')

        #se suscribe al topico /analog, ya que debe coincidir en topico, tipo de mensaje
        #y QoS con el publicador
        self.subscription_ = self.create_subscription(Int32, '/analog', self.analog_callback, 10)
        self.get_logger().info('Esperando datos')
    #se ejecuta cada que llega un mensaje al al topico
    def analog_callback(self, msg):
        #se saca el valor del campo data y se imprime
        valor = msg.data
        self.get_logger().info(f'ADC = {valor}')

def main(args=None):
    #se inicia el contexto de ros
    rclpy.init(args=args)
    #se instancia el nodo
    node = AnalogSubscriber()
    #se deja spin en espera de mensaje del topico
    rclpy.spin(node)
    #se libera  puerto, se destruye el nodo y libera contexto
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
