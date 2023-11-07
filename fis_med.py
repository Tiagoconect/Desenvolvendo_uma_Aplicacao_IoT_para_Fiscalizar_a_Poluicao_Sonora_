from pymongo import MongoClient
from datetime import datetime

# Conectando ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0  # Escolha o banco de dados de acesso do projeto
colecao = db["tratando_testeH"]

# Criar uma nova coleção para valores que violaram os limites
colecao_violacoes = db["violacoes"]

# Limites de decibéis permitidos
limite_dB_dia = 50  # Limite durante o dia
limite_dB_noite = 45  # Limite durante a noite

# Definir as horas de início (7:00:00) e fim (22:00:00) no formato de hora com segundos
hora_inicio = datetime.strptime("07:00:00", "%H:%M:%S").time()
hora_fim = datetime.strptime("22:00:00", "%H:%M:%S").time()

# Consultando os documentos na coleção
for documento in colecao.find():
    angulo = documento["servo_angle"]
    media_anomalias = documento.get("media_anomalias", 0.0)
    inicio_intervalo = documento.get("inicio_intervalo", {}).get("hora", "00:00:00")
    fim_intervalo = documento.get("fim_intervalo", {}).get("hora", "00:00:00")
    anomalous_values = documento.get("anomalous_values", [])
    percentagem_anomalias = documento["percentage_anomalies"]

    # Converta as horas para o formato de hora com segundos
    hora_inicio_intervalo = datetime.strptime(inicio_intervalo, "%H:%M:%S").time()
    hora_fim_intervalo = datetime.strptime(fim_intervalo, "%H:%M:%S").time()
    if percentagem_anomalias > 10:
        tipo_violacao = None
        print(f"Ângulo do Servo: {angulo}, Percentual de Anomalia: {percentagem_anomalias:.2f}%")
        print(f"Média das Anomalias: {media_anomalias:.2f}")
        if anomalous_values:
            fim_intervalo = anomalous_values[0]
            inicio_intervalo  = anomalous_values[-1]
            print(f"Intervalo de Anomalias: Início - {inicio_intervalo['tempo']}, Fim - {fim_intervalo['tempo']}")
    # Verificar se o horário (inicio_intervalo ou fim_intervalo) está entre 7:00:00 e 22:00:00
        if hora_inicio <= hora_inicio_intervalo <= hora_fim or hora_inicio <= hora_fim_intervalo <= hora_fim:
           if media_anomalias > limite_dB_dia:
               print(f"Ângulo do Servo: {angulo}, Média em dB: {media_anomalias:.2f} (Ultrapassou o limite diurno)")
               tipo_violacao = "Limite diurno"

        else:
            if media_anomalias > limite_dB_noite:
                print(f"Ângulo do Servo: {angulo}, Média em dB: {media_anomalias:.2f} (Ultrapassou o limite noturno)")
                tipo_violacao = "Limite noturno"
       
        if tipo_violacao:
            # Criar um documento para a coleção de violações
            documento_violacao = {
                "angulo": angulo,
                "inicio_intervalo": inicio_intervalo,
                "fim_intervalo": fim_intervalo,
                "percentagem_anomalias": percentagem_anomalias,
                "media_anomalias": media_anomalias,
                "tipo_violacao": tipo_violacao
            }
            # Inserir o documento na coleção de violações
            colecao_violacoes.insert_one(documento_violacao)



