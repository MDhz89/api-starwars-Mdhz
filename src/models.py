from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Modelo People
class People(db.Model):
    __tablename__ = 'people'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(50))
    height = db.Column(db.Float)
    
    def __repr__(self):
        return f'<People {self.name}>'
    
    # Método serialize
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'height': self.height
        }

# Modelo Planet
class Planet(db.Model):
    __tablename__ = 'planets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    climate = db.Column(db.String(255))
    terrain = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Planet {self.name}>'
    
    # Método serialize
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'climate': self.climate,
            'terrain': self.terrain
        }

# Modelo User
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    
    # Relación con Favorite
    favorites = db.relationship('Favorite', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    # Método serialize
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'favorites': [favorite.serialize() for favorite in self.favorites]  # Serializa los favoritos
        }

# Modelo Favorite
class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Favorite {self.id}>'

    # Método serialize
    def serialize(self):
        data = {'id': self.id, 'user_id': self.user_id}

        # Si tiene un planeta asociado, agregarlo a la serialización
        if self.planet_id:
            planet = Planet.query.get(self.planet_id)
            data['planet'] = planet.serialize() if planet else None

        # Si tiene una persona asociada, agregarla a la serialización
        if self.people_id:
            person = People.query.get(self.people_id)
            data['people'] = person.serialize() if person else None

        return data
