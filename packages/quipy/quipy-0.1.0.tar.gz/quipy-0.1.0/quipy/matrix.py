import numpy as np
import json
from typing import List, Tuple, Union


def affine_matrix(
        source_points: List[Union[List[float], Tuple[float]]],
        target_points: List[Union[List[float], Tuple[float]]]
) -> str:
    """
    通过最小二乘法计算源坐标系到目标坐标系的仿射变换矩阵
    :param source_points: 源坐标系中的点集，格式 [(x1, y1), (x2, y2), ...]
    :param target_points: 目标坐标系中的点集，格式 [(x1, y1), (x2, y2), ...]
    :return: JSON字符串表示的3x3齐次变换矩阵
    """

    # 转换为NumPy数组并进行矩阵运算
    src = np.array(source_points, dtype=np.float64)
    dst = np.array(target_points, dtype=np.float64)

    # 构造最小二乘求解的系数矩阵
    A = np.hstack([src, np.ones((len(src), 1))])

    # 求解仿射变换参数
    H, *_ = np.linalg.lstsq(A, dst, rcond=None)

    # 构建齐次变换矩阵
    transform_matrix = np.vstack([H.T, [0, 0, 1]])

    # 返回JSON序列化结果
    return json.dumps(transform_matrix.tolist())


def apply_affine_transform(
        x: float,
        y: float,
        transform_matrix_json: str,
        acc: int = 6,
) -> Tuple[float, float]:
    """
    应用仿射变换矩阵到指定坐标点
    :param x: 原始横坐标
    :param y: 原始纵坐标
    :param transform_matrix_json: JSON字符串表示的3x3仿射变换矩阵
    :param acc: 精准度
    :return: 转换后的坐标点 (x', y')
    """
    
    # 从JSON加载变换矩阵
    H = np.array(json.loads(transform_matrix_json), dtype=np.float64)
    # 构造齐次坐标 (x, y, 1)
    homogeneous_point = np.array([x, y, 1.0])
    # 应用变换矩阵
    transformed_point = np.dot(homogeneous_point, H.T)
    # 转换回笛卡尔坐标
    res = transformed_point.flatten()[:2]
    result = np.array(res)
    return round(float(result[0]), acc), round(float(result[1]), acc)
