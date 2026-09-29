#LaunchDescription es el objeto que describe todo lo que se va a lanzar
from launch import LaunchDescription
#Node representa cada nodo que se quiere ejecutar
from launch_ros.actions import Node


#esta funcion es la que ros2 launch busca y ejecuta, el nombre debe ser
#exactamente este
def generate_launch_description():

    #se devuelve una lista con los tres nodos del sistema del joystick
    return LaunchDescription([

        #primer nodo: el simulador, viene del paquete turtlesim y no del mio
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen'
        ),

        #segundo nodo: el que lee el puerto serial y publica los valores
        #crudos del joystick en /joystick_raw
        Node(
            package='basics',
            executable='joystick_serial_pub.py',
            output='screen'
        ),

        #tercer nodo: el que convierte esos valores en velocidades y las
        #manda a /turtle1/cmd_vel
        Node(
            package='basics',
            executable='turtle_controller.py',
            output='screen'
        ),
    ])
