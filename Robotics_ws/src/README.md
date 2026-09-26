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

---

# Act3-Publicador y publicador serial

## 1. Descripción de la actividad

En esta actividad se integró una tarjeta ESP32 al entorno de ROS 2 a través de la
comunicación por puerto serial, trabajando los ejemplos vistos en clase.

El repositorio se reorganizó en dos directorios: `basics/`, con los nodos de ROS 2, y
`colmibot_firmware/esp32_basics/`, con los sketches de Arduino y los scripts de Python
que hablan directamente con la tarjeta.

## 2. Preparación del entorno

Se instaló el Arduino IDE 2.3.10 como AppImage y, desde el Board Manager, el paquete
**esp32 by Espressif Systems**. La tarjeta utilizada se selecciona en el IDE como
*DOIT ESP32 DEVKIT V1* y aparece en Linux como el puerto `/dev/ttyUSB0`.

```bash
# Verificar que el sistema reconoce la tarjeta
ls /dev/ttyUSB*

# Permiso para escribir en el puerto serial (requiere cerrar sesión)
sudo usermod -aG dialout $USER
groups | grep dialout

# Biblioteca de Python para el puerto serial
sudo apt install python3-serial
```

---

## 3. Ejemplo del LED

En este ejemplo la información va de la computadora hacia el hardware: ROS 2 manda
comandos de encendido y apagado y la ESP32 los ejecuta sobre un LED.

Se comprobó en tres niveles, uno sobre otro. Esto permite aislar en qué capa está una
falla si algo no funciona.

### Nivel 1: el sketch en la ESP32

`LED_Serial.ino` es el único código que no corre en la computadora, sino dentro del
microcontrolador. Define el GPIO 2, donde está el LED azul integrado de la tarjeta, lo
configura como salida e inicia el puerto serial a 115200 baudios.

En el `loop()` revisa con `Serial.available()` si hay bytes esperando en el buffer de
entrada. Si los hay, lee un carácter y lo compara: si es `'1'` pone el pin en alto y el
LED enciende, si es `'0'` lo pone en bajo y se apaga. La comparación es contra el
carácter y no contra el número entero.

La comprobación de este nivel se hizo desde el Serial Monitor del IDE, configurado a
115200, escribiendo 1 y 0 a mano.

### Nivel 2: Python sin ROS

`serial_led.py` hace lo mismo que el Serial Monitor, pero desde Python. Abre el puerto
con la biblioteca pyserial y, en un ciclo, pide al usuario que escriba 1, 0 o q, y envía
el carácter correspondiente como bytes.

Tiene una pausa de dos segundos después de abrir el puerto: al establecerse la conexión
serial con la ESP32 se reinicia, y sin esa espera los primeros comandos se pierden mientras
la tarjeta arranca.

### Nivel 3: los nodos de ROS 2

Aquí la comunicación pasa por un tópico, lo que separa la lógica del control de la
lógica del hardware.

| Elemento | Valor |
|---|---|
| Tópico | `/led_command` |
| Tipo de mensaje | `std_msgs/msg/Int32` |
| Profundidad de cola (QoS) | 10 |
| Periodo de publicación | 1.0 s |

Se usa `Int32` porque el comando solo necesita ser 1 o 0; no hace falta un flotante ni
un mensaje compuesto.

**`led_blink.py`** publica el estado del LED en `/led_command`. Arranca con el estado en
1 y un temporizador de un segundo que invierte ese valor en cada llamada, de modo que el
ciclo completo de parpadeo dura dos segundos. El constructor publica una primera vez
antes de que el temporizador entre en acción, para que el LED responda de inmediato y no
después del primer segundo.

**`serial_bridge.py`** es el puente entre ROS y el hardware. Se suscribe a
`/led_command` y abre el puerto serial. Cada vez que llega un mensaje, traduce el entero
recibido al carácter equivalente y lo escribe en el puerto: el mensaje trae el número 1,
pero lo que viaja por el cable es el carácter `'1'`, que es lo que el sketch espera.

