import math

# 常量定义
A: int = 6378245
EE: float = 0.00669342162296594323


def transform_lon(lon: float, lat: float) -> float:
    """
    辅助函数，用于WGS84到GCJ02和GCJ02到WGS84的转换
    :param lon: 经度
    :param lat: 纬度
    :return: 经度偏移量
    """
    ret = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + 0.1 * lon * lat + 0.1 * math.sqrt(abs(lon))
    ret += (20.0 * math.sin(6.0 * lon * math.pi) + 20.0 * math.sin(2.0 * lon * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lon * math.pi) + 40.0 * math.sin(lon / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lon / 12.0 * math.pi) + 300.0 * math.sin(lon / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def transform_lat(lon: float, lat: float) -> float:
    """
    辅助函数，用于WGS84到GCJ02和GCJ02到WGS84的转换
    :param lon: 经度
    :param lat: 纬度
    :return: 纬度偏移量
    """
    ret = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + 0.1 * lon * lat + 0.2 * math.sqrt(abs(lon))
    ret += (20.0 * math.sin(6.0 * lon * math.pi) + 20.0 * math.sin(2.0 * lon * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lon: float, lat: float, acc: int = 8) -> tuple[float, float]:
    """
    WGS84坐标转换为GCJ02坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 经纬度
    """
    dLon = transform_lon(lon - 105.0, lat - 35.0)
    dLat = transform_lat(lon - 105.0, lat - 35.0)
    radLat = lat / 180.0 * math.pi
    magic = 1 - EE * math.sin(radLat) * math.sin(radLat)
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * math.pi)
    dLon = (dLon * 180.0) / (A / sqrtMagic * math.cos(radLat) * math.pi)
    mgLon = lon + dLon
    mgLat = lat + dLat
    return round(mgLon, acc), round(mgLat, acc)


def gcj02_to_wgs84(lon: float, lat: float, acc: int = 8) -> tuple[float, float]:
    """
    GCJ02坐标转换为WGS84坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 经纬度
    """
    dLat = transform_lat(lon - 105.0, lat - 35.0)
    dLon = transform_lon(lon - 105.0, lat - 35.0)
    radLat = lat / 180.0 * math.pi
    magic = math.sin(radLat)
    magic = 1 - EE * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((A * (1 - EE)) / (magic * sqrtMagic) * math.pi)
    dLon = (dLon * 180.0) / (A / sqrtMagic * math.cos(radLat) * math.pi)
    mglon = lon + dLon
    mglat = lat + dLat
    return round(lon * 2 - mglon, acc), round(lat * 2 - mglat, acc)


def gcj02_to_bd09(lon: float, lat: float, acc: int = 8) -> tuple[float, float]:
    """
    GCJ02坐标转换为BD09坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 经纬度
    """
    x_pi = math.pi * 3000.0 / 180.0
    z = math.sqrt(lon * lon + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lon) + 0.000003 * math.cos(lon * x_pi)
    bd_lon = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return round(bd_lon, acc), round(bd_lat, acc)


def bd09_to_gcj02(lon: float, lat: float, acc: int = 8) -> tuple[float, float]:
    """
    BD09坐标转换为GCJ02坐标
    :param lon: 经度
    :param lat: 纬度
    :param acc: 精确度
    :return: 经纬度
    """
    x_pi = math.pi * 3000.0 / 180.0
    x = lon - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lon = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return round(gg_lon, acc), round(gg_lat, acc)
