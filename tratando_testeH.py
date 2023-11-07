# Importando bibliotecas necessárias
from pymongo import MongoClient
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Conectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # escolha do banco de dados de acesso do projeto

# iniciando a função para analizar as anormalia o intervalo amostral, percental e a posição levando em conta o zcalq
def calcular_percentagem_anomalias(dados_sensor, z_critico):
    angulos_servo = set(dado["valor_servo"] for dado in dados_sensor)
    contagens_anomalias = {angulo: [] for angulo in angulos_servo}
    
    for dado in dados_sensor:
        escore_z = abs((dado["valor_sensor"] - media) / desvio_padrao)
        if escore_z > z_critico:
            contagens_anomalias[dado["valor_servo"]].append(dado)
    
    return contagens_anomalias

# selecionando a coleção que tem os valores do sensor, tempo e angulo do servo
colecao = db["valores_enviados_pela_esp"] 

# Restrigindo o intervalo de coleta das ultimas 70 amsostras do banco de dados
dados_sensor = list(colecao.find().sort([("tempo", -1)]).limit(70))

# convertendo os valores do sensor de string para float
for dado in dados_sensor:
    dado["valor_sensor"] = float(dado["valor_sensor"])

# Calculando media e descio padrão
media = np.mean([dado["valor_sensor"] for dado in dados_sensor])  # media
desvio_padrao = np.std([dado["valor_sensor"] for dado in dados_sensor])  # desvio padrão

#definindo o valor de alfa
alfa = 0.1

# Calcula o z critico
z_critico = stats.norm.ppf(1 - alfa / 2)

# Calcula as anomalias nas últimas 70 amostras
anomalous_values_by_angle = calcular_percentagem_anomalias(dados_sensor, z_critico)

# Crie uma nova coleção chamada "tratando_testeH"
tratando_testeH = db["tratando_testeH"]

# Calcula a média das anomalias
medias_anomalias = {angulo: np.mean([dado["valor_sensor"] for dado in anomalous_values]) for angulo, anomalous_values in anomalous_values_by_angle.items()}

#Armazena os resultados na nova coleção
for angulo, anomalous_values in anomalous_values_by_angle.items():
    percentagem = (len(anomalous_values) / 10) * 100
    print(f"Servo Angle {angulo}: {percentagem:.2f}% anomalies")
    print("Anomalous Values:")
    for anomalous_value in anomalous_values:
        print(anomalous_value)
    
    # criando uma nova coleção para inserir os valores significativos da análise do testeH em função da posição do servo
    tratando_testeH.insert_one({
        "servo_angle": angulo,
        "media_anomalias": medias_anomalias[angulo],
        "percentage_anomalies": percentagem,
        "anomalous_values": anomalous_values
    })

# criando gráfico para ver a taxa de anormalidade em um intervalo amostral de 70 amostras e um função da podição do servo
angulos = list(anomalous_values_by_angle.keys())
percentagens = [(len(values) / 10) * 100 for values in anomalous_values_by_angle.values()]

plt.bar(angulos, percentagens)
plt.xlabel("Angulo do Servo")
plt.ylabel("Porcentagem de valores anormais (%)")
plt.title("Porcentagem de valores anormais por angulo do servo")

# Adiciona a média sobre as barras
for i, valor in enumerate(percentagens):
    plt.text(angulos[i], valor, f"{medias_anomalias[angulos[i]]:.2f}", ha='center', va='bottom')

plt.show()
