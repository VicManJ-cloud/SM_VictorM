import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


# Este nodo publica 1 vez aproximadamente cada segundo
class VelocityPublisher(Node):

    def __init__(self):
        # Inicializa el nodo y se le nombra velocity_publisher, asi es como
        # aparece en la lista de nodos
        super().__init__('velocity_publisher')

        # Crea el publicador (con 3 argumentos: el tipo de mensaje, el topico
        # y el tamano de la cola)
        # el topico lleva diagonal, /velocity, para indicar que es una ruta absoluta
        # el tamano de cola es la cantidad de mensajes que se guardan, en este caso 10
        self.publisher_ = self.create_publisher(Float32,'/velocity',10)

        # Velocidad inicial del valor por publicar, se incrementa en cada publicacion
        self.Vel = 0.0

        # Este es un temporizador que llama a publish_velocity() cada segundo
        self.timer_ = self.create_timer(1.0,self.publish_velocity)

    def publish_velocity(self):
        # Se crea un mensaje con Float de 32 bits, este comenzara en 0.0
        msg = Float32()

        # Se copia la velocidad al campo data del mensaje
        msg.data = self.Vel

        # Se envia el mensaje al topico /velocity y de ahi llega a los nodos suscritos
        self.publisher_.publish(msg)

        # Imprime en la terminal el valor de lo que se publica
        self.get_logger().info(f'Vel = {self.Vel}')

        # Se incrementa la velocidad de 0.1 en 0.1 hasta llegar a 1.5
        # y despues se reinicia en 0.0
        if self.Vel < 1.5:
            self.Vel = round(self.Vel + 0.1, 1)
        else:
            self.Vel = 0.0

def main(args = None):
    # Arranca el contexto de ROS 2
    rclpy.init(args=args)

    # Se crea la instancia del nodo
    node = VelocityPublisher()

    # spin deja el nodo corriendo
    rclpy.spin(node)

    # Se libera el nodo y se cierra el contexto
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
