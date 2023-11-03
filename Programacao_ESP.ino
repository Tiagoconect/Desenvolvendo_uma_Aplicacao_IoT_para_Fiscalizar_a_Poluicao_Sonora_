#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Servo.h>

const char* ssid = "tiago";
const char* password = "ajux2896";
const char* serverAddress = "http://192.168.15.34/receber-dados";

#include <NTPClient.h>
#include <WiFiUdp.h>
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "br.pool.ntp.org", -10800, 60000);

Servo myServo;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando ao WiFi...");
  }

  myServo.attach(D3);
  myServo.write(0); // Define a posição inicial do servo como 0 graus.
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    timeClient.update();
    int sensorValue = analogRead(A0);
    int servoPosition = myServo.read();

    String dataToSend = "sensor=" + String(sensorValue) + "&servo=" + String(servoPosition) + "&time=" + timeClient.getFormattedTime();

    HTTPClient http;
    WiFiClient client;
    http.begin(client, serverAddress);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    int httpCode = http.POST(dataToSend);

    if (httpCode == HTTP_CODE_OK) {
      Serial.println("Dados enviados com sucesso.");
    } else {
      Serial.println("Falha ao enviar dados.");
    }

    http.end();

    myServo.write(servoPosition + 30);

    delay(10000);
  }
}