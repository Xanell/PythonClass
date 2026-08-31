from src.config.Enums import BoxStatus, ResourceType, WashMode, PaymentType
import datetime
from src.core.AbstractCarWash import AbstractCarWash
from src.User_Class import User

# Основной класс
class RobotWashStation(AbstractCarWash):

    def __init__(self, id: int, adress: str, box_number: int):
        super().__init__(id, adress, box_number)
        
        # Ресурсы (cons)
        self.MAX_WATER = 500.0
        self.MAX_OSMOS = 50.0
        self.MAX_WAX = 5.0
        self.MAX_SHAMPOO = 10.0
        
        # Режимы (расход)

        # Экспресс (cons)
        self.EXPRESS_WATER_CONSUMPTION = 50     # литры
        self.EXPRESS_SHAMPOO_CONSUMPTION = 2    # литры
        
        # Стандарт (cons)
        self.STANDART_WATER_CONSUMPTION = 70    # литры
        self.STANDART_SHAMPOO_CONSUMPTION = 3   # литры
        self.STANDART_OSMOS_CONSUMPTION = 20    # литры
        
        # Премиум (cons)
        self.PREMIUM_WATER_CONSUMPTION = 120    # литры
        self.PREMIUM_SHAMPOO_CONSUMPTION = 5    # литры
        self.PREMIUM_OSMOS_CONSUMPTION = 30     # литры
        self.PREMIUM_WAX_CONSUMPTION = 3        # литры

        # Цены
        self.EXPRESS_WASH = 300     # рубли
        self.STANDART_WASH = 500    # рубли
        self.PREMIUM_WASH = 1000    # рубли
        

    # Вспомогательные методы

    # абстрактный метод на запись ошибок
    def get_error_history_log(self):
        return self.error_history_log

    # Методы для проверок

    # Хватит ли ресурсов для Экспресса?
    def check_express(self):

        if self.WATER >= self.EXPRESS_WATER and self.SHAMPOO >= self.EXPRESS_SHAMPOO:
            return True
        else:
            error_msg = (f"Не хватает ресурсов для мойки, вызовите техника!")
            self.add_error_history_log(error_msg)
    
    # Хватит ли ресурсов для Стандарта?
    def check_standard(self):

        if (self.WATER >= self.STANDART_WATER and 
                self.SHAMPOO >= self.STANDART_SHAMPOO and 
                self.OSMOS >= self.STANDART_OSMOS):
            return True
        else:
            error_msg = (f"Не хватает ресурсов для мойки, вызовите техника!")
            self.add_error_history_log(error_msg)

    # Хватит ли ресурсов для Премиума?
    def check_premium(self):

        if (self.WATER >= self.PREMIUM_WATER and 
                self.SHAMPOO >= self.PREMIUM_SHAMPOO and 
                self.OSMOS >= self.PREMIUM_OSMOS and 
                self.WAX >= self.PREMIUM_WAX):
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
    
    # Полная заправка всех ресурсов
    def full_refill(self):

        self.wash_status = BoxStatus.MAINTENANCE
        
        self.WATER = 500.0
        self.OSMOS = 50.0
        self.WAX = 5.0
        self.SHAMPOO = 10.0
        
        self.wash_status = BoxStatus.FREE
        print("Все ресурсы заправлены до максимума!")

    def get_resources(self):
        return {
            "current_water" : round(self.WATER, 2),
            "current_osmos" : round(self.OSMOS, 2),
            "current_wax": round(self.WAX, 2),
            "current_shampoo": round(self.SHAMPOO, 2)
        }

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

    # Запуск мойки
    def start_wash_session(self, mode: WashMode, payment_type: PaymentType, user: User = None, cash_amount: float = 0.0) -> dict:
        
        # Проверка статуса
        if self.box_status != BoxStatus.FREE:
            raise ValueError (f"Бокс № {self.box_number} недоступен!")
        
        
        # Получение параметров режима
        if mode == WashMode.EXPRESS:
            mode_name = "Экспресс"
        elif mode == WashMode.STANDARD:
            mode_name = "Стандарт"
        elif mode == WashMode.PREMIUM:
            mode_name = "Премиум"
        else:
            return {"Сообщение": "Неизвестный режим!"}
        
        # Проверка ресурсов
        if not self.check_resources(mode):
            # Если Премиум недоступен - предлагаем Экспресс
            if mode == WashMode.PREMIUM and self.check_express():
                return {"Сообщение": "Недостаточно ресурсов для Премиум. Доступен Экспресс"}
            else:
                return {"Сообщение": "Недостаточно ресурсов для мойки! Обратитесь к технику!"}
        
        # Запуск цикла мойки
        self.wash_status = BoxStatus.BUSY
        self.log_action("Сообщение", f"Начало {mode_name} мойки")
        
        # Списываем ресурсы
        if mode == WashMode.EXPRESS:
            self.WATER -= self.EXPRESS_WATER
            self.SHAMPOO -= self.EXPRESS_SHAMPOO
            self.cash += self.EXPRESS_WASH
        elif mode == WashMode.STANDARD:
            self.WATER -= self.STANDART_WATER
            self.SHAMPOO -= self.STANDART_SHAMPOO
            self.OSMOS -= self.STANDART_WATER
            self.cash += self.STANDART_WASH
        elif mode == WashMode.PREMIUM:
            self.WATER -= self.PREMIUM_WATER
            self.SHAMPOO -= self.PREMIUM_SHAMPOO
            self.OSMOS -= self.PREMIUM_OSMOS
            self.WAX -= self.PREMIUM_WAX
            self.cash += self.PREMIUM_WASH
        
        # Обновляем статистику
        self.total_washes += 1

        # Переводим статус
        self.wash_status = BoxStatus.FREE


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

