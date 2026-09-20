//valores medidos en pruebas:
//centro X ~1890, centro Y ~1828
//X: izquierda 0, derecha 4095
//Y: arriba 0, abajo 4095

//Asociamos los pines de X y Y del joystick a los pines 34 y 35
//estos solo son de entrada en el esp32
#define VRX 34
#define VRY 35

//el setup solo se inicia 1 vez al iniciar
void setup() {
  // se inicia el puerto en 115200 baudios
  //esta velocidad debe ser la misma que la del nodo que lee del otro lado
  Serial.begin(115200);
}

//>Se inicia el loop indefinidamente
void loop() {
  //Se lee cada uno de los ejes desde analog read y el pin
  //primero X y luego Y
  int x = analogRead(VRX);
  int y = analogRead(VRY);

  //se mandan dos valores en una sola linea en formato x,y/n
  Serial.print(x);
  Serial.print(",");
  Serial.println(y);
  
  //espera 50 ms entre lecturas para no saturar el puerto
  delay(50);
}