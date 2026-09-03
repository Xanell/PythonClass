import pytest
import sys
import os

# Насторйка путей
tests_dir = os.path.dirname(__file__)
project_root = os.path.dirname(tests_dir)
sys.path.append(project_root)

from src.config.Enums import BoxStatus, ResourceType, WashMode, PaymentType
from src.models.RobotWash_Class import RobotWashStation
from src.User_Class import User


@pytest.fixture
def station():
    """Создает станцию с ресурсами по умолчанию"""
    return RobotWashStation(1, "ул. Тестовая, 1", 1)


@pytest.fixture
def station_with_custom_resources():
    """Создает станцию с кастомными ресурсами"""
    return RobotWashStation(
        id=1,
        address="ул. Тестовая, 1",
        box_number=1,
        curr_water=300.0,
        curr_osmos=30.0,
        curr_wax=2.0,
        curr_shampoo=5.0
    )


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

class TestRobotWashStationInit:
    """Тесты инициализации"""

    def test_init_default_resources(self, station):
        """Тест: инициализация с ресурсами по умолчанию"""
        assert station.car_wash_Id == 1
        assert station.box_number == 1
        assert station.box_status == BoxStatus.FREE

        assert station.curr_water == 500.0
        assert station.curr_osmos == 50.0
        assert station.curr_wax == 5.0
        assert station.curr_shampoo == 10.0

        assert station.MAX_WATER == 500.0
        assert station.MAX_OSMOS == 50.0
        assert station.MAX_WAX == 5.0
        assert station.MAX_SHAMPOO == 10.0

    def test_init_custom_resources(self, station_with_custom_resources):
        """Тест: инициализация с кастомными ресурсами"""
        station = station_with_custom_resources
        assert station.curr_water == 300.0
        assert station.curr_osmos == 30.0
        assert station.curr_wax == 2.0
        assert station.curr_shampoo == 5.0

    def test_init_consumption_values(self, station):
        """Тест: проверка значений расхода"""
        assert station.EXPRESS_WATER_CONSUMPTION == 50
        assert station.EXPRESS_SHAMPOO_CONSUMPTION == 2
        assert station.STANDART_WATER_CONSUMPTION == 70
        assert station.STANDART_SHAMPOO_CONSUMPTION == 3
        assert station.STANDART_OSMOS_CONSUMPTION == 20
        assert station.PREMIUM_WATER_CONSUMPTION == 120
        assert station.PREMIUM_SHAMPOO_CONSUMPTION == 5
        assert station.PREMIUM_OSMOS_CONSUMPTION == 30
        assert station.PREMIUM_WAX_CONSUMPTION == 3

    def test_init_prices(self, station):
        """Тест: проверка цен"""
        assert station.EXPRESS_WASH == 300
        assert station.STANDART_WASH == 500
        assert station.PREMIUM_WASH == 1000

    def test_init_wash_times(self, station):
        """Тест: проверка времени мойки"""
        assert station.EXPRESS_WASH_TIME == 120
        assert station.STANDART_WASH_TIME == 240
        assert station.PREMIUM_WASH_TIME == 360

    @pytest.mark.parametrize("id_value, address, box_number", [
        (1, "ул. Ленина, 1", 1),
        (2, "ул. Пушкина, 2", 2),
        (100, "пр. Мира, 100", 10),
        (5, "д. Юркино, Солнечная ул. 7", 3),
    ])
    def test_init_different_values(self, id_value, address, box_number):
        """Тест: создание с разными значениями"""
        station = RobotWashStation(id_value, address, box_number)
        assert station.car_wash_Id == id_value
        assert station.car_wash_address == address
        assert station.box_number == box_number


# ============================================
# 2. ТЕСТЫ ПРОВЕРКИ РЕСУРСОВ
# ============================================

