# Importando bibliotecas necessárias
from pymongo import MongoClient
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd
from datetime import timedelta

# Conectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # escolha do banco de dados de acesso do projeto

# iniciando a função para analisar as anomalias no intervalo amostral, percentual e a posição levando em conta o z-calq
def calcular_percentagem_anomalias(dados_sensor, z_critico):
    angulos_servo = set(dado["valor_servo"] for dado in dados_sensor)
    contagens_anomalias = {angulo: [] for angulo in angulos_servo}
    
    for dado in dados_sensor:
        escore_z = abs((dado["valor_sensor"] - media) / desvio_padrao)
        if escore_z > z_critico:
            contagens_anomalias[dado["valor_servo"]].append(dado)
    
    return contagens_anomalias

# selecionando a coleção que tem os valores do sensor, tempo e ângulo do servo
colecao = db["valores_enviados_pela_esp"]

# Restringindo o intervalo de coleta das últimas 70 amostras do banco de dados
dados_sensor = list(colecao.find().sort([("tempo", -1)]).limit(70))

# convertendo os valores do sensor de string para float
for dado in dados_sensor:
    dado["valor_sensor"] = float(dado["valor_sensor"])

# Calculando média e desvio padrão
media = np.mean([dado["valor_sensor"] for dado in dados_sensor])
desvio_padrao = np.std([dado["valor_sensor"] for dado in dados_sensor])

# definindo o valor de alfa
alfa = 0.1

# Calcula o z crítico
z_critico = stats.norm.ppf(1 - alfa / 2)

# Calcula as anomalias nas últimas 70 amostras
anomalous_values_by_angle = calcular_percentagem_anomalias(dados_sensor, z_critico)

# Crie uma nova coleção chamada "tratando_testeH"
tratando_testeH = db["tratando_testeH"]

# Armazena os resultados na nova coleção
for angulo, anomalous_values in anomalous_values_by_angle.items():
    percentagem = (len(anomalous_values) / 10) * 100
    print(f"Servo Angle {angulo}: {percentagem:.2f}% anomalies")
    print("Anomalous Values:")
    for anomalous_value in anomalous_values:
        print(anomalous_value)
    
    # criando uma nova coleção para inserir os valores significativos da análise do testeH em função da posição do servo
    tratando_testeH.insert_one({
        "servo_angle": angulo,
        "percentage_anomalies": percentagem,
        "anomalous_values": anomalous_values
    })

# criando gráfico para ver a taxa de anomalia em um intervalo amostral de 70 amostras em função da posição do servo
angulos = list(anomalous_values_by_angle.keys())
percentagens = [len(values) / 10 * 100 for values in anomalous_values_by_angle.values()]

plt.bar(angulos, percentagens)
plt.xlabel("Ângulo do Servo")
plt.ylabel("Porcentagem de valores anormais (%)")
plt.title("Porcentagem de valores anormais por ângulo do servo")

# Usando um estilo de gráfico de fundo escuro
plt.style.use('dark_background')

# Criando e configurando o gráfico
plt.figure(figsize=(10, 6))

# Variáveis locais para receber valores do sensor, tempo e ângulo do servo no MongoDB
sensor_data = []
timestamps = []  # Adicione essa linha
servo_angles = []
rolling_window = 10  # Janela para a média móvel

for doc in colecao.find().sort("tempo", 1):
    sensor_value = float(doc["valor_sensor"])
    timestamp = pd.to_datetime(doc["tempo"])
    servo_angle = float(doc["valor_servo"])

    sensor_data.append(sensor_value)
    timestamps.append(timestamp)  # Adicione essa linha
    servo_angles.append(servo_angle)

# Calculando a média móvel em função do tempo

# Escolha o intervalo de tempo desejado para a média móvel
intervalo_de_tempo = timedelta(seconds=70)  # Intervalo de 70 segundos

# Crie listas para armazenar os valores do sensor e as anomalias dentro do intervalo de tempo
sensor_data_in_interval = []
anomalous_data_in_interval = []

# Itere pelas leituras do sensor e das anomalias
for timestamp, sensor_value in zip(timestamps, sensor_data):
    sensor_data_in_interval.append(sensor_value)

# Calculando a média móvel para os valores do sensor no intervalo de 70 segundos
sensor_data_avg_in_interval = np.convolve(sensor_data_in_interval, np.ones(rolling_window) / rolling_window, mode='same')

# Plotando os valores do sensor e a média móvel
plt.plot(timestamps, sensor_data, marker='o', linestyle='-', markersize=2, label='Valor do Sensor', color='lightblue')
plt.plot(timestamps, sensor_data_avg_in_interval, linestyle='-', label=f'Média (intervalo_amostral=70s)', color='red')

# Configurando o gráfico
plt.xlabel('Tempo')
plt.ylabel('Valor do Sensor')
plt.title('Valores do Sensor ao Longo do Tempo')
plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M:%S"))
plt.xticks(rotation=45)
plt.legend()

# Salvar o gráfico em um arquivo
plt.savefig('templates/IMG_graficos/media_movel.png', bbox_inches='tight')

# Exibir o gráfico na tela
plt.show()
