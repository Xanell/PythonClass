from enum import Enum

class BoxStatus(Enum) :
    FREE = "Свободен"
    BUSY = "Занят"
    MAINTANCE = "На обслуживании"

class BoxWashMode(Enum) :
    WATER = "Мойка водой"
    FOAM = "Мойка пеной"
    WAX = "Защита воском"

class PaymentType(Enum) :
    CASH = "Наличные"
    TERMINAL = "Терминал"
    APP = "Приложение"