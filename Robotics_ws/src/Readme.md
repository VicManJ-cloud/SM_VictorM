# Práctica: Publicador y Suscriptor en ROS 2

**Alumno:** Victor Manuel Jimenez Gonzalez

**Entorno:** ROS 2 Jazzy Jalisco sobre Ubuntu 24.04

---

## 1. Descripción de la actividad

La actividad consiste en implementar la comunicación básica entre dos nodos de ROS 2 que
se ejecutan de manera simultánea en terminales distintas:

- `velocity_publisher.py`: publica un valor de velocidad en el tópico `/velocity`.
- `velocity_subscriber.py`: se suscribe a ese tópico, recibe los mensajes y los muestra
  en la terminal.

Además de escribir los nodos, se comprueba el funcionamiento del sistema con las
herramientas de línea de comandos de ROS 2 (`ros2 node`, `ros2 topic`) y con el grafo
de comunicación que genera `rqt_graph`.

---

## 2. Funcionamiento

### Tópico y tipo de mensaje

| Elemento | Valor |
|---|---|
| Tópico | `/velocity` |
| Tipo de mensaje | `std_msgs/msg/Float32` |
| Profundidad de cola (QoS) | 10 |
| Periodo de publicación | 1.0 s (1 Hz) |
| Dato publicado | rampa de 0.0 a 1.5 en pasos de 0.1 |

Se usa `std_msgs/msg/Float32` porque para esta práctica se usa una velocidad,
 y ese mensaje contiene un único campo `data` de tipo `float32`. El
nombre del tópico se escribe con diagonal inicial, `/velocity`, es decir como nombre
absoluto, de modo que se resuelve igual sin importar el namespace de los nodos.

### Publicador

`rclpy.init()` arranca el contexto de ROS 2 y en seguida se crea la clase
`VelocityPublisher`, que hereda de `Node` y se registra en el grafo con el nombre
`velocity_publisher`. En el constructor se crea el publicador con
`create_publisher(Float32, '/velocity', 10)` y se registra un temporizador con
`create_timer(1.0, self.publish_velocity)`, que es la forma de publicar periódicamente
en ROS 2 sin bloquear el nodo.

Cada segundo, `publish_velocity()` construye un mensaje `Float32`, le asigna el valor
actual de `self.Vel`, lo publica y lo imprime con el logger. Al final del callback
avanza la rampa: mientras el valor sea menor a 1.5 se le suman 0.1, y al rebasar ese
límite se reinicia en 0.0. El `round(self.Vel + 0.1, 1)` evita que se acumule el error
de representación de los flotantes. Que el dato cambie en cada ciclo permite verificar
con `ros2 topic echo` que la comunicación está activa.

### Suscriptor

`VelocitySubscriber` también hereda de `Node` y se registra con el nombre
`velocity_subscriber`. En el constructor se crea la suscripción con
`create_subscription(Float32, '/velocity', self.velocity_callback, 10)`. Para que la
conexión se establezca deben coincidir con el publicador el nombre del tópico, el tipo
de mensaje y un perfil de QoS compatible; si falla cualquiera de los tres, el nodo corre
sin marcar error pero nunca recibe nada.

A diferencia del publicador, este nodo no tiene temporizador ni ciclo propio: es
reactivo. `rclpy.spin()` lo deja en espera y el middleware ejecuta
`velocity_callback(msg)` cada vez que llega un mensaje. Dentro del callback se lee
`msg.data`, que es donde `Float32` transporta la información, y se imprime con un
decimal. Comparar esa salida contra la del publicador es la comprobación de que los
datos llegan completos y en orden.

---

## 3. Comandos utilizados

Los nodos se desarrollaron dentro de un paquete de ROS 2 llamado `basics`, ubicado en el
workspace `robotics_ws`. En este repositorio los scripts se entregan sueltos dentro de
`src` para cumplir con la estructura solicitada, por lo que se documentan las dos formas
de ejecutarlos.

### desde el paquete `basics`

Registro de los ejecutables en `setup.py`:

```python
entry_points={
    'console_scripts': [
        'velocity_publisher.py = basics.velocity_publisher:main',
        'velocity_subscriber.py = basics.velocity_subscriber:main',
    ],
},
```

Compilación del workspace:

```bash
cd ~/Documentos/SM_VictorM/robotics_ws
colcon build
ls install/basics/lib/basics/      # verifica que se generaron los ejecutables
```

**Terminal 1 — publicador**

