from enum import Enum

class BoxStatus(Enum) :
    """Статусы мойки"""
    FREE = "Свободен"
    BUSY = "Занят"
    MAINTENANCE = "На обслуживании"

class ResourceType(Enum) :
    """Ресурсы"""
    WATER = "Вода"
    FOAM = "Пена"
    WAX = "Воск"
    OSMOS = "Осмос"
    SHAMPOO = "Шампунь"

class PaymentType(Enum) :
    """Тип оплаты"""
    CASH = "Наличные"
    APP = "Приложение"

class WashMode(Enum):
    """Режимы мойки"""
    EXPRESS = "Экспресс мойка"
    STANDARD = "Стандартная мойка"
    PREMIUM = "Премиум мойка"