class TestRobotWashStationCheckResources:
    """Тесты проверки ресурсов"""

    def test_check_express_success(self, full_station):
        """Тест: ресурсов достаточно для Экспресс"""
        assert full_station.check_express() is True

    def test_check_express_fail_water(self, station):
        """Тест: не хватает воды для Экспресс"""
        station.curr_water = 10.0
        with pytest.raises(ValueError) as exc:
            station.check_express()
        assert "Не хватает ресурсов" in str(exc.value)

    def test_check_express_fail_shampoo(self, station):
        """Тест: не хватает шампуня для Экспресс"""
        station.curr_shampoo = 0.0
        with pytest.raises(ValueError) as exc:
            station.check_express()
        assert "Не хватает ресурсов" in str(exc.value)

    def test_check_standard_success(self, full_station):
        """Тест: ресурсов достаточно для Стандарт"""
        assert full_station.check_standard() is True

    def test_check_standard_fail_osmos(self, station):
        """Тест: не хватает осмоса для Стандарт"""
        station.curr_osmos = 0.0
        with pytest.raises(ValueError) as exc:
            station.check_standard()
        assert "Не хватает ресурсов" in str(exc.value)

    def test_check_premium_success(self, full_station):
        """Тест: ресурсов достаточно для Премиум"""
        assert full_station.check_premium() is True

    def test_check_premium_fail_wax(self, station):
        """Тест: не хватает воска для Премиум"""
        station.curr_wax = 0.0
        with pytest.raises(ValueError) as exc:
            station.check_premium()
        assert "Не хватает ресурсов" in str(exc.value)

    @pytest.mark.parametrize("mode", [
        WashMode.EXPRESS,
        WashMode.STANDARD,
        WashMode.PREMIUM
    ])
    def test_check_resources_success(self, full_station, mode):
        """Тест: проверка ресурсов для всех режимов (успешно)"""
        assert full_station.check_resources(mode) is True

    @pytest.mark.parametrize("mode, resource_to_drain", [
        (WashMode.EXPRESS, "curr_water"),
        (WashMode.STANDARD, "curr_osmos"),
        (WashMode.PREMIUM, "curr_wax"),
    ])
    def test_check_resources_fail(self, station, mode, resource_to_drain):
        """Тест: проверка ресурсов для всех режимов (неуспешно)"""
        setattr(station, resource_to_drain, 0.0)
        with pytest.raises(ValueError):
            station.check_resources(mode)


# ============================================
# 3. ТЕСТЫ МЕТОДОВ ДЛЯ ТЕХНИКА
# ============================================

class TestRobotWashStationTechnician:
    """Тесты для техника"""

    def test_full_refill(self, station):
        """Тест полной заправки"""
        station.curr_water = 100.0
        station.curr_osmos = 10.0
        station.curr_wax = 1.0
        station.curr_shampoo = 2.0

        result = station.full_refill()

        assert station.curr_water == 500.0
        assert station.curr_osmos == 50.0
        assert station.curr_wax == 5.0
        assert station.curr_shampoo == 10.0
        assert station.box_status == BoxStatus.FREE
        assert result["current_water"] == 500.0

    def test_get_resources(self, station):
        """Тест получения всех ресурсов"""
        resources = station.get_resources()
        assert resources["current_water"] == 500.0
        assert resources["current_osmos"] == 50.0
        assert resources["current_wax"] == 5.0
        assert resources["current_shampoo"] == 10.0

    @pytest.mark.parametrize("resource, expected", [
        (ResourceType.WATER, 500.0),
        (ResourceType.OSMOS, 50.0),
        (ResourceType.WAX, 5.0),
        (ResourceType.SHAMPOO, 10.0),
    ])
    def test_get_current_resources(self, station, resource, expected):
        """Тест получения конкретного ресурса"""
        result = station.get_current_resources(resource)
        assert result == expected

    def test_get_current_resources_unknown(self, station):
        """Тест получения неизвестного ресурса"""
        class UnknownResource:
            pass
        with pytest.raises(ValueError) as exc:
            station.get_current_resources(UnknownResource())  # type: ignore
        assert "Такого ресурса нету" in str(exc.value)

    def test_refill_resource_success_water(self, station):
        """Тест успешного долива воды"""
        # Устанавливаем воду ниже максимума
        station.curr_water = 300.0
        initial = station.curr_water
        
        result = station.refill_resource(ResourceType.WATER, 50.0)
        
        # Проверяем, что результат - словарь
        assert isinstance(result, dict)
        assert station.curr_water == initial + 50.0
        assert result["current_water"] == initial + 50.0

    def test_refill_resource_success_osmos(self, station):
        """Тест успешного долива осмоса"""
        station.curr_osmos = 30.0
        initial = station.curr_osmos
        
        result = station.refill_resource(ResourceType.OSMOS, 10.0)
        
        assert isinstance(result, dict)
        assert station.curr_osmos == initial + 10.0
        assert result["current_osmos"] == initial + 10.0

    def test_refill_resource_success_wax(self, station):
        """Тест успешного долива воска"""
        station.curr_wax = 3.0
        initial = station.curr_wax
        
        result = station.refill_resource(ResourceType.WAX, 1.0)
        
        assert isinstance(result, dict)
        assert station.curr_wax == initial + 1.0
        assert result["current_wax"] == initial + 1.0

    def test_refill_resource_success_shampoo(self, station):
        """Тест успешного долива шампуня"""
        station.curr_shampoo = 6.0
        initial = station.curr_shampoo
        
        result = station.refill_resource(ResourceType.SHAMPOO, 2.0)
        
        assert isinstance(result, dict)
        assert station.curr_shampoo == initial + 2.0
        assert result["current_shampoo"] == initial + 2.0

    @pytest.mark.parametrize("resource, amount", [
        (ResourceType.WATER, 150.0),
        (ResourceType.OSMOS, 60.0),
        (ResourceType.WAX, 10.0),
        (ResourceType.SHAMPOO, 15.0),
    ])
    def test_refill_resource_overflow(self, station, resource, amount):
        """Тест: долив с превышением максимума"""
        result = station.refill_resource(resource, amount)
        # Проверяем, что вернулась ошибка (список ошибок)
        assert isinstance(result, list)
        assert len(result) > 0


