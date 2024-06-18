from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from utils.diving_fish_api import get_b50
from src.db_mgr import register_user, get_user_id, get_password, user_exists, update_user_info, get_user_info, \
    check_favorite_exists, add_favorite, remove_favorite, get_favorite_songs
from src.template import ret_content_template

user_info_bp = Blueprint('user', __name__)
jwt = None


def init_jwt(app):
    global jwt
    jwt = JWTManager(app)


def check_bind_success(username):
    success, content = get_b50(username)
    if success != 200:
        return False, content
    return True, content


@user_info_bp.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify(ret_content_template(400, "Missing JSON in request", {}))

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return jsonify(ret_content_template(400, "Missing username parameter", {}))
    if not password:
        return jsonify(ret_content_template(400, "Missing password parameter", {}))

    if user_exists(username):
        return jsonify(ret_content_template(400, "Username already exists", {}))

    hashed_password = generate_password_hash(password)
    register_user(username, hashed_password)

    return jsonify(ret_content_template(200, "User created successfully", {}))


@user_info_bp.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify(ret_content_template(400, "Missing JSON in request", {}))

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return jsonify(ret_content_template(400, "Missing username parameter", {}))
    if not password:
        return jsonify(ret_content_template(400, "Missing password parameter", {}))

    user_password = get_password(username)
    if user_password is None or not check_password_hash(user_password, password):
        return jsonify(ret_content_template(401, "Bad username or password", {}))

    access_token = create_access_token(identity=username)
    return jsonify(ret_content_template(200, "Login successful", {"access_token": 'Bearer ' + access_token}))


@user_info_bp.route('/update_info', methods=['POST'])
@jwt_required()
def update_info():
    if not request.is_json:
        return jsonify(ret_content_template(400, "Missing JSON in request", {}))

    new_info = request.json.get('new_info', None)

    if not new_info:
        return jsonify(ret_content_template(400, "Missing new_info parameter", {}))

    username = get_jwt_identity()
    if new_info['password'] is not None:
        new_info['password'] = generate_password_hash(new_info['password'])

    update_user_info(username, new_info)

    return jsonify(ret_content_template(200, "User info updated successfully", {}))


@user_info_bp.route('/bind_mai_user', methods=['POST'])
@jwt_required()
def bind_mai_user():
    if not request.is_json:
        return jsonify(ret_content_template(400, "Missing JSON in request", {}))

    mai_user = request.json.get('mai_user', None)

    if not mai_user:
        return jsonify(ret_content_template(400, "Missing mai_user parameter", {}))

    mai_check, content = check_bind_success(mai_user)
    if not mai_check:
        return jsonify(ret_content_template(400, content, {}))

    username = get_jwt_identity()

    update_user_info(username, {"mai_user": mai_user})

    return jsonify(ret_content_template(200, "success", {}))


@user_info_bp.route('/user_info', methods=['GET'])
@jwt_required()
def user_info():
    username = get_jwt_identity()
    res_user_info = get_user_info(username)
    return jsonify(ret_content_template(200, "success", res_user_info))


@user_info_bp.route('/favorite', methods=['POST'])
@jwt_required()
def add_or_remove_favorite_song():
    if not request.is_json:
        return jsonify(ret_content_template(400, "Missing JSON in request", {}))

    song_id = request.json.get('song_id', None)

    if not song_id:
        return jsonify(ret_content_template(400, "Missing song_id parameter", {}))

    username = get_jwt_identity()

    user_id = get_user_id(username)

    if check_favorite_exists(user_id, song_id):
        remove_favorite(user_id, song_id)
        return jsonify(ret_content_template(200, "Song unfavorited successfully", {}))

    add_favorite(user_id, song_id)
    return jsonify(ret_content_template(200, "Song favorited successfully", {}))


@user_info_bp.route('/get_favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    username = get_jwt_identity()
    user_id = get_user_id(username)
    favorites = get_favorite_songs(user_id)
    return jsonify(ret_content_template(200, "success", favorites))
