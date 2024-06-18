import random
from typing import List

from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint

import src.maimaidx_music as music
from game_info import get_player_tags
from template import ret_content_template
from utils.diving_fish_api import get_b50
from src.db_mgr import register_user, get_user_id, get_password, user_exists, update_user_info, get_user_info, \
    check_favorite_exists, add_favorite, remove_favorite, get_favorite_songs, update_user_chart_tags, \
    get_user_chart_tags, get_chart_tags, get_charts_tags, get_charts_tags_rate
from utils.suggest_algorithm import Player, Chart, get_suggestion

suggestion_module_bp = Blueprint('suggestion', __name__)


@suggestion_module_bp.route('/evaluate', methods=['POST'])
@jwt_required()
def evaluate():
    user_name = get_jwt_identity()
    user_id = get_user_id(user_name)
    song_id = request.json.get('song_id')
    tags = request.json.get('tags')
    ind = request.json.get('ind')
    chart_id = music.total_list.get_chart_id(int(song_id), int(ind))
    update_user_chart_tags(user_id, int(chart_id), tags)
    return jsonify(ret_content_template(200, "User created successfully", {}))


@suggestion_module_bp.route('/get_user_chart_tag', methods=['GET'])
@jwt_required()
def get_user_chart_tag():
    user_name = get_jwt_identity()
    user_id = get_user_id(user_name)
    song_id = request.json.get('song_id')
    ind = request.json.get('ind')
    chart_id = music.total_list.get_chart_id(int(song_id), int(ind))
    tags = get_user_chart_tags(user_id, int(chart_id))
    return jsonify(ret_content_template(200, "User created successfully", tags))


@suggestion_module_bp.route('/get_chart_tags', methods=['GET'])
def chart_tags():
    song_id = request.json.get('song_id')
    ind = request.json.get('ind')
    chart_id = music.total_list.get_chart_id(int(song_id), int(ind))
    tags_sum, tags = get_chart_tags(int(chart_id))
    ret = {
        'tags_sum': tags_sum,
        'tags': tags
    }
    return jsonify(ret_content_template(200, "User created successfully", ret))


@suggestion_module_bp.route('/get_song_suggest', methods=['GET'])
@jwt_required()
def suggest():
    user_name = get_jwt_identity()
    count = request.args.get('count', default=5, type=int)
    player_tags = get_player_tags(user_name)
    user_id = get_user_id(user_name)
    player = Player(user_id, player_tags)
    charts = music.total_list.get_all_charts()
    chart_ids = [chart.chart_id for chart in charts]
    chart_tags_pool = get_charts_tags_rate(chart_ids)
    random.shuffle(chart_tags_pool)
    chart_list: List[Chart] = []
    for i in range(len(charts)):
        chart_list.append(Chart(charts[i].chart_id, chart_tags_pool[i]))

    suggestions = get_suggestion(chart_list, count, player)
    ret = []
    for chart in suggestions:
        song_id, ind = music.total_list.get_song_id_and_index_by_chart_id(chart.chart_id)
        ret.append({
            'song_id': song_id,
            'ind': ind,
            'chart_id': chart.chart_id
        })
    return jsonify(ret_content_template(200, "User created successfully", ret))
