import math
from typing import Tuple, Union, Sequence

# 常量定义
R: float = 6371_000.0


def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float, acc: int = 2) -> float:
    """
    计算两个经纬度点之间的弧面距离
    :param lon1: 第一个点的经度（单位：度）
    :param lat1: 第一个点的纬度（单位：度）
    :param lon2: 第二个点的经度（单位：度）
    :param lat2: 第二个点的纬度（单位：度）
    :param acc: 精确度
    :return: 两点间的弧面距离（米）
    """
    # 将十进制度数转换为弧度
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    # Haversine公式计算
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # 计算距离
    distance = round(R * c, acc)
    return distance


def coordinate_translation(lon: float, lat: float, dx: float, dy: float, acc: int = 8) -> Tuple[float, float]:
    """
    计算从原点经纬度移动指定距离后的新坐标
    :param lon: 原点经度（单位：度）
    :param lat: 原点纬度（单位：度）
    :param dx: 东西方向移动距离(米)，东为正，西为负
    :param dy: 南北方向移动距离(米)，北为正，南为负
    :param acc: 精准度
    :return: 目标坐标 (x2, y2)
    """
    # 计算南北方向移动（纬度变化）
    dlat = dy / R
    new_lat = lat + math.degrees(dlat)
    # 计算东西方向移动（经度变化）
    avg_lat = math.radians((lat + new_lat) / 2.0)
    dlon = dx / (R * math.cos(avg_lat))
    new_lon = lon + math.degrees(dlon)
    # 处理边界情况（经度范围-180到180）
    new_lon = (new_lon + 180) % 360 - 180
    return round(new_lat, acc), round(new_lon, acc)


def polygon_area(points: Sequence[Sequence[Union[int, float]]]) -> float:
    """
    计算由一系列坐标点首尾相连形成的多边形的面积
    :param points: [(x1, y1), (x2, y2), ..., (xn, yn)]
    :return: 多边形的面积
    """
    n = len(points)
    if n < 3:
        raise ValueError("多边形至少需要三个顶点")
    area = 0.0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]  # 使用模运算处理最后一个点与第一个点的连接
        area += x1 * y2 - y1 * x2
    return abs(area) / 2
