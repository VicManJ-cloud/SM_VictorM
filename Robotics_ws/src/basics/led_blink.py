import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class LedBlink(Node):
    def __init__(self):
        super().__init__('led_blink')
        self.publisher_ = self.create_publisher(Int32, '/led_command', 10)

        self.estado = 1
        self.timer_ = self.create_timer(1.0, self.blink_callback)
        self.get_logger().info('Nodo iniciado')
        self.publicar_estado()

    def blink_callback(self):
        if self.estado == 1:
            self.estado = 0
        else:
            self.estado = 1

        self.publicar_estado()

    def publicar_estado(self):
        msg = Int32()
        msg.data = self.estado

        self.publisher_.publish(msg)
        self.get_logger().info(f'Publicando: {self.estado}')

def main(args=None):
    rclpy.init(args=args)
    node = LedBlink()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
