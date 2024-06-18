from typing import Dict
import requests

from typing import List


class Chart(Dict):
    def __init__(self, chart_dict: dict):
        super().__init__()
        self.achievements = chart_dict['achievements']
        self.ds = chart_dict['ds']
        self.dxScore = chart_dict['dxScore']
        self.fc = chart_dict['fc']
        self.fs = chart_dict['fs']
        self.level = chart_dict['level']
        self.level_index = chart_dict['level_index']
        self.level_label = chart_dict['level_label']
        self.ra = chart_dict['ra']
        self.rate = chart_dict['rate']
        self.song_id = chart_dict['song_id']
        self.title = chart_dict['title']
        self.type = chart_dict['type']

    def to_dict(self):
        return {
            'achievements': self.achievements,
            'ds': self.ds,
            'dxScore': self.dxScore,
            'fc': self.fc,
            'fs': self.fs,
            'level': self.level,
            'level_index': self.level_index,
            'level_label': self.level_label,
            'ra': self.ra,
            'rate': self.rate,
            'song_id': self.song_id,
            'title': self.title,
            'type': self.type
        }


class Charts:
    def __init__(self, charts_dict: dict):
        self.dx = [Chart(chart) for chart in charts_dict['dx']]
        self.sd = [Chart(chart) for chart in charts_dict['sd']]

    def to_dict(self):
        return {
            'dx': [chart.to_dict() for chart in self.dx],
            'sd': [chart.to_dict() for chart in self.sd]
        }


class B50:
    def __init__(self, b50_dict: dict):
        self.additional_rating = b50_dict['additional_rating']
        self.charts = Charts(b50_dict['charts'])
        self.nickname = b50_dict['nickname']
        self.plate = b50_dict['plate']
        self.rating = b50_dict['rating']
        self.username = b50_dict['username']
        self.user_general_data = b50_dict['user_general_data']

    def to_dict(self):
        return {
            'additional_rating': self.additional_rating,
            'charts': self.charts.to_dict(),
            'nickname': self.nickname,
            'plate': self.plate,
            'rating': self.rating,
            'username': self.username,
            'user_general_data': self.user_general_data
        }


def get_b50(username: str):
    payload = {'username': username, 'b50': True}
    res = requests.post(
        'https://www.diving-fish.com/api/maimaidxprober/query/player', json=payload
    )
    b50 = res.json()
    success = res.status_code
    if success == 400:
        return 400, "未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。"
    elif success == 403:
        return 403, "该用户禁止了其他人获取数据。"
    return 200, B50(b50)
