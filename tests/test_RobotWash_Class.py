import pytest
import sys
import os

current_dir = os.path.dirname(__file__)  # Python-Class/
sys.path.append(current_dir)  # Добавляем Python-Class в путь

from src.config.Enums import BoxStatus, ResourceType, WashMode, PaymentType
from src.models.RobotWash_Class import RobotWashStation
from src.User_Class import User


@pytest.fixture
def station():
    """Создает станцию с начальными ресурсами"""
    return RobotWashStation(1, "ул. Тестовая, 1", 1)

@pytest.fixture
def user():
    """Создает пользователя с балансом"""
    return User(1, "Иван Петров", 1000.0)

@pytest.fixture
def poor_user():
    """Создает пользователя с малым балансом"""
    return User(2, "Бедный Петров", 50.0)

@pytest.fixture
def full_station(station):
    """Создает станцию с полными ресурсами"""
    station.full_refill()
    return station

# ============================================
# 1. ТЕСТЫ ИНИЦИАЛИЗАЦИИ
# ============================================
class TestRobotWashStation:
    def test_init(self, station):
        """Тест инициализации станции"""
        assert station.car_wash_Id == 1
        assert station.box_number == 1
        assert station.box_status == BoxStatus.FREE
        
        # Проверка начальных ресурсов
        assert station.WATER == 400.0
        assert station.OSMOS == 40.0
        assert station.WAX == 4.0
        assert station.SHAMPOO == 8.0
        
        # Проверка максимальных значений
        assert station.MAX_WATER == 500.0
        assert station.MAX_OSMOS == 50.0
        assert station.MAX_WAX == 5.0
        assert station.MAX_SHAMPOO == 10.0
        
        # Проверка цен
        assert station.EXPRESS_WASH == 300
        assert station.STANDART_WASH == 500
        assert station.PREMIUM_WASH == 1000

    @pytest.mark.parametrize("id_value, address, box_number, expected_id", [
    (1, "ул. Ленина, 1", 1, 1),
    (2, "ул. Пушкина, 2", 2, 2),
    (100, "пр. Мира, 100", 10, 100),
    (5, "д. Юркино, Солнечная ул. 7", 3, 5),
    (999, "Москва, ул. Тверская, 15", 7, 999),
    ])

    def test_init_different_values(self, id_value, address, box_number, expected_id):
        """Тест: создание с разными значениями"""
        station = RobotWashStation(id_value, address, box_number)
        assert station.car_wash_Id == expected_id
        assert station.car_wash_address == address
        assert station.box_number == box_number

    @pytest.mark.parametrize("attr_name, expected_type", [
    ("car_wash_Id", int),
    ("car_wash_address", str),
    ("box_number", int),
    ("box_status", BoxStatus),
    ("WATER", float),
    ("OSMOS", float),
    ("WAX", float),
    ("SHAMPOO", float),
    ("EXPRESS_WASH", int),
    ("STANDART_WASH", int),
    ("PREMIUM_WASH", int),
    ])

    def test_init_attribute_types(self, attr_name, expected_type):
        """Тест: проверка типов данных"""
        station = RobotWashStation(1, "ул. Тестовая, 1", 1)
        assert isinstance(getattr(station, attr_name), expected_type)

# ============================================
# 2. ТЕСТЫ ПОЛУЧЕНИЯ РЕСУРСОВ
# ============================================

    def test_get_resources(self, station):
        """Тест получения всех ресурсов"""
        resources = station.get_resources()
    
        assert resources["current_water"] == 400.0
        assert resources["current_osmos"] == 40.0
        assert resources["current_wax"] == 4.0
        assert resources["current_shampoo"] == 8.0

    @pytest.mark.parametrize("resource, expected_value", [
    (ResourceType.WATER, 400.0),
    (ResourceType.OSMOS, 40.0),
    (ResourceType.WAX, 4.0),
    (ResourceType.SHAMPOO, 8.0),
    ])

    def test_get_current_resources(self, station, resource, expected_value):
        """Тест получения конкретного ресурса"""
        result = station.get_current_resources(resource)
        assert result == expected_value

    def test_get_current_resources_unknown(self, station):
        """Тест получения неизвестного ресурса"""
        # Создаем фиктивный ресурс
        class UnknownResource:
            pass
        result = station.get_current_resources(UnknownResource())  # type: ignore
        assert result == "Такого ресурса нет!"
        assert len(station.error_history_log) > 0