# ============================================
# 4. ТЕСТЫ МЕТОДОВ ДЛЯ КЛИЕНТА
# ============================================

class TestRobotWashStationClient:
    """Тесты для клиента"""

    def test_get_tariff_and_time_express(self, station):
        """Тест получения тарифа и времени для Экспресс"""
        tariff, time = station.get_tariff_and_time(WashMode.EXPRESS)
        assert tariff == 300
        assert time == 120

    def test_get_tariff_and_time_standard(self, station):
        """Тест получения тарифа и времени для Стандарт"""
        tariff, time = station.get_tariff_and_time(WashMode.STANDARD)
        assert tariff == 500
        assert time == 240

    def test_get_tariff_and_time_premium(self, station):
        """Тест получения тарифа и времени для Премиум"""
        tariff, time = station.get_tariff_and_time(WashMode.PREMIUM)
        assert tariff == 1000
        assert time == 360

    def test_get_tariff_and_time_unknown(self, station):
        """Тест получения тарифа для неизвестного режима"""
        class UnknownMode:
            pass
        tariff, time = station.get_tariff_and_time(UnknownMode())  # type: ignore
        assert tariff == 0.0
        assert time == 0.0

    @pytest.mark.parametrize("mode, expected_tariff, expected_time", [
        (WashMode.EXPRESS, 300, 120),
        (WashMode.STANDARD, 500, 240),
        (WashMode.PREMIUM, 1000, 360),
    ])
    def test_get_tariff_and_time_parametrize(self, station, mode, expected_tariff, expected_time):
        """Тест: параметризованная проверка всех режимов"""
        tariff, time = station.get_tariff_and_time(mode)
        assert tariff == expected_tariff
        assert time == expected_time

    def test_consumption_resources_express(self, station):
        """Тест списания ресурсов для Экспресс"""
        initial_water = station.curr_water
        initial_shampoo = station.curr_shampoo
        station.consumption_resources(WashMode.EXPRESS)
        assert station.curr_water == initial_water - 50
        assert station.curr_shampoo == initial_shampoo - 2

    def test_consumption_resources_standard(self, station):
        """Тест списания ресурсов для Стандарт"""
        initial_water = station.curr_water
        initial_shampoo = station.curr_shampoo
        initial_osmos = station.curr_osmos
        station.consumption_resources(WashMode.STANDARD)
        assert station.curr_water == initial_water - 70
        assert station.curr_shampoo == initial_shampoo - 3
        assert station.curr_osmos == initial_osmos - 20

    def test_consumption_resources_premium(self, station):
        """Тест списания ресурсов для Премиум"""
        initial_water = station.curr_water
        initial_shampoo = station.curr_shampoo
        initial_osmos = station.curr_osmos
        initial_wax = station.curr_wax
        station.consumption_resources(WashMode.PREMIUM)
        assert station.curr_water == initial_water - 120
        assert station.curr_shampoo == initial_shampoo - 5
        assert station.curr_osmos == initial_osmos - 30
        assert station.curr_wax == initial_wax - 3

    def test_validate_app_payment_success(self, station, user):
        """Тест успешной проверки оплаты через приложение"""
        station.validate_app_payment(user, 300.0)

    def test_validate_app_payment_user_none(self, station):
        """Тест: оплата без пользователя"""
        with pytest.raises(ValueError) as exc:
            station.validate_app_payment(None, 300.0)
        assert "указать пользователя" in str(exc.value)

    def test_validate_app_payment_insufficient(self, station, poor_user):
        """Тест: недостаток средств на балансе"""
        with pytest.raises(ValueError) as exc:
            station.validate_app_payment(poor_user, 300.0)
        assert "Недостаточно средств" in str(exc.value)

    def test_validate_cash_payment_success(self, station):
        """Тест успешной проверки оплаты наличными"""
        station.validate_cash_payment(500.0, 300.0)

    @pytest.mark.parametrize("cash_amount, tariff, expected_error", [
        (0.0, 300.0, "положительной"),
        (-100.0, 300.0, "положительной"),
        (100.0, 300.0, "Недостаточно средств"),
    ])
    def test_validate_cash_payment_invalid(self, station, cash_amount, tariff, expected_error):
        """Тест: неверная сумма наличных"""
        with pytest.raises(ValueError) as exc:
            station.validate_cash_payment(cash_amount, tariff)
        assert expected_error in str(exc.value)


