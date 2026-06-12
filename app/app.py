import os
import time
from flask import Flask, render_template, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Configuración mediante variables de entorno
APP_NAME = os.getenv("APP_NAME", "Mi Aplicación Flask")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def get_db_connection():
    """Intenta conectar a la base de datos con reintentos."""
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            time.sleep(2)
    return None

def init_db():
    """Crea la tabla e inserta datos de prueba si está vacía."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # Crear tabla
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                precio NUMERIC(10, 2) NOT NULL,
                stock INT NOT NULL
            );
        ''')
        
        # Verificar si ya existen registros
        cursor.execute('SELECT COUNT(*) FROM productos;')
        if cursor.fetchone()[0] == 0:
            productos_semilla = [
                ('Laptop', 899.99, 10),
                ('Mouse Óptico', 19.99, 50),
                ('Teclado Mecánico', 49.99, 30),
                ('Monitor 24"', 159.99, 15),
                ('Auriculares Gamer', 35.50, 25)
            ]
            cursor.executemany(
                'INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s);',
                productos_semilla
            )
        conn.commit()
        cursor.close()
        conn.close()

# Inicializar la base de datos al arrancar
init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        status = "Conectado exitosamente"
        conn.close()
    else:
        status = "Error de conexión"
        
    return render_template('index.html', app_name=APP_NAME, version=APP_VERSION, status=status)

@app.route('/productos')
def listar_productos():
    conn = get_db_connection()
    if not conn:
        return "Error al conectar a la base de datos", 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT id, nombre, precio, stock FROM productos;')
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('productos.html', productos=productos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)