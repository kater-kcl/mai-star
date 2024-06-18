import os
from configparser import ConfigParser
from typing import Optional


class DefaultConfig:
    jwt_sec: str
    def __init__(self, *args):
        self.jwt_sec = args[0]

class DbConfig:
    sql_host: str
    sql_port: int
    sql_user: str
    sql_pass: str
    sql_database: str

    def __init__(self, *args):
        self.sql_host = args[0]
        self.sql_port = args[1]
        self.sql_user = args[2]
        self.sql_pass = args[3]
        self.sql_database = args[4]


default_config: Optional[DefaultConfig] = None
db_config: Optional[DbConfig] = None


def init_config(from_env: bool = True, config_path: str = None, app=None):
    global db_config, default_config
    if from_env:
        sql_host = os.environ.get('SQL_HOST')
        sql_port = os.environ.get('SQL_PORT')
        sql_user = os.environ.get('SQL_USER')
        sql_pass = os.environ.get('SQL_PASS')
        sql_database = os.environ.get('SQL_DATABASE')
        jwt_sec = os.environ.get('JWT_SEC')
    else:
        config = ConfigParser()
        config.read(config_path)
        sql_host = config.get('mysql', 'host')
        sql_port = config.get('mysql', 'port')
        sql_user = config.get('mysql', 'username')
        sql_pass = config.get('mysql', 'password')
        sql_database = config.get('mysql', 'database_name')
        jwt_sec = config.get('default', 'jwt_sec')
    default_config = DefaultConfig(jwt_sec)
    app.config['JWT_SECRET_KEY'] = jwt_sec
    db_config = DbConfig(sql_host, sql_port, sql_user, sql_pass, sql_database)
