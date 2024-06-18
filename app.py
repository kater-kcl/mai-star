import os

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from src.g_config import init_config, default_config
from src.route import route_blueprint
from src.db_mgr import init_database, get_all_music_and_charts
from src.maimaidx_music import music_list_init
import src.maimaidx_music as music

app = Flask(__name__, static_folder='resources')
app.register_blueprint(route_blueprint)
CORS(app, resources=r'/*')
init_config(False, 'config/config.ini', app)
jwt = JWTManager(app)
init_database()
music_list_init(get_all_music_and_charts())

# 添加全局404路由
@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return 'This page does not exist', 404

@app.route('/cover/<path:filename>')
def cover(filename):
    return send_from_directory(app.static_folder + '/mai_cover', filename)

@app.route('/index')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("re")
    # 打印启动信息
    print(app.url_map)
    app.run()
