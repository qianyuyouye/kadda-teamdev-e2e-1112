from decimal import Decimal

import pytest

from src.billing import (
    BILLING_TITLE,
    ERROR_INVALID_COUPON,
    ERROR_INVALID_ORDER_AMOUNT,
    calculate_bill,
    total_amount,
)


# ---------------------------------------------------------------------------
# 既有规则：账单页标题 / 账单总额等于各明细金额之和
# ---------------------------------------------------------------------------


def test_rule_cd987896_billing_title_is_my_billing():
    """Rule cd987896: src/billing.py must define BILLING_TITLE as string '我的账单'."""
    assert BILLING_TITLE == "我的账单"
    assert isinstance(BILLING_TITLE, str)


def test_rule_bug_d5122f4e_empty_detail_total_is_zero():
    """Rule BUG-d5122f4e: 账单明细为空（空列表 / None）时总额应为 0。"""
    assert total_amount([]) == 0
    assert total_amount(None) == 0
    assert total_amount(()) == 0


def test_rule_bug_d5122f4e_non_empty_detail_total_sums_items():
    """明细非空时总额为各项金额之和。"""
    assert total_amount([12.5, 7.5]) == 20
    assert total_amount([0]) == 0


def test_rule_bill_total_equals_sum_of_details():
    """Rule d0760e7e: 账单总额等于各明细金额之和。"""
    items = [19.9, 0.1, 80]
    assert total_amount(items) == sum(items) == 100
    assert total_amount([Decimal("1.10"), Decimal("2.20")]) == Decimal("3.30")


# ---------------------------------------------------------------------------
# calculate_bill：无优惠券 / 正常优惠 / 超额优惠
# ---------------------------------------------------------------------------


def test_bill_without_coupon_keeps_order_amount():
    result = calculate_bill(100)
    assert result["error"] is None
    assert result["order_amount"] == Decimal("100.00")
    assert result["discount_amount"] == Decimal("0.00")
    assert result["payable_amount"] == Decimal("100.00")


def test_bill_with_empty_coupon_has_zero_discount():
    for coupon in (None, 0, 0.0, "0", Decimal("0")):
        result = calculate_bill(100, coupon)
        assert result["error"] is None
        assert result["discount_amount"] == Decimal("0.00")
        assert result["payable_amount"] == Decimal("100.00")


def test_bill_with_valid_coupon_subtracts_discount():
    result = calculate_bill(100, 10)
    assert result["error"] is None
    assert result["order_amount"] == Decimal("100.00")
    assert result["discount_amount"] == Decimal("10.00")
    assert result["payable_amount"] == Decimal("90.00")


def test_bill_with_coupon_mapping():
    result = calculate_bill(100, {"amount": 10})
    assert result["error"] is None
    assert result["discount_amount"] == Decimal("10.00")
    assert result["payable_amount"] == Decimal("90.00")


def test_bill_discount_never_exceeds_order_amount():
    result = calculate_bill(100, 200)
    assert result["error"] is None
    assert result["discount_amount"] == Decimal("100.00")
    assert result["payable_amount"] == Decimal("0.00")


def test_bill_negative_coupon_is_treated_as_zero():
    """优惠券金额为负数时按 0 处理（N1 规则由账单模块直接复用）。"""
    result = calculate_bill(100, -5)
    assert result["error"] is None
    assert result["discount_amount"] == Decimal("0.00")
    assert result["payable_amount"] == Decimal("100.00")


def test_bill_rounds_amounts_to_two_decimals():
    result = calculate_bill(10.005, 1.234)
    assert result["error"] is None
    assert result["order_amount"] == Decimal("10.01")
    assert result["discount_amount"] == Decimal("1.23")
    assert result["payable_amount"] == Decimal("8.78")


