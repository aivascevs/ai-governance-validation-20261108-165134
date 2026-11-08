import pytest

from orders import OrderStore, mask_email


def test_create_and_get():
    store = OrderStore()
    order = store.create("ana@example.test", 1250)
    assert store.get(order.id) == order
    assert order.refunded is False


def test_amount_must_be_positive():
    with pytest.raises(ValueError):
        OrderStore().create("ana@example.test", 0)


def test_unknown_order():
    with pytest.raises(KeyError):
        OrderStore().get(999)


def test_refund_once_only():
    store = OrderStore()
    order = store.create("ana@example.test", 500)
    assert store.refund(order.id).refunded is True
    with pytest.raises(ValueError):
        store.refund(order.id)


def test_lookup_value_is_not_sql():
    store = OrderStore()
    store.create("ana@example.test", 500)
    with pytest.raises((KeyError, ValueError, TypeError)):
        store.get("1 OR 1=1")


@pytest.mark.parametrize(
    "email, masked",
    [("ana@example.test", "a***@example.test"), ("not-an-email", "***")],
)
def test_mask_email(email, masked):
    assert mask_email(email) == masked


def test_logs_do_not_contain_email(caplog):
    caplog.set_level("INFO")
    OrderStore().create("ana@example.test", 700)
    assert "ana@example.test" not in caplog.text


def test_refunded_total_sums_refunded_orders_only():
    store = OrderStore()
    a = store.create("ana@example.test", 1000)
    store.create("ana@example.test", 300)
    b = store.create("ana@example.test", 200)
    store.refund(a.id)
    store.refund(b.id)
    assert store.refunded_total("ana@example.test") == 1200


def test_refunded_total_without_refunds_is_zero():
    store = OrderStore()
    store.create("ben@example.test", 900)
    assert store.refunded_total("ben@example.test") == 0


def test_refunded_total_does_not_log_email(caplog):
    caplog.set_level("INFO")
    OrderStore().refunded_total("ana@example.test")
    assert "ana@example.test" not in caplog.text
