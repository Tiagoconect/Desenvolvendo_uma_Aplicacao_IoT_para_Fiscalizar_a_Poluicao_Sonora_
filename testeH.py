from pymongo import MongoClient
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Configuração do estilo de gráfico
plt.style.use('dark_background')

# Conectectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  

#função para encontrar e verificar valores anormais em função do angulo (fonte: chatGPT)
def count_anomalous_by_servo_angle(sensor_data, z_critical):
    servo_angles = set(data["valor_servo"] for data in sensor_data)
    anomalous_counts = {angle: [] for angle in servo_angles}

    for data in sensor_data:
        z_score = abs((data["valor_sensor"] - mean) / std_dev)
        if z_score > z_critical:
            anomalous_counts[data["valor_servo"]].append(data)
    
    return anomalous_counts

# coleção que contém os valores do sensor, tempo e ângulo
collection = db["valores_enviados_pela_esp"]  

# Recupere os valores do sensor, tempo e ângulo a partir do MongoDB
sensor_data = []
for doc in collection.find():
    sensor_value = float(doc["valor_sensor"])
    timestamp = doc["tempo"]
    servo_angle = doc["valor_servo"]
    sensor_data.append({"valor_sensor": sensor_value, "tempo": timestamp, "valor_servo": servo_angle})

# Cálculo das estatísticas básicas
mean = np.mean([data["valor_sensor"] for data in sensor_data])  # Média
std_dev = np.std([data["valor_sensor"] for data in sensor_data])  # Desvio Padrão

# Definindo um limite de significância (alfa) para o teste Z
alfa = 0.05  #ajustar esse valor

# Calcular o valor crítico do teste Z para o limite de significância
z_critical = stats.norm.ppf(1 - alfa / 2)

# Verificar valores atípicos com base no teste Z (chamdo valores retornado pela função)
anomalous_counts = count_anomalous_by_servo_angle(sensor_data, z_critical)

# Salvar valores atípicos em outra coleção
denied_collection = db["Valores_Atipicos"]  # Nome da nova coleção

for angle, data_list in anomalous_counts.items():
    for data in data_list:
        denied_collection.insert_one(data)

# Imprimindo os valores da media e o desvi padrão
print("Média:", mean)
print("Desvio Padrão:", std_dev)

# Imprimindo os valores atípicos com tempo e ângulo correspondentes
if anomalous_counts:
    print("Valores atípicos:")
    for angle, data_list in anomalous_counts.items():
        for data in data_list:
            print("Valor Sensor:", data["valor_sensor"])
            print("Tempo:", data["tempo"])
            print("Ângulo do Servo:", data["valor_servo"])
else:
    print("Nenhum valor atípico detectado")

# Criando o gráfico de barras com estilo dark
angles = list(anomalous_counts.keys())
counts = [len(anomalous_counts[angle]) for angle in angles]

# Configuração de cores para as barras
colors = ['red' for _ in angles]  # Define a cor das barras como vermelho (ou escolha a cor desejada)

plt.bar(angles, counts, color=colors)
plt.xlabel("Ângulo do Servo")
plt.ylabel("Quantidade de Valores Atípicos")
plt.title("Valores Atípicos por Ângulo do Servo")

# Salvar o gráfico em um arquivo
plt.savefig('templates/IMG_graficos/anormalidade_regiao.png', bbox_inches='tight')
plt.show()