@pytest.mark.parametrize(
    ("order", "coupon"),
    [
        (100, None),
        (100, 0),
        (100, 10),
        (100, 99.99),
        (100, 200),
        (0, 0),
        (0.01, 0.005),
        ("88.88", "8.88"),
    ],
)
def test_bill_payable_invariants(order, coupon):
    result = calculate_bill(order, coupon)
    assert result["error"] is None
    assert isinstance(result["order_amount"], Decimal)
    assert isinstance(result["discount_amount"], Decimal)
    assert isinstance(result["payable_amount"], Decimal)
    assert result["discount_amount"] <= result["order_amount"]
    assert result["payable_amount"] == result["order_amount"] - result["discount_amount"]
    assert result["payable_amount"] >= 0


def test_bill_amount_fields_are_two_decimal_decimals():
    result = calculate_bill(100, 10)
    for key in ("order_amount", "discount_amount", "payable_amount"):
        assert isinstance(result[key], Decimal)
        assert result[key].as_tuple().exponent == -2


@pytest.mark.parametrize(
    "order_amount", [-1, "-0.01", "abc", None, object(), float("nan"), float("inf"), [1, 2], {}]
)
def test_bill_invalid_order_amount_returns_error(order_amount):
    result = calculate_bill(order_amount)
    assert result["error"] == ERROR_INVALID_ORDER_AMOUNT
    assert result["order_amount"] is None
    assert result["discount_amount"] == Decimal("0.00")
    assert result["payable_amount"] == Decimal("0.00")


@pytest.mark.parametrize(
    "coupon", ["abc", object(), {"foo": 1}, float("nan"), float("inf"), [1, 2]]
)
def test_bill_invalid_coupon_returns_error(coupon):
    result = calculate_bill(100, coupon)
    assert result["error"] == ERROR_INVALID_COUPON
    assert result["order_amount"] == Decimal("100.00")
    assert result["discount_amount"] == Decimal("0.00")
    assert result["payable_amount"] == Decimal("0.00")


def test_bill_error_result_keeps_unified_shape():
    result = calculate_bill(-1)
    assert set(result) == {"order_amount", "discount_amount", "payable_amount", "error"}
    assert isinstance(result["error"], str)


def test_bill_delegates_coupon_calculation_to_n1(monkeypatch):
    """账单模块不重复实现优惠券扣减，优惠金额来自 N1 的 calculate_coupon_amount。"""
    calls = []

    def fake_calculate_coupon_amount(amount):
        calls.append(amount)
        return Decimal("3.33")

    monkeypatch.setattr("src.billing.calculate_coupon_amount", fake_calculate_coupon_amount)

    result = calculate_bill(100, 50)
    assert calls == [50]
    assert result["error"] is None
    assert result["discount_amount"] == Decimal("3.33")
    assert result["payable_amount"] == Decimal("96.67")


def test_bill_upstream_exception_returns_error(monkeypatch):
    """上游 calculate_coupon_amount 抛异常时返回统一错误结果，不产生未捕获异常。"""

    def boom(amount):
        raise RuntimeError("upstream down")

    monkeypatch.setattr("src.billing.calculate_coupon_amount", boom)

    result = calculate_bill(100, 10)
    assert result["error"] == ERROR_INVALID_COUPON
    assert result["discount_amount"] == Decimal("0.00")
    assert result["payable_amount"] == Decimal("0.00")


# ---------------------------------------------------------------------------
# total_amount：负数明细按 0 计
# ---------------------------------------------------------------------------


def test_total_amount_negative_detail_counts_as_zero():
    """负数明细按 0 计，正数照常相加：total_amount([10, -5, 3]) == 13。"""
    assert total_amount([10, -5, 3]) == 13


def test_total_amount_all_negative_details_is_zero():
    """全部为负数明细时总额为 0，不是负数。"""
    assert total_amount([-10, -2.5]) == 0


def test_total_amount_negative_detail_with_decimals():
    """Decimal 明细同样适用：负数按 0 计，正数正常保留精度相加。"""
    assert total_amount([Decimal("1.10"), Decimal("-2.20"), Decimal("3.30")]) == Decimal("4.40")
