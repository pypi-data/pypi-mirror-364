from typing import Iterable


def multiply_all_ints(vals: Iterable[int]) -> int:
    result = 1
    for val in vals:
        result *= val
    return result


def multiply_all_floats(vals: Iterable[float]) -> float:
    result = 1.
    for val in vals:
        result *= val
    return result


def clamp_int(value: int, min_value: int, max_value: int) -> int:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value


def clamp_float(value: float, min_value: float, max_value: float) -> float:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    return value
