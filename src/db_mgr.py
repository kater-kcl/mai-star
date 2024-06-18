# 引入数据库
from typing import Dict, List

import mysql.connector
import src.g_config as cfg

from maimaidx_music import Music, MusicList, Chart


class DatabaseManager:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.cnx = None
        self.cursor = None

    def connect(self):
        self.cnx = mysql.connector.connect(user=self.user, password=self.password,
                                           host=self.host, database=self.database,
                                           port=self.port, charset='utf8mb4')  # specify collation here
        self.cursor = self.cnx.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.cnx:
            self.cnx.close()

    def execute_query(self, query, params=None):
        self.connect()
        self.cursor.execute(query, params)
        result = self.cursor.fetchall()
        self.close()
        return result

    def execute_update(self, query, params=None):
        self.connect()
        self.cursor.execute(query, params)
        self.cnx.commit()
        self.close()

    def execute_update_return_id(self, query, params=None):
        self.connect()
        self.cursor.execute(query, params)
        self.cnx.commit()
        last_insert_id = self.cursor.lastrowid
        self.close()
        return last_insert_id


db_mgr: DatabaseManager = None


def init_database():
    global db_mgr
    args = {
        'host': cfg.db_config.sql_host,
        'port': cfg.db_config.sql_port,
        'user': cfg.db_config.sql_user,
        'password': cfg.db_config.sql_pass,
        'database': cfg.db_config.sql_database
    }
    db_mgr = DatabaseManager(**args)
    create_tables()


def create_tables():
    query = ['''
create table if not exists arcade
(
    id            int auto_increment
        primary key,
    name          char(255) null,
    address       char(255) null,
    machine_count int       null
);
''', '''
create table if not exists favorite
(
    id      int auto_increment
        primary key,
    song_id int null,
    user_id int null
);''', '''
create table if not exists music
(
    id      int auto_increment
        primary key,
    title   varchar(255) null,
    genre   varchar(255) null,
    type    varchar(255) null,
    bpm     float        null,
    version varchar(255) null,
    artist  varchar(255) null
);''',

             '''
create table if not exists chart
(
    id       int auto_increment
        primary key,
    tap      int       null,
    slide    int       null,
    hold     int       null,
    touch    int       null,
    brk      int       null,
    charter  char(255) null,
    music_id int       null,
    ds       float     null,
    level    char(10)  null,
    constraint chart_ibfk_1
        foreign key (music_id) references music (id)
);''',
             '''
create table if not exists user_table
(
    id            int auto_increment
        primary key,
    username      varchar(255) not null,
    password      varchar(255) not null,
    bind_username varchar(255) null,
    constraint bind_username
        unique (bind_username),
    constraint username
        unique (username)
);''',

             '''
create table if not exists user_chart_tags
(
    id       int auto_increment
        primary key,
    user_id  int        not null,
    chart_id int        not null,
    tag_1    tinyint(1) null,
    tag_2    tinyint(1) null,
    tag_3    tinyint(1) null,
    tag_4    tinyint(1) null,
    tag_5    tinyint(1) null,
    tag_6    tinyint(1) null,
    tag_7    tinyint(1) null,
    tag_8    tinyint(1) null,
    tag_9    tinyint(1) null,
    tag_10   tinyint(1) null,
    tag_11   tinyint(1) null,
    tag_12   tinyint(1) null,
    tag_13   tinyint(1) null,
    tag_14   tinyint(1) null,
    tag_15   tinyint(1) null,
    tag_16   tinyint(1) null,
    tag_17   tinyint(1) null,
    tag_18   tinyint(1) null,
    tag_19   tinyint(1) null,
    tag_20   tinyint(1) null,
    constraint user_chart_tags_pk
        unique (chart_id, user_id),
    constraint user_chart_tags_chart_id_fk
        foreign key (chart_id) references chart (id),
    constraint user_chart_tags_user_table_id_fk
        foreign key (user_id) references user_table (id)
);''']
    for q in query:
        db_mgr.execute_update(q)


def insert_music_and_charts(music: Music):
    query = 'INSERT INTO music (id, title, genre, type, bpm, version, artist) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    music_data = (
        music.id, music.title, music.genre, music.type, music.bpm, music.version, music.artist)
    music_id = db_mgr.execute_update_return_id(query, music_data)
    for chart in music.charts:
        query = 'INSERT INTO chart (music_id, tap, slide, hold, touch, brk, charter) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        chart_data = (music_id, chart.tap, chart.slide, chart.hold, chart.touch, chart.brk, chart.charter)
        db_mgr.execute_update(query, chart_data)


def record_to_dict(record, chart_record):
    print(record, chart_record, chart_record[6])
    return ({
                'id': record[0],
                'title': record[1],
                'genre': record[2],
                'type': record[3],
                'bpm': record[4],
                'version': record[5],
                'artist': record[6]
            },
            {
                'tap': chart_record[1],
                'slide': chart_record[2],
                'hold': chart_record[3],
                'touch': chart_record[4],
                'brk': chart_record[5],
                'charter': chart_record[6],
                'chart_id': chart_record[0],
                'ds': chart_record[8],
                'level': chart_record[9]
            })


