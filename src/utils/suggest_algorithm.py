from typing import List

import numpy as np


class Player:
    tag: List = [True, False]

    def __init__(self, player_id: int, tags: List):
        self.player_id = player_id
        self.tags = tags
        pass


class Chart:
    chart_id = 0
    tags: List = [True, False]

    def __init__(self, chart_id: int, tags: List):
        self.chart_id = chart_id
        self.tags = tags
        pass




def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# 计算player与所有chart的相似度
def calculate_similarity(player_tags, charts):
    similarities = {}
    for chart in charts:
        similarity = cosine_similarity(player_tags, chart.tags)
        similarities[chart] = similarity
    return similarities


def get_suggestion(pool: List[Chart], count: int, player: Player):
    similarities = calculate_similarity(player.tags, pool)
    # 相似度排序
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    # 选取前count个chart
    selected_charts = [chart for chart, similarity in sorted_similarities[:count]]
    return selected_charts
