import rclpy
from rclpy.node import Node

# Este tiene que ser del mismo tipo que el que usa el publisher,
# en este caso Twist
from geometry_msgs.msg import Twist

class VelocityTurtleSubscriber(Node):

    def __init__(self):
        # Se crea el nodo con el nombre de 'velocity_turtle_subscriber'
        super().__init__('velocity_turtle_subscriber')

        # Se crea una suscripcion que tiene como parametros el tipo de mensaje,
        # el topico al que se conecta, la funcion que se ejecuta al llegar un
        # dato y el tamano de la cola de QoS
        # Esto debe ser compatible con la cola de QoS del publisher
        # El topico es /turtle1/cmd_vel, el mismo donde escucha turtlesim, asi
        # que ese topico termina con dos suscriptores
        self.subscription_ = self.create_subscription(Twist,'/turtle1/cmd_vel',self.velocity_callback,10)

    def velocity_callback(self, msg):
        # Esta funcion no se manda a llamar, solo se ejecuta cuando llega
        # un nuevo dato

        # Se saca el contenido del mensaje, la velocidad translacional viene
        # en el campo linear.x del Twist
        Velocity = msg.linear.x

        # Se imprime para comparar si llegan bien los datos
        self.get_logger().info(f'Vel = {Velocity:.1f} m/s')


def main(args = None):
    # Arranca el contexto de ROS 2
    rclpy.init(args=args)

    # Se crea una instancia del nodo suscriptor
    node = VelocityTurtleSubscriber()

    # Aqui spin solo deja corriendo el nodo y esperando mensajes del topico
    # donde esta suscrito
    rclpy.spin(node)

    # Se cierra el nodo
    node.destroy_node()

    # Se cierra el contexto
    rclpy.shutdown()


if __name__ == '__main__':
    main()