def get_all_music_and_charts():
    query = '''
    SELECT music.*, chart.*
    FROM music
    LEFT JOIN chart ON music.id = chart.music_id
    '''
    all_music_and_charts_records = db_mgr.execute_query(query)

    all_music_and_charts = MusicList()

    current_charts = []
    current_ds = []
    current_level = []

    current_music = None

    for record in all_music_and_charts_records:
        music_record, chart_record = record_to_dict(record[:7], record[7:])

        if current_music is None or music_record['id'] != current_music.id:
            if current_music is not None:
                current_music.charts = current_charts
                current_music.ds = current_ds
                current_music.level = current_level
                all_music_and_charts.append(current_music)

            current_music = Music(music_record)
            current_charts = []
            current_ds = []
            current_level = []

        current_charts.append(Chart(chart_record))
        current_ds.append(chart_record['ds'])
        current_level.append(chart_record['level'])

    if current_music is not None:
        current_music.charts = current_charts
        current_music.ds = current_ds
        current_music.level = current_level
        all_music_and_charts.append(current_music)
    return all_music_and_charts


def register_user(username: str, password: str):
    query = 'INSERT INTO user_table (username, password) VALUES (%s, %s)'
    db_mgr.execute_update(query, (username, password))


def get_user_id(username: str):
    query = 'SELECT id FROM user_table WHERE username = %s'
    result = db_mgr.execute_query(query, (username,))
    if len(result) == 0:
        return None
    return result[0][0]


def get_user_info(username: str):
    query = 'SELECT * FROM user_table WHERE username = %s'
    result = db_mgr.execute_query(query, (username,))
    if len(result) == 0:
        return None
    return ({
        'id': result[0][0],
        'username': result[0][1],
        'bind_username': result[0][3]
    })


def get_password(username: str):
    query = 'SELECT password FROM user_table WHERE username = %s'
    result = db_mgr.execute_query(query, (username,))
    if len(result) == 0:
        return None
    return result[0][0]


def user_exists(username: str):
    query = 'SELECT id FROM user_table WHERE username = %s'
    result = db_mgr.execute_query(query, (username,))
    return len(result) > 0


def update_user_info(username: str, new_info: Dict):
    new_username = new_info.get('username', None)
    new_password = new_info.get('password', None)
    new_maiuser = new_info.get('maiuser', None)
    if new_username is not None:
        query = 'UPDATE user_table SET username = %s WHERE username = %s'
        db_mgr.execute_update(query, (new_username, username))
    if new_password is not None:
        query = 'UPDATE user_table SET password = %s WHERE username = %s'
        db_mgr.execute_update(query, (new_password, username))
    if new_maiuser is not None:
        query = 'UPDATE user_table SET bind_username = %s WHERE username = %s'
        db_mgr.execute_update(query, (new_maiuser, username))


def query_all_arcade():
    query = 'SELECT * FROM arcade'
    result = db_mgr.execute_query(query)
    return {
        'arcades': [{
            'id': record[0],
            'name': record[1],
            'address': record[2],
            'machine_count': record[3]
        } for record in result]
    }


def query_arcade(arcade_id: int):
    query = 'SELECT * FROM arcade WHERE id = %s'
    result = db_mgr.execute_query(query, (arcade_id,))
    if len(result) == 0:
        return None
    return {
        'id': result[0][0],
        'name': result[0][1],
        'address': result[0][2],
        'machine_count': result[0][3]
    }


def check_favorite_exists(user_id: int, song_id: int):
    query = 'SELECT id FROM favorite WHERE user_id = %s AND song_id = %s'
    result = db_mgr.execute_query(query, (user_id, song_id))
    return len(result) > 0


def get_favorite_songs(user_id: int):
    query = 'SELECT song_id FROM favorite WHERE user_id = %s'
    result = db_mgr.execute_query(query, (user_id,))
    return [record[0] for record in result]


def add_favorite(user_id: int, song_id: int):
    query = 'INSERT INTO favorite (user_id, song_id) VALUES (%s, %s)'
    db_mgr.execute_update(query, (user_id, song_id))


def remove_favorite(user_id: int, song_id: int):
    query = 'DELETE FROM favorite WHERE user_id = %s AND song_id = %s'
    db_mgr.execute_update(query, (user_id, song_id))


def update_user_chart_tags(user_id: int, chart_id: int, tags: List):
    # Convert the tags dictionary to a list of values

    # Prepare the SQL query
    query = '''
    INSERT INTO user_chart_tags (user_id, chart_id, tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8, tag_9, tag_10, tag_11, tag_12, tag_13, tag_14, tag_15, tag_16, tag_17, tag_18, tag_19, tag_20)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    tag_1 = VALUES(tag_1), tag_2 = VALUES(tag_2), tag_3 = VALUES(tag_3), tag_4 = VALUES(tag_4), tag_5 = VALUES(tag_5),
    tag_6 = VALUES(tag_6), tag_7 = VALUES(tag_7), tag_8 = VALUES(tag_8), tag_9 = VALUES(tag_9), tag_10 = VALUES(tag_10),
    tag_11 = VALUES(tag_11), tag_12 = VALUES(tag_12), tag_13 = VALUES(tag_13), tag_14 = VALUES(tag_14), tag_15 = VALUES(tag_15),
    tag_16 = VALUES(tag_16), tag_17 = VALUES(tag_17), tag_18 = VALUES(tag_18), tag_19 = VALUES(tag_19), tag_20 = VALUES(tag_20)
    '''

    # Execute the SQL query
    db_mgr.execute_update(query, [user_id, chart_id] + tags)


