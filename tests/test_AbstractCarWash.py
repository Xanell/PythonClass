import pytest
from src.core.AbstractCarWash import AbstractCarWash
from src.config.Enums import BoxStatus, PaymentType
from src.User_Class import User

# Тестовый подкласс, реализующий абстрактный метод
class DummyCarWash(AbstractCarWash):
    def get_resources(self):
        return {"water": 100.0, "foam": 50.0}


@pytest.fixture
def wash_box():
    """Фикстура создаёт экземпляр тестового подкласса"""
    return DummyCarWash(id=1, address="ул. Тестовая, 1", box_number=5)


@pytest.fixture
def user():
    """Фикстура создаёт пользователя с балансом 100.0"""
    return User(user_id=1, user_name="Тестовый Пользователь", initial_balance=100.0)


# --- Тесты инициализации ---
def test_init(wash_box):
    assert wash_box.car_wash_Id == 1
    assert wash_box.car_wash_address == "ул. Тестовая, 1"
    assert wash_box.box_number == 5
    assert wash_box.box_status == BoxStatus.FREE
    assert wash_box.cash_box == 0.0
    assert wash_box.total_revenue == 0.0
    assert wash_box.total_washes == 0
    assert wash_box.pay_history_log == {}
    assert wash_box.statistics_log == {}
    assert wash_box.error_history_log == []


# --- Тесты методов журнала ошибок ---
def test_get_error_history_log_empty(wash_box):
    assert wash_box.get_error_history_log() == []


def test_add_error_history_log(wash_box):
    wash_box.add_error_history_log("Ошибка 1")
    wash_box.add_error_history_log("Ошибка 2")
    assert wash_box.get_error_history_log() == ["Ошибка 1", "Ошибка 2"]


# --- Тесты журнала платежей ---
def test_add_pay_history_log(wash_box):
    wash_box.add_pay_history_log(total_price=10.0, time_passed=30)
    wash_box.add_pay_history_log(total_price=15.5, time_passed=45)

    assert wash_box.total_washes == 2
    # Проверяем структуру журнала: {box_number: [(цена, время), ...]}
    assert wash_box.pay_history_log == {
        5: [(10.0, 30), (15.5, 45)]
    }


def test_get_pay_history_log(wash_box):
    assert wash_box.get_pay_history_log() == {}
    wash_box.add_pay_history_log(7.0, 20)
    assert wash_box.get_pay_history_log() == {5: [(7.0, 20)]}


# --- Тесты получения статистики ---
def test_get_statistics(wash_box):
    wash_box.add_pay_history_log(10.0, 30)
    wash_box.add_error_history_log("Тестовая ошибка")
    stats = wash_box.get_statistics()

    assert stats["box_number"] == 5
    assert stats["address"] == "ул. Тестовая, 1"
    assert stats["cash_box"] == 0.0
    assert stats["total_revenue"] == 0.0
    assert stats["total_washes"] == 1
    assert stats["resources"] == {"water": 100.0, "foam": 50.0}
    assert stats["errors"] == ["Тестовая ошибка"]


# --- Тесты отчёта о статусе ---
def test_get_status_report(wash_box):
    report = wash_box.get_status_report()
    assert report == {
        "box_number": 5,
        "cash_box": 0.0,
        "status": BoxStatus.FREE,
    }


# --- Тесты управления статусом ---
def test_set_maintenance_status(wash_box):
    result = wash_box.set_maintenance_status()
    assert wash_box.box_status == BoxStatus.MAINTENANCE
    assert result == {"box_number": 5, "status": BoxStatus.MAINTENANCE}


def test_finish_maintenance_status(wash_box):
    wash_box.box_status = BoxStatus.MAINTENANCE
    result = wash_box.finish_maintenance_status()
    assert wash_box.box_status == BoxStatus.FREE
    assert result == {"box_number": 5, "box_status": BoxStatus.FREE}


# --- Тесты оплаты ---
def test_process_payment_cash(wash_box):
    result = wash_box.process_payment(amount=50.0, payment_type=PaymentType.CASH, user=None)
    assert result is True
    assert wash_box.cash_box == 50.0
    assert wash_box.total_revenue == 50.0


def test_process_payment_app_success(wash_box, user):
    result = wash_box.process_payment(amount=30.0, payment_type=PaymentType.APP, user=user)
    assert result is True
    assert user.balance == 70.0
    assert wash_box.cash_box == 0.0  # наличные не меняются
    assert wash_box.total_revenue == 30.0


def test_process_payment_app_insufficient_funds(wash_box, user):
    with pytest.raises(ValueError, match="недостаточно средств"):
        wash_box.process_payment(amount=150.0, payment_type=PaymentType.APP, user=user)
    # Баланс пользователя не изменился
    assert user.balance == 100.0
    # Выручка и касса не изменились
    assert wash_box.total_revenue == 0.0
    assert wash_box.cash_box == 0.0


def test_process_payment_app_user_none(wash_box):
    with pytest.raises(AttributeError):
        wash_box.process_payment(amount=10.0, payment_type=PaymentType.APP, user=None)