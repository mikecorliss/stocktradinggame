from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = 'stock-trader-2026-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockgame.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    cash = db.Column(db.Float, default=10000.0)
    portfolio = db.Column(db.JSON, default=dict)
    day = db.Column(db.Integer, default=0)
    start_date = db.Column(db.String(10), default='2026-05-14')
    stocks = db.Column(db.JSON, default=dict)
    price_history = db.Column(db.JSON, default=dict)

def init_user_game(user):
    if not user.stocks:
        user.stocks = {
            'AAPL': {'name': 'Apple Inc.', 'price': 226.84},
            'MSFT': {'name': 'Microsoft Corporation', 'price': 416.42},
            'GOOGL': {'name': 'Alphabet Inc.', 'price': 165.29},
            'AMZN': {'name': 'Amazon.com, Inc.', 'price': 179.34},
            'TSLA': {'name': 'Tesla, Inc.', 'price': 241.50},
        }
        user.portfolio = {}
        user.day = 0
        user.price_history = {sym: [{'date': 'May 14', 'price': data['price']}] for sym, data in user.stocks.items()}

with app.app_context():
    db.create_all()

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        if not username or len(password) < 6:
            return jsonify({'error': 'Username required, password min 6 chars'}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        init_user_game(user)
        session['user_id'] = user.id
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True)
        user = User.query.filter_by(username=data.get('username')).first()
        if user and check_password_hash(user.password_hash, data.get('password')):
            session['user_id'] = user.id
            return jsonify({'success': True})
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({
        'username': user.username,
        'cash': user.cash,
        'portfolio': user.portfolio,
        'stocks': user.stocks,
        'day': user.day,
        'date': 'May 14, 2026',
        'price_history': user.price_history
    })

@app.route('/api/buy', methods=['POST'])
def buy():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    symbol = data['symbol']
    shares = int(data['shares'])
    if symbol not in user.stocks:
        return jsonify({'error': 'Invalid symbol'}), 400
    cost = user.stocks[symbol]['price'] * shares
    if cost > user.cash:
        return jsonify({'error': 'Not enough cash'}), 400
    user.cash -= cost
    user.portfolio[symbol] = user.portfolio.get(symbol, 0) + shares
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/sell', methods=['POST'])
def sell():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    symbol = data['symbol']
    shares = int(data['shares'])
    if symbol not in user.portfolio or user.portfolio[symbol] < shares:
        return jsonify({'error': 'Not enough shares'}), 400
    proceeds = user.stocks[symbol]['price'] * shares
    user.cash += proceeds
    user.portfolio[symbol] -= shares
    if user.portfolio[symbol] <= 0:
        user.portfolio.pop(symbol, None)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/next_day', methods=['POST'])
def next_day():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    user.day += 1
    # Update prices (simulated for now)
    for sym in user.stocks:
        change = random.uniform(-0.03, 0.03)
        if random.random() < 0.15:
            change = random.uniform(-0.10, 0.10)
        user.stocks[sym]['price'] *= (1 + change)
        user.stocks[sym]['price'] = max(1.00, round(user.stocks[sym]['price'], 2))
    date_str = 'May 14'
    for sym in user.stocks:
        if sym not in user.price_history:
            user.price_history[sym] = []
        user.price_history[sym].append({'date': date_str, 'price': user.stocks[sym]['price']})
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/')
def index():
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return 'Index file not found', 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)