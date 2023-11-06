from flask import Flask, request, render_template, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo 

app = Flask(__name__)
# Conectando ao banco de dados cluster0 do projeto radar
uri = "mongodb+srv://tiagodois0:80432162@cluster0.zxazakw.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["cluster0"]  # Nome do banco de dados criado no MongoDB Atlas

# Recebendo dados via HTTP usando método POST
@app.route('/receber-dados', methods=['POST'])
def receber_dados():
    if request.method == 'POST':
        valor_sensor = request.form.get('sensor')
        valor_servo = request.form.get('servo')
        valor_tempo = request.form.get('time')

        # Imprimindo os valores recebidos pelo servidor
        print("Valor do sensor recebido:", valor_sensor)
        print("Valor do servo recebido:", valor_servo)
        print("Tempo recebido:", valor_tempo)

        # Enviar os valores para o MongoDB e criar uma nova coleção de dados
        collection = db["valores_enviados_pela_esp"]
        collection.insert_one({
            "valor_sensor": valor_sensor,
            "valor_servo": valor_servo,
            "tempo": valor_tempo
        })

        # Indicação de que o MongoDB recebeu os dados
        return "Valores recebidos com sucesso!"

# Definir a coleção fora da função "receber_dados"
collection = db["valores_enviados_pela_esp"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    sensor_data = []
    servo_data = []
    for doc in collection.find().sort("tempo", 1):
        sensor_data.append(float(doc["valor_sensor"]))
        servo_data.append(float(doc["valor_servo"]))
    data = {
        'servo_data': servo_data,
        'sensor_data': sensor_data
    }
    return jsonify(data)

@app.route('/index1')
def index1():
    return render_template('index1.html')

@app.route('/get_data1')
def get_data1():
    data = []
    for doc in collection.find().sort("tempo", 1):
        data.append({
            'tempo': doc["tempo"],
            'valor_sensor': float(doc["valor_sensor"])
        })
    return jsonify(data)

@app.route('/radar')
def radar():
    # Get the latest servo angle from the MongoDB collection
    latest_data = collection.find_one(sort=[("tempo", pymongo.DESCENDING)])
    servo_angle = latest_data["valor_servo"] if latest_data else 0  # Default to 0 degrees if no data

    return render_template('radar.html', servo_angle=servo_angle)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
