import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import serial


class AnalogSerialPublisher(Node):
    def __init__(self):
        super().__init__('analog_serial_pub')

        self.publisher_ = self.create_publisher(Int32,'/analog', 10)
        self.serial_ = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        self.timer_ = self.create_timer(0.01, self.read_serial)
        self.get_logger().info('ESP32 conectada')

    def read_serial(self):
        if self.serial_.in_waiting > 0:
            linea = self.serial_.readline().decode().strip()

            if linea.isdigit():
                valor = int(linea)
                msg = Int32()
                msg.data = valor
                self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AnalogSerialPublisher()
    rclpy.spin(node)
    node.serial_.close()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
