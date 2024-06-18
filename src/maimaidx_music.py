import json
import random
from typing import Dict, List, Optional, Union, Tuple, Any
from copy import deepcopy

import requests

chart_tags = ['底力', '侧重键盘', '侧重星星', '交互', '纵连', '扫键', '转圈', '散打', '叠键', '位移', '出张', '错位',
              '节奏乱',
              '慢速星星', '一笔画', '短时间爆发', '耐力', '防蹭', '绝赞难抓', 'touch']


def get_cover_len5_id(mid) -> str:
    mid = int(mid)
    if 10000 < mid <= 11000:
        mid -= 10000
    return f'{mid:05d}'

def get_cover_url(song_id):
    song_id = str(song_id).zfill(5)
    return f"/cover/{song_id}.png"



def cross(checker: List[Any], elem: Optional[Union[Any, List[Any]]], diff):
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    if isinstance(elem, List):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if __e in elem:
                diff_ret.append(_j)
                ret = True
    elif isinstance(elem, Tuple):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem[0] <= __e <= elem[1]:
                diff_ret.append(_j)
                ret = True
    else:
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem == __e:
                return True, [_j]
    return ret, diff_ret


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem


class Chart(Dict):
    tap: Optional[int] = None
    slide: Optional[int] = None
    hold: Optional[int] = None
    touch: Optional[int] = None
    brk: Optional[int] = None
    charter: Optional[int] = None
    ds: Optional[float] = None
    level: Optional[str] = None
    chart_id: Optional[str] = None

    def to_dict(self):
        return {
            'tap': self.tap,
            'slide': self.slide,
            'hold': self.hold,
            'touch': self.touch,
            'brk': self.brk,
            'charter': self.charter,
            'ds': self.ds,
            'level': self.level,
            'chart_id': self.chart_id,
        }

    def __getattribute__(self, item):
        if item == 'tap':
            return self['tap']
        elif item == 'hold':
            return self['hold']
        elif item == 'slide':
            return self['slide']
        elif item == 'touch':
            return self.get('touch') if self.get('touch') is not None else 0
        elif item == 'brk':
            return self['brk']
        elif item == 'charter':
            return self['charter']
        elif item == 'ds':
            return self['ds']
        elif item == 'level':
            return self['level']
        elif item == 'chart_id':
            return self['chart_id']
        return super().__getattribute__(item)


class Music(Dict):
    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Optional[str] = None
    bpm: Optional[float] = None
    version: Optional[str] = None
    charts: Optional[List[Chart]] = None
    artist: Optional[str] = None

    diff: List[int] = []

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'type': self.type,
            'bpm': self.bpm,
            'version': self.version,
            'artist': self.artist,
            'charts': [chart.to_dict() for chart in self.charts],
            'cover': get_cover_url(self.id),
        }
    def __getattribute__(self, item):
        if item in self:
            return self[item]
        return super().__getattribute__(item)


class MusicList(List[Music]):
    def by_id(self, music_id: int) -> Optional[Music]:
        for music in self:
            if music.id == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[Music]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self, count: int = 1):
        return random.sample(self, count)

    def filter(self,
               *,
               level: Optional[Union[str, List[str]]] = ...,
               ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               title_search: Optional[str] = ...,
               genre: Optional[Union[str, List[str]]] = ...,
               bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               type: Optional[Union[str, List[str]]] = ...,
               diff: List[int] = ...,
               ):
        new_list = MusicList()
        for music in self:
            diff2 = diff
            music = deepcopy(music)
            ret, diff2 = cross(music.level, level, diff2)
            if not ret:
                continue
            ret, diff2 = cross(music.ds, ds, diff2)
            if not ret:
                continue
            if not in_or_equal(music.genre, genre):
                continue
            if not in_or_equal(music.type, type):
                continue
            if not in_or_equal(music.bpm, bpm):
                continue
            if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
                continue
            music.diff = diff2
            new_list.append(music)
        return new_list

    def get_chart_id(self, music_id: int, chart_index: int) -> Optional[str]:
        # Find the music by its ID
        music = self.by_id(music_id)
        if music is None:
            return None

        # Check if the chart index is valid
        if chart_index < 0 or chart_index >= len(music.charts):
            return None

        # Return the chart_id of the specified chart
        print(music.charts[chart_index])
        return music.charts[chart_index].chart_id

    def get_all_charts(self):
        charts = []
        for music in self:
            for chart in music.charts:
                charts.append(chart)
        return charts

    def get_song_id_and_index_by_chart_id(self, chart_id: str) -> (Optional[int],Optional[int]):
        for music in self:
            for chart in music.charts:
                if chart.chart_id == chart_id:
                    return music.id, music.charts.index(chart)
        return None


total_list: MusicList


def music_list_init(music_list: MusicList):
    global total_list
    total_list = music_list
