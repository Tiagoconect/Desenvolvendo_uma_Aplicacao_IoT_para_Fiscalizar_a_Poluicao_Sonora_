from pymongo import MongoClient
import pandas as pd

# Conectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # Escolha o banco de dados do projeto

# Coleção com os valores da média móvel
colecao_media_movel = db["valores_media_movel"]

# Coleção com os resultados do teste H (tratando_testeH)
colecao_tratando_testeH = db["tratando_testeH"]

# Função para verificar se um valor está dentro dos limites de ruído permitidos
def verificar_limite_ruido(valor, periodo):
    limite_diurno = 55  # Limite diurno em decibéis
    limite_noturno = 50  # Limite noturno em decibéis

    if periodo == "diurno":
        return valor <= limite_diurno
    elif periodo == "noturno":
        return valor <= limite_noturno

# Função para verificar se um valor anormal viola a legislação de ruído
def verificar_violacao_legislacao(angulo_servo, media_movel, tempo):
    if 7 <= tempo.hour < 20:
        periodo = "diurno"
    else:
        # Verifique se o próximo dia é domingo ou feriado
        proximo_dia = tempo + pd.DateOffset(days=1)
        if proximo_dia.weekday() == 6 or proximo_dia in feriados:
            if 20 <= tempo.hour < 9:
                periodo = "noturno"
        else:
            if 20 <= tempo.hour < 7:
                periodo = "noturno"

    if verificar_limite_ruido(media_movel, periodo):
        return f"Ângulo {angulo_servo} às {tempo}: {media_movel} dB no período {periodo} viola a legislação"
    else:
        return None

# Iterar pela coleção de valores da média móvel
for doc in colecao_media_movel.find():
    angulo_servo = doc["valor_servo"]
    media_movel = doc["media_movel"]
    tempo = doc["tempo"]
    
    # Verificar se há algum valor anormal na coleção tratando_testeH no mesmo horário
    query = {
        "servo_angle": angulo_servo,
        "anomalous_values.tempo": tempo
    }
    resultado = colecao_tratando_testeH.find_one(query)
    
    if resultado:
        anomalous_values = resultado["anomalous_values"]
        
        for anomalous_value in anomalous_values:
            tempo_anomalia = anomalous_value["tempo"]
            
            # Verificar se o valor anormal também viola a legislação
            violacao = verificar_violacao_legislacao(angulo_servo, media_movel, tempo_anomalia)
            
            if violacao:
                print(violacao)
