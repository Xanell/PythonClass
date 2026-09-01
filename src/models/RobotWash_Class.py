from src.config.Enums import BoxStatus, ResourceType, WashMode, PaymentType
from src.core.AbstractCarWash import AbstractCarWash
from src.User_Class import User

# Основной класс
class RobotWashStation(AbstractCarWash):

    def __init__(self, id: int, adress: str, box_number: int):
        super().__init__(id, adress, box_number)

        # Ресурсы
        self.WATER = 400.0
        self.OSMOS = 40.0
        self.WAX = 4.0
        self.SHAMPOO = 8.0
        
        # Максимальные значения ресурсов
        self.MAX_WATER = 500.0
        self.MAX_OSMOS = 50.0
        self.MAX_WAX = 5.0
        self.MAX_SHAMPOO = 10.0
        
        # Режимы (расход)

        # Экспресс
        self.EXPRESS_WATER_CONSUMPTION = 50     # литры
        self.EXPRESS_SHAMPOO_CONSUMPTION = 2    # литры
        
        # Стандарт
        self.STANDART_WATER_CONSUMPTION = 70    # литры
        self.STANDART_SHAMPOO_CONSUMPTION = 3   # литры
        self.STANDART_OSMOS_CONSUMPTION = 20    # литры
        
        # Премиум
        self.PREMIUM_WATER_CONSUMPTION = 120    # литры
        self.PREMIUM_SHAMPOO_CONSUMPTION = 5    # литры
        self.PREMIUM_OSMOS_CONSUMPTION = 30     # литры
        self.PREMIUM_WAX_CONSUMPTION = 3        # литры

        # Цены
        self.EXPRESS_WASH = 300     # рубли
        self.STANDART_WASH = 500    # рубли
        self.PREMIUM_WASH = 1000    # рубли
        

    # Вспомогательные методы

    # Реализованный в родительском метод хранения ошибок
    def get_error_history_log(self):
        return self.error_history_log

    # Методы для проверок

    # Хватит ли ресурсов для Экспресса?
    def check_express(self):

        if self.WATER >= self.EXPRESS_WATER_CONSUMPTION and self.SHAMPOO >= self.EXPRESS_SHAMPOO_CONSUMPTION:
            return True
        else:
            error_msg = (f"Не хватает ресурсов для мойки, вызовите техника!")
            self.add_error_history_log(error_msg)
            return False
    
    # Хватит ли ресурсов для Стандарта?
    def check_standard(self):

        if (self.WATER >= self.STANDART_WATER_CONSUMPTION and 
                self.SHAMPOO >= self.STANDART_SHAMPOO_CONSUMPTION and 
                self.OSMOS >= self.STANDART_OSMOS_CONSUMPTION):
            return True
        else:
            error_msg = (f"Не хватает ресурсов для мойки, вызовите техника!")
            self.add_error_history_log(error_msg)

    # Хватит ли ресурсов для Премиума?
    def check_premium(self):

        if (self.WATER >= self.PREMIUM_WATER_CONSUMPTION and 
                self.SHAMPOO >= self.PREMIUM_SHAMPOO_CONSUMPTION and 
                self.OSMOS >= self.PREMIUM_OSMOS_CONSUMPTION and 
                self.WAX >= self.PREMIUM_WAX_CONSUMPTION):
            return True
        else:
            error_msg = (f"Не хватает ресурсов для мойки, вызовите техника!")
            self.add_error_history_log(error_msg)

    # Универсальная проверка ресурсов
    def check_resources(self, mode: WashMode) -> bool:
        
        if mode == WashMode.EXPRESS:
            return self.check_express()
        elif mode == WashMode.STANDARD:
            return self.check_standard()
        elif mode == WashMode.PREMIUM:
            return self.check_premium()
        return False
    

    # Методы для техника

    # Получить значения всех ресурсов
    def get_resources(self):
        return {
            "current_water" : round(self.WATER, 2),
            "current_osmos" : round(self.OSMOS, 2),
            "current_wax": round(self.WAX, 2),
            "current_shampoo": round(self.SHAMPOO, 2)
        }
    
    # Полная заправка всех ресурсов
    def full_refill(self):

        self.box_status = BoxStatus.MAINTENANCE
        
        self.WATER = self.MAX_WATER
        self.OSMOS = self.MAX_OSMOS
        self.WAX = self.MAX_WAX
        self.SHAMPOO = self.MAX_SHAMPOO
        
        self.wash_status = BoxStatus.FREE
        print("Все ресурсы заправлены до максимума!")


    # Получить текущее значение ресурса
    def get_current_resources(self, resource: ResourceType) -> float:

        if resource == ResourceType.WATER:
            return self.WATER
        elif resource == ResourceType.OSMOS:
            return self.OSMOS
        elif resource == ResourceType.WAX:
            return self.WAX
        elif resource == ResourceType.SHAMPOO:
            return self.SHAMPOO
        else:
            error_msg = (f"Такого ресурса нет!")
            self.add_error_history_log(error_msg)
        return error_msg

    # Долив конкретного ресурса
    def refill_resource(self, resource: ResourceType, amount: float):

        # Максимальная ёмкость
        max_capacity = {
            ResourceType.WATER: 500.0,
            ResourceType.OSMOS: 50.0,
            ResourceType.WAX: 5.0,
            ResourceType.SHAMPOO: 10.0
        }
        
        # Проверяем, не превысит ли лимит, падаем с ошибкой
        current = self.get_resources(resource)
        if current + amount > max_capacity[resource]:
            error_msg = (f"Нельзя долить больше {max_capacity[resource]}!")
            self.add_error_history_log(error_msg)

        # Доливаем
        if resource == ResourceType.WATER:
            self.WATER += amount
        elif resource == ResourceType.OSMOS:
            self.OSMOS += amount
        elif resource == ResourceType.WAX:
            self.WAX += amount
        elif resource == ResourceType.SHAMPOO:
            self.SHAMPOO += amount

    # Методы для клиента =======================

    # Получить ценник тарифа
    def get_tariff(self, mode: WashMode):
        if mode == WashMode.EXPRESS:
            return self.EXPRESS_WASH
        if mode == WashMode.STANDARD:
            return self.STANDART_WASH
        if mode == WashMode.PREMIUM:
            return self.PREMIUM_WASH

    # Метод проверки баланса кошелька
    def validate_app_payment(self, user: User, tariff: float) -> None :
        if user is None:
            raise ValueError("Для оплаты через приложение необходимо указать пользователя")
        
        if user.balance < tariff:
            raise ValueError(
                f"Недостаточно средств на балансе: нужно {tariff} руб., "
                f"На на балансе {user.balance} руб."
            )
        
    # Метод проверки оплаты наличными
    def validate_cash_payment(self, cash_amount: float) -> None :
        if cash_amount <= 0:
            raise ValueError("Внесённая сумма должна быть положительной")

    # Запуск мойки
    def start_wash_session(self, mode: WashMode, payment_type: PaymentType, user: User = None, cash_amount: float = 0.0) -> dict:
        try:
            # Проверка статуса
            if self.box_status != BoxStatus.FREE:
                raise ValueError (f"Бокс № {self.box_number} недоступен!")
            
            # Проверка ресурсов
            self.check_resources(mode)
            tariff = self.get_tariff(mode)

            # Предварительные проверки в зависимости от типа оплаты
            if payment_type == PaymentType.APP:
                self.validate_app_payment(user, tariff)
            elif payment_type == PaymentType.CASH:
                self.validate_cash_payment(cash_amount)
            else:
                raise ValueError("Неизвестный тип оплаты")
    
            # Запуск цикла мойки
            self.box_status = BoxStatus.BUSY
            
            # Списываем ресурсы
            if mode == WashMode.EXPRESS:
                self.WATER -= self.EXPRESS_WATER_CONSUMPTION
                self.SHAMPOO -= self.EXPRESS_SHAMPOO_CONSUMPTION
            elif mode == WashMode.STANDARD:
                self.WATER -= self.STANDART_WATER_CONSUMPTION
                self.SHAMPOO -= self.STANDART_SHAMPOO_CONSUMPTION
                self.OSMOS -= self.STANDART_OSMOS_CONSUMPTION
            elif mode == WashMode.PREMIUM:
                self.WATER -= self.PREMIUM_WATER_CONSUMPTION
                self.SHAMPOO -= self.PREMIUM_SHAMPOO_CONSUMPTION
                self.OSMOS -= self.PREMIUM_OSMOS_CONSUMPTION
                self.WAX -= self.PREMIUM_WAX_CONSUMPTION

            # Реализован в родительском метод оплаты (списывем деньги, кладем в общую выручку)
            if payment_type == PaymentType.APP:
                self.process_payment(amount=tariff, payment_type=PaymentType.APP, user=user)
            else:
                self.process_payment(amount=tariff, payment_type=PaymentType.CASH, user=None)
            
            # Переводим статус
            self.wash_status = BoxStatus.FREE

        except ValueError as error:
            self.add_error_history_log(error)


'''
station = RobotWashStation(1, "д. Юркино, Солнечная ул. 7", 2)


station.wash_status = BoxStatus.MAINTENANCE
print("Мойка на обслуживании!")
station.full_refill()
station.show_resources()

station.wash_status = BoxStatus.FREE
print ("Мойка свободна")

print("Доступные режимы:")
print(f"Экспресс - мойка")
print(f"Стандарт - мойка")
print(f"Премиум - мойка")


print("Клиент 1: Иван, Экcпресс - мойка")
result = station.start_wash(WashMode.EXPRESS)

print("Клиент 2 : Пётр, Стандартная мойка")
result = station.start_wash(WashMode.STANDARD)

print("Клиент 3 : Мария, Премиум мойка")
result = station.start_wash(WashMode.PREMIUM)

print("Остатки ресурсов после моек")
station.show_resources()
'''



'''
station.refill_resource(ResourceType.WATER, 10)
'''


'''
station.full_refill()
station.show_resources()

station.show_history()

station.print_statistics()

station.get_error_history_log()
'''

