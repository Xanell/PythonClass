from enum import Enum

class BoxStatus(Enum) :
    FREE = "Свободен"
    BUSY = "Занят"
    MAINTANCE = "На обслуживании"

class ResourceType(Enum) :
    WATER = "вода"
    FOAM = "пена"
    WAX = "воск"
    OSMOS = "осмос"
    SHAMPOO = "шампунь"

class PaymentType(Enum) :
    CASH = "Наличные"
    APP = "Приложение"

class WashMode(Enum):
    """Режимы мойки"""
    EXPRESS = "Экспресс мойка"
    STANDARD = "Стандартная мойка"
    PREMIUM = "Премиум мойка"