from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

# Flaskアプリとモジュールの初期化
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/crisismap'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)

# Userモデル
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

users = {"testuser": {"id": 1, "password": "password"}}

@login_manager.user_loader
def load_user(user_id):
    for username, user_data in users.items():
        if user_data["id"] == int(user_id):
            return User(user_data["id"], username)
    return None

# Postモデル
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "category": self.category,
            "timestamp": self.timestamp.isoformat()
        }

@app.before_first_request
def create_tables():
    db.create_all()

# 投稿取得エンドポイント
@app.route('/api/posts', methods=['GET'])
def get_posts():
    category = request.args.get('category')
    if category:
        posts = Post.query.filter_by(category=category).order_by(Post.timestamp.desc()).all()
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    return jsonify([post.to_dict() for post in posts])

# 投稿作成エンドポイント
@app.route('/api/posts', methods=['POST'])
def add_post():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    new_post = Post(
        title=data['title'],
        content=data['content'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        category=data['category']
    )
    db.session.add(new_post)
    db.session.commit()
    socketio.emit('new_post', new_post.to_dict())
    return jsonify(new_post.to_dict()), 201

# WebSocket接続イベント
@socketio.on('connect')
def handle_connect():
    print("Client connected")

# ログインエンドポイント
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    if username in users and users[username]['password'] == password:
        user = User(users[username]['id'], username)
        login_user(user)
        return jsonify({"message": "Logged in"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# ログアウトエンドポイント
@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200

# 現在のユーザー情報取得
@app.route('/current_user', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({"username": current_user.username}), 200
    return jsonify({"error": "Not authenticated"}), 401

if __name__ == '__main__':
    socketio.run(app, debug=True)
