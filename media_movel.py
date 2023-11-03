from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd  # pandas para usar o formato de data/hora

# Conectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # Replace with the correct database name

# solicitando dados da coleção do banco de dados que estão os valores da enviados pela esp
collection = db["valores_enviados_pela_esp"]  

# Variáveis locais para receber valores do sensor e tempo no MongoDB
sensor_data = []
timestamps = []

for doc in collection.find().sort("tempo", 1):
    sensor_data.append(float(doc["valor_sensor"]))
    timestamps.append(doc["tempo"])  

# Convertendo o formato de dados com pandas 
timestamps = [pd.to_datetime(ts) for ts in timestamps]

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

# Calculando a média móvel em função do tempo e plotando junto com o valor do sensor em função do tempo
rolling_window = 10 
sensor_data_avg = np.convolve(sensor_data, np.ones(rolling_window) / rolling_window, mode='same')
plt.plot(timestamps, sensor_data_avg, linestyle='-', label=f'Média (intervalo_amostral={rolling_window})', color='red')

# Adicionando legenda no gráfico
plt.legend()

# Salvar o gráfico em um arquivo
plt.savefig('templates/IMG_graficos/media_movel.png', bbox_inches='tight')

# Exibir o gráfico na tela
plt.show()
