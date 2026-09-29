//se asocia el valor 15 a la palabra pot. en ese pin se conecta el pin de en medio
//del potenciometro
#define POT 15

void setup() {
	//se inicia el puerto a 115200 baudios
  Serial.begin(115200);
}
//se inicia un loop indefinido
void loop() {
	//analogRead convierte el voltaje del pin a un numero
  int valor = analogRead(POT);
  //se manda el valor del puerto serial junto con salto de linea para separar un valor de otro
  Serial.println(valor);
  //se esperan 100 ms
  delay(100);
}