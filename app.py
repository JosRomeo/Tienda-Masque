from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.secret_key = "supersecretkey" 

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://JSr:NITO2004@localhost/web'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Usuario
class Usuario(UserMixin, db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'

# Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Producto {self.name} = available {self.quantity}>'

# Configuración de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login" 

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

#  Rutas 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalogo')
def list_products():
    return render_template('list_products.html')

# Iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['password']

        user = Usuario.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)  
            return redirect(url_for('index'))
        else:
            flash("Usuario o contraseña incorrectos")
            return redirect(url_for("login"))
        

    return render_template('login.html')

# Crear cuenta
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['password']

        existing_user = Usuario.query.filter_by(username=username).first()
        if existing_user:
            return "El nombre de usuario ya existe. Por favor, elige otro."

        new_user = Usuario(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    
    return render_template('register.html')

# Cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=666, debug=True)
