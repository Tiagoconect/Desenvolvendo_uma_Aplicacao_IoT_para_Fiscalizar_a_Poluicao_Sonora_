from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd  # pandas para usar o formato de data/hora

# Conectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # acessando o bando de dados do projeto radar

# coleção que contém os valores do sensor
collection = db["valores_enviados_pela_esp"]  # Use o nome correto da coleção

# variveis para recebe os valores do sensor e as informações de tempo a partir do MongoDB
sensor_data = []
timestamps = []

for doc in collection.find().sort([("tempo", 1)]):
    sensor_data.append(float(doc["valor_sensor"]))
    timestamps.append(doc["tempo"])  

# Convertendo timestamps para um formato adequado para gráficos
timestamps = [pd.to_datetime(ts) for ts in timestamps]

# criando e configurando gráfico de valores do sensor em função do tempo
plt.figure(figsize=(10, 6))
plt.plot(timestamps, sensor_data, marker='o', linestyle='-', markersize=2)
plt.xlabel('Tempo')
plt.ylabel('Valor do Sensor')
plt.title('Valores do Sensor ao Longo do Tempo')
plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M:%S"))
plt.xticks(rotation=45)

# Exibir o gráfico
plt.show()
