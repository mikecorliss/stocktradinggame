from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "stock-trader-2026-super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stockgame.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    cash = db.Column(db.Float, default=10000.0)
    portfolio = db.Column(db.JSON, default=dict)
    day = db.Column(db.Integer, default=0)
    start_date = db.Column(db.String(10), default="2026-05-14")
    stocks = db.Column(db.JSON, default=dict)
    price_history = db.Column(db.JSON, default=dict)

def init_user_game(user):
    if not user.stocks:
        user.stocks = {
            "AAPL": {"name": "Apple Inc.", "price": 226.84},
            "MSFT": {"name": "Microsoft Corporation", "price": 416.42},
            "GOOGL": {"name": "Alphabet Inc.", "price": 165.29},
            "AMZN": {"name": "Amazon.com, Inc.", "price": 179.34},
            "TSLA": {"name": "Tesla, Inc.", "price": 241.50},
        }
        user.portfolio = {}
        user.day = 0
        user.price_history = {sym: [{"date": "May 14", "price": data["price"]}] for sym, data in user.stocks.items()}

with app.app_context():
    db.create_all()

@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json(force=True)
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or len(password) < 6:
            return jsonify({"error": "Username required and password must be at least 6 characters"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 400

        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        init_user_game(user)
        session["user_id"] = user.id

        return jsonify({"success": True, "username": username})
    except Exception as e:
        db.session.rollback()
        print("Register error:", str(e))
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)
        user = User.query.filter_by(username=data.get("username")).first()
        if user and check_password_hash(user.password_hash, data.get("password")):
            session["user_id"] = user.id
            return jsonify({"success": True})
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/status", methods=["GET"])
def status():
    user_id = session.get("user_id")
    user = User.query.get(user_id) if user_id else None
    if not user:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({
        "username": user.username,
        "cash": user.cash,
        "portfolio": user.portfolio,
        "stocks": user.stocks,
        "day": user.day,
        "date": "May 14, 2026",
        "price_history": user.price_history
    })

@app.route("/")
def index():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "templates/index.html not found. Please make sure the file exists.", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)