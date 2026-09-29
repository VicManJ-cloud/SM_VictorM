import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

# Este nodo publica el estado de led cada segundo
class LedBlink(Node):
    def __init__(self):
        #se registra como led_blink
        super().__init__('led_blink')
        #se crea el publicador con el tipo de mensaje, el topico y el tamaño
        self.publisher_ = self.create_publisher(Int32, '/led_command', 10)
        #el estado inicial se define como encendido
        self.estado = 1
        #el temporizador llama a blink_callback cada segundo
        self.timer_ = self.create_timer(1.0, self.blink_callback)
        self.get_logger().info('Nodo iniciado')
        #se publica el estado
        self.publicar_estado()

    def blink_callback(self):
        # Aqui se invierte el estado de 1  a 0 o de 0 a 1
        if self.estado == 1:
            self.estado = 0
        else:
            self.estado = 1

        self.publicar_estado()
    #este metodo se llama desde el init y desde el callback
    def publicar_estado(self):
        #se crea el mensaje y se le pone el estado en camo de data
        msg = Int32()
        msg.data = self.estado
        #se envia el mensaje al topico  /led_command'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publicando: {self.estado}')

def main(args=None):
    #arranca el contexto de ros2
    rclpy.init(args=args)
    #se crea una instancia del nodo
    node = LedBlink()
    #spin deja corriendo pero en espera del temporizador
    rclpy.spin(node)
    #se libera el nodo y se cierra contexto
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
