from pymongo import MongoClient

# Conectar ao banco de dados MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # Substitua pelo nome correto do banco de dados

# Coleção onde os valores da média móvel são armazenados
collection = db["valores_media_movel"]

# Definir os limites de ruído permitidos pela legislação em dB
limite_diurno = 50
limite_noturno = 45

# Recuperar os últimos 100 valores da média móvel do banco de dados
valores_media_movel = [doc["media_movel"] for doc in collection.find().sort("tempo", -1).limit(100)]

# Função para verificar se o valor da média móvel excede o limite atual
def verificar_limite(valor, limite):
    return valor > limite

# Verificar o limite com base no horário atual
# Neste exemplo, consideramos um horário fixo para a análise
limite_atual = limite_diurno  # Você pode ajustar o limite com base na hora atual, se necessário

# Realizar a análise e imprimir os resultados
for valor in valores_media_movel:
    excede_limite = verificar_limite(valor, limite_atual)
    if excede_limite:
        print(f"Valor da média móvel excede o limite ({limite_atual} dB). Valor atual: {valor} dB")
    else:
        print(f"Valor da média móvel está dentro do limite ({limite_atual} dB). Valor atual: {valor} dB")
