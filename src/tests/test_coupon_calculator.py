"""优惠券计算单元测试。

对应任务：新增优惠券计算核心函数 / 负数金额归零和两位小数舍入。
"""

from decimal import Decimal

import pytest

from src.coupon.calculator import calculate_coupon_amount


def test_positive_integer_keeps_two_decimals():
    assert calculate_coupon_amount(10) == Decimal("10.00")


def test_positive_float_keeps_two_decimals():
    assert calculate_coupon_amount(1.2) == Decimal("1.20")


def test_zero_amount_is_two_decimals():
    assert calculate_coupon_amount(0) == Decimal("0.00")
    assert calculate_coupon_amount(0.0) == Decimal("0.00")


def test_negative_amount_becomes_zero():
    assert calculate_coupon_amount(-5) == Decimal("0.00")


def test_small_negative_amount_becomes_zero():
    assert calculate_coupon_amount(-0.01) == Decimal("0.00")


def test_rounding_half_up_rounds_up():
    assert calculate_coupon_amount(1.236) == Decimal("1.24")


def test_rounding_half_up_rounds_down():
    assert calculate_coupon_amount(1.234) == Decimal("1.23")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (0.005, Decimal("0.01")),
        (2.675, Decimal("2.68")),  # 避免二进制浮点误差
        ("3.456", Decimal("3.46")),
        (Decimal("7.891"), Decimal("7.89")),
        (0.1 + 0.2, Decimal("0.30")),
        (-1.5, Decimal("0.00")),
    ],
)
def test_edges(raw, expected):
    assert calculate_coupon_amount(raw) == expected


def test_result_is_decimal_with_two_decimal_places():
    result = calculate_coupon_amount(5)
    assert isinstance(result, Decimal)
    assert str(result) == "5.00"
    assert result.as_tuple().exponent == -2


def test_invalid_input_raises_value_error():
    with pytest.raises(ValueError):
        calculate_coupon_amount("not-a-number")
