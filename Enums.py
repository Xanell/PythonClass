from enum import Enum

class BoxStatus(Enum) :
    FREE = "Свободен"
    BUSY = "Занят"
    MAINTENANCE = "На обслуживании"

class ResourceType(Enum) :
    WATER = "Мойка водой"
    FOAM = "Мойка пеной"
    WAX = "Защита воском"
    OSMOS = "Сушка осмосом"
    SHAMPOO = "Мойка шампунем"

class PaymentType(Enum) :
    CASH = "Наличные"
    APP = "Приложение"

class WashMode(Enum):
    """Режимы мойки"""
    EXPRESS = "Экспресс мойка"
    STANDARD = "Стандартная мойка"
    PREMIUM = "Премиум мойка"