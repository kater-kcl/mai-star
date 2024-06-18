from flask import request, jsonify
import src.maimaidx_music as music
from flask import Blueprint
from src.template import ret_content_template

base_info_bp = Blueprint('base', __name__)

@base_info_bp.route('/query_songs', methods=['GET'])
def query_songs():
    try:
        # 获取查询参数
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        level = request.args.get('level', type=str)
        ds = request.args.get('ds', type=float)
        title_search = request.args.get('title_search', type=str)
        genre = request.args.get('genre', type=str)
        bpm = request.args.get('bpm', type=float)
        type = request.args.get('type', type=str)
        diff = request.args.get('diff', type=int)
        # 检查查询参数
        if page < 1 or per_page < 1:
            return jsonify(ret_content_template(400, 'Invalid query parameters', {}))

        # 使用 MusicList 的 filter 方法过滤音乐数据
        filtered_music_list = music.total_list.filter(
            level=level if level != "" else Ellipsis,
            ds=ds if ds is not None else Ellipsis,
            title_search=title_search if title_search is not None else Ellipsis,
            genre=genre if genre != "" else Ellipsis,
            bpm=bpm if bpm is not None else Ellipsis,
            type=type if type != "" else Ellipsis,
            diff=[diff] if diff is not None else Ellipsis,
        )

        # 计算开始和结束的索引
        start = (page - 1) * per_page
        end = start + per_page

        # 检查索引
        if start >= len(filtered_music_list):
            return jsonify(ret_content_template(400, 'Page out of range', {}))

        # 从过滤后的 MusicList 中获取音乐数据
        songs = filtered_music_list[start:end]

        # 将 Music 对象转换为字典，以便进行 JSON 序列化
        songs_dict = [song.to_dict() for song in songs]

        # 添加总数据量
        total_count = len(filtered_music_list)

        ret = ret_content_template(0, 'success', {'songs': songs_dict, 'total_count': total_count})
        # 返回 JSON 响应
        return jsonify(ret)

    except ValueError:
        return jsonify(ret_content_template(400, 'Invalid query parameters', {}))
@base_info_bp.route('/get_song', methods=['GET'])
def get_song():
    try:
        song_id = request.args.get('song_id', type=int)
        # 从数据库中获取音乐数据
        song = music.total_list.by_id(song_id)

        # 检查音乐是否存在
        if song is None:
            return jsonify(ret_content_template(404, 'Song not found', {}))

        # 将Music对象转换为字典，以便进行JSON序列化
        song_dict = song.to_dict()

        # 返回JSON响应
        return jsonify(ret_content_template(0, 'success', song_dict))

    except ValueError:
        return jsonify(ret_content_template(400, 'Invalid song ID', {}))


@base_info_bp.route('/random', methods=['GET'])
def random_song():
    try:
        count = request.args.get('count', default=1, type=int)

        # 从 MusicList 中随机获取一首音乐
        songs = music.total_list.random(count)

        # 将 Music 对象转换为字典，以便进行 JSON 序列化
        song_dict = [song.to_dict() for song in songs]

        # 返回 JSON 响应
        return jsonify(ret_content_template(0, 'success', song_dict))

    except ValueError:
        return jsonify(ret_content_template(400, 'Invalid song ID', {}))