Lo importante de esta separación es que `led_blink.py` no sabe nada de la ESP32 ni del
puerto serial: solo publica números en un tópico. Se podría cambiar la tarjeta o la forma
de conectarla modificando únicamente el puente, sin tocar el nodo que genera los
comandos.

### Comandos utilizados

```bash
# Compilación del paquete
cd ~/Documentos/SM_VictorM/robotics_ws
colcon build
ls install/basics/lib/basics/

# En cada terminal
source /opt/ros/jazzy/setup.bash
source ~/Documentos/SM_VictorM/robotics_ws/install/setup.bash
```

```bash
# Terminal 1: el puente, se levanta primero porque es quien abre el puerto
ros2 run basics serial_bridge.py

# Terminal 2: el nodo que publica el parpadeo
ros2 run basics led_blink.py
```

Comprobación desde una tercera terminal:

```bash
# Nodos activos: /led_blink y /serial_bridge
ros2 node list

# Tópicos con su tipo de mensaje
ros2 topic list -t

# Publicadores y suscriptores del tópico
ros2 topic info /led_command
ros2 topic info /led_command --verbose

# Detalle del nodo puente
ros2 node info /serial_bridge

# Contenido de los mensajes
ros2 topic echo /led_command

# Frecuencia de publicación
ros2 topic hz /led_command

# Grafo de comunicación
ros2 run rqt_graph rqt_graph
```

En el grafo se observa `/led_blink` publicando en `/led_command` y `/serial_bridge`
suscrito a ese tópico.

También se comprobó publicando el comando de forma manual, con el nodo `led_blink`
detenido:

```bash
ros2 topic pub --once /led_command std_msgs/msg/Int32 "{data: 1}"
```

El LED enciende y permanece encendido, lo que confirma que el puente responde a
cualquier publicador y no solo al nodo del parpadeo.

### Problemas encontrados y soluciones

**`Permission denied: '/dev/ttyUSB0'` al subir el sketch.**
La tarjeta era reconocida por el sistema, pero el usuario no pertenecía al grupo
`dialout`, que es el que tiene permiso de escritura sobre los puertos seriales. Se resolvió
con `sudo usermod -aG dialout $USER`. El cambio no surte efecto hasta cerrar sesión y
volver a entrar, porque los grupos se asignan al iniciar sesión; como solución temporal
puede usarse `sudo chmod 666 /dev/ttyUSB0`.

**El Arduino IDE no abría por un error de sandbox.**
El AppImage está basado en Electron, y Ubuntu 24.04 restringe la creación de espacios de
nombres de usuario sin privilegios, que es lo que el sandbox necesita. Se resolvió
ejecutándolo con la opción `--no-sandbox`.

**`IndentationError` en `setup.py` al compilar.**
Al agregar los nuevos ejecutables, el bloque `entry_points` quedó duplicado y colocado
después del paréntesis que cierra la llamada a `setup()`, lo que dejó código indentado
fuera de cualquier bloque. Se resolvió reescribiendo el archivo con un solo bloque.

**`IndentationError` en `led_blink.py`.**
El archivo tenía la última línea de `main()` con tres espacios en lugar de cuatro. Se
corrigió unificando la indentación.

**`SyntaxError` al comentar el código.**
A una línea de comentario se le olvidó el `#` inicial, y Python intentó interpretarla
como código. A diferencia de Arduino, que tiene `/* */` para bloques, en Python cada
línea de comentario necesita su propio símbolo. Para detectar este tipo de errores sin
tener que recompilar todo el paquete se usó `python3 -m py_compile archivo.py`.

**Los cambios no se reflejaban al ejecutar.**
`ros2 run` no ejecuta los archivos que se editan en el repositorio, sino la copia
instalada en `install/`. Cada vez que se modifica un nodo hay que copiarlo al paquete y
volver a correr `colcon build`.

### Evidencia en video

