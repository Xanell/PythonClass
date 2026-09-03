from src.CarWash.Utils import BoxStatus, ResourceType, WashMode, PaymentType
from src.CarWash.Boxes import AbstractCarWash
from src.CarWash.User import User

# Основной класс
class RobotWashStation(AbstractCarWash):

    def __init__(self, id: int, address: str, box_number: int, curr_water: float = None, curr_osmos: float = None, curr_wax: float = None, curr_shampoo: float = None):
        super().__init__(id, address, box_number)
        
        # Максимальные значения ресурсов
        self.MAX_WATER = 500.0      # литры
        self.MAX_OSMOS = 50.0       # литры
        self.MAX_WAX = 5.0          # литры
        self.MAX_SHAMPOO = 10.0     # литры
        
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

        # Время мойки
        self.EXPRESS_WASH_TIME = 120    # минуты
        self.STANDART_WASH_TIME = 240   # минуты
        self.PREMIUM_WASH_TIME =  360   # минуты

        # Значения ресурсов по умолчанию
        self.curr_water = curr_water if curr_water is not None else self.MAX_WATER
        self.curr_osmos = curr_osmos if curr_osmos is not None else self.MAX_OSMOS
        self.curr_wax = curr_wax if curr_wax is not None else self.MAX_WAX
        self.curr_shampoo = curr_shampoo if curr_shampoo is not None else self.MAX_SHAMPOO

    # Методы для проверок

    # Хватит ли ресурсов для Экспресса?
    def check_express(self):

        if self.curr_water >= self.EXPRESS_WATER_CONSUMPTION and self.curr_shampoo >= self.EXPRESS_SHAMPOO_CONSUMPTION:
            return True
        else:
            raise ValueError(f"Не хватает ресурсов для мойки, вызовите техника!")
    
    # Хватит ли ресурсов для Стандарта?
    def check_standard(self):

        if (self.curr_water >= self.STANDART_WATER_CONSUMPTION and 
                self.curr_shampoo >= self.STANDART_SHAMPOO_CONSUMPTION and 
                self.curr_osmos >= self.STANDART_OSMOS_CONSUMPTION):
            return True
        else:
            raise ValueError(f"Не хватает ресурсов для мойки, вызовите техника!")

    # Хватит ли ресурсов для Премиума?
    def check_premium(self):

        if (self.curr_water >= self.PREMIUM_WATER_CONSUMPTION and 
                self.curr_shampoo >= self.PREMIUM_SHAMPOO_CONSUMPTION and 
                self.curr_osmos >= self.PREMIUM_OSMOS_CONSUMPTION and 
                self.curr_wax >= self.PREMIUM_WAX_CONSUMPTION):
            return True
        else:
            raise ValueError(f"Не хватает ресурсов для мойки, вызовите техника!")

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
            "current_water" : round(self.curr_water, 2),
            "current_osmos" : round(self.curr_osmos, 2),
            "current_wax": round(self.curr_wax, 2),
            "current_shampoo": round(self.curr_shampoo, 2)
        }
    
    # Полная заправка всех ресурсов
    def full_refill(self):

        self.box_status = BoxStatus.MAINTENANCE
        
        self.curr_water = 500.0
        self.curr_osmos = 50.0
        self.curr_wax = 5.0
        self.curr_shampoo = 10.0
        
        self.box_status = BoxStatus.FREE
        return self.get_resources()


    # Получить текущее значение ресурса
    def get_current_resources(self, resource: ResourceType) -> float:

        if resource == ResourceType.WATER:
            return self.curr_water
        elif resource == ResourceType.OSMOS:
            return self.curr_osmos
        elif resource == ResourceType.WAX:
            return self.curr_wax
        elif resource == ResourceType.SHAMPOO:
            return self.curr_shampoo
        else:
            raise ValueError("Такого ресурса нету!")
        
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
        current = self.get_current_resources(resource)
        if current + amount > max_capacity[resource]:
            error_msg = (f"Нельзя долить больше {max_capacity[resource]}!")
            self.add_error_history_log(error_msg) # метод логирования ошибок в родителе
            return self.get_error_history_log()

        # Доливаем
        if resource == ResourceType.WATER:
            self.curr_water += amount
        elif resource == ResourceType.OSMOS:
            self.curr_osmos += amount
        elif resource == ResourceType.WAX:
            self.curr_wax += amount
        elif resource == ResourceType.SHAMPOO:
            self.curr_shampoo += amount

        return self.get_resources()

    # Методы для клиента

    # Метод определения тарифа и времени в зависимости от выбраного тарифа
    def get_tariff_and_time(self, mode: WashMode) -> tuple[float, float]:
        if mode == WashMode.EXPRESS:
            return self.EXPRESS_WASH, self.EXPRESS_WASH_TIME
        elif mode == WashMode.STANDARD:
            return self.STANDART_WASH, self.STANDART_WASH_TIME
        elif mode == WashMode.PREMIUM:
            return self.PREMIUM_WASH, self.PREMIUM_WASH_TIME
        else:
            return 0.0, 0.0
        
    # Метод списывания ресурсов
    def consumption_resources(self, mode: WashMode):
        if mode == WashMode.EXPRESS:
            self.curr_water -= self.EXPRESS_WATER_CONSUMPTION
            self.curr_shampoo -= self.EXPRESS_SHAMPOO_CONSUMPTION
        elif mode == WashMode.STANDARD:
            self.curr_water -= self.STANDART_WATER_CONSUMPTION
            self.curr_shampoo -= self.STANDART_SHAMPOO_CONSUMPTION
            self.curr_osmos -= self.STANDART_OSMOS_CONSUMPTION 
        elif mode == WashMode.PREMIUM:
            self.curr_water -= self.PREMIUM_WATER_CONSUMPTION
            self.curr_shampoo -= self.PREMIUM_SHAMPOO_CONSUMPTION
            self.curr_osmos -= self.PREMIUM_OSMOS_CONSUMPTION
            self.curr_wax -= self.PREMIUM_WAX_CONSUMPTION

    # Метод проверки баланса кошелька
    def validate_app_payment(self, user: User, tariff: float) -> None :
        if user is None:
            raise ValueError("Для оплаты через приложение необходимо указать пользователя")
        
        if user.balance < tariff:
            raise ValueError(
                f"Недостаточно средств на балансе: нужно {tariff} руб., "
                f"На балансе {user.balance} руб."
            )
        
    # Метод проверки оплаты наличными
    def validate_cash_payment(self, cash_amount: float, tariff: float) -> None :
        if cash_amount <= 0:
            raise ValueError("Внесённая сумма должна быть положительной")
        if cash_amount < tariff:
            raise ValueError(f"Недостаточно средств для начала мойки! Внесено {cash_amount} руб., требуется {tariff} руб.")

    # Запуск мойки
    def start_wash_session(self, mode: WashMode, payment_type: PaymentType, user: User = None, cash_amount: float = 0.0) -> dict:

        try:
            # Проверка статуса
            if self.box_status != BoxStatus.FREE:
                raise ValueError (f"Бокс № {self.box_number} недоступен!")
            
            # Проверка ресурсов, тарифа, времени
            self.check_resources(mode)
            tariff, time_passed = self.get_tariff_and_time(mode)

            # Предварительные проверки в зависимости от типа оплаты
            if payment_type == PaymentType.APP:
                self.validate_app_payment(user, tariff)
            elif payment_type == PaymentType.CASH:
                self.validate_cash_payment(cash_amount, tariff)
            else:
                raise ValueError("Неизвестный тип оплаты")
    
            # Запуск цикла мойки
            self.box_status = BoxStatus.BUSY
            
            # Списываем ресурсы
            self.consumption_resources(mode)

            # Реализован в родительском метод оплаты (списывем деньги, кладем в общую выручку)
            if payment_type == PaymentType.APP:
                self.process_payment(tariff, PaymentType.APP, user)
            else:
                self.process_payment(tariff, PaymentType.CASH, user=None)
            self.add_pay_history_log(tariff, time_passed) # метод логирования оплаты в родителе
            
            # Переводим статус
            self.box_status = BoxStatus.FREE

            return {
                "message": "Мойка успешно завершена", 
                "box_number": self.box_number, 
                "status": self.box_status,
                "time": time_passed,
                "total_price": tariff, 
                "remaining_balance": round(user.balance, 2) if user else None
            }
        
        except ValueError as error:
            self.add_error_history_log(error)
            return{
                "message": "Произошла ошибка",
                "box_number": self.box_number,
                "status": self.box_status,
                "error": error,
            }

