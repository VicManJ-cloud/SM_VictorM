import rclpy
from rclpy.node import Node
#Point es el tipo que publica el nodo del joystick
from geometry_msgs.msg import Point
#Twist es el tipo que entiende turtlesim para mover la tortuga
from geometry_msgs.msg import Twist


#este nodo recibe los valores directos del joystick y los convierte en
#velocidades para la tortuga
class TurtleController(Node):
    def __init__(self):
        #se registra el nodo con el nombre turtle_controller
        super().__init__('turtle_controller')

        #se suscribe al topico donde publica el nodo del joystick
        self.subscription_ = self.create_subscription(Point, '/joystick_raw', self.joystick_callback, 10)

        #se publica en el topico que escucha turtlesim
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        #valores de reposo medidos con el joystick sin tocar, no son
        #2048 porque el modulo no queda centrado por default
        self.centro_x = 1890
        self.centro_y = 1828

        #zona muerta en unidades del ADC, si la lectura se aleja menos
        #que esto del centro se toma como cero ya que las mediciones
        #se pone 100 por que hay variaciones de 60  puntos
        self.zona_muerta = 100

        #velocidades maximas, la tortuga llega a estas cuando el
        #joystick esta en el tope
        self.vel_lineal_max = 2.0
        self.vel_angular_max = 2.0

        self.get_logger().info('Controlador listo, esperando joystick')

    #convierte una lectura del ADC del ESP32
     # en un valor de -1.0 a 1.0
    def normalizar(self, valor, centro, vel_max):
        #primero calculamos cual seria el centro
        #distancia del centro, positiva o negativa segun el lado
        desviacion = valor - centro

        #si esta dentro de la zona muerta se devuelve cero, asi el ruido
        #del ADC no mueve la tortuga
        if abs(desviacion) < self.zona_muerta:
            return 0.0

        #el recorrido no es igual de los dos lados porque el centro no
        #esta a la mitad, por eso cada lado se divide entre su propio
        #rango y asi la velocidad maxima es la misma en ambos sentidos
        if desviacion > 0:
            rango = 4095 - centro - self.zona_muerta
            desviacion = desviacion - self.zona_muerta
        else:
            rango = centro - self.zona_muerta
            desviacion = desviacion + self.zona_muerta

        #regla de tres: la desviacion se escala al rango de velocidad
        return (desviacion / rango) * vel_max

    def joystick_callback(self, msg):
        #se ejecuta cada vez que llega una lectura del joystick

        #el eje Y va invertido: arriba da 0 y abajo 4095, pero arriba
        #debe avanzar, por eso el signo negativo
        lineal = -self.normalizar(msg.y, self.centro_y, self.vel_lineal_max)

        #el eje X tambien se invierte: derecha da 4095, pero en ROS un
        #angular.z positivo gira a la izquierda
        angular = -self.normalizar(msg.x, self.centro_x, self.vel_angular_max)

        #se arma el mensaje de velocidad y se manda a turtlesim
        cmd = Twist()
        cmd.linear.x = lineal
        cmd.angular.z = angular
        self.publisher_.publish(cmd)

        self.get_logger().info(f'lineal = {lineal:.2f} | angular = {angular:.2f}')

def main(args=None):
    #arranca el contexto de ROS 2
    rclpy.init(args=args)
    #se crea la instancia del nodo
    node = TurtleController()
    #spin deja el nodo esperando mensajes del topico
    rclpy.spin(node)
    #se libera el nodo y se cierra el contexto
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()