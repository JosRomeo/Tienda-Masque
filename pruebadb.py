from app import app, db, Usuario  
from werkzeug.security import generate_password_hash
from datetime import datetime
import random

# Listas de datos de prueba
frutas = ['Manzana', 'Plátano', 'Naranja', 'Fresa', 'Mango', 'Uva']
estados = ['Aguascalientes', 'Baja California', 'Chiapas', 'Jalisco', 'Yucatán', 'Ciudad de México']

# Número de usuarios
NUM_USUARIOS = 200  

with app.app_context(): 
    Usuario.query.delete()
    db.session.commit()

    for i in range(1, NUM_USUARIOS + 1):
        # Contraseña de prueba (segura)
        password = generate_password_hash('123456')

        # Crear usuario de prueba
        usuario = Usuario(
            username=f"Usuario{i}",
            email=f"user{i}@correo.com",
            fruta_favorita=random.choice(frutas),
            nacimiento=random.randint(1980, 2010),
            ubicacion=random.choice(estados),
            fecha_creacion=datetime.now(),
            password_hash=password
        )

        db.session.add(usuario)

    db.session.commit()
    print(f"Se han generado {NUM_USUARIOS} usuarios de prueba en la base de datos")


