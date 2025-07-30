import math

# 常量定义
R: float = 20037508.34


def lonlat_to_mercator(lon: float, lat: float, acc: int = 2) -> tuple[float, float]:
    """
    将经纬度转换为墨卡托投影坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 横纵坐标
    """
    x = lon * R / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180) * R / 180
    return round(x, acc), round(y, acc)


def mercator_to_lonlat(x: float, y: float, acc: int = 8) -> tuple[float, float]:
    """
    将墨卡托投影坐标转换为经纬度
    :param x: 横坐标
    :param y: 纵坐标
    :param acc: 精确度
    :return: 经纬度
    """
    lon = x * 180 / R
    lat = 180 / math.pi * (2 * math.atan(math.exp(y * 180 / R * math.pi / 180)) - math.pi / 2)
    return round(lon, acc), round(lat, acc)
