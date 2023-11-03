from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt

from pymongo import MongoClient
import matplotlib.pyplot as plt

# Connectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # selecinando o banco de dados

# abrindo/acessando dados da coleção que contem dados enviados pela esp
collection = db["valores_enviados_pela_esp"]  

# variaveis locais para receber os valores do sensor e o angulo do servo
sensor_data = []
servo_data = []

#coletando dados do mangoDB
for doc in collection.find().sort("tempo", 1):
    sensor_data.append(float(doc["valor_sensor"]))
    servo_data.append(float(doc["valor_servo"]))

# Criando e confugrando o grafico do valor do sensor em DB em função do servo do angulo do servo
plt.figure(figsize=(10, 6))
plt.scatter(servo_data, sensor_data, marker='o', s=20)
plt.xlabel('Valor do Servo')
plt.ylabel('Valor do Sensor')
plt.title('Gráfico de Dispersão: Valor do Sensor em Função do Valor do Servo')

# plotando o gráfico
plt.show()
