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
`src` para cumplir con la estructura solicitada, por lo que se documenta a continuación
la forma de ejecutarlos desde el paquete.

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

## 5. Evidencia en video

https://drive.google.com/file/d/1KU2068QJYkuXJSf9DigumxEfl-JWwXP0/view?usp=drive_link

---

## 6. Control de versiones

| Commit | Contenido |
|---|---|
| 1 | Nodos vistos en clase. |
| 2 | Suscriptor comentado y comprobación de funcionamiento. |
| 3 | Documentación de la práctica. |

---

# Act2 - Pub y subs de velocidad Turtlesim

## 1. Descripción de la actividad

A partir de los nodos de la actividad anterior se generaron dos copias,
`velocity_turtle_publisher.py` y `velocity_turtle_subscriber.py`, y se modificaron para
mover la tortuga de turtlesim.

El publicador manda la velocidad translacional de la tortuga empezando en 0.0, con un
incremento de 0.1 cada medio segundo hasta llegar a 1.2, y al alcanzar ese valor la
tortuga se detiene. El suscriptor escucha lo que publica ese nodo y muestra la velocidad
en la terminal.

> Nota: el enunciado menciona el nombre `velocity_turtle_pub.py`; en este repositorio el
> archivo se entrega como `velocity_turtle_publisher.py`.

---

## 2. Modificaciones realizadas

### En el publicador

| Antes | Después | Motivo |
|---|---|---|
| `from std_msgs.msg import Float32` | `from geometry_msgs.msg import Twist` | Turtlesim solo entiende mensajes `Twist` para mover la tortuga. |
| Nodo `velocity_publisher` | Nodo `velocity_turtle_publisher` | Dos nodos con el mismo nombre no se distinguen en el grafo. |
| Tópico `/velocity` | Tópico `/turtle1/cmd_vel` | Es el tópico donde turtlesim escucha los comandos de movimiento. |
| `create_timer(1.0, ...)` | `create_timer(0.5, ...)` | El incremento debe ocurrir cada medio segundo. |
| `msg.data = self.Vel` | `msg.linear.x = self.Vel` | `Twist` es un mensaje compuesto; la velocidad translacional es `linear.x`. |
| Rampa hasta 1.5 con reinicio | Rampa hasta 1.2 con bandera `detenido` | La tortuga debe detenerse al llegar al límite y no volver a acelerar. |

El cambio de fondo está en la lógica de la rampa. En la actividad anterior el valor se
reiniciaba en 0.0 y volvía a subir, formando un ciclo infinito. Aquí eso no sirve: al
poner la velocidad en 0.0 la condición `self.Vel < 1.2` volvería a cumplirse y la
tortuga arrancaría de nuevo. Por eso se agregó la bandera `self.detenido`, que al
levantarse impide que el bloque vuelva a ejecutarse.

También se agregó `msg.angular.z = 0.0` para que la tortuga avance en línea recta sin
girar.

Como el `publish()` ocurre antes de evaluar la rampa, el valor 1.2 sí alcanza a
publicarse; lo que hace el `else` es dejar la velocidad en 0.0 para el siguiente ciclo.
El nodo sigue publicando ceros en lugar de dejar de publicar, para que el tópico no
quede mudo y se pueda seguir comprobando con `ros2 topic echo` y `ros2 topic hz`.

### En el suscriptor

| Antes | Después | Motivo |
|---|---|---|
| `from std_msgs.msg import Float32` | `from geometry_msgs.msg import Twist` | Debe coincidir con el tipo que usa el publicador. |
| Nodo `velocity_subscriber` | Nodo `velocity_turtle_subscriber` | Para distinguirlo del nodo de la actividad anterior. |
| Tópico `/velocity` | Tópico `/turtle1/cmd_vel` | Es donde publica el nuevo nodo publicador. |
| `Velocity = msg.data` | `Velocity = msg.linear.x` | El dato ya no es un número suelto, sino un campo dentro del `Twist`. |

---

## 3. Funcionamiento

| Elemento | Valor |
|---|---|
| Tópico | `/turtle1/cmd_vel` |
| Tipo de mensaje | `geometry_msgs/msg/Twist` |
| Profundidad de cola (QoS) | 10 |
| Periodo de publicación | 0.5 s (2 Hz) |
| Dato publicado | rampa de 0.0 a 1.2 en pasos de 0.1, después 0.0 permanente |

`geometry_msgs/msg/Twist` es un mensaje compuesto: contiene dos vectores, `linear` y
`angular`, cada uno con componentes `x`, `y`, `z`. La velocidad translacional
corresponde a `linear.x` y el giro sobre el propio eje a `angular.z`. Su estructura se
puede consultar con `ros2 interface show geometry_msgs/msg/Twist`.