```bash
source /opt/ros/jazzy/setup.bash
source ~/Documentos/SM_VictorM/robotics_ws/install/setup.bash
ros2 run basics velocity_publisher.py
```

**Terminal 2 — suscriptor**

```bash
source /opt/ros/jazzy/setup.bash
source ~/Documentos/SM_VictorM/robotics_ws/install/setup.bash
ros2 run basics velocity_subscriber.py
```



### Comprobación del funcionamiento

Con los dos nodos corriendo, desde una tercera terminal:

```bash
# Nodos activos: deben aparecer /velocity_publisher y /velocity_subscriber
ros2 node list

# Tópicos activos con su tipo de mensaje
ros2 topic list -t

# Publicadores y suscriptores conectados al tópico
ros2 topic info /velocity
ros2 topic info /velocity --verbose    # incluye el perfil de QoS

# Detalle del nodo suscriptor
ros2 node info /velocity_subscriber

# Estructura del mensaje utilizado
ros2 interface show std_msgs/msg/Float32

# Contenido de los mensajes que viajan por el tópico
ros2 topic echo /velocity

# Frecuencia real de publicación (debe rondar 1 Hz)
ros2 topic hz /velocity
```

La comprobación clave es `ros2 topic info /velocity`, donde debe reportarse un
publicador y un suscriptor conectados.

### Grafo de ROS

```bash
ros2 run rqt_graph rqt_graph
```

En el grafo se observa `/velocity_publisher` unido por una flecha etiquetada `/velocity`
hacia `/velocity_subscriber`. Hay que desmarcar la casilla *Debug* y presionar el botón
de refrescar para que se muestren los nodos.

---

## 4. Problemas encontrados y soluciones

**`Package 'basics' not found` al ejecutar `ros2 run`.**
La terminal no tenía cargado el workspace. Estar posicionado dentro de la carpeta no es
suficiente, porque ROS busca en las rutas que registran los archivos de entorno. Se
resolvió ejecutando `source /opt/ros/jazzy/setup.bash` y
`source ~/Documentos/SM_VictorM/robotics_ws/install/setup.bash` en cada terminal nueva.

**`ros2 run` no encontraba el ejecutable aunque `colcon build` terminaba bien.**
El bloque `entry_points` de `setup.py` estaba vacío, así que colcon instalaba el módulo
pero no generaba ningún ejecutable. Se resolvió declarando ambos nodos en
`console_scripts` y recompilando. La verificación es
`ls install/basics/lib/basics/`: si esa carpeta no existe, los ejecutables no se
generaron.

**`IndentationError: expected an indented block after class definition`.**
Los comentarios se habían escrito entre comillas en lugar de usar `#`. Un texto entre
comillas no es un comentario sino una cadena, y solo la primera de un bloque cuenta como
docstring, por lo que debe ir indentada. Se resolvió cambiando todos los comentarios a
`#`, que sí pueden ir en cualquier columna.

**Indentación inconsistente entre tabuladores y espacios.**
Algunas líneas empezaban con tabulador y otras con espacios, lo que Python interpreta
como niveles distintos. Se unificó todo a cuatro espacios. Para validar la sintaxis sin
tener que compilar y ejecutar se usó `python3 -m py_compile archivo.py`.

**El error de indentación seguía apareciendo después de corregir el archivo.**
`ros2 run` no ejecuta el archivo que se edita, sino la copia instalada en `install/`,
que solo se actualiza al recompilar. Se resolvió copiando los archivos corregidos a
`robotics_ws/src/basics/basics/` y volviendo a correr `colcon build` antes de probar.

**Traceback con `KeyboardInterrupt` al detener los nodos con `Ctrl+C`.**
No es una falla de funcionamiento: `rclpy.spin()` lanza esa excepción al recibir la
señal de interrupción y, al no estar atrapada, Python imprime el rastreo antes de salir.
Se dejó el comportamiento tal cual, ya que corresponde al código visto en clase. Puede
evitarse envolviendo `rclpy.spin(node)` en un bloque `try/except KeyboardInterrupt`.


---

## 5. Control de versiones

| Commit | Contenido |
|---|---|
| 1 | Nodos vistos en clase. |
| 2 | Suscriptor comentado y comprobación de funcionamiento. |
| 3 | Documentación de la práctica. |

https://drive.google.com/file/d/1KU2068QJYkuXJSf9DigumxEfl-JWwXP0/view?usp=drive_link
