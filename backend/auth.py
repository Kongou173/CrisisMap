from flask import Blueprint, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

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

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    if username in users and users[username]['password'] == password:
        user = User(users[username]['id'], username)
        login_user(user)
        return jsonify({"message": "Logged in"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200
