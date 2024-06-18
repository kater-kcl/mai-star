from flask import Blueprint
from src.base_info import base_info_bp
from src.user_info import user_info_bp
from src.game_info import game_info_bp
from src.game_tools import game_tools_bp
from suggestion_module import suggestion_module_bp

route_blueprint = Blueprint('route', __name__)

route_blueprint.register_blueprint(base_info_bp, url_prefix='/base')
route_blueprint.register_blueprint(user_info_bp, url_prefix='/user')
route_blueprint.register_blueprint(game_info_bp, url_prefix='/gameinfo')
route_blueprint.register_blueprint(game_tools_bp, url_prefix='/tool')
route_blueprint.register_blueprint(suggestion_module_bp, url_prefix='/suggestion')
