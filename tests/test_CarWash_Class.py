import pytest
from src.CarWash.Boxes import StandartWashBox
from src.CarWash.User import User
from src.CarWash.Utils import BoxStatus, PaymentType, ResourceType


# ---------- Фикстуры ----------
@pytest.fixture
def wash_box():
    """Создаёт бокс с полностью заполненными баками."""
    return StandartWashBox(
        id=1,
        address="ул. Ленина, 1",
        box_number=1,
        curr_foam=50.0,
        curr_wax=10.0
    )


@pytest.fixture
def empty_wash_box():
    """Создаёт бокс с пустыми баками."""
    return StandartWashBox(
        id=2,
        address="ул. Ленина, 2",
        box_number=2,
        curr_foam=0.0,
        curr_wax=0.0
    )


@pytest.fixture
def user_with_balance():
    """Создаёт объект пользователя с балансом."""
    class User:
        def __init__(self, balance):
            self.balance = balance
    return User(balance=500.0)


@pytest.fixture
def user_with_low_balance():
    """Создаёт пользователя с недостаточным балансом."""
    class User:
        def __init__(self, balance):
            self.balance = balance
    return User(balance=10.0)


# ---------- Тесты для get_resources ----------
def test_get_resources(wash_box):
    """Проверка получения текущих ресурсов."""
    resources = wash_box.get_resources()
    assert resources == {
        "current_foam": round(wash_box.current_foam, 2),
        "current_wax": round(wash_box.current_wax, 2)
    }


# ---------- Тесты для restock_foam и restock_wax ----------
def test_restock_foam_within_limit(empty_wash_box):
    """Пополнение пены в пределах лимита."""
    added = 20.0
    result = empty_wash_box.restock_foam(added)
    assert empty_wash_box.current_foam == added
    assert empty_wash_box.box_status == BoxStatus.MAINTENANCE
    assert result == {
        "box_number": empty_wash_box.box_number,
        "current_foam": added,
        "status": BoxStatus.MAINTENANCE
    }


def test_restock_foam_overflow(empty_wash_box):
    """Пополнение пены с превышением максимума (50 л)."""
    added = 60.0
    result = empty_wash_box.restock_foam(added)
    assert empty_wash_box.current_foam == empty_wash_box.MAX_FOAM  # 50
    assert empty_wash_box.box_status == BoxStatus.MAINTENANCE
    assert result == {
        "box_number": empty_wash_box.box_number,
        "current_foam": empty_wash_box.MAX_FOAM,
        "status": BoxStatus.MAINTENANCE
    }


def test_restock_wax_within_limit(empty_wash_box):
    """Пополнение воска в пределах лимита."""
    added = 5.0
    result = empty_wash_box.restock_wax(added)
    assert empty_wash_box.current_wax == added
    assert empty_wash_box.box_status == BoxStatus.MAINTENANCE
    assert result == {
        "box_number": empty_wash_box.box_number,
        "current_wax": added,
        "status": BoxStatus.MAINTENANCE
    }


def test_restock_wax_overflow(empty_wash_box):
    """Пополнение воска с превышением максимума (10 л)."""
    added = 15.0
    result = empty_wash_box.restock_wax(added)
    assert empty_wash_box.current_wax == empty_wash_box.MAX_WAX  # 10
    assert empty_wash_box.box_status == BoxStatus.MAINTENANCE
    assert result == {
        "box_number": empty_wash_box.box_number,
        "current_wax": empty_wash_box.MAX_WAX,
        "status": BoxStatus.MAINTENANCE
    }


# ---------- Тесты для get_tariff_and_consumption ----------
@pytest.mark.parametrize("mode, expected_tariff, expected_consumption", [
    (ResourceType.WATER, 0.15, 0.0),
    (ResourceType.FOAM, 0.40, 0.4),   # расход уточнить по реальной реализации
    (ResourceType.WAX, 0.30, 0.5),
])
def test_get_tariff_and_consumption(wash_box, mode, expected_tariff, expected_consumption):
    tariff, consumption = wash_box.get_tariff_and_consumption(mode)
    assert tariff == expected_tariff
    assert consumption == expected_consumption


