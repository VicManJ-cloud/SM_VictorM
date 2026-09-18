import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import serial


class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')

        self.subscription_ = self.create_subscription(Int32, '/led_command', self.led_callback,10)
        self.serial_ = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

        self.get_logger().info('Esperando mensajes')

    def led_callback(self, msg):
        if msg.data == 1:
            self.serial_.write(b'1\n')
            self.get_logger().info('ROS 2 -> Serial: 1')

        elif msg.data == 0:
            self.serial_.write(b'0\n')
            self.get_logger().info('ROS 2 -> Serial: 0')


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    rclpy.spin(node)
    node.serial_.close()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
