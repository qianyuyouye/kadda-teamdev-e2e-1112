# Billing page module
#
# 账单计算公共入口。金额一律使用 Decimal 并保留两位小数，
# 复用 N1 优惠券计算模块（src.coupon.calculator）的返回约定。

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Iterable, Mapping, Optional, Union

from src.coupon.calculator import calculate_coupon_amount

# Rule cd987896: billing page title must be "我的账单"
BILLING_TITLE = "我的账单"
BILLING_PAY_LABEL = "立即支付"

Number = Union[int, float, str, Decimal]

_CENT = Decimal("0.01")
_ZERO = Decimal("0.00")

# 统一错误信息：调用方只判断 error 是否为空，不需要捕获异常。
ERROR_INVALID_ORDER_AMOUNT = "订单金额无效：必须是大于等于 0 的有限数值"
ERROR_INVALID_COUPON = "优惠券参数无效或优惠券计算失败"


def total_amount(items: Optional[Iterable[Number]]) -> Number:
    """账单总额：明细为空（None 或空列表）时返回 0，否则返回各项金额之和。"""
    if not items:
        return 0
    return sum(items)


def _to_decimal(value: Any) -> Decimal:
    """把金额转换成 Decimal；非法值抛 ValueError，由 calculate_bill 统一收敛。"""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"无法解析为金额: {value!r}") from exc
    if not amount.is_finite():
        raise ValueError(f"金额必须是有限数值: {value!r}")
    return amount


def _quantize(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def _result(
    order_amount: Optional[Decimal],
    discount_amount: Decimal,
    payable_amount: Decimal,
    error: Optional[str] = None,
) -> dict:
    return {
        "order_amount": order_amount,
        "discount_amount": discount_amount,
        "payable_amount": payable_amount,
        "error": error,
    }


def _error(message: str, order_amount: Optional[Decimal] = None) -> dict:
    return _result(order_amount, _ZERO, _ZERO, message)


def _coupon_value(coupon: Any) -> Any:
    """从优惠券信息中取出优惠券面额，交给 N1 的金额计算函数。"""
    if isinstance(coupon, Mapping):
        for key in ("amount", "discount_amount"):
            if key in coupon:
                return coupon[key]
        raise ValueError("优惠券信息缺少金额字段")
    return coupon


def calculate_bill(order_amount: Number, coupon: Any = None) -> dict:
    """计算账单：订单金额 - 优惠金额 = 应付金额。

    参数：
    - ``order_amount``：订单金额，接受 int / float / str / Decimal，必须大于等于 0；
    - ``coupon``：优惠券信息，``None`` 表示无优惠券；也可传优惠券面额，
      或带 ``amount`` / ``discount_amount`` 字段的映射。

    返回（始终返回 dict，不抛出异常）：
    - ``order_amount``：订单金额，Decimal（两位小数）；订单金额非法时为 None；
    - ``discount_amount``：优惠金额，Decimal（两位小数），不超过订单金额；
    - ``payable_amount``：应付金额，Decimal（两位小数），等于订单金额减优惠金额；
    - ``error``：成功为 None，失败为统一错误信息字符串。
    """
    try:
        order = _quantize(_to_decimal(order_amount))
    except (ValueError, TypeError, ArithmeticError):
        return _error(ERROR_INVALID_ORDER_AMOUNT)

    if order < 0:
        return _error(ERROR_INVALID_ORDER_AMOUNT)

    if coupon is None:
        discount = _ZERO
    else:
        try:
            discount = calculate_coupon_amount(_coupon_value(coupon))
        except Exception:
            # 上游异常、非法优惠券参数统一收敛为错误结果，不向上抛出。
            return _error(ERROR_INVALID_COUPON, order_amount=order)

    # 优惠金额不超过订单金额，保证应付金额非负。
    discount = _quantize(min(discount, order))
    payable = _quantize(order - discount)
    return _result(order, discount, payable)
