//se asocia el valor 2 a la palabra LED, es una sustitucion de texto
//que se hace antes de compilar, no es una variable
//el pin 2 es donde esta el led azul de la placa
#define LED 2

//setup se ejecuta una sola vez al encender o reiniciar la placa
void setup() {
  //se configura el pin 2 como salida
  pinMode(LED, OUTPUT);
  //se inicia el puerto a 115200 baudios, debe ser la misma velocidad
  //que del otro lado o llegan caracteres basura
  Serial.begin(115200);
}
//se inicia el loop indefinidamente
void loop() {
  //si serial tiene algo de datos entra el if
  if (Serial.available() > 0) {
    //lee el dato que esta en serial
    char dato = Serial.read();
    //si el dato es el caracter 1 se enciende el led, es el caracter
    //y no el numero
    if (dato == '1') {
      //HIGH pone 3.3 V en el pin
      digitalWrite(LED, HIGH);
    }
    //si el dato es 0 se apaga el led
    if (dato == '0') {
      //LOW deja el pin en 0 V
      digitalWrite(LED, LOW);
    }
  }
}