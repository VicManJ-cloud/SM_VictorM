#LaunchDescription es el objeto que describe todo lo que se va a lanzar
from launch import LaunchDescription
#Node representa cada nodo que se quiere ejecutar
from launch_ros.actions import Node


#esta funcion es la que ros2 launch busca y ejecuta, el nombre debe ser
#exactamente este
def generate_launch_description():

    #se devuelve una lista con los nodos a lanzar
    return LaunchDescription([

        #primer nodo: el publicador
        #package es el paquete donde vive
        #executable es el nombre registrado en el entry_points del setup.py
        #output='screen' hace que los mensajes del logger salgan en la terminal
        Node(
            package='basics',
            executable='velocity_publisher.py',
            output='screen'
        ),

        #segundo nodo: el suscriptor
        Node(
            package='basics',
            executable='velocity_subscriber.py',
            output='screen'
        ),
    ])
