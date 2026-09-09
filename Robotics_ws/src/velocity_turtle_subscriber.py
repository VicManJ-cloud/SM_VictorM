import rclpy
from rclpy.node import Node

# Este tiene que ser del mismo tipo que el que usa el publisher,
# en este caso Float32
from std_msgs.msg import Float32


class VelocitySubscriber(Node):

    def __init__(self):
        # Se crea el nodo con el nombre de 'velocity_subscriber'
        super().__init__('velocity_subscriber')

        # Se crea una suscripcion que tiene como parametros el tipo de mensaje,
        # el topico al que se conecta, la funcion que se ejecuta al llegar un
        # dato y el tamano de la cola de QoS
        # Esto debe ser compatible con la cola de QoS del publisher
        self.subscription_ = self.create_subscription(Float32,'/velocity',self.velocity_callback,10)

    def velocity_callback(self, msg):
        # Esta funcion no se manda a llamar, solo se ejecuta cuando llega
        # un nuevo dato

        # Se saca el contenido del mensaje
        Velocity = msg.data

        # Se imprime para comparar si llegan bien los datos
        self.get_logger().info(f'Vel = {Velocity:.1f} m/s')


def main(args = None):
    # Arranca el contexto de ROS 2
    rclpy.init(args=args)

    # Se crea una instancia del nodo suscriptor
    node = VelocitySubscriber()

    # Aqui spin solo deja corriendo el nodo y esperando mensajes del topico
    # donde esta suscrito
    rclpy.spin(node)

    # Se cierra el nodo
    node.destroy_node()

    # Se cierra el contexto
    rclpy.shutdown()


if __name__ == '__main__':
    main()