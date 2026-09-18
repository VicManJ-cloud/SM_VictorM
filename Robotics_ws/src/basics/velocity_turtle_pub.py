import rclpy
from rclpy.node import Node

# Ahora el mensaje es Twist y no Float32, porque turtlesim solo entiende
# ese tipo en el topico /turtle1/cmd_vel
from geometry_msgs.msg import Twist


# Este nodo publica 1 vez cada medio segundo
class VelocityTurtlePublisher(Node):

    def __init__(self):
        # Inicializa el nodo y se le nombra velocity_turtle_publisher, asi es
        # como aparece en la lista de nodos
        super().__init__('velocity_turtle_publisher')

        # Crea el publicador (con 3 argumentos: el tipo de mensaje, el topico
        # y el tamano de la cola)
        # el topico es /turtle1/cmd_vel, que es donde turtlesim escucha los
        # comandos de movimiento de la tortuga
        # el tamano de cola es la cantidad de mensajes que se guardan, en este caso 10
        self.publisher_ = self.create_publisher(Twist,'/turtle1/cmd_vel',10)

        # Velocidad inicial del valor por publicar, se va incrementando en cada
        # publicacion hasta que la tortuga se detiene
        self.Vel = 0.0

        # Bandera que indica si la tortuga ya llego a 1.2 y se detuvo.
        # Sin ella la rampa volveria a arrancar al poner la velocidad en 0.0
        self.detenido = False

        # Este es un temporizador que llama a publish_velocity() cada medio segundo
        self.timer_ = self.create_timer(0.5,self.publish_velocity)

    def publish_velocity(self):
        # Se crea el mensaje Twist. Los parentesis son necesarios para crear
        # una instancia; sin ellos se estaria usando la clase
        msg = Twist()

        # La velocidad translacional de la tortuga es el campo linear.x
        msg.linear.x = self.Vel

        # Se deja el giro en cero para que la tortuga avance en linea recta
        msg.angular.z = 0.0

        # Se envia el mensaje al topico /turtle1/cmd_vel y de ahi llega a
        # turtlesim y a los demas nodos suscritos.
        # El nodo sigue publicando aunque la velocidad ya sea 0.0, asi el
        # topico no se queda mudo y se puede seguir comprobando con
        # ros2 topic echo y ros2 topic hz
        self.publisher_.publish(msg)

        # Imprime en la terminal el valor de lo que se publica
        self.get_logger().info(f'Vel = {self.Vel}')

        # Se incrementa la velocidad de 0.1 en 0.1 hasta llegar a 1.2.
        # Como el publish ya paso, el 1.2 si alcanza a mandarse; lo que hace el
        # else es dejar la velocidad en 0.0 para el siguiente ciclo y levantar
        # la bandera, para que la tortuga se detenga y ya no vuelva a acelerar
        if not self.detenido:
            if self.Vel < 1.2:
                self.Vel = round(self.Vel + 0.1, 1)
            else:
                self.Vel = 0.0
                self.detenido = True

def main(args = None):
    # Arranca el contexto de ROS 2
    rclpy.init(args=args)

    # Se crea la instancia del nodo
    node = VelocityTurtlePublisher()

    # spin deja el nodo corriendo
    rclpy.spin(node)

    # Se libera el nodo y se cierra el contexto
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()