**Enlace:** [Video del ejemplo del LED](https://drive.google.com/file/d/1qnMKwCRMwNu4t9Ia2L7cUFXtskBHE2zh/view?usp=drive_link)
---

## 4. Ejemplo del potenciómetro

En este ejemplo la información va en sentido contrario al anterior: el dato nace en el
hardware y llega a ROS 2. La ESP32 lee un valor analógico y lo envía por el puerto
serial, y del lado de la computadora se publica en un tópico.

Se comprobó con los mismos tres niveles que el ejemplo del LED.

### Conexión

El potenciómetro se conecta con la pata de en medio al GPIO 15 y las de los extremos a
3.3 V y GND. Las dos patas de los extremos son intercambiables; lo único que cambia es
hacia qué lado sube el valor al girar la perilla.

### Nivel 1: el sketch en la ESP32

`ADC_Pot.ino` define el GPIO 15 como entrada del potenciómetro e inicia el puerto serial
a 115200 baudios. Las entradas analógicas no necesitan `pinMode`, a diferencia de las
salidas digitales del ejemplo anterior.

En el `loop()`, `analogRead()` convierte el voltaje presente en el pin a un número
entero. El convertidor analógico-digital de la ESP32 es de 12 bits, así que el rango va
de 0 a 4095: 0 V da 0 y 3.3 V da 4095.

El valor se envía con `Serial.println()`, que además del número agrega un salto de
línea. Ese salto es lo que permite separar un valor del siguiente cuando se leen del
otro lado; sin él llegaría una cadena continua de dígitos imposible de interpretar.

El `delay(100)` da aproximadamente diez lecturas por segundo. Sin esa pausa la tarjeta
saturaría el puerto con miles de valores.

La comprobación de este nivel se hizo desde el Serial Monitor del IDE a 115200,
confirmando que al girar la perilla los valores recorren todo el rango de 0 a 4095. Una
variación de unas pocas unidades con el potenciómetro quieto es normal: es ruido
eléctrico propio de cualquier lectura analógica.

### Nivel 2: Python sin ROS

`serial_pot.py` abre el puerto y en un ciclo lee lo que llega. La línea central del
script encadena tres operaciones, que son el camino inverso de lo que se hacía en el
ejemplo del LED:

```python
linea = esp32.readline().decode().strip()
```

`readline()` lee bytes hasta encontrar el salto de línea que agregó el `println` del
sketch, `decode()` convierte esos bytes a texto, y `strip()` elimina el salto y los
espacios sobrantes, dejando solo los dígitos.

El `if linea:` posterior evita imprimir líneas en blanco: si se cumple el timeout de un
segundo sin que llegue nada, `readline()` devuelve una cadena vacía.

### Nivel 3: los nodos de ROS 2

| Elemento | Valor |
|---|---|
| Tópico | `/analog` |
| Tipo de mensaje | `std_msgs/msg/Int32` |
| Profundidad de cola (QoS) | 10 |
| Periodo del temporizador | 0.01 s |
| Frecuencia real de publicación | ~10 Hz |

Se usa `Int32` porque la lectura del ADC es un entero sin decimales.

**`analog_serial_pub.py`** es el puente, pero en dirección opuesta a `serial_bridge.py`:
en lugar de escribir al puerto, lo lee. Abre el puerto serial y registra un temporizador
que se ejecuta cada 10 ms. En cada llamada revisa con `in_waiting` si hay bytes
esperando en el buffer; si los hay, lee la línea, verifica con `isdigit()` que sean
puros números (lo que descarta basura o líneas incompletas), la convierte a entero y la
publica en `/analog`.

El temporizador corre cien veces por segundo, pero la frecuencia real de publicación es
de unas diez, porque es el ritmo al que la ESP32 manda datos. Revisar el puerto más
seguido de lo que llega el dato evita que se acumule retraso en el buffer.

**`analog_subs.py`** solo se suscribe a `/analog` e imprime el valor recibido. No sabe
nada del puerto serial ni de la ESP32: para él la fuente del dato es indiferente.

Cabe señalar que el nodo se registra con el nombre `analog_subscriber`, que no coincide
con el nombre del archivo, tal como viene en el código visto en clase. Lo que aparece en
`ros2 node list` es el nombre del nodo, no el del archivo.

### Comandos utilizados

```bash
# En cada terminal
source /opt/ros/jazzy/setup.bash
source ~/Documentos/SM_VictorM/robotics_ws/install/setup.bash
```

```bash
# Terminal 1: el publicador, se levanta primero porque es quien abre el puerto
ros2 run basics analog_serial_pub.py

# Terminal 2: el suscriptor
ros2 run basics analog_subs.py
```

Comprobación desde una tercera terminal:

```bash
# Nodos activos: /analog_serial_pub y /analog_subscriber
ros2 node list

# Tópicos con su tipo de mensaje
ros2 topic list -t

# Publicadores y suscriptores del tópico
ros2 topic info /analog
ros2 topic info /analog --verbose

# Detalle del nodo suscriptor
ros2 node info /analog_subscriber

# Contenido de los mensajes
ros2 topic echo /analog

# Frecuencia real de publicación
ros2 topic hz /analog

# Grafo de comunicación
ros2 run rqt_graph rqt_graph
```

En el grafo se observa `/analog_serial_pub` publicando en `/analog` y
`/analog_subscriber` suscrito a ese tópico.

### Problemas encontrados y soluciones

**El archivo `ADC_Pot.ino` estaba incompleto.**
Al copiarlo faltaba la llave de cierre de la función `loop()`, por lo que el sketch no
compilaba. Se resolvió agregándola.

**El puerto serial solo admite un proceso a la vez.**
Al intentar correr los nodos con el Serial Monitor del IDE todavía abierto, o con
`serial_pot.py` en ejecución, el puerto aparece ocupado. Hay que cerrar el proceso
anterior antes de levantar el siguiente.

**La frecuencia medida no correspondía al temporizador.**
`ros2 topic hz /analog` reporta alrededor de 10 Hz aunque el temporizador del nodo esté
configurado a 100 Hz. No es un error: el nodo solo publica cuando hay datos en el
puerto, y quien marca el ritmo real es el `delay(100)` del sketch.

### Evidencia en video

**Enlace:** [Video del ejemplo del potenciómetro](https://drive.google.com/file/d/1CdxGgUXTdYfajxs87hcphMLrhs7PaWYN/view?usp=drive_link)





---

# Act4-Turtle_Controller

## 1. Descripción de la actividad

En esta actividad se integró lo visto en las anteriores para construir un sistema que
controla la tortuga de Turtlesim con un joystick físico de dos ejes conectado a una
ESP32.

El sistema consta de tres etapas:

1. **Lectura**: la ESP32 lee los dos ejes analógicos del joystick y envía los
   valores por el puerto serial.
2. **Publicación**: un nodo de ROS 2 lee el puerto serial y publica los valores crudos en
   un tópico, sin enviar nada a Turtlesim.
3. **Control**: un segundo nodo se suscribe a ese tópico, convierte las lecturas en
   velocidades lineal y angular, y las publica al tópico que mueve la tortuga.

Las tres etapas están separadas, lo que permite que cada pieza sea independiente: el
nodo publicador no sabe qué se hará con los datos, y el nodo de control no sabe de dónde
vienen.

## 2. Hardware y asignación de pines

El módulo utilizado es un joystick de dos ejes **HW-504**, que internamente son dos
potenciómetros con retorno a centro por resorte.

| Pin del módulo | Pin de la ESP32 | Justificación |
|---|---|---|
| GND | GND | Referencia común |
| +5V | **3.3v** | El ADC de la ESP32 no tolera más de 3.3 V en sus entradas |
| VRx | **GPIO 34** (ADC1_6) | Canal del ADC1, disponible siempre y pin de solo entrada |
| VRy | **GPIO 35** (ADC1_7) | Canal del ADC1, disponible siempre y pin de solo entrada |
| SW | sin conectar | El pulsador no se utiliza en esta actividad |

Se eligieron GPIO 34 y GPIO 35 porque, de acuerdo con el diagrama de pines proporcionado, 
ambos cuentan con canal ADC (ADC1_6 y ADC1_7) y son pines de solo entrada, 
sin funciones alternas que pudieran interferir con la lectura.


## 3. Calibración medida

Antes de escribir los nodos se midieron los valores reales del joystick con el Serial
Monitor:

| Medición | Eje X | Eje Y |
|---|---|---|
| Reposo (centro real) | ~1890 | ~1828 |
| Fluctuación en reposo | ~12 unidades | ~8 unidades |
| Extremo mínimo | 0 (izquierda) | 0 (arriba) |
| Extremo máximo | 4095 (derecha) | 4095 (abajo) |

Dos observaciones importantes que salieron de aquí:

**El centro no es 2048.** Aunque el rango del ADC de 12 bits va de 0 a 4095 y su punto
medio sería 2048, el joystick sin mover se queda en alrededor de 1890 y 1828. Si se hubiera
usado 2048 como referencia, la tortuga se movería sola aun con la palanca sin tocar.

**El recorrido no es simétrico.** Con el centro en 1890, hacia el máximo quedan 2205
unidades y hacia el mínimo solo 1890. Por eso el cálculo de velocidad escala cada lado
con su propio rango; de otro modo la tortuga alcanzaría distinta velocidad máxima según
la dirección.

## 4. Archivos generados

### `joystick.ino`

Define los dos pines, inicia el puerto serial a 115200 baudios y en cada ciclo lee ambos
ejes con `analogRead()`, que devuelve un entero de 0 a 4095.

Los dos valores se envían en una sola línea separados por coma (`1890,1828`) y
terminados con `println`, que agrega el salto de línea. Ese formato permite que del lado
de Python se separen con un `split(',')` y que cada lectura quede delimitada.

Se eligió enviar una lectura cada 50 ms, es decir 20 por segundo. Si se mandaran más seguido, 
llegarían más datos de los que los nodos alcanzan a procesar y se irían acumulando. Si se mandaran 
más espaciados, se notaría un retraso entre mover la palanca y ver reaccionar a la tortuga.

### `joystick_serial_pub.py`

| Elemento | Valor |
|---|---|
| Nombre del nodo | `joystick_serial_pub` |
| Tópico publicado | `/joystick_raw` |
| Tipo de mensaje | `geometry_msgs/msg/Point` |
| Profundidad de cola (QoS) | 10 |

Abre el puerto serial y revisa el buffer cada 10 ms. Cuando hay datos, lee la línea, la
separa por la coma y valida que hayan llegado exactamente dos partes y que ambas sean
numéricas. Esa validación es necesaria porque al arrancar el buffer puede contener
líneas cortadas a la mitad, que sin la comprobación harían fallar el nodo.

Se eligió `Point` porque sus campos `x` e `y` corresponden de forma natural a los dos
ejes del joystick y el mensaje se lee con claridad en `ros2 topic echo`. El tópico se
nombró `/joystick_raw` para dejar explícito que transporta lecturas crudas del ADC y no
velocidades ya calculadas. Conforme a lo solicitado, este nodo no envía nada a
Turtlesim.

### `turtle_controller.py`

| Elemento | Valor |
|---|---|
| Nombre del nodo | `turtle_controller` |
| Tópico al que se suscribe | `/joystick_raw` (`geometry_msgs/msg/Point`) |
| Tópico que publica | `/turtle1/cmd_vel` (`geometry_msgs/msg/Twist`) |

Es el nodo que hace la conversión. Por cada lectura recibida calcula una velocidad
lineal y una angular, las arma en un mensaje `Twist` y lo publica al tópico que escucha
Turtlesim.

La conversión la realiza el método `normalizar()`, que recibe la lectura, el centro del
eje y la velocidad máxima correspondiente, y devuelve la velocidad. El procedimiento es:

1. Calcula la desviación respecto al centro: `valor - centro`.
2. Si el valor absoluto de esa desviación es menor que la zona muerta, devuelve cero.
3. En caso contrario, resta la zona muerta y divide entre el rango restante del lado
   correspondiente, lo que da un factor entre 0 y 1.
4. Multiplica ese factor por la velocidad máxima.

Restar la zona muerta antes de escalar evita un salto: si no se hiciera, al salir de la
zona muerta la velocidad brincaría de golpe a un valor distinto de cero en lugar de
crecer de forma continua desde ahí. Esto es lo que garantiza el **control proporcional**
que pide la actividad: la velocidad varía de manera continua según la inclinación, y no
de forma encendido/apagado.

**Inversión de signos.** Ambos ejes se invierten con un signo negativo:

- El eje Y entrega 0 cuando la palanca va hacia adelante, que es el valor más bajo, pero
  hacia adelante la tortuga debe avanzar. Sin la inversión retrocedería.
- El eje X entrega 4095 hacia la derecha, pero en ROS un `angular.z` positivo gira en
  sentido antihorario, es decir a la izquierda. Sin la inversión, mover la palanca a la
  derecha giraría la tortuga a la izquierda.

**Movimiento combinado.** Como cada eje se procesa por separado y ambos resultados se
colocan en el mismo mensaje `Twist`, una inclinación simultánea en X y Y produce
velocidad lineal y angular al mismo tiempo, sin que haga falta lógica adicional.

## 5. Parámetros elegidos y su justificación

### Límites de velocidad

| Valor probado | Resultado |
|---|---|
| 1.0 | La tortuga responde con demasiada lentitud; cruzar la ventana toma un tiempo excesivo |
| Superiores a 2.0 | La tortuga se desplaza tan rápido que alcanza el borde antes de poder reaccionar, y el giro impide apuntarla con precisión |
| **2.0** | **Valor elegido**: respuesta ágil manteniendo el control |

La ventana de Turtlesim mide aproximadamente 11 unidades de lado a lado. Con una
velocidad lineal máxima de 2.0 la tortuga la recorre en poco más de cinco segundos, lo
que resulta cómodo para maniobrar. Para la velocidad angular se usó el mismo valor, que
permite una vuelta completa en unos tres segundos.

### Zona muerta

La zona muerta es un rango alrededor del centro dentro del cual la lectura se interpreta
como cero. Es necesaria porque el ADC presenta fluctuaciones aun con el joystick en
reposo, y porque el resorte no devuelve la palanca exactamente al mismo punto cada vez.

| Valor probado | Resultado |
|---|---|
| 20 | En la terminal aparecían esporádicamente velocidades de 0.01 con la palanca en reposo. El movimiento no llegaba a percibirse en Turtlesim, pero el ruido del ADC sí atravesaba el filtro |
| **100** | **Valor elegido**: las velocidades permanecen en 0.00 de forma constante con la palanca sin tocar |

Se eligió 100, que es alrededor del 5% del recorrido de cada lado. Como en reposo el valor solo 
varía unas 12 unidades, este margen es lo bastante amplio para cubrir esa variación. Tambien por que
es una parte pequeña del recorrido total, así que no se pierde sensibilidad al mover la palanca

## 6. Comandos utilizados

Registro de los nuevos ejecutables en `setup.py`:

```python
entry_points={
    'console_scripts': [
        ...
        'joystick_serial_pub.py = basics.joystick_serial_pub:main',
        'turtle_controller.py = basics.turtle_controller:main',
    ],
},
```

Compilación:

```bash
cd ~/Documentos/SM_VictorM/robotics_ws
colcon build
ls install/basics/lib/basics/
```

Ejecución, con el entorno cargado en cada terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Documentos/SM_VictorM/robotics_ws/install/setup.bash
```

```bash
# Terminal 1: simulador
ros2 run turtlesim turtlesim_node

# Terminal 2: publicador del joystick (abre el puerto serial)
ros2 run basics joystick_serial_pub.py

# Terminal 3: nodo de control
ros2 run basics turtle_controller.py
```

Comprobación desde una cuarta terminal:

```bash
# Nodos activos: turtlesim, joystick_serial_pub y turtle_controller
ros2 node list

# Tópicos con su tipo de mensaje
ros2 topic list -t

# Valores crudos del joystick
ros2 topic echo /joystick_raw

# Velocidades enviadas a la tortuga
ros2 topic echo /turtle1/cmd_vel

# Publicadores y suscriptores de cada tópico
ros2 topic info /joystick_raw
ros2 topic info /turtle1/cmd_vel

# Detalle del nodo de control
ros2 node info /turtle_controller

# Frecuencia real de publicación
ros2 topic hz /joystick_raw

# Grafo de comunicación
ros2 run rqt_graph rqt_graph
```

En el grafo se observa la cadena completa: `/joystick_serial_pub` publica en
`/joystick_raw`, `/turtle_controller` está suscrito a ese tópico y a su vez publica en
`/turtle1/cmd_vel`, donde escucha `/turtlesim`.

## 7. Problemas encontrados y soluciones

**Las lecturas no cambiaban al mover el joystick.**
Durante la primera prueba los cuatro movimientos entregaban los mismos valores. La causa
fue un error al registrar las mediciones, no un fallo del circuito. Al repetir la prueba
observando cada eje por separado se confirmó que ambos recorren el rango completo de 0 a
4095.

**El centro del joystick no coincidía con el punto medio teórico.**
El ADC de 12 bits tiene un punto medio de 2048, pero el joystick reposa en 1890 y 1828.
Usar 2048 como referencia habría provocado que la tortuga se desplazara sola. Se
resolvió midiendo el reposo real de cada eje y usando esos valores como centro en el
nodo de control.

**El recorrido de la palanca no es simétrico respecto al centro.**
Al no estar el reposo a la mitad del rango, un mismo divisor para ambos lados habría
dado distinta velocidad máxima según la dirección. Se resolvió calculando el rango de
cada lado por separado dentro del método `normalizar()`.

**Los cambios no se reflejaban al ejecutar.**
Tras modificar los valores de velocidad y recompilar, el comportamiento seguía igual. La
causa es que `ros2 run` ejecuta la copia instalada en `install/`, y el proceso que ya
está corriendo mantiene en memoria la versión con la que arrancó. Hay que copiar el
archivo al paquete, recompilar y **reiniciar el nodo**.

**Las pruebas de parámetros se mezclaban entre sí.**
Al intentar cambiar velocidad y zona muerta en la misma compilación no era posible
atribuir el resultado a uno u otro parámetro. Se resolvió probando una variable a la
vez, dejando la otra fija en su valor de referencia.

## 8. Evidencia en video

**Enlace:** [Video de la actividad 4](https://drive.google.com/file/d/10Pt82b2CD7FWio6Xp_YW1JXTmUPyLWgp/view?usp=drive_link)

## 9. Control de versiones

| Commit | Contenido |
|---|---|
| 1 | Programa de Arduino con la lectura del joystick. |
| 2 | Nodo publicador del joystick verificado. |
| 3 | Verificación de recepción de datos en el nodo subscriptor. |
| 4 | Ajuste final de límites de velocidad y zona muerta. |
| 5 | Documentación completa en el README. |











---

# Act5-Launch Publicador y publicador

## 1. Descripción de la actividad

En esta actividad se generó un archivo launch para ejecutar los dos nodos de la primera
práctica, `velocity_publisher` y `velocity_subscriber`, desde una sola terminal en lugar
de una por nodo.

Un archivo launch es un script de Python que describe qué nodos deben arrancarse.
`ros2 launch` lee esa descripción y lanza cada uno como un proceso independiente,
mostrando todas las salidas en la misma terminal.

## 2. Archivo generado

### `velocity_system.launch.py`

El archivo define la función `generate_launch_description()`, cuyo nombre es obligatorio
porque es la que `ros2 launch` busca al ejecutar el archivo. Esa función devuelve un
objeto `LaunchDescription` con la lista de nodos a lanzar.

Cada nodo se declara con tres datos:

| Parámetro | Valor | Significado |
|---|---|---|
| `package` | `basics` | Paquete donde vive el ejecutable |
| `executable` | `velocity_publisher.py` / `velocity_subscriber.py` | Nombre registrado en `entry_points` |
| `output` | `screen` | Envía los mensajes del logger a la terminal |

El `executable` debe coincidir exactamente con el nombre declarado en `console_scripts`
dentro de `setup.py`. En este repositorio los ejecutables se registraron conservando la
extensión `.py`, por lo que el launch los invoca de esa forma.

## 3. Registro en `setup.py`

A diferencia de los nodos, el archivo launch no se declara en `entry_points` sino en
`data_files`:

```python
data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name + '/launch', ['launch/velocity_system.launch.py']),
],
```

La razón es que `entry_points` sirve para generar **ejecutables** a partir de una
función `main`, mientras que el launch no es un programa sino un archivo de datos que
`ros2 launch` lee. La línea agregada copia el archivo a `share/basics/launch/`, que es
donde el comando lo busca. Sin ese registro el archivo existe en el código fuente pero
`ros2 launch` no lo encuentra.

## 4. Comandos utilizados

Creación del directorio y el archivo:

```bash
cd ~/Documentos/SM_VictorM/robotics_ws/src/basics
mkdir launch
touch launch/velocity_system.launch.py
```

Compilación y ejecución:

```bash
cd ~/Documentos/SM_VictorM/robotics_ws
colcon build
source install/setup.bash
ros2 launch basics velocity_system.launch.py
```

Comprobación desde una segunda terminal:

```bash
# Nodos activos: /velocity_publisher y /velocity_subscriber
ros2 node list

