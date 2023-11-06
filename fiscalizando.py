from pymongo import MongoClient
import datetime
import uuid

# Conexão ao MongoDB
client = MongoClient("mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/test")
db = client.cluster0

# Coleção "tratando_testeH" com os valores anormais
tratando_testeH = db["tratando_testeH"]
valores_enviados_pela_esp = db["valores_enviados_pela_esp"]

# Coleção para armazenar os valores que violaram a lei do PSIU
valores_violados_psiu = db["valores_violados_psiu"]

# Função para calcular a média móvel
def calcular_media_movel(data, window_size):
    return sum(data[-window_size:]) / window_size

# Função para verificar a lei de poluição sonora de São Paulo (PSIU)
def verificar_lei_psiu(valor_anormal, media_movel, hora_anomalia):
    if hora_anomalia >= datetime.time(7, 0) and hora_anomalia < datetime.time(20, 0):
        limite_diurno = 55
        if valor_anormal > limite_diurno:
            return "Violou a lei do PSIU no período diurno"
    else:
        limite_noturno = 50
        if hora_anomalia >= datetime.time(20, 0) or hora_anomalia < datetime.time(7, 0):
            # Verifica se o dia seguinte é domingo ou feriado
            dia_anterior = hora_anomalia - datetime.timedelta(days=1)
            dia_seguinte = hora_anomalia + datetime.timedelta(days=1)
            if dia_anterior.weekday() == 6 or dia_seguinte.weekday() == 6:
                limite_noturno = 50
                if valor_anormal > limite_noturno:
                    return "Violou a lei do PSIU no período noturno estendido"
        else:
            if valor_anormal > limite_noturno:
                return "Violou a lei do PSIU no período noturno"
    return None

# Consulta os valores anormais da coleção "tratando_testeH"
for registro in tratando_testeH.find():
    servo_angle = registro["servo_angle"]
    anomalous_values = registro.get("anomalous_values", [])  # Obter valores anormais ou uma lista vazia
    if not anomalous_values:
        continue  # Não há valores anormais para este ângulo do servo
    
    for anomalous_value in anomalous_values:
        hora_anomalia_str = anomalous_value["tempo"]
    
        # Converte a string de data/hora em um objeto datetime com uma data fictícia
        data_referencia = datetime.datetime(2023, 1, 1)
        data_completa = datetime.datetime.strptime(hora_anomalia_str, "%H:%M:%S")
        hora_anomalia = data_completa.time()
    
        # Consulta a média móvel para o mesmo horário
        media_movel_hora_anomalia = calcular_media_movel(
            [float(valor["valor_sensor"]) for valor in valores_enviados_pela_esp.find({"tempo": {"$lte": data_completa}})],
            window_size=10  # Tamanho da janela para a média móvel
        )
    
        # Verifica a lei do PSIU
        resultado_psiu = verificar_lei_psiu(anomalous_value["valor_sensor"], media_movel_hora_anomalia, hora_anomalia)
        
        if resultado_psiu is not None:
            # Gere um identificador único (pode ser um UUID, por exemplo)
            codigo_item_infracao = str(uuid.uuid4())
            
            # Converte a data de datetime.date para uma string no formato ISO 8601
            data_anomalia_str = data_completa.strftime("%Y-%m-%d")
            
            # Insira os dados na coleção "valores_violados_psiu"
            valores_violados_psiu.insert_one({
                "hora_anomalia": hora_anomalia_str,
                "data_anomalia": data_anomalia_str,
                "valor_anormal": anomalous_value["valor_sensor"],
                "media_movel": media_movel_hora_anomalia,
                "angulo_servo": servo_angle,
                "codigo_item_infracao": codigo_item_infracao
            })