# ---------- Тесты для check_resources ----------
def test_check_resources_sufficient(wash_box):
    """Ресурсов достаточно — метод выполняется без ошибок."""
    mode = ResourceType.FOAM
    consumption = 10.0
    # Метод ничего не возвращает, просто не бросает исключение
    wash_box.check_resources(mode, consumption)


def test_check_resources_insufficient(empty_wash_box):
    """Ресурсов недостаточно — выбрасывается ValueError."""
    mode = ResourceType.FOAM
    consumption = 1.0
    with pytest.raises(ValueError):
        empty_wash_box.check_resources(mode, consumption)


# ---------- Тесты для consume_resources ----------
def test_consume_resources(wash_box):
    """Списание ресурса должно уменьшать соответствующий бак."""
    initial_foam = wash_box.current_foam
    mode = ResourceType.FOAM
    consumption = 5.0
    wash_box.consume_resources(mode, consumption)
    assert wash_box.current_foam == initial_foam - consumption


# ---------- Тесты для validate_app_payment ----------
def test_validate_app_payment_success(user_with_balance):
    """Проверка баланса проходит, если денег достаточно."""
    box = StandartWashBox(id=3, address="ул. Ленина, 3", box_number=3)
    duration = 60
    tariff = 0.40
    # Метод не возвращает значение, при успехе просто завершается без исключения
    box.validate_app_payment(user_with_balance, tariff, duration)


def test_validate_app_payment_insufficient(user_with_low_balance):
    """Проверка баланса не проходит при недостатке средств — выбрасывается ValueError."""
    box = StandartWashBox(id=4, address="ул. Ленина, 4", box_number=4)
    duration = 60
    tariff = 0.40
    with pytest.raises(ValueError):
        box.validate_app_payment(user_with_low_balance, tariff, duration)


# ---------- Тесты для validate_cash_payment ----------
def test_validate_cash_payment_success():
    """Внесённой суммы достаточно (минимальная сумма не указана, считаем, что достаточно любой >0)."""
    box = StandartWashBox(id=5, address="ул. Ленина, 5", box_number=5)
    cash = 100.0
    box.validate_cash_payment(cash)  # не должно быть исключения


def test_validate_cash_payment_insufficient():
    """Внесённая сумма равна нулю или отрицательна – вызывается ValueError."""
    box = StandartWashBox(id=6, address="ул. Ленина, 6", box_number=6)
    with pytest.raises(ValueError):
        box.validate_cash_payment(0.0)
    with pytest.raises(ValueError):
        box.validate_cash_payment(-5.0)


# ---------- Тесты для start_wash_session (APP) ----------
def test_start_wash_session_app_success(wash_box, user_with_balance):
    """Успешная мойка по приложению на фиксированное время."""
    mode = ResourceType.FOAM
    duration = 10
    tariff, consumption = wash_box.get_tariff_and_consumption(mode)

    initial_balance = user_with_balance.balance
    initial_foam = wash_box.current_foam

    wash_box.start_wash_session(
        mode=mode,
        payment_type=PaymentType.APP,
        user=user_with_balance,
        duration_seconds=duration
    )

    assert user_with_balance.balance == pytest.approx(initial_balance - duration * tariff)
    assert wash_box.current_foam == pytest.approx(initial_foam - duration * consumption)


def test_start_wash_session_app_insufficient_balance(wash_box, user_with_low_balance):
    """Мойка по приложению не должна запускаться при недостатке средств."""
    mode = ResourceType.FOAM
    duration = 60
    with pytest.raises(ValueError):
        wash_box.start_wash_session(
            mode=mode,
            payment_type=PaymentType.APP,
            user=user_with_low_balance,
            duration_seconds=duration
        )


