from flask import Flask, redirect, render_template, request
import sqlite3
import random
import string

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE,
            original_url TEXT,
            clicks INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def generar_codigo():
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['url']
    
    if not original_url.startswith('http'):
        original_url = 'https://' + original_url
    
    short_code = generar_codigo()
    
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO urls (short_code, original_url) VALUES (?, ?)',
        (short_code, original_url)
    )
    conn.commit()
    conn.close()
    
    short_url = f"http://localhost:5000/{short_code}"
    return render_template('index.html', short_url=short_url, original=original_url)

@app.route('/<short_code>')
def redirigir(short_code):
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT original_url FROM urls WHERE short_code = ?', (short_code,))
    resultado = cursor.fetchone()
    
    if resultado:
        cursor.execute('UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?', (short_code,))
        conn.commit()
        conn.close()
        return redirect(resultado[0])
    
    conn.close()
    return "URL no encontrada", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)