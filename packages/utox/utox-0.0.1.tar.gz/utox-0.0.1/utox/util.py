import json
from typing import Any, List, Optional


def pre_condition(condition: bool, msg: str):
    """
        判断条件是否发生了异常

    :param bool condition: 条件
    :param str msg: 信息
    :raises ModelExcption: 异常
    """
    if not condition:
        raise Exception(msg)


def pre_condition_data_err(condition: bool, msg: str):
    pre_condition(condition, f"数据异常:{msg}")


def is_str_empty_in_list(v: List[str]) -> bool:
    """
    判断列表中是否有空字符串

    :param v:
    :return:
    """
    return any(map(is_empty, v))


def is_empty(string: Optional[str]) -> bool:
    if string is None:
        return True
    if string.rstrip() == "":
        return True

    return False


def is_not_empty(string: Optional[str]) -> bool:
    return not is_empty(string)


def to_response(code: int, msg: str, data: Any):
    """
    按照标准的数据结构进行返回信息

    :param int code: 成功与否的标识
    :param str msg: 提示的内容信息
    :param Any data: 模型实际返回的消息
    """
    return {"code": code, "msg": msg, "data": data}


def is_segments_crossing_1d(segment1, segment2, safe_d=0):
    """
    判断两个一维线段是否交叉
    :param segment1: 第一个线段 [start1, end1]
    :param segment2: 第二个线段 [start2, end2]
    :return: 如果交叉返回 True，否则返回 False
    """
    # 确保线段的起点和终点是有序的 (起点 <= 终点)
    start1, end1 = sorted(segment1)
    start2, end2 = sorted(segment2)

    # 判断两个区间是否有重叠
    return max(start1, start2) - safe_d <= min(end1, end2)
