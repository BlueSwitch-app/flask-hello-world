from flask import Flask, jsonify 
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ServerSelectionTimeoutError
import certifi
uri = "mongodb+srv://crisesv4:Tanke280423@cluster0.ejxv3jy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(
    uri,
    server_api=ServerApi("1"),
    tlsCAFile=certifi.where(),   # <- certificado raíz actualizado
    serverSelectionTimeoutMS=5000
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
        client = MongoClient(uri, server_api=ServerApi("1"), serverSelectionTimeoutMS=5000)
        client.admin.command("ping")  # Test de conexión
        return jsonify({"status": "success", "message": "Conectado a MongoDB"})
    except ServerSelectionTimeoutError as e:
        return jsonify({"status": "error", "message": str(e)}), 500