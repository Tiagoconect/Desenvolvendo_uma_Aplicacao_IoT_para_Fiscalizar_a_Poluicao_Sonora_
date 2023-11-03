

#include <NTPClient.h>
#include <WiFiUdp.h>
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP,"br.pool.ntp.org", -10800, 60000);
const int hour = 10;
const int minute = 0;

#include <ESP8266WiFi.h>
#include "index.h" // Conteudo da pagina HTML com javascript
const char* ssid = "Aqui";
const char* senha = "92961063a";
#include <ESP8266WebServer.h>
ESP8266WebServer server(80);

//Iniciando comunicação com firebase


const int pinoMicrofone = A0;

const char* index_html = R"(
  <!DOCTYPE html>
  <!-- Conteúdo do index.html -->
)";

WiFiClient cliente;

int picoAnteriorMaximo = 0;
int picoAnteriorMinimo= 1023;
unsigned long tempoAnteriorPico = 0;
int picoMaximo = 0;
float mediaAmostral = 0;


int servoAngulo = 0; 

#include <vector>


float calcularMedia(int pino, int amostras, int intervalo) {
  int soma = 0;

  for (int i = 0; i < amostras; i++) {
    int valorSom = analogRead(pino);
    soma += valorSom;
    delay(intervalo);
  }

  return (float)soma / amostras;
}

int encontrarPicoMaximo(int pino, int amostras, int intervalo) {
  int picoMaximo = 0;

  for (int i = 0; i < amostras; i++) {
    int valorSom = analogRead(pino);
    if (valorSom > picoMaximo) {
      picoMaximo = valorSom;
    }
    delay(intervalo);
  }

  return picoMaximo;
}

int encontrarPicoMinimo(int pino, int amostras, int intervalo) {
  int picoMinimo = 1023;

  for (int i = 0; i < amostras; i++) {
    int valorSom = analogRead(pino);
    if (valorSom < picoMinimo) {
      picoMinimo = valorSom;
    }
    delay(intervalo);
  }

  return picoMinimo;
}






void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println();
  Serial.println("Conectando à rede Wi-Fi...");
  WiFi.begin(ssid, senha);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conexão à rede Wi-Fi falhou. Tentando novamente...");
  }

  Serial.println("Conectado à rede Wi-Fi");
  Serial.print("Endereço IP do Arduino: ");
  Serial.println(WiFi.localIP());

   server.on("/", HTTP_GET, [](void) {
    //server.send_P(200, "text/html", index_html, strlen(index_html));
     String s = MAIN_page; // Le o conteudo HTML
     server.send(200, "text/html", s); // Envia a pagina web

  });

  server.on("/sensor", HTTP_GET, []() {
    String json = "{\"mediaAmostral\":" + String(mediaAmostral) + ", \"pico\":" + String(picoMaximo) + "}";
    server.send(200, "application/json", json);
});


  server.begin();

 
 
}

void loop() {
  server.handleClient();
  timeClient.update();
  unsigned long inicioAmostragem = millis();
  unsigned long intervaloAmostragem = 1000;
  int amostras = 10;

  float frequencia = 0.0;

  
  mediaAmostral = calcularMedia(pinoMicrofone, amostras, intervaloAmostragem);
  picoMaximo = encontrarPicoMaximo(pinoMicrofone, amostras, intervaloAmostragem);
  int picoMinimo = encontrarPicoMinimo(pinoMicrofone, amostras, intervaloAmostragem);
  
  Serial.print("Média amostral do som: ");
  Serial.println(mediaAmostral);
  Serial.print("Pico máximo do som: ");
  Serial.println(picoMaximo);
  Serial.print("Pico mínimo do som: ");
  Serial.println(picoMinimo);

  if (picoMaximo !=  picoAnteriorMaximo && picoMinimo !=  picoAnteriorMinimo) {
    unsigned long tempoAtual = millis();
    unsigned long tempoPicoaPico = tempoAtual - tempoAnteriorPico;
    tempoAnteriorPico = tempoAtual;
    
    
    float frequencia = 1000.0 / tempoPicoaPico;  
    Serial.print("frequencia: ");
    Serial.println(frequencia, 2);  
  }

  picoAnteriorMaximo = picoMaximo;
  picoAnteriorMinimo = picoMinimo;
  
  Serial.println(timeClient.getFormattedTime());
  atualizarEDetectarAnomalias(picoMaximo);
  
 int horaAtual = timeClient.getHours();
 bool violacao = analisarViolacao(mediaAmostral);

  if (violacao) {
    Serial.println("Violação do limite de ruído detectada!");
  }

  delay(1000); 
  

  
}


// Função para detectar anomalias com base no Z-Score
bool detectarAnomalia(int valor, double media, double desvioPadrao, double limite) {
    double zScore = (valor - media) / desvioPadrao;
    return abs(zScore) > limite;
}

// Variáveis para manter o histórico de amostras
const int tamanhoHistorico = 10;
std::vector<int> historicoPicoMaximo;

// Função para atualizar o histórico de amostras e detectar anomalias
void atualizarEDetectarAnomalias(int picoMaximo) {
    // Adicione o valor atual do picoMaximo ao histórico
    historicoPicoMaximo.push_back(picoMaximo);
    
    // Certifique-se de que o histórico não seja maior do que tamanhoHistorico
    if (historicoPicoMaximo.size() > tamanhoHistorico) {
        historicoPicoMaximo.erase(historicoPicoMaximo.begin());
    }
    
    // Calcule a média e o desvio padrão do histórico
    double media = 0.0;
    for (int valor : historicoPicoMaximo) {
        media += valor;
    }
    media /= historicoPicoMaximo.size();
    
    double desvioPadrao = 0.0;
    for (int valor : historicoPicoMaximo) {
        double diferenca = valor - media;
        desvioPadrao += diferenca * diferenca;
    }
    desvioPadrao = sqrt(desvioPadrao / historicoPicoMaximo.size());
    
    // Defina o limite de anomalia com base nos seus dados
    const double limiteAnomalia = 3.0;
    
    // Verifique se o valor atual é uma anomalia
    bool eAnomalia = detectarAnomalia(picoMaximo, media, desvioPadrao, limiteAnomalia);
    
    if (eAnomalia) {
        // Lidar com a anomalia, por exemplo, emitindo um alerta
        Serial.println("Anomalia detectada no pico máximo!");
    }
}



bool analisarViolacao(float mediaAmostral) {
  // Obtenha a hora atual do objeto timeClient
  int horaAtual = timeClient.getHours();

  // Defina os limites com base na hora do dia
  int limiteSuperior = 0;
  int limiteInferior = 0;

  if (horaAtual >= 7 && horaAtual < 20) {
    // Horário diurno
    limiteSuperior = 70;  // Defina o limite diurno apropriado
    limiteInferior = 55;  // Defina o limite diurno apropriado
  } else if ((horaAtual >= 20 && horaAtual < 23) || (horaAtual >= 0 && horaAtual < 7)) {
    // Horário noturno
    limiteSuperior = 65;  // Defina o limite noturno apropriado
    limiteInferior = 45;  // Defina o limite noturno apropriado
  }

  // Verifique se a média amostral está fora dos limites
  if (mediaAmostral > limiteSuperior || mediaAmostral < limiteInferior) {
    // Violou os limites do PSIU
    return true;
  }

  // Não houve violação
  return false;
}
