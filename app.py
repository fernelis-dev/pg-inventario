from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_config import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# ==================== Configuración Inicial ====================
app = Flask(__name__)
app.secret_key = 'Fmirandat'

# ==================== Decoradores ====================

def login_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario' not in session:
            flash('Inicia sesión primero', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorador

def solo_admin(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if session.get('tipo') != 'admin':
            flash('Acceso solo para administradores', 'danger')
            return redirect(url_for('bienvenida'))
        return f(*args, **kwargs)
    return decorador

def solo_usuario(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if session.get('tipo') != 'usuario':
            flash('Acceso solo para usuarios', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorador

# ==================== Filtros de Seguridad ====================

@app.before_request
def requerir_login():
    rutas_publicas = ['login', 'static', 'registro']
    if 'usuario' not in session and request.endpoint not in rutas_publicas:
        return redirect(url_for('login'))

# ==================== Rutas de Autenticación ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        tipo = request.form['tipo']

        if tipo == 'admin':
            if usuario == 'administradorfer' and contraseña == 'Fteheranm2004':
                session['usuario'] = usuario
                session['tipo'] = 'admin'
                flash('Inicio de sesión como administrador exitoso.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Credenciales de administrador incorrectas.', 'danger')

        elif tipo == 'usuario':
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (usuario,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user['contraseña'], contraseña):
                session['usuario'] = user['nombre']
                session['tipo'] = 'usuario'
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('bienvenida'))
            else:
                flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = generate_password_hash(request.form['contraseña'])

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, correo, contraseña) VALUES (%s, %s, %s)", (nombre, correo, contraseña))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Usuario registrado correctamente. Inicia sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))

# ==================== Vistas ====================

# Vista para ADMIN: CRUD
@app.route('/')
@login_requerido
@solo_admin
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('index.html', productos=productos)

# Vista para USUARIO: Página de bienvenida
@app.route('/bienvenida')
@login_requerido
@solo_usuario
def bienvenida():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()

    nombre_usuario = session.get('usuario')
    return render_template('bienvenida.html', productos=productos, nombre_usuario=nombre_usuario)

# ==================== Funcionalidades del CRUD ====================

@app.route('/agregar', methods=['GET', 'POST'])
@login_requerido
@solo_admin
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        cantidad = request.form['cantidad']
        precio = request.form['precio']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, cantidad, precio)
            VALUES (%s, %s, %s, %s)
        """, (nombre, descripcion, cantidad, precio))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_product.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_requerido
@solo_admin
def editar(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        cantidad = request.form['cantidad']
        precio = request.form['precio']

        cursor.execute("""
            UPDATE productos
            SET nombre = %s, descripcion = %s, cantidad = %s, precio = %s
            WHERE id = %s
        """, (nombre, descripcion, cantidad, precio, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_product.html', producto=producto)

@app.route('/eliminar/<int:id>', methods=['POST'])
@login_requerido
@solo_admin
def eliminar(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

# ==================== Ejecutar App ====================
if __name__ == '__main__':
    app.run(debug=True)
