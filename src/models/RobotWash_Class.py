from src.config.Enums import BoxStatus, ResourceType, WashMode
import datetime
from src.core.AbstractCarWash import AbstractCarWash

# Основной класс
class RobotWashStation(AbstractCarWash):

    def __init__(self, id: int, adress: str, box_number: int):
        super().__init__(id, adress, box_number)
        
        # Ресурсы (cons)
        self.WATER = 500.0      # литры 
        self.OSMOS = 50.0       # литры
        self.WAX = 5.0          # литры
        self.SHAMPOO = 10.0     # литры
        
        # Режимы (расход)

        # Экспресс (cons)
        self.EXPRESS_WATER = 50     # литры
        self.EXPRESS_SHAMPOO = 2    # литры
        
        # Стандарт (cons)
        self.STANDART_WATER = 70    # литры
        self.STANDART_SHAMPOO = 3   # литры
        self.STANDART_OSMOS = 20    # литры
        
        # Премиум (cons)
        self.PREMIUM_WATER = 120    # литры
        self.PREMIUM_SHAMPOO = 5    # литры
        self.PREMIUM_OSMOS = 30     # литры
        self.PREMIUM_WAX = 3        # литры

        # Цены
        self.EXPRESS_WASH = 300     # рубли
        self.STANDART_WASH = 500    # рубли
        self.PREMIUM_WASH = 1000    # рубли
        
        # Статистика
        self.total_washes = 0       # всего помек
        self.cash = 0               # итоговая выручка

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
        self.log_action("Сообщение", "Все ресурсы заправлены")
        print("Все ресурсы заправлены до максимума!")

    # Получить текущее значение ресурса
    def get_resource(self, resource: ResourceType) -> float:

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
        current = self.get_resource(resource)
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
        
        self.log_action("Сообщение", f"Ресурс: {resource.value} заправлен на {amount} л.")

    # Показать все ресурсы
    def show_resources(self):

        print(f"Вода: {self.WATER} л")
        print(f"Осмос: {self.OSMOS} л")
        print(f"Воск: {self.WAX} л")
        print(f"Шампунь: {self.SHAMPOO} л")
    

    # Методы для клиента =======================

    # Запуск мойки
    def start_wash(self, mode: WashMode) -> dict:
        
        # Проверка статуса
        if self.wash_status == BoxStatus.MAINTENANCE:
            return {"Сообщение": "Станция на обслуживании!"}
        if self.wash_status == BoxStatus.BUSY:
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

        # Запись в историю
        self.log_action("Сообщение", "Мойка завершена")
        
    # Собрать статистику станции
    def get_statistics(self) -> dict:

        return {
            "Номер станции": self.car_wash_Id,
            "Адрес": self.car_wash_Adress,
            "Всего моек за день": self.total_washes,
            "Выручка за день": self.cash,
            "Остаток воды": self.WATER,
            "Остаток осмоса": self.OSMOS,
            "Остаток воска": self.WAX,
            "Остаток шампуня": self.SHAMPOO,
            "Записей в истории": len(self.history)
        }

    # Вывести статистику
    def print_statistics(self):

        stats = self.get_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")


station = RobotWashStation(1, "д. Юркино, Солнечная ул. 7", 2)


station.wash_status = BoxStatus.MAINTANCE
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



station.refill_resource(ResourceType.WATER, 10)



station.full_refill()
station.show_resources()

station.show_history()

station.print_statistics()

station.get_error_history_log()

