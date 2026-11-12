from src.billing import BILLING_TITLE, total_amount


def test_rule_cd987896_billing_title_is_my_billing():
    """Rule cd987896: src/billing.py must define BILLING_TITLE as string '我的账单'."""
    assert BILLING_TITLE == "我的账单"
    assert isinstance(BILLING_TITLE, str)


def test_rule_bug_d5122f4e_empty_detail_total_is_zero():
    """Rule BUG-d5122f4e: 账单明细为空（空列表 / None）时总额应为 0。"""
    assert total_amount([]) == 0
    assert total_amount(None) == 0


def test_rule_bug_d5122f4e_non_empty_detail_total_sums_items():
    """明细非空时总额为各项金额之和。"""
    assert total_amount([12.5, 7.5]) == 20
    assert total_amount([0]) == 0
