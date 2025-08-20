from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ServerSelectionTimeoutError
import certifi
import uuid
from datetime import datetime
import math
from typing import Annotated
from pydantic import BaseModel, constr, Field
import secrets

uri = "mongodb+srv://crisesv4:Tanke280423@cluster0.ejxv3jy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
import cloudinary
import cloudinary.uploader
cloudinary.config( 
    cloud_name = "dkjlygxse", 
    api_key = "111946664427639", 
    api_secret = "iYwxs47jmdPmb-xCGtJfWKtg-F8", # Click 'View API Keys' above to copy your API secret
    secure=True
)
def upload_image(image_path):
# Configuration       

# Upload an image
    upload_result = cloudinary.uploader.upload(image_path,
                                           public_id="")
    return(upload_result["secure_url"])
# Cliente global con TLS y certifi
client = MongoClient(
    uri,
    server_api=ServerApi("1"),
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000,
    tls=True
)
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
db = client["BlueSwitchData"]


def CalculateCO2forDevice(devices):
    CO2Total = []
    for device in devices:
        created_at_list = device.get("created_at", [])

        if isinstance(created_at_list, list):
            for interval in created_at_list:
                if isinstance(interval, list) and len(interval) == 2:
                    start, end = interval

                    try:
                        # Convertir start a datetime aware en UTC
                        if start:
                            start_datetime = datetime.datetime.fromisoformat(str(start))
                            if start_datetime.tzinfo is None:
                                start_datetime = start_datetime.replace(tzinfo=datetime.timezone.utc)
                        else:
                            continue

                        # Convertir end o usar ahora (también aware en UTC)
                        if end:
                            end_datetime = datetime.datetime.fromisoformat(str(end))
                            if end_datetime.tzinfo is None:
                                end_datetime = end_datetime.replace(tzinfo=datetime.timezone.utc)
                        else:
                            end_datetime = datetime.datetime.now(datetime.timezone.utc)

                        # Calcular tiempo en horas
                        time_difference = end_datetime - start_datetime
                        hours = time_difference.total_seconds() / 3600

                        # Calcular CO2
                        watts = device.get("watts", 0)
                        CO2 = (watts * hours / 1000) * 0.44
                        CO2Total.append([round(CO2, 2),round(hours, 2)])
               

                    except Exception as e:
                        print(f"Error procesando intervalo {interval}: {e}")
    return CO2Total
import secrets

class TeamMember(BaseModel):
    email: str
    role: str

class Team(BaseModel):
    Name: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    StringId: str = Field(default_factory=lambda: secrets.token_hex(6))
    Members: list[TeamMember] = []
def calculateWatts(devices):
    watts = 0
    for device in devices:
        watts += device['watts']
    return watts/len(devices)
from pydantic import BaseModel, constr, Field, field_validator
from typing import Annotated, List
class User(BaseModel):
    nombre: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    email: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    password: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    phone: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    city: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    avatar: Annotated[str, constr(min_length=1, strip_whitespace=True)]= "https://res.cloudinary.com/dkjlygxse/image/upload/v1746846631/is-there-a-sniper-default-pfp-that-someone-made-v0-78az45pd9f6c1_ymnf4h.webp"
userscollection = db["Users"]
devicescollection = db["Devices"]
discardDevicesCollection = db["discardDevices"]
teamscollection = db["Teams"]
class Producto(BaseModel):
    nombre: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    categoria: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    watts: int
    color: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    state: bool = True
    created_at: List[datetime] = Field(default_factory=lambda: [datetime.utcnow().isoformat()])
    email: Annotated[str, constr(min_length=1, strip_whitespace=True)]
    favorite: bool = False
    team: Annotated[str, constr(min_length=1, strip_whitespace=True)]

    @field_validator('watts')
    @classmethod
    def validar_watts_positivo(cls, valor):
        if valor <= 0:
            raise ValueError('El valor de los watts debe ser positivo')
        return valor