El publicador crea el publicador sobre `/turtle1/cmd_vel` y un temporizador de medio
segundo. En cada llamada construye un `Twist`, le asigna la velocidad actual en
`linear.x`, lo publica y avanza la rampa mientras la bandera `detenido` sea falsa.

El suscriptor declara la suscripción al mismo tópico y con el mismo tipo de mensaje, y
en su callback lee `msg.linear.x` para imprimirlo. No tiene temporizador ni ciclo
propio: es reactivo, y el middleware ejecuta el callback cada vez que llega un mensaje.

Un detalle importante de esta actividad es que `/turtle1/cmd_vel` termina con **dos
suscriptores**: el nodo `turtlesim`, que mueve la tortuga, y
`velocity_turtle_subscriber`, que imprime el dato. Esto muestra que un mismo tópico
puede alimentar a varios nodos independientes sin que el publicador sepa quiénes son.

---

## 4. Comandos utilizados

Registro de los nuevos ejecutables en `setup.py`:

```python
entry_points={
    'console_scripts': [
        'velocity_publisher.py = basics.velocity_publisher:main',
        'velocity_subscriber.py = basics.velocity_subscriber:main',
        'velocity_turtle_publisher.py = basics.velocity_turtle_publisher:main',
        'velocity_turtle_subscriber.py = basics.velocity_turtle_subscriber:main',
    ],
},
```

Compilación:

```bash
cd ~/Documentos/SM_VictorM/robotics_ws
colcon build
ls install/basics/lib/basics/
```

Ejecución, cada nodo en su propia terminal y con el entorno cargado en todas:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Documentos/SM_VictorM/robotics_ws/install/setup.bash
```

```bash
# Terminal 1: simulador
ros2 run turtlesim turtlesim_node

# Terminal 2: publicador
ros2 run basics velocity_turtle_publisher.py

# Terminal 3: suscriptor
ros2 run basics velocity_turtle_subscriber.py
```

### Comprobación del funcionamiento

Desde una cuarta terminal:

```bash
# Nodos activos: turtlesim, publicador y suscriptor
ros2 node list

# Tópicos activos con su tipo de mensaje
ros2 topic list -t

# Publicadores y suscriptores del tópico: debe reportar 2 suscriptores
ros2 topic info /turtle1/cmd_vel
ros2 topic info /turtle1/cmd_vel --verbose

# Detalle del nodo suscriptor
ros2 node info /velocity_turtle_subscriber

# Estructura del mensaje utilizado
ros2 interface show geometry_msgs/msg/Twist

# Contenido de los mensajes que viajan por el tópico
ros2 topic echo /turtle1/cmd_vel

# Frecuencia real de publicación (debe rondar 2 Hz)
ros2 topic hz /turtle1/cmd_vel
```

### Grafo de ROS

```bash
ros2 run rqt_graph rqt_graph
```

En el grafo se observa `/velocity_turtle_publisher` publicando en `/turtle1/cmd_vel`, y
de ese tópico salen dos flechas: una hacia `/turtlesim` y otra hacia
`/velocity_turtle_subscriber`.

---

## 5. Problemas encontrados y soluciones

**`msg = Twist` sin paréntesis.**
Al escribir el mensaje sin los paréntesis se estaba asignando la clase en lugar de crear
una instancia, por lo que la asignación de `linear.x` no correspondía a ningún mensaje.
Se corrigió con `msg = Twist()`, que es lo que ejecuta el constructor.

**`NameError` al ejecutar los nodos nuevos.**
Como los archivos se generaron copiando los originales, en la función `main` quedó el
nombre de la clase anterior (`VelocityPublisher` y `VelocitySubscriber`). El error no
aparece al validar con `python3 -m py_compile`, porque Python resuelve los nombres hasta
la ejecución. Se corrigió usando `VelocityTurtlePublisher` y `VelocityTurtleSubscriber`.

**El grafo de `rqt_graph` aparecía vacío y después saturado.**
La primera vez solo se veía el nodo del propio rqt, porque los nodos no estaban
corriendo al abrirlo. Al levantarlos y refrescar aparecieron todos, pero junto con los
tópicos internos de ROS y los de acción de turtlesim, que hacían ilegible el diagrama.
Se resolvió levantando los nodos antes de abrir la herramienta y filtrando con las
casillas *Debug*, *Dead sinks*, *Leaf topics* y desmarcando *Actions*.

**Los cambios no se reflejaban al ejecutar.**
`ros2 run` no ejecuta el archivo que se edita, sino la copia instalada en `install/`. Se
resolvió copiando los archivos al paquete y volviendo a correr `colcon build` antes de
cada prueba.

---

## 6. Evidencia en video

**Enlace:** `<pegar aquí la liga del video de la actividad 2>`

---

## 7. Control de versiones

| Commit | Contenido |
|---|---|
| 1 | Copias de los scripts originales con los nuevos nombres. |
| 2 | Nodos de la tortuga funcionando y comprobados. |
| 3 | Documentación de la actividad. |