def test_start_wash_session_app_insufficient_resources(empty_wash_box, user_with_balance):
    """Мойка по приложению при недостатке ресурсов возвращает словарь с ошибкой."""
    mode = ResourceType.FOAM
    duration = 5
    initial_foam = empty_wash_box.current_foam
    initial_balance = user_with_balance.balance

    result = empty_wash_box.start_wash_session(
        mode=mode,
        payment_type=PaymentType.APP,
        user=user_with_balance,
        duration_seconds=duration
    )

    # Ресурс не изменился
    assert empty_wash_box.current_foam == initial_foam
    # Баланс не изменился
    assert user_with_balance.balance == pytest.approx(initial_balance)
    # Возвращён словарь с ошибкой
    assert result["message"] == "Мойка принудительно остановлена"
    assert result["time"] == 0
    assert result["total_price"] == 0.0
    assert "error" in result
    assert isinstance(result["error"], ValueError)
    # Проверяем, что ошибка связана с ресурсами (можно уточнить текст)
    assert empty_wash_box.box_status == BoxStatus.MAINTENANCE


# ---------- Тесты для start_wash_session (CASH) ----------
def test_start_wash_session_cash_success(wash_box):
    """Мойка за наличные работает до исчерпания денег или ресурсов."""
    mode = ResourceType.FOAM
    cash_amount = 100.0
    tariff, consumption = wash_box.get_tariff_and_consumption(mode)

    initial_foam = wash_box.current_foam
    expected_duration = cash_amount / tariff
    expected_actual_duration = min(expected_duration, initial_foam / consumption)

    wash_box.start_wash_session(
        mode=mode,
        payment_type=PaymentType.CASH,
        cash_amount=cash_amount
    )

    assert wash_box.current_foam == pytest.approx(initial_foam - expected_actual_duration * consumption)


def test_start_wash_session_cash_insufficient_cash(wash_box):
    """Мойка за наличные не запускается при нулевой или отрицательной сумме."""
    with pytest.raises(ValueError):
        wash_box.start_wash_session(
            mode=ResourceType.FOAM,
            payment_type=PaymentType.CASH,
            cash_amount=0.0
        )

def test_start_wash_session_cash_insufficient_resources(empty_wash_box):
    """Мойка за наличные при пустых ресурсах возвращает словарь с ошибкой."""
    initial_foam = empty_wash_box.current_foam
    result = empty_wash_box.start_wash_session(
        mode=ResourceType.FOAM,
        payment_type=PaymentType.CASH,
        cash_amount=50.0
    )
    # Ресурс не изменился
    assert empty_wash_box.current_foam == initial_foam
    # Возвращён словарь с ошибкой, время 0, цена 0
    assert result["message"] == "Мойка принудительно остановлена"
    assert result["time"] == 0
    assert result["total_price"] == 0.0
    assert "error" in result
    assert isinstance(result["error"], ValueError)
    assert empty_wash_box.box_status == BoxStatus.MAINTENANCE

def test_start_wash_session_cash_stops_by_resource(wash_box):
    mode = ResourceType.FOAM
    cash_amount = 1000.0
    consumption = wash_box.get_tariff_and_consumption(mode)[1]
    initial_foam = wash_box.current_foam

    result = wash_box.start_wash_session(
        mode=mode,
        payment_type=PaymentType.CASH,
        cash_amount=cash_amount
    )

    # Ресурс должен быть полностью израсходован
    assert wash_box.current_foam == pytest.approx(0.0)
    # Время мойки должно соответствовать расходу ресурса
    expected_time = initial_foam / consumption
    assert result["time"] == pytest.approx(expected_time)
    assert result["total_price"] == pytest.approx(expected_time * 0.40)
    assert wash_box.box_status == BoxStatus.MAINTENANCE


# ---------- Тест на статус после пополнения ----------
def test_restock_sets_maintenance(wash_box):
    """После пополнения статус становится MAINTENANCE и мойка недоступна."""
    wash_box.restock_foam(10)
    assert wash_box.box_status == BoxStatus.MAINTENANCE

    # Проверим, что при статусе MAINTENANCE запуск мойки выбрасывает ошибку
    user = User(user_id=3, user_name="Test", initial_balance=1000.0)
    with pytest.raises(ValueError, match="Бокс №1 недоступен!"):
        wash_box.start_wash_session(
            mode=ResourceType.WATER,
            payment_type=PaymentType.APP,
            user=user,
            duration_seconds=1
        )