def CalculateCO2(devices):
    CO2Total = 0
    device_CO2 = {}  # CO2 por dispositivo
    device_emails = {}  # Email por dispositivo

    for device in devices:
        device_name = device.get("nombre", "Desconocido")
        device_email = device.get("email", "Desconocido")
        device_CO2[device_name] = 0
        device_emails[device_name] = device_email

        created_at_list = device.get("created_at", [])
        if isinstance(created_at_list, list):
            for interval in created_at_list:
                if isinstance(interval, list) and len(interval) == 2:
                    start, end = interval
                    try:
                        # start
                        if start:
                            start_datetime = datetime.datetime.fromisoformat(str(start))
                            if start_datetime.tzinfo is None:
                                start_datetime = start_datetime.replace(tzinfo=datetime.timezone.utc)
                        else:
                            continue
                        # end
                        if end:
                            end_datetime = datetime.datetime.fromisoformat(str(end))
                            if end_datetime.tzinfo is None:
                                end_datetime = end_datetime.replace(tzinfo=datetime.timezone.utc)
                        else:
                            end_datetime = datetime.datetime.now(datetime.timezone.utc)

                        hours = (end_datetime - start_datetime).total_seconds() / 3600
                        watts = device.get("watts", 0)
                        CO2 = (watts * hours / 1000) * 0.44
                        CO2Total += CO2
                        device_CO2[device_name] += CO2

                    except Exception as e:
                        print(f"Error procesando intervalo {interval}: {e}")

    # Obtener dispositivo con más CO2
    if device_CO2:
        max_device_name = max(device_CO2, key=device_CO2.get)
        max_device_email = device_emails.get(max_device_name, None)
    else:
        max_device_name = None
        max_device_email = None

    total_CO2 = round(CO2Total, 3) if CO2Total > 0 else (1 if CO2Total < 0 else 0)
    return total_CO2, {"nombre": max_device_name, "email": max_device_email}
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
@app.route("/create_user", methods=["POST"])
def create_user():
    data = request.get_json(force=True)
    try:
        user = User(
            nombre=data["nombre"],
            email=data["email"],
            password=data["password"],
            city=data["city"],
            phone=data["phone"]
        )
        userscollection.insert_one(user.__dict__)
        return jsonify({"mensaje": "Usuario creado con exito"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_user", methods=['POST'])
def get_user_info():
    data = request.get_json(force=True)
    email = data.get('email')
    try:
        user = userscollection.find_one({"email": email}, {"_id": False})
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update_user", methods=["POST"])
def update_user():
    data = request.get_json(force=True)
    email = data.get("email")
    if not email:
        return jsonify({"success": False, "error": "Email is required"}), 400

    update_fields = {k: v for k, v in data.items() if v and k != "email"}
    result = userscollection.update_one({"email": email}, {"$set": update_fields})

    if result.matched_count > 0:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "error": "User not found"}), 404

@app.route("/upload_avatar", methods=["POST"])
def upload_avatar():
    data = request.get_json(force=True)
    email = data.get("email")
    imageUri = data.get("imageUri")
    if not email or not imageUri:
        return jsonify({"success": False, "error": "Email and avatar are required"}), 400
    
    try:
        avatar = upload_image(imageUri)
        userscollection.update_one({"email": email}, {"$set": {"avatar": avatar}})
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -------- DISPOSITIVOS --------
@app.route("/crear-device", methods=["POST"])
def crear_producto():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"mensaje": "No se recibió información"}), 400

    campos_requeridos = ["nombre", "categoria", "watts", "color", "team_code", "email"]
    for campo in campos_requeridos:
        if campo not in data or data[campo] == "" or data[campo] is None:
            return jsonify({"mensaje": f"All fields are required"}), 400

    try:
        producto = Producto(
            nombre=data["nombre"],
            categoria=data["categoria"],
            watts=data["watts"],
            color=data["color"],
            state=True,
            email=data["email"],
            created_at=[],
            team=data["team_code"]
        )
        producto_dict = producto.model_dump(exclude_unset=False)
        producto_dict["stringid"] = str(uuid.uuid4())
        producto_dict["created_at"] = [[datetime.now().isoformat(), None]]
        devicescollection.insert_one(producto_dict)
        return jsonify({"mensaje": "Producto creado exitosamente"}), 200
    except Exception as e:
        return jsonify({"mensaje": "Error inesperado en el servidor", "error": str(e)}), 500

