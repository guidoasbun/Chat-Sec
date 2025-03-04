from flask import Blueprint, request, jsonify
from models import db, User, Session
import jwt
import datetime
import os
from werkzeug.security import generate_password_hash
from flask_cors import CORS

SECRET_KEY = os.getenv("JWT_SECRET")

auth_bp = Blueprint('auth', __name__)
CORS(auth_bp)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint("auth", __name__)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Fetch user from database
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 401  # ✅ Better error message

    if not user.check_password(password):
        return jsonify({"error": "Incorrect password"}), 401  # ✅ More specific

    # Generate JWT token
    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200



@auth_bp.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token required"}), 403

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(decoded['user_id'])
        return jsonify({"message": "Access granted", "user": user.username})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


# Add this route to auth_routes.py

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get the current user's information"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200