import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200
@app.route('/user', methods=['POST'])
def create_user():
    # Obtener los datos del cuerpo de la solicitud
    data = request.get_json()

    # Validar si los datos están presentes
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # Extraer los datos necesarios
    username = data.get('username')
    planet_ids = data.get('favorite_planets', [])  # Lista de IDs de planetas favoritos
    people_ids = data.get('favorite_people', [])   # Lista de IDs de personas favoritas

    # Validar que el campo `username` esté presente
    if not username:
        return jsonify({"error": "Missing required field: username"}), 400

    # Crear un nuevo usuario
    new_user = User(username=username)

    # Añadir el nuevo usuario a la base de datos
    db.session.add(new_user)
    db.session.commit()

    # Agregar los planetas favoritos
    for planet_id in planet_ids:
        planet = Planet.query.get(planet_id)  # Buscar el planeta por ID
        if planet:  # Si existe el planeta
            new_favorite = Favorite(user_id=new_user.id, planet_id=planet.id)
            db.session.add(new_favorite)

    # Agregar las personas favoritas
    for people_id in people_ids:
        person = People.query.get(people_id)  # Buscar la persona por ID
        if person:  # Si existe la persona
            new_favorite = Favorite(user_id=new_user.id, people_id=person.id)
            db.session.add(new_favorite)

    # Confirmar los cambios en la base de datos
    db.session.commit()

    # Responder con los datos del nuevo usuario
    return jsonify(new_user.serialize()), 201


# Endpoint para listar todas las personas (People)
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_list = [person.serialize() for person in people]
    return jsonify(people_list), 200

# Endpoint para obtener los detalles de una persona específica por id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person_by_id(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404
    return jsonify(person.serialize()), 200

# Endpoint para agregar una nueva persona
@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    name = data.get('name')
    gender = data.get('gender')
    height = data.get('height')

    if not name or not gender or not height:
        return jsonify({"error": "Missing required fields"}), 400

    new_person = People(name=name, gender=gender, height=height)
    db.session.add(new_persn)
    db.session.commit()

    return jsonify(new_person.serialize()), 201


# Endpoint para listar todos los planetas (Planets)
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_list = [planet.serialize() for planet in planets]
    return jsonify(planets_list), 200

# Endpoint para obtener los detalles de un planeta específico por id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

# Endpoint para agregar un nuevo planeta
@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()

    # Verificar si los campos necesarios están en los datos
    if 'name' not in data or 'climate' not in data or 'terrain' not in data:
        return jsonify({"error": "Missing required fields: name, climate or terrain"}), 400

    # Crear un nuevo planeta
    new_planet = Planet(name=data['name'], climate=data['climate'], terrain=data['terrain'])
    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 201

# Endpoint para listar todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [user.serialize() for user in users]
    return jsonify(users_list), 200

# Endpoint para listar todos los favoritos del usuario actual
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorite_planets = [favorite.planet.serialize() for favorite in favorites if favorite.planet]
    favorite_people = [favorite.people.serialize() for favorite in favorites if favorite.people]
    
    return jsonify({"planets": favorite_planets, "people": favorite_people}), 200

# Endpoint para agregar un planeta a los favoritos del usuario
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        return jsonify({"message": "Planet already in favorites"}), 400

    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Planet added to favorites"}), 201

# Endpoint para agregar una persona a los favoritos del usuario
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite:
        return jsonify({"message": "Person already in favorites"}), 400

    new_favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Person added to favorites"}), 201

# Endpoint para eliminar un planeta de los favoritos del usuario
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Planet not in favorites"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Planet removed from favorites"}), 200

# Endpoint para eliminar una persona de los favoritos del usuario
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people(people_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"error": "Person not in favorites"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Person removed from favorites"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