def get_user_chart_tags(user_id: int, chart_id: int):
    query = '''
    SELECT tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8, tag_9, tag_10, tag_11, tag_12, tag_13, tag_14, tag_15, tag_16, tag_17, tag_18, tag_19, tag_20
    FROM user_chart_tags
    WHERE user_id = %s AND chart_id = %s
    '''
    result = db_mgr.execute_query(query, (user_id, chart_id))
    if len(result) == 0:
        return None
    return result[0]


def get_chart_tags_rate(chart_id: int):
    # 返回tag中true占所有评价中的比例
    query = '''
    SELECT tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8, tag_9, tag_10, tag_11, tag_12, tag_13, tag_14, tag_15, tag_16, tag_17, tag_18, tag_19, tag_20
    FROM user_chart_tags
    WHERE chart_id = %s
    '''
    result = db_mgr.execute_query(query, (chart_id,))
    if len(result) == 0:
        # 返回20个0
        return [0.0] * 20
    tag_count = len(result)
    tag_sum = [0.0] * 20
    for record in result:
        for i in range(20):
            tag_sum[i] += record[i]
    return [tag / tag_count for tag in tag_sum]


def get_charts_tags_rate(charts: List[int]):
    # Generate the placeholders for the IN clause
    placeholders = ', '.join(['%s'] * len(charts))

    query = f'''
    SELECT chart_id, tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8, tag_9, tag_10, tag_11, tag_12, tag_13, tag_14, tag_15, tag_16, tag_17, tag_18, tag_19, tag_20
    FROM user_chart_tags
    WHERE chart_id IN ({placeholders})
    '''

    # Execute the SQL query
    result = db_mgr.execute_query(query, charts)
    if len(result) == 0:
        # Return 20 zeros for each chart
        return [[0.0] * 20] * len(charts)

    # Initialize a dictionary to store the tag sums for each chart
    tag_sums = {chart: [0.0] * 20 for chart in charts}

    # Count the number of tags for each chart
    tag_counts = {chart: 0.0 for chart in charts}

    for record in result:
        chart_id = record[0]
        tag_counts[chart_id] += 1
        for i in range(20):
            tag_sums[chart_id][i] += record[i + 1]

    # Calculate the rate for each tag in each chart
    tag_rates = {chart: [tag_sum / tag_counts[chart] if tag_counts[chart] != 0 else 0 for tag_sum in tag_sums[chart]]
                 for chart in charts}
    # Convert the dictionary to a list of lists
    return [tag_rates[chart] for chart in charts]


def get_chart_tags(chart_id: int):
    # 统计该谱面下所有用户的tag，返回20个tag的计数以及总评价数
    query = '''
    SELECT tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8, tag_9, tag_10, tag_11, tag_12, tag_13, tag_14, tag_15, tag_16, tag_17, tag_18, tag_19, tag_20
    FROM user_chart_tags
    WHERE chart_id = %s
    '''
    result = db_mgr.execute_query(query, (chart_id,))
    if len(result) == 0:
        # 返回20个0
        return [0] * 20
    count = len(result)
    tag_sum = [0] * 20
    for record in result:
        for i in range(20):
            tag_sum[i] += record[i]
    return count, tag_sum


def get_charts_tags(chart_ids: List[int]):
    # Generate the placeholders for the IN clause
    placeholders = ', '.join(['%s'] * len(chart_ids))

    query = f'''
    SELECT chart_id, tag_1, tag_2, tag_3, tag_4, tag_5, tag_6, tag_7, tag_8, tag_9, tag_10, tag_11, tag_12, tag_13, tag_14, tag_15, tag_16, tag_17, tag_18, tag_19, tag_20
    FROM user_chart_tags
    WHERE chart_id IN ({placeholders})
    '''

    # Execute the SQL query
    result = db_mgr.execute_query(query, chart_ids)
    if len(result) == 0:
        # Return 20 zeros for each chart
        return [[0] * 20] * len(chart_ids)

    # Initialize a dictionary to store the tag sums for each chart
    tag_sums = {chart: [0] * 20 for chart in chart_ids}

    # Count the number of tags for each chart
    tag_counts = {chart: 0 for chart in chart_ids}

    for record in result:
        chart_id = record[0]
        tag_counts[chart_id] += 1
        for i in range(20):
            tag_sums[chart_id][i] += record[i + 1]

    # Convert the dictionary to a list of lists
    return [(tag_counts[chart], tag_sums[chart]) for chart in chart_ids]
