import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class VelocitySubscriber(Node):

    def __init__(self):
        super().__init__('velocity_subscriber')
        self.subscription_ = self.create_subscription(Float32,'/velocity',self.velocity_callback,10)

    def velocity_callback(self, msg):
        Velocity = msg.data
        self.get_logger().info(f'Vel = {Velocity:.1f} m/s')


def main(args = None):
    rclpy.init(args=args)
    node = VelocitySubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
