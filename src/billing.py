# Billing page module

from typing import Iterable, Optional, Union

# Rule cd987896: billing page title must be "我的账单"
BILLING_TITLE = "我的账单"
BILLING_PAY_LABEL = "立即支付"

Number = Union[int, float]


def total_amount(items: Optional[Iterable[Number]]) -> Number:
    """账单总额：明细为空（None 或空列表）时返回 0，否则返回各项金额之和。"""
    if not items:
        return 0
    return sum(items)