# ============================================
# 5. ТЕСТЫ ЗАПУСКА МОЙКИ
# ============================================

class TestRobotWashStationStartWash:
    """Тесты запуска мойки"""

    def test_start_wash_express_app_success(self, full_station, user):
        """Тест успешного запуска Экспресс через приложение"""
        initial_balance = user.balance
        initial_water = full_station.curr_water
        initial_shampoo = full_station.curr_shampoo

        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )

        assert result["message"] == "Мойка успешно завершена"
        assert result["box_number"] == 1
        assert result["status"] == BoxStatus.FREE
        assert result["time"] == 120
        assert result["total_price"] == 300

        assert user.balance == initial_balance - 300
        assert full_station.curr_water == initial_water - 50
        assert full_station.curr_shampoo == initial_shampoo - 2
        assert full_station.total_washes == 1

    def test_start_wash_standard_app_success(self, full_station, user):
        """Тест успешного запуска Стандарт через приложение"""
        initial_balance = user.balance
        initial_water = full_station.curr_water
        initial_shampoo = full_station.curr_shampoo
        initial_osmos = full_station.curr_osmos

        result = full_station.start_wash_session(
            mode=WashMode.STANDARD,
            payment_type=PaymentType.APP,
            user=user
        )

        assert result["message"] == "Мойка успешно завершена"
        assert result["time"] == 240
        assert result["total_price"] == 500

        assert user.balance == initial_balance - 500
        assert full_station.curr_water == initial_water - 70
        assert full_station.curr_shampoo == initial_shampoo - 3
        assert full_station.curr_osmos == initial_osmos - 20

    def test_start_wash_premium_app_success(self, full_station, user):
        """Тест успешного запуска Премиум через приложение"""
        initial_balance = user.balance
        initial_water = full_station.curr_water
        initial_shampoo = full_station.curr_shampoo
        initial_osmos = full_station.curr_osmos
        initial_wax = full_station.curr_wax

        result = full_station.start_wash_session(
            mode=WashMode.PREMIUM,
            payment_type=PaymentType.APP,
            user=user
        )

        assert result["message"] == "Мойка успешно завершена"
        assert result["time"] == 360
        assert result["total_price"] == 1000

        assert user.balance == initial_balance - 1000
        assert full_station.curr_water == initial_water - 120
        assert full_station.curr_shampoo == initial_shampoo - 5
        assert full_station.curr_osmos == initial_osmos - 30
        assert full_station.curr_wax == initial_wax - 3

    def test_start_wash_standard_cash_success(self, full_station):
        """Тест успешного запуска Стандарт за наличные"""
        initial_cash = full_station.cash_box

        result = full_station.start_wash_session(
            mode=WashMode.STANDARD,
            payment_type=PaymentType.CASH,
            cash_amount=500.0
        )

        assert result["message"] == "Мойка успешно завершена"
        assert full_station.cash_box == initial_cash + 500
        assert full_station.total_revenue == 500

    @pytest.mark.parametrize("mode", [
        WashMode.EXPRESS,
        WashMode.STANDARD,
        WashMode.PREMIUM
    ])
    def test_start_wash_insufficient_resources(self, station, user, mode):
        """Тест: запуск при недостатке ресурсов"""
        station.curr_water = 0.0
        station.curr_shampoo = 0.0
        station.curr_osmos = 0.0
        station.curr_wax = 0.0

        result = station.start_wash_session(
            mode=mode,
            payment_type=PaymentType.APP,
            user=user
        )

        assert result["message"] == "Произошла ошибка"
        assert "error" in result

    def test_start_wash_box_busy(self, full_station, user):
        """Тест: запуск при занятом боксе"""
        full_station.box_status = BoxStatus.BUSY

        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )

        assert result["message"] == "Произошла ошибка"
        assert "error" in result

    def test_start_wash_insufficient_balance(self, full_station, poor_user):
        """Тест: недостаток средств на балансе"""
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=poor_user
        )

        assert result["message"] == "Произошла ошибка"
        assert "error" in result

    def test_start_wash_insufficient_cash(self, full_station):
        """Тест: недостаток наличных"""
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.CASH,
            cash_amount=100.0
        )

        assert result["message"] == "Произошла ошибка"
        assert "error" in result

    def test_start_wash_unknown_payment(self, full_station, user):
        """Тест: неизвестный тип оплаты"""
        class UnknownPayment:
            pass

        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=UnknownPayment(),  # type: ignore
            user=user
        )

        assert result["message"] == "Произошла ошибка"
        assert "error" in result


