from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd  # pandas para usar o formato de data/hora

# Conectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # Substitua pelo nome correto do banco de dados

# Solicitando dados da coleção do banco de dados onde os valores enviados pela ESP estão armazenados
collection = db["valores_enviados_pela_esp"]

# Variáveis locais para receber valores do sensor, tempo e ângulo do servo no MongoDB
sensor_data = []
timestamps = []
servo_angles = []
rolling_window = 10  # Janela para a média móvel

for doc in collection.find().sort("tempo", 1):
    sensor_value = float(doc["valor_sensor"])
    timestamp = pd.to_datetime(doc["tempo"])
    servo_angle = float(doc["valor_servo"])

    sensor_data.append(sensor_value)
    timestamps.append(timestamp)
    servo_angles.append(servo_angle)

    # Calculando a média móvel com base no novo valor do sensor
    if len(sensor_data) > rolling_window:
        sensor_data_avg = np.mean(sensor_data[-rolling_window:])
    else:
        sensor_data_avg = sensor_value

    # Criando um documento com os valores para inserir na coleção
    document = {
        "tempo": timestamp,
        "valor_sensor": sensor_value,
        "media_movel": sensor_data_avg,
        "angulo_servo": servo_angle
    }

    # Inserindo o documento na coleção
    db["valores_media_movel"].insert_one(document)

# Usando um estilo de gráfico de fundo escuro
plt.style.use('dark_background')

# Criando e configurando o gráfico
plt.figure(figsize=(10, 6))
plt.plot(timestamps, sensor_data, marker='o', linestyle='-', markersize=2, label='Valor do Sensor', color='lightblue')
plt.xlabel('Tempo')
plt.ylabel('Valor do Sensor')
plt.title('Valores do Sensor ao Longo do Tempo')
plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M:%S"))
plt.xticks(rotation=45)

# Continuar com o restante do código para criar o gráfico de média móvel e salvar/exibir o gráfico
# ...

# Calculando a média móvel em função do tempo e plotando junto com o valor do sensor em função do tempo
sensor_data_avg = np.convolve(sensor_data, np.ones(rolling_window) / rolling_window, mode='same')
plt.plot(timestamps, sensor_data_avg, linestyle='-', label=f'Média (intervalo_amostral={rolling_window})', color='red')

# Adicionando legenda no gráfico
plt.legend()

# Salvar o gráfico em um arquivo
plt.savefig('templates/IMG_graficos/media_movel.png', bbox_inches='tight')

# Exibir o gráfico na tela
plt.show()
