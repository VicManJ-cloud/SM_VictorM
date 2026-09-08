import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class VelocityPublisher(Node):

    def __init__(self):
        super().__init__('velocity_publisher')

        self.publisher_ = self.create_publisher(Float32,'/velocity',10)
        self.Vel = 0.0
        self.timer_ = self.create_timer(1.0,self.publish_velocity)

    def publish_velocity(self):
        msg = Float32()
        msg.data = self.Vel
        self.publisher_.publish(msg)

        self.get_logger().info(f'Vel = {self.Vel}')

        if self.Vel < 1.5:
            self.Vel = round(self.Vel + 0.1, 1)
        else:
            self.Vel = 0.0

def main(args = None):
    rclpy.init(args=args)
    node = VelocityPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