# Tópicos con su tipo de mensaje
ros2 topic list -t

# Publicadores y suscriptores conectados
ros2 topic info /velocity

# Contenido de los mensajes
ros2 topic echo /velocity

# Grafo de comunicación
ros2 run rqt_graph rqt_graph
```

## 5. Observaciones del funcionamiento

Al ejecutar el launch, la terminal reporta el identificador de proceso de cada nodo:

```
[INFO] [velocity_publisher-1]: process started with pid [7698]
[INFO] [velocity_subscriber-2]: process started with pid [7699]
```

Cada nodo se lanza como un proceso independiente del sistema operativo. Como ambas
salidas comparten la misma terminal, cada línea se antepone con el nombre del nodo y su
número de orden para distinguir cuál la escribió. Un `Ctrl+C` detiene los dos a la vez,
porque `ros2 launch` reenvía la señal a todos los procesos que administra.

El grafo obtenido es igual al de la primera práctica: `velocity_publisher` publicando
en `/velocity` y `velocity_subscriber` suscrito a ese tópico. Esto nos confirma que el
launch no modifica la arquitectura del sistema; los nodos siguen siendo procesos
independientes que se comunican por un tópico y no tienen forma de saber cómo fueron
arrancados. Lo único que cambia es el mecanismo de como se ejecutan.

La ventaja se ve conforme hay mas nodos. Con dos nodos la diferencia es poca,
pero un sistema robótico completo podria tener más nodos entre sensores, control y
navegación, y abrir una terminal para cada no sería practico. El launch permite
describir el sistema una sola vez y levantarlo con un único comando.

## 6. Evidencia en video

**Enlace:** [Video del archivo launch](https://drive.google.com/file/d/1g1Np2wFy1dw6wDU_ae-GWLHqdYgOaUYf/view?usp=drive_link)

## 7. Control de versiones

| Commit | Contenido |
|---|---|
| 1 | Archivo launch funcionando. |
| 2 | Documentación del ejemplo del launch. |
