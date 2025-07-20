# app.py

from flask import Flask, request, render_template_string
import sqlite3
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'insecure-key'  # hardcoded secret
app.config['WTF_CSRF_ENABLED'] = False     # CSRF protection disabled

# Set up logging without sanitization
logging.basicConfig(filename='app.log', level=logging.INFO)

def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn

@app.route('/')
def index():
    return '<h1>Welcome to Vulnerable Flask App</h1>'

# 🚨 Potential SQL Injection
@app.route('/search')
def search():
    username = request.args.get('user')
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return str(result)

# 🚨 XSS Vulnerability
@app.route('/greet', methods=['GET', 'POST'])
def greet():
    if request.method == 'POST':
        name = request.form.get('name')
        return render_template_string(f'<h2>Hello {name}!</h2>')  # unsanitized input
    return '''
        <form method="POST">
            Name: <input name="name">
            <input type="submit">
        </form>
    '''

# 🚨 Insecure exception handling
@app.route('/divide')
def divide():
    try:
        a = int(request.args.get('a', 1))
        b = int(request.args.get('b', 0))  # default to zero
        result = a / b
        return f"Result: {result}"
    except Exception as e:
        logging.error(f"Exception occurred: {e}")  # sensitive info may leak
        return f"Error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
