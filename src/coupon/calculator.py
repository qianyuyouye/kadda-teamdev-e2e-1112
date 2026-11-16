# Coupon amount calculation.

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Union

Number = Union[int, float, str, Decimal]

_CENT = Decimal("0.01")
_ZERO = Decimal("0")


def calculate_coupon_amount(amount: Number) -> Decimal:
    """计算优惠券金额。

    规则：
    - 金额为负数时按 0 处理；
    - 结果统一保留两位小数，使用 ROUND_HALF_UP 舍入，避免二进制浮点误差；
    - 返回值始终是 ``Decimal``，且指数为两位小数（如 ``Decimal('10.00')``）。
    """
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"优惠券金额无法转换为 Decimal: {amount!r}") from exc

    if not value.is_finite():
        raise ValueError(f"优惠券金额必须是有限数值: {amount!r}")

    if value < _ZERO:
        value = _ZERO

    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def calculate_coupon_deduction(coupon_amount: Number, order_amount: Number) -> Decimal:
    """优惠券实际抵扣金额：面额大于订单金额时以订单金额为上限，实付不为负。"""
    coupon = calculate_coupon_amount(coupon_amount)
    order = calculate_coupon_amount(order_amount)
    return min(coupon, order)