# ============================================
# 6. ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================

class TestRobotWashStationIntegration:
    """Интеграционные тесты"""

    def test_full_wash_cycle(self, full_station, user):
        """Тест полного цикла мойки"""
        initial_balance = user.balance
        initial_water = full_station.curr_water

        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )

        assert result["message"] == "Мойка успешно завершена"
        assert full_station.curr_water == initial_water - 50
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
# 7. ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ
# ============================================

class TestRobotWashStationEdgeCases:
    """Тесты граничных случаев"""

    def test_exactly_enough_resources(self, station, user):
        """Тест: ровно столько ресурсов, сколько нужно"""
        station.curr_water = 50.0
        station.curr_shampoo = 2.0

        result = station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )

        assert result["message"] == "Мойка успешно завершена"
        assert station.curr_water == 0.0
        assert station.curr_shampoo == 0.0

    def test_exactly_enough_balance(self, full_station, user):
        """Тест: ровно столько денег, сколько нужно"""
        user.balance = 300.0

        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )

        assert result["message"] == "Мойка успешно завершена"
        assert user.balance == 0.0


# ============================================
# 8. ТЕСТЫ СТАТИСТИКИ И БЕЗОПАСНОСТИ
# ============================================

class TestRobotWashStationStatistics:
    """Тесты статистики"""

    def test_get_statistics(self, full_station):
        """Тест получения статистики"""
        stats = full_station.get_statistics()

        assert stats["box_number"] == 1
        assert stats["address"] == "ул. Тестовая, 1"
        assert stats["cash_box"] == 0.0
        assert stats["total_revenue"] == 0.0
        assert stats["total_washes"] == 0
        assert "current_water" in stats["resources"]
        assert "current_osmos" in stats["resources"]

    def test_error_history_log(self, station):
        """Тест лога ошибок"""
        station.add_error_history_log("Тестовая ошибка")
        assert len(station.error_history_log) == 1
        assert station.error_history_log[0] == "Тестовая ошибка"


class TestRobotWashStationSecurity:
    """Тесты безопасности"""

    def test_cannot_wash_without_user(self, full_station):
        """Тест: нельзя запустить мойку без пользователя"""
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=None
        )

        assert result["message"] == "Произошла ошибка"
        assert "error" in result

    def test_cannot_wash_with_negative_cash(self, full_station):
        """Тест: нельзя запустить с отрицательными наличными"""
        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.CASH,
            cash_amount=-100.0
        )

        assert result["message"] == "Произошла ошибка"
        assert "error" in result

    def test_cannot_wash_when_maintenance(self, full_station, user):
        """Тест: нельзя запустить в режиме обслуживания"""
        full_station.box_status = BoxStatus.MAINTENANCE

        result = full_station.start_wash_session(
            mode=WashMode.EXPRESS,
            payment_type=PaymentType.APP,
            user=user
        )

        assert result["message"] == "Произошла ошибка"
        assert "error" in result