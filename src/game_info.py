from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from utils.diving_fish_api import get_b50
from src.db_mgr import register_user, get_user_id, get_password, user_exists, update_user_info, get_user_info, \
    get_chart_tags_rate, get_charts_tags_rate
from src.template import ret_content_template
import src.user_info as user_info
import src.maimaidx_music as music

game_info_bp = Blueprint('game_info', __name__)


def get_cover_url(song_id):
    song_id = str(song_id).zfill(5)
    return f"/cover/{song_id}.png"


def add_cover_url(chart):
    chart['cover'] = get_cover_url(chart['song_id'])
    return chart


def get_player_tags(username):
    bind_info = get_user_info(username)['bind_username']
    success, content = user_info.check_bind_success(bind_info)
    charts = content.to_dict()['charts']['dx'] + content.to_dict()['charts']['sd']
    if not success:
        return jsonify(ret_content_template(400, content, {}))
    for chart in charts:
        print(chart)
    chart_ids = [int(music.total_list.get_chart_id(chart['song_id'], chart['level_index'])) for chart in charts]
    print(get_charts_tags_rate(chart_ids))
    chart_tags = [[1 if rate > 0.5 else 0 for rate in rates]for rates in get_charts_tags_rate(chart_ids)]
    # 将每一个tag求和/20求rate
    tags_sum = [sum(tags) / 20 for tags in zip(*chart_tags)]
    return tags_sum


@game_info_bp.route('/b50', methods=['GET'])
@jwt_required()
def b50():
    username = get_jwt_identity()
    bind_info = get_user_info(username)['bind_username']
    success, content = user_info.check_bind_success(bind_info)
    if not success:
        return jsonify(ret_content_template(400, content, {}))
    ret = content.to_dict()
    ret['charts']['dx'] = [add_cover_url(chart) for chart in ret['charts']['dx']]
    return jsonify(ret_content_template(200, "Success", content.to_dict()))


@game_info_bp.route('/song_achievement', methods=['GET'])
@jwt_required()
def get_song_achievement():
    username = get_jwt_identity()
    bind_info = get_user_info(username)['bind_username']
    success, content = get_b50(bind_info)
    if not success:
        return jsonify(ret_content_template(400, content, {}))
    b50 = content
    song_id = request.args.get('song_id')
    if song_id is None:
        return jsonify(ret_content_template(400, "Missing song_id parameter", {}))
    song_id = int(song_id)
    for chart in b50.charts.dx:
        if chart.song_id == song_id:
            return jsonify(ret_content_template(200, "Success", chart.to_dict()))
    for chart in b50.charts.sd:
        if chart.song_id == song_id:
            return jsonify(ret_content_template(200, "Success", chart.to_dict()))
    return jsonify(ret_content_template(400, "Song not found", {}))
