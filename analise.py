from pymongo import MongoClient
import numpy as np

# Conectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # Use o nome correto do banco de dados

# Acessando a coleçãon que contém os valores do sensor
collection = db["valores_enviados_pela_esp"]  # Use o nome correto da coleção

# recuperando os valores do seosor no MongoDB e convertendo de strings para números
sensor_data = [float(doc["valor_sensor"]) for doc in collection.find()]

# Cálculo das estatísticas básicas
mean = np.mean(sensor_data)  # Média
median = np.median(sensor_data)  # Mediana
std_dev = np.std(sensor_data)  # Desvio Padrão

#  limite de desvio padrão para identificar valores anormais (ajustavel)
threshold = 1.5  

# Verifificando valores anormais com base no desvio padrão
anomalous_values = [value for value in sensor_data if abs(value - mean) > threshold * std_dev]

# Imprimindo as estatísticas
print("Média:", mean)
print("Mediana:", median)
print("Desvio Padrão:", std_dev)

# Imprimindo os valores anormais
if anomalous_values:
    print("Valores anormais:", anomalous_values)
else:
    print("Nenhum valor anormal detectado.")
