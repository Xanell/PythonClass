from Enums import BoxStatus, ResourceType, WashMode
import datetime
from AbstractCarWash import AbstractCarWash

# Основной класс
class RobotWashStation(AbstractCarWash):
    
    def __init__(self, id: int, adress: str, box_number: int):
        super().__init__(id, adress, box_number)

        # Инфо о станции
        self.wash_status = WashStatus.FREE
        
        # Ресурсы
        self.water = 500.0      # литры   # конс
        self.osmos = 50.0       # литры
        self.wax = 5.0          # литры
        self.shampoo = 10.0     # литры
        
        # Режимы

        # Экспресс
        self.express_water = 50
        self.express_shampoo = 2
        
        # Стандарт
        self.standard_water = 70
        self.standard_shampoo = 3
        self.standard_osmos = 20
        
        # Премиум
        self.premium_water = 120
        self.premium_shampoo = 5
        self.premium_osmos = 30
        self.premium_wax = 3
        
        # Статистика
        self.total_washes = 0
        
        # История операций
        self.history = []
    

    # Вспомогательные методы

    # Запись в историю
    def log_action(self, action: str, details: str):

        self.history.append({
            'time': datetime.datetime.now(),
            'action': action,
            'details': details
        })

    # Вывод истории операций
    def show_history(self):

        for record in self.history:
            date_time = datetime.datetime.now()
            print(f"   [{date_time}] {record['action']}: {record['details']}")

    # Методы для проверок

    # Хватит ли ресурсов для Экспресса?
    def check_express(self):

        return self.water >= self.express_water and self.shampoo >= self.express_shampoo

    # Хватит ли ресурсов для Стандарта?
    def check_standard(self):

        return (self.water >= self.standard_water and 
                self.shampoo >= self.standard_shampoo and 
                self.osmos >= self.standard_osmos)

    # Хватит ли ресурсов для Премиума?
    def check_premium(self):

        return (self.water >= self.premium_water and 
                self.shampoo >= self.premium_shampoo and 
                self.osmos >= self.premium_osmos and 
                self.wax >= self.premium_wax)

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

        self.wash_status = WashStatus.MAINTENANCE
        
        self.water = 500.0
        self.osmos = 50.0
        self.wax = 5.0
        self.shampoo = 10.0
        
        self.wash_status = WashStatus.IDLE
        self.log_action("Сообщение", "Все ресурсы заправлены")
        print("Все ресурсы заправлены до максимума!")

    # Получить текущее значение ресурса
    def get_resource(self, resource: ResourceType) -> float:

        if resource == ResourceType.WATER:
            return self.water
        elif resource == ResourceType.OSMOS:
            return self.osmos
        elif resource == ResourceType.WAX:
            return self.wax
        elif resource == ResourceType.SHAMPOO:
            return self.shampoo
        return 0.0

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
        current = self.get_resource(resource)
        if current + amount > max_capacity[resource]:
            raise ValueError(f"Нельзя долить больше {max_capacity[resource]}!")
        
        # Доливаем
        if resource == ResourceType.WATER:
            self.water += amount
        elif resource == ResourceType.OSMOS:
            self.osmos += amount
        elif resource == ResourceType.WAX:
            self.wax += amount
        elif resource == ResourceType.SHAMPOO:
            self.shampoo += amount
        
        self.log_action("Сообщение", f"Ресурс {resource.value} заправлен на {amount} л.")

    # Показать все ресурсы
    def show_resources(self):

        print(f"Вода: {self.water} л")
        print(f"Осмос: {self.osmos} л")
        print(f"Воск: {self.wax} л")
        print(f"Шампунь: {self.shampoo} л")
    

    # Методы для клиента =======================

    # Запуск мойки
    def start_wash(self, mode: WashMode) -> dict:
        
        # Проверка статуса
        if self.wash_status == WashStatus.MAINTENANCE:
            return {"Сообщение": "Станция на обслуживании!"}
        if self.wash_status == WashStatus.BUSY:
            return {"Сообщение": "Станция занята!"}
        
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
        self.wash_status = WashStatus.BUSY
        self.log_action("Сообщение", f"Начало {mode_name} мойки")
        
        # Списываем ресурсы
        if mode == WashMode.EXPRESS:
            self.water -= self.express_water
            self.shampoo -= self.express_shampoo
        elif mode == WashMode.STANDARD:
            self.water -= self.standard_water
            self.shampoo -= self.standard_shampoo
            self.osmos -= self.standard_osmos
        elif mode == WashMode.PREMIUM:
            self.water -= self.premium_water
            self.shampoo -= self.premium_shampoo
            self.osmos -= self.premium_osmos
            self.wax -= self.premium_wax
        
        # Обновляем статистику
        self.total_washes += 1

        # Переводим статус
        self.wash_status = WashStatus.IDLE

        # Запись в историю
        self.log_action("Сообщение", "Мойка завершена")
        
    # Собрать статистику станции
    def get_statistics(self) -> dict:

        return {
            "Номер станции": self.station_id,
            "Адрес": self.location,
            "Всего моек за день": self.total_washes,
            "Остаток воды": self.water,
            "Остаток осмоса": self.osmos,
            "Остаток воска": self.wax,
            "Остаток шампуня": self.shampoo,
            "Записей в истории": len(self.history)
        }

    # Вывести статистику
    def print_statistics(self):

        stats = self.get_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")

'''
station = RobotWashStation(1, "д. Юркино, Солнечная ул. 7")


station.wash_status = WashStatus.MAINTENANCE
print("Мойка на обслуживании!")
station.full_refill()
station.show_resources()

station.wash_status = WashStatus.IDLE
print ("Мойка свободна")

print("Доступные режимы:")
print(f"Экспресс - мойка")
print(f"Стандарт - мойка")
print(f"Премиум - мойка")


print("Клиент 1: Иван, Экпресс - мойка")
result = station.start_wash(WashMode.EXPRESS)

print("Клиент 2 : Пётр, Стандартная мойка")
result = station.start_wash(WashMode.STANDARD)

print("Клиент 3 : Мария, Премиум мойка")
result = station.start_wash(WashMode.PREMIUM)

print("Остатки ресурсов после моек")
station.show_resources()
'''
'''
station.refill_resource(ResourceType.WATER, 600)
'''
'''
station.full_refill()
station.show_resources()

station.show_history()

station.print_statistics()
'''