# ============================================
# 3. ТЕСТЫ ПРОВЕРКИ РЕСУРСОВ
# ============================================

    def test_check_express_success(self, full_station):
        """Тест: ресурсов достаточно для Экспресс"""
        assert full_station.check_express() is True

    def test_check_express_fail_water(self, station):
        """Тест: не хватает воды для Экспресс"""
        station.WATER = 10.0
        assert station.check_express() is False
        assert len(station.error_history_log) > 0

    def test_check_express_fail_shampoo(self, station):
        """Тест: не хватает шампуня для Экспресс"""
        station.SHAMPOO = 0.0
        assert station.check_express() is False
        assert len(station.error_history_log) > 0

    def test_check_standard_success(self, full_station):
        """Тест: ресурсов достаточно для Стандарт"""
        assert full_station.check_standard() is True

    def test_check_standard_fail_osmos(self, station):
        """Тест: не хватает осмоса для Стандарт"""
        station.OSMOS = 0.0
        assert station.check_standard() is False
        assert len(station.error_history_log) > 0

    def test_check_premium_success(self, full_station):
        """Тест: ресурсов достаточно для Премиум"""
        assert full_station.check_premium() is True

    def test_check_premium_fail_wax(self, station):
        """Тест: не хватает воска для Премиум"""
        station.WAX = 0.0
        assert station.check_premium() is False
        assert len(station.error_history_log) > 0

    @pytest.mark.parametrize("mode, expected", [
    (WashMode.EXPRESS, True),
    (WashMode.STANDARD, True),
    (WashMode.PREMIUM, True),
    ])

    def test_check_resources_success(self, full_station, mode, expected):
        """Тест: проверка ресурсов для всех режимов (успешно)"""
        assert full_station.check_resources(mode) == expected

    @pytest.mark.parametrize("mode, resource_to_drain", [
        (WashMode.EXPRESS, "WATER"),
        (WashMode.STANDARD, "OSMOS"),
        (WashMode.PREMIUM, "WAX"),
        ])

    def test_check_resources_fail(self, station, mode, resource_to_drain):
        """Тест: проверка ресурсов для всех режимов (неуспешно)"""
        setattr(station, resource_to_drain, 0.0)
        assert station.check_resources(mode) is False

    # ============================================
    # 4. ТЕСТЫ ДЛЯ ТЕХНИКА
    # ============================================

    def test_refill_resource_success_water(self, station):
        """Тест успешного долива воды"""
        initial = station.WATER
        station.refill_resource(ResourceType.WATER, 50.0)
        assert station.WATER == initial + 50.0

    def test_refill_resource_success_osmos(self, station):
        """Тест успешного долива осмоса"""
        initial = station.OSMOS
        station.refill_resource(ResourceType.OSMOS, 10.0)
        assert station.OSMOS == initial + 10.0

    def test_refill_resource_success_wax(self, station):
        """Тест успешного долива воска"""
        initial = station.WAX
        station.refill_resource(ResourceType.WAX, 1.0)
        assert station.WAX == initial + 1.0

    def test_refill_resource_success_shampoo(self, station):
        """Тест успешного долива шампуня"""
        initial = station.SHAMPOO
        station.refill_resource(ResourceType.SHAMPOO, 2.0)
        assert station.SHAMPOO == initial + 2.0

    @pytest.mark.parametrize("resource, amount, expected_error", [
        (ResourceType.WATER, 150.0, "Нельзя долить больше 500.0!"),
        (ResourceType.OSMOS, 20.0, "Нельзя долить больше 50.0!"),
        (ResourceType.WAX, 10.0, "Нельзя долить больше 5.0!"),
        (ResourceType.SHAMPOO, 5.0, "Нельзя долить больше 10.0!"),
        ])

    def test_refill_resource_overflow(self, station, resource, amount, expected_error):
        """Тест: долив с превышением максимума"""
        # Проверяем, что ошибка записывается в лог
        station.refill_resource(resource, amount)
        assert len(station.error_history_log) > 0
        # Проверяем, что ресурс не превысил максимум
        if resource == ResourceType.WATER:
            assert station.WATER <= station.MAX_WATER
        elif resource == ResourceType.OSMOS:
            assert station.OSMOS <= station.MAX_OSMOS
        elif resource == ResourceType.WAX:
            assert station.WAX <= station.MAX_WAX
        elif resource == ResourceType.SHAMPOO:
            assert station.SHAMPOO <= station.MAX_SHAMPOO

    # ============================================
    # 5. ТЕСТЫ ТАРИФОВ
    # ============================================

    @pytest.mark.parametrize("mode, expected_price", [
        (WashMode.EXPRESS, 300),
        (WashMode.STANDARD, 500),
        (WashMode.PREMIUM, 1000),
        ])

    def test_get_tariff(self, station, mode, expected_price):
        """Тест получения цены для всех режимов"""
        assert station.get_tariff(mode) == expected_price

    def test_get_tariff_unknown(self, station):
        """Тест получения цены неизвестного режима"""
        class UnknownMode:
            pass
        result = station.get_tariff(UnknownMode())  # type: ignore
        assert result is None

    # ============================================
    # 6. ТЕСТЫ ВАЛИДАЦИИ ОПЛАТЫ
    # ============================================

    def test_validate_app_payment_success(self, station, user):
        """Тест успешной проверки оплаты через приложение"""
        station.validate_app_payment(user, 300.0)

    def test_validate_app_payment_user_none(self, station):
        """Тест: оплата без пользователя"""
        with pytest.raises(ValueError) as exc:
            station.validate_app_payment(None, 300.0)
        assert "необходимо указать пользователя" in str(exc.value)

    def test_validate_app_payment_insufficient(self, station, poor_user):
        """Тест: недостаток средств на балансе"""
        with pytest.raises(ValueError) as exc:
            station.validate_app_payment(poor_user, 300.0)
        assert "Недостаточно средств" in str(exc.value)

    def test_validate_cash_payment_success(self, station):
        """Тест успешной проверки оплаты наличными"""
        station.validate_cash_payment(500.0)

    @pytest.mark.parametrize("cash_amount", [0.0, -100.0])
    def test_validate_cash_payment_invalid(self, station, cash_amount):
        """Тест: неверная сумма наличных"""
        with pytest.raises(ValueError) as exc:
            station.validate_cash_payment(cash_amount)
        assert "положительной" in str(exc.value)

    # ============================================
    # 7. ТЕСТЫ ЗАПУСКА МОЙКИ
    # ============================================

    def test_start_wash_express_app_success(self, full_station, user):
        """Тест успешного запуска Экспресс через приложение"""
        initial_balance = user.balance
        initial_water = full_station.WATER
        initial_shampoo = full_station.SHAMPOO
        
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )
        
        assert result is None
        assert user.balance == initial_balance - 300
        assert full_station.WATER == initial_water - 50
        assert full_station.SHAMPOO == initial_shampoo - 2
        assert full_station.total_washes == 1

    def test_start_wash_standard_app_success(self, full_station, user):
        """Тест успешного запуска Стандарт через приложение"""
        initial_balance = user.balance
        initial_water = full_station.WATER
        initial_shampoo = full_station.SHAMPOO
        initial_osmos = full_station.OSMOS
        
        result = full_station.start_wash_session(
            mode=WashMode.STANDARD,
            payment_type=PaymentType.APP,
            user=user
        )
        
        assert result is None
        assert user.balance == initial_balance - 500
        assert full_station.WATER == initial_water - 70
        assert full_station.SHAMPOO == initial_shampoo - 3
        assert full_station.OSMOS == initial_osmos - 20
        assert full_station.total_washes == 1

    def test_start_wash_premium_app_success(self, full_station, user):
        """Тест успешного запуска Премиум через приложение"""
        initial_balance = user.balance
        initial_water = full_station.WATER
        initial_shampoo = full_station.SHAMPOO
        initial_osmos = full_station.OSMOS
        initial_wax = full_station.WAX
        
        result = full_station.start_wash_session(
            mode=WashMode.PREMIUM,
            payment_type=PaymentType.APP,
            user=user
        )
        
        assert result is None
        assert user.balance == initial_balance - 1000
        assert full_station.WATER == initial_water - 120
        assert full_station.SHAMPOO == initial_shampoo - 5
        assert full_station.OSMOS == initial_osmos - 30
        assert full_station.WAX == initial_wax - 3
        assert full_station.total_washes == 1

    def test_start_wash_standard_cash_success(self, full_station):
        """Тест успешного запуска Стандарт за наличные"""
        initial_cash = full_station.cash_box
        
        result = full_station.start_wash_session(
            mode=WashMode.STANDARD,
            payment_type=PaymentType.CASH,
            cash_amount=500.0
        )
        
        assert result is None
        assert full_station.cash_box == initial_cash + 500
        assert full_station.total_revenue == 500

    @pytest.mark.parametrize("mode", [
        WashMode.EXPRESS,
        WashMode.STANDARD,
        WashMode.PREMIUM
        ])
    def test_start_wash_insufficient_resources(self, station, user, mode):
        """Тест: запуск при недостатке ресурсов"""
        station.WATER = 0.0
        station.SHAMPOO = 0.0
        station.OSMOS = 0.0
        station.WAX = 0.0
        
        result = station.start_wash_session(
            mode=mode,
            payment_type=PaymentType.APP,
            user=user
        )
        
        assert len(station.error_history_log) > 0
        assert result is None

    def test_start_wash_box_busy(self, full_station, user):
        """Тест: запуск при занятом боксе"""
        full_station.box_status = BoxStatus.BUSY
        
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )
        
        assert len(full_station.error_history_log) > 0
        assert result is None

    def test_start_wash_insufficient_balance(self, full_station, poor_user):
        """Тест: недостаток средств на балансе"""
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=poor_user
        )
        
        assert len(full_station.error_history_log) > 0
        assert result is None

    def test_start_wash_insufficient_cash(self, full_station):
        """Тест: недостаток наличных"""
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.CASH,
            cash_amount=100.0
        )
        
        assert len(full_station.error_history_log) > 0
        assert result is None

    # ============================================
    # 8. ИНТЕГРАЦИОННЫЕ ТЕСТЫ
    # ============================================

    def test_full_wash_cycle(self, full_station, user):
        """Тест полного цикла мойки"""
        initial_balance = user.balance
        initial_water = full_station.WATER
        
        full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )
        
        assert full_station.WATER == initial_water - 50
        assert user.balance == initial_balance - 300
        assert full_station.total_revenue == 300
        assert full_station.total_washes == 1
        assert full_station.box_status == BoxStatus.FREE

    def test_multiple_washes(self, full_station, user):
        """Тест нескольких моек подряд"""
        full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )
        assert full_station.total_washes == 1
        
        full_station.start_wash_session(
            mode=WashMode.STANDARD,
            payment_type=PaymentType.APP,
            user=user
        )
        assert full_station.total_washes == 2
        
        assert full_station.total_revenue == 300 + 500

    # ============================================
    # 9. ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ
    # ============================================

    def test_exactly_enough_resources(self, station, user):
        """Тест: ровно столько ресурсов, сколько нужно"""
        station.WATER = 50.0
        station.SHAMPOO = 2.0
        
        station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )
        
        assert station.WATER == 0.0
        assert station.SHAMPOO == 0.0

    def test_exactly_enough_balance(self, full_station, user):
        """Тест: ровно столько денег, сколько нужно"""
        user.balance = 300.0
        
        full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )
        
        assert user.balance == 0.0

    # ============================================
    # 10. ТЕСТЫ СТАТИСТИКИ
    # ============================================

    def test_get_statistics(self, full_station):
        """Тест получения статистики"""
        stats = full_station.get_statistics()
        
        assert stats["box_number"] == 1
        assert stats["address"] == "ул. Тестовая, 1"
        assert stats["cash_box"] == 0.0
        assert stats["total_revenue"] == 0.0
        assert stats["total_washes"] == 0
        assert "water" in stats["resources"]
        assert "osmos" in stats["resources"]

    # ============================================
    # 11. ТЕСТЫ БЕЗОПАСНОСТИ
    # ============================================

    def test_cannot_wash_without_user(self, full_station):
        """Тест: нельзя запустить мойку без пользователя"""
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=None
        )
        
        assert len(full_station.error_history_log) > 0
        assert result is None

    def test_cannot_wash_with_negative_cash(self, full_station):
        """Тест: нельзя запустить с отрицательными наличными"""
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.CASH,
            cash_amount=-100.0
        )
        
        assert len(full_station.error_history_log) > 0
        assert result is None

    def test_cannot_wash_when_maintenance(self, full_station, user):
        """Тест: нельзя запустить в режиме обслуживания"""
        full_station.box_status = BoxStatus.MAINTENANCE
        
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )
        
        assert len(full_station.error_history_log) > 0
        assert result is None
