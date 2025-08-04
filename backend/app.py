from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)
DB_PATH = 'water_reminder.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        weight REAL,
        gender TEXT,
        activity TEXT,
        climate TEXT,
        wake_time TEXT,
        sleep_time TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS intake (
        id INTEGER PRIMARY KEY,
        amount REAL,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/calculate_goal', methods=['POST'])
def calculate_goal():
    data = request.json
    weight = data.get('weight', 0)
    goal = weight * 30
    return jsonify({'daily_goal_ml': goal})

@app.route('/log_intake', methods=['POST'])
def log_intake():
    data = request.json
    amount = data.get('amount_ml')
    timestamp = data.get('timestamp', datetime.now().isoformat())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO intake (amount, timestamp) VALUES (?, ?)', (amount, timestamp))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/get_progress', methods=['GET'])
def get_progress():
    today = datetime.now().date().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT SUM(amount) FROM intake WHERE DATE(timestamp) = ?', (today,))
    total = c.fetchone()[0] or 0
    conn.close()
    return jsonify({'total_today': total})

@app.route('/get_history', methods=['GET'])
def get_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT amount, timestamp FROM intake ORDER BY timestamp DESC LIMIT 30')
    history = [{'amount': row[0], 'timestamp': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify({'history': history})

if __name__ == '__main__':
    app.run(debug=True)
