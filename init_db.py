#Ajuste base de datos 


from app import app, db

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Tablas creadas correctamente en la base de datos")
