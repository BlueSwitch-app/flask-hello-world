from flask import Flask, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ServerSelectionTimeoutError
import certifi

uri = "mongodb+srv://crisesv4:Tanke280423@cluster0.ejxv3jy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Cliente global con TLS y certifi
client = MongoClient(
    uri,
    server_api=ServerApi("1"),
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000,
    tls=True
)

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route("/connection", methods=["GET"])
def connection():
    try:
        # Aquí usamos el client global ya configurado
        client.admin.command("ping")
        return jsonify({"status": "success", "message": "Conectado a MongoDB"})
    except ServerSelectionTimeoutError as e:
        return jsonify({"status": "error", "message": str(e)}), 500
