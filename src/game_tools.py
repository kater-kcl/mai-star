from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from utils.diving_fish_api import get_b50
from src.db_mgr import register_user, get_user_id, get_password, user_exists, update_user_info, get_user_info, \
    query_all_arcade, query_arcade
from src.template import ret_content_template
import src.user_info as user_info

game_tools_bp = Blueprint('game_tools', __name__)

arcade_count = {}


@game_tools_bp.route('/arcade_all', methods=['GET'])
def arcade_all():
    return jsonify(ret_content_template(200, "Success", query_all_arcade()))


@game_tools_bp.route('/arcade_info', methods=['GET'])
def arcade_info():
    arcade_id = request.args.get('arcade_id')
    if arcade_id is None:
        return jsonify(ret_content_template(400, "arcade_id is required", {}))
    info = query_arcade(int(arcade_id))
    if arcade_id not in arcade_count:
        arcade_count[arcade_id] = 0
    info['count'] = arcade_count[arcade_id]
    return jsonify(ret_content_template(200, "Success", info))


@game_tools_bp.route('/change_count', methods=['POST'])
@jwt_required()
def change_count():
    arcade_id = request.args.get('arcade_id')
    count = request.args.get('count')
    if arcade_id is None:
        return jsonify(ret_content_template(400, "arcade_id is required", {}))
    if arcade_id not in arcade_count:
        arcade_count[arcade_id] = 0
    arcade_count[arcade_id] = count
    return jsonify(ret_content_template(200, "Success", {}))
