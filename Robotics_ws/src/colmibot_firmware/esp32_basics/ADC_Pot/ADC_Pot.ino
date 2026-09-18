#define POT 15

void setup() {
  Serial.begin(115200);
}

void loop() {
  int valor = analogRead(POT);
  Serial.println(valor);
  delay(100);
}