@app.route("/get_devices", methods=["POST"])
def get_devices():
    data = request.get_json(force=True)
    email = data.get("email")
    team_code = data.get("team_code")
    if not email and not team_code:
        return jsonify({"error": "Either email or team_code is required"}), 400

    query = {"email": email} if email else {"team": team_code}
    devices = list(devicescollection.find(query, {"_id": False}))
    return jsonify(devices), 200

@app.route("/update-status", methods=['PUT'])
def update_device_status():
    data = request.get_json(force=True)
    device_id = data.get('id')
    new_status = data.get('status')
    args = data.get('argument')
    if device_id is None or new_status is None:
        return jsonify({'error': 'Faltan id o status'}), 400
    try:
        device = devicescollection.find_one({'stringid': device_id})
        if not device:
            return jsonify({'error': 'Dispositivo no encontrado'}), 404

        if args == "Switch":
            historial = device.get('created_at', [])
            now = datetime.utcnow().isoformat()
            if device.get('state') == new_status:
                return jsonify({'mensaje': 'El estado ya está actualizado'}), 200
            if new_status is True:
                historial.append([now, None])
            elif new_status is False and historial and historial[-1][1] is None:
                historial[-1][1] = now
            devicescollection.update_one({'stringid': device_id}, {'$set': {'state': new_status, 'created_at': historial}})
            return jsonify({'mensaje': 'Estado y fechas actualizados correctamente'}), 200
        elif args == "Delete":
            discardDevicesCollection.insert_one(device)
            devicescollection.delete_one({'stringid': device_id})
            return jsonify({'mensaje': 'Dispositivo eliminado correctamente'}), 200
        elif args == "Favorite":
            current_status = device.get('favorite', False)
            new_status = not current_status
            devicescollection.update_one({'stringid': device_id}, {'$set': {'favorite': new_status}})
            return jsonify({'mensaje': 'Estado actualizado correctamente'}), 200
        else:
            return jsonify({'mensaje': 'La acción no es válida'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/read-CO2", methods=["POST"])
def read_CO2():
    data = request.get_json(force=True)
    email = data.get("email")
    team_code = data.get("team_code")
    if not email and not team_code:
        return jsonify({"error": "Email or team_code required"}), 400
    devices = list(devicescollection.find({"email": email} if email else {"team": team_code}, {"_id": False}))
    total_CO2, max_device_info = CalculateCO2(devices)
    return jsonify({"total_CO2": total_CO2, "device_mas_CO2": max_device_info}), 200

@app.route("/read_perDev", methods=['POST'])
def read_perDev():
    data = request.get_json(force=True)
    devices = data.get("data", [])
    try:
        CO2 = CalculateCO2forDevice(devices)
        return jsonify(CO2), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/readstatisdics_peruser", methods=["POST"])
def statistics_per_user():
    data = request.get_json(force=True)
    email = data.get("email")
    team_code = data.get("team_code")
    if not email or not team_code:
        return jsonify({"success": False, "error": "Email and team_code are required"}), 400
    statistics = list(devicescollection.find({"email": email, "team": team_code}, {"_id": False}))
    if not statistics:
        return jsonify({"success": True, "data": {"CO2": 0, "numdevices": 0, "trees": 0, "watts": 0}}), 200
    CO2 = CalculateCO2forDevice(statistics)
    Watts = calculateWatts(statistics)
    co2_value = CO2[0][0] if CO2 and CO2[0][0] else 0
    trees_value = math.ceil(co2_value / 22)
    return jsonify({"success": True, "data": {"CO2": co2_value, "numdevices": len(statistics), "trees": trees_value, "watts": Watts if Watts else 0}}), 200

# -------- EQUIPOS --------
@app.route('/create_team', methods=['POST'])
def create_team():
    data = request.get_json(force=True)
    team_name = data['team_name']
    user_email = data['email']
    try:
        team = Team(Name=team_name, Members=[TeamMember(email=user_email, role="admin")])
        teamscollection.insert_one(team.model_dump())
        return jsonify({"mensaje": "Equipo creado con éxito", "team": team.dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/join_team', methods=['POST'])
def join_team():
    data = request.get_json(force=True)
    team_name = data['team_name']
    user_email = data['email']
    team_code = data['team_code']
    team = teamscollection.find_one({'Name': team_name, 'StringId': team_code})
    if not team:
        return jsonify({"mensaje": "El equipo no existe o el código es incorrecto"}), 400
    for member in team.get('Members', []):
        if member.get('email') == user_email:
            return jsonify({"mensaje": "Ya eres miembro del equipo"}), 400
    teamscollection.update_one({'Name': team_name, 'StringId': team_code}, {'$push': {'Members': {'email': user_email, 'role': 'member'}}})
    return jsonify({"mensaje": "Te uniste al equipo con éxito"}), 200

@app.route("/read_teams", methods=['POST'])
def read_teams():
    data = request.get_json(force=True)
    user_email = data['email']
    teams_cursor = teamscollection.find({'Members.email': user_email})
    teams = []
    for team in teams_cursor:
        for member in team.get('Members', []):
            if member.get('email') == user_email:
                teams.append({'name': team.get('Name'), 'code': team.get('StringId'), 'role': member.get('role')})
                break
    return jsonify({'teams': teams}), 200

@app.route("/get_members", methods=['POST'])
def get_members():
    data = request.get_json(force=True)
    team_code = data['team_code']
    if not team_code:
        return jsonify({"mensaje": "El código del equipo es requerido"}), 400
    team = teamscollection.find_one({'StringId': team_code})
    if not team:
        return jsonify({"mensaje": "El equipo no existe"}), 404
    return jsonify({"members": team.get('Members', [])}), 200

@app.route("/update_members", methods=['POST'])
def update_members():
    data = request.get_json(force=True)
    team_code = data['teamcode']
    user_email = data['email']
    mode = data['action']
    if not team_code or not user_email:
        return jsonify({"mensaje": "teamcode y email requeridos"}), 400
    if mode == "promote":
        teamscollection.update_one({'StringId': team_code, 'Members.email': user_email}, {'$set': {'Members.$.role': 'assistant'}})
        return jsonify({"mensaje": "El usuario ha sido promovido a asistente"}), 200
    elif mode == "demote":
        teamscollection.update_one({'StringId': team_code, 'Members.email': user_email}, {'$set': {'Members.$.role': 'member'}})
        return jsonify({"mensaje": "El usuario ha sido degradado a miembro"}), 200
    elif mode == "delete":
        teamscollection.update_one({'StringId': team_code}, {'$pull': {'Members': {'email': user_email}}})
        return jsonify({"mensaje": "El usuario ha sido eliminado del equipo"}), 200
    else:
        return jsonify({"mensaje": "La acción no es válida"}), 400

@app.route("/delete_team", methods=['POST'])
def delete_team():
    data = request.get_json(force=True)
    team_code = data['teamcode']
    if not team_code:
        return jsonify({"mensaje": "El código del equipo es requerido"}), 400
    teamscollection.delete_one({'StringId': team_code})
    return jsonify({"mensaje": "El equipo ha sido eliminado"}), 200

@app.route("/leave_team", methods=['POST'])
def leave_team():
    data = request.get_json(force=True)
    user_email = data['email']
    team_code = data['teamcode']
    teamscollection.update_one({'StringId': team_code}, {'$pull': {'Members':{'email': user_email}}})
    result = list(devicescollection.find({"email": user_email, "team": team_code}))
    for doc in result:
        doc.pop("_id", None)
    discardDevicesCollection.insert_many(result)
    devicescollection.update_many({"email": user_email, "team": team_code}, {"$set": {"team": "no_team"}})
    return jsonify({"mensaje": "El usuario ha dejado el equipo"}), 200
print("AQUi")
if __name__ == "__main__":
    print("SI")
    app.run(debug=True, host="0.0.0.0", port=5000)
