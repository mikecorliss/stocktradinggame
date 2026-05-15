from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import date, timedelta
import yfinance as yf
import json

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

def update_prices(user):
    for sym in user.stocks:
        try:
            ticker = yf.Ticker(sym)
            data = ticker.history(period='1d')
            if not data.empty:
                current_price = round(data['Close'].iloc[-1], 2)
                user.stocks[sym]['price'] = current_price
            else:
                user.stocks[sym]['price'] *= (1 + random.uniform(-0.03, 0.03))
        except:
            user.stocks[sym]['price'] *= (1 + random.uniform(-0.03, 0.03))
        user.stocks[sym]['price'] = max(1.0, round(user.stocks[sym]['price'], 2))

    date_str = (date.fromisoformat(user.start_date) + timedelta(days=user.day)).strftime('%b %d')
    for sym in user.stocks:
        if sym not in user.price_history:
            user.price_history[sym] = []
        user.price_history[sym].append({'date': date_str, 'price': user.stocks[sym]['price']})

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    users = User.query.all()
    data = []
    for u in users:
        net = u.cash + sum(shares * u.stocks.get(sym, {'price':0})['price'] for sym, shares in u.portfolio.items())
        data.append({'username': u.username, 'net_worth': round(net, 2)})
    data.sort(key=lambda x: x['net_worth'], reverse=True)
    return jsonify(data[:10])

# (other routes for register, login, status, buy, sell, next_day with yfinance update)
# Full code abbreviated for tool call
print('App ready with yfinance and leaderboard')
