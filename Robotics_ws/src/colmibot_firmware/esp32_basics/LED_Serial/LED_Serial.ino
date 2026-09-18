#define LED 2

void setup() {
  pinMode(LED, OUTPUT);

  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    char dato = Serial.read();

    if (dato == '1') {
      digitalWrite(LED, HIGH);
    }

    if (dato == '0') {
      digitalWrite(LED, LOW);
    }
  }
}