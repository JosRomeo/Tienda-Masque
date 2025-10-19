from flask import Flask, render_template, request, redirect, url_for, flash, session
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
    email = db.Column(db.String(120), unique=True, nullable=False)
    fruta_favorita = db.Column(db.String(50), nullable=True)
    nacimiento = db.Column(db.Integer, nullable=True)
    ubicacion = db.Column(db.String(120), nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
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

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalogo')
def list_products():
    productos = Producto.query.all()
    return render_template('list_products.html', productos=productos)

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['password']
        email = request.form['email']
        fruta_favorita = request.form.get('fruta_favorita')
        nacimiento = request.form.get('nacimiento')
        ubicacion = request.form.get('ubicacion')

        existing_user = Usuario.query.filter_by(username=username).first()
        if existing_user:
            flash("El nombre de usuario ya existe.")
            return redirect(url_for('register'))

        new_user = Usuario(
            username=username,
            email=email,
            fruta_favorita=fruta_favorita,
            nacimiento=nacimiento,
            ubicacion=ubicacion
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", usuario=current_user)

# Carrito de compras
@app.route("/carrito")
def carrito():
    if 'cart' not in session:
        session['cart'] = []

    cart_items = []
    for item in session['cart']:
        producto = Producto.query.get(item['id'])  # usar item['id']
        if producto:
            cart_items.append({
                "id": producto.id,
                "name": producto.name,
                "price": producto.price,
                "quantity": item['quantity'],
                "image_url": f"/static/images/products/{producto.name.replace(' ', '')}.jpg"
            })

    subtotal = sum(i["price"] * i["quantity"] for i in cart_items)
    shipping = 0
    total = subtotal + shipping

    return render_template(
        "carrito.html",
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        total=total
    )

# Actualizar carrito
@app.route('/update_cart/<action>/<int:product_id>', methods=['POST'])
def update_cart(action, product_id):
    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']

    # Buscar si el producto ya está en el carrito
    product_in_cart = next((item for item in cart if item['id'] == product_id), None)

    if action == 'add':
        if product_in_cart:
            # Incrementar la cantidad si ya existe
            product_in_cart['quantity'] += 1
        else:
            # Si no existe, agregarlo con cantidad 1
            cart.append({'id': product_id, 'quantity': 1})

    elif action == 'remove':
        if product_in_cart:
            # Restar cantidad o eliminar si llega a 0
            product_in_cart['quantity'] -= 1
            if product_in_cart['quantity'] <= 0:
                cart = [item for item in cart if item['id'] != product_id]

    elif action == 'clear':
        cart.clear()

    # Guardar cambios en session
    session['cart'] = cart
    return redirect(url_for('carrito'))


#Compra realizada
@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        flash("Tu carrito está vacío", "error")
        return redirect(url_for('carrito'))

    for item in session['cart']:
        producto = Producto.query.get(item['id'])  # <--- aquí usamos item['id']
        if producto:
            if producto.quantity >= item['quantity']:
                producto.quantity -= item['quantity']  # restar según la cantidad comprada
                db.session.add(producto)
            else:
                flash(f"No hay suficientes unidades de {producto.name}", "error")
                return redirect(url_for('carrito'))

    db.session.commit()
    session['cart'] = []  # vaciar carrito
    return render_template("compra.html")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=666, debug=True)
