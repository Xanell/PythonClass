from AbstractCarWash import AbstractCarWash
from Enums import BoxStatus, ResourceType, PaymentType 
from User_Class import User

class StandartWashBox(AbstractCarWash) : 
    def __init__(self, id: int, address: str, box_number: int, curr_foam: float = None, curr_wax: float = None):
        super().__init__(id, address, box_number)
        # Константы максимальная вместимость баков
        self.MAX_FOAM = 50.0
        self.MAX_WAX = 10.0
        # Константы тарифов на каждый вид мойки в рублях за секунду
        self.TARIFF_WATER_PER_SEC = 0.15 # 9р в минуту
        self.TARIFF_FOAM_PER_SEC = 0.40 # 24р в минуту
        self.TARIFF_WAX_PER_SEC = 0.30 # 18р в минуту
        # Константы расхода ресурсов за секунду
        self.FOAM_CONSUMPTION_PER_SEC = 0.4
        self.WAX_CONSUMPTION_PER_SEC = 0.5
        # Проверяем текущее состояние остатков мыла и воска, если они не переданы, то баки полные по дефолту и имеют значение 50, 10
        self.current_foam = curr_foam if curr_foam is not None else self.MAX_FOAM
        self.current_wax = curr_wax if curr_wax is not None else self.MAX_WAX

    # Метод залития мыла в баки
    def restock_foam(self, foam_liters: float) -> dict[str, any] :
        self.current_foam += foam_liters
        self.box_status = BoxStatus.MAINTENANCE

        if self.current_foam > self.MAX_FOAM:
            print("Ошибка, залито слишком много пены! Излишки пены слиты через аварийный клапан.")
            self.current_foam = self.MAX_FOAM

        return{
            "Box_Number": self.box_number,
            "Current_Foam": self.current_foam,
            "Status": self.box_status
        }
    # Метод залития воска в баки
    def restock_wax(self, wax_liters: float) -> dict[str, any] :
        self.current_wax += wax_liters
        self.box_status = BoxStatus.MAINTENANCE

        if self.current_wax > self.MAX_WAX :
            print("Ошибка, залито слишком много воска! Излишки воска слиты через аварийный клапан.")
            self.current_wax = self.MAX_WAX

        return{
            "Box_Number": self.box_number,
            "Current_Wax": self.current_wax,
            "Status": self.box_status
        }
    # Метод начала мойки машины 
def start_wash_session(self, mode: ResourceType, payment_type: PaymentType,
                       user: User = None, duration_seconds: int = 0,
                       cash_amount: float = 0.0) -> dict[str, any]:
    """
    Универсальный метод запуска мойки.
    - payment_type=APP: требуется user и duration_seconds > 0.
    - payment_type=CASH: требуется cash_amount > 0, duration_seconds игнорируется.
    """
    # Проверка доступности бокса
    if self.box_status != BoxStatus.FREE:
        raise ValueError(f"Бокс №{self.box_number} недоступен!")

    # Определение тарифа и расхода ресурсов
    if mode == ResourceType.FOAM:
        tariff = self.TARIFF_FOAM_PER_SEC
        consumption = self.FOAM_CONSUMPTION_PER_SEC
    elif mode == ResourceType.WAX:
        tariff = self.TARIFF_WAX_PER_SEC
        consumption = self.WAX_CONSUMPTION_PER_SEC
    else:  # WATER
        tariff = self.TARIFF_WATER_PER_SEC
        consumption = 0.0

    # Предварительные проверки в зависимости от типа оплаты
    if payment_type == PaymentType.APP:
        if user is None:
            raise ValueError("Для оплаты через приложение необходимо указать пользователя")
        if duration_seconds <= 0:
            raise ValueError("Укажите длительность мойки в секундах")
        total_cost = duration_seconds * tariff
        if user.balance < total_cost:
            raise ValueError(f"Недостаточно средств на балансе: нужно {total_cost:.2f} руб., а на балансе {user.balance:.2f} руб.")
        max_seconds = duration_seconds
        # Для APP лимит по времени фиксирован
    elif payment_type == PaymentType.CASH:
        if cash_amount <= 0:
            raise ValueError("Внесённая сумма должна быть положительной")
        # Для CASH лимит определяется внесёнными деньгами (без сдачи)
        session_balance = cash_amount
    else:
        raise ValueError("Неизвестный тип оплаты")

    # Запуск мойки
    self.box_status = BoxStatus.BUSY
    seconds_passed = 0

    try:
        while True:
            # Проверка ресурсов
            if mode == ResourceType.FOAM and self.current_foam < consumption:
                self.set_maintenance_status()   # исправлено имя метода
                raise ValueError("Ресурсы в баке пены закончились!")
            if mode == ResourceType.WAX and self.current_wax < consumption:
                self.set_maintenance_status()
                raise ValueError("Ресурсы в баке воска закончились!")

            # Проверка денег (только для наличных, для APP уже проверено)
            if payment_type == PaymentType.CASH:
                if session_balance < tariff:
                    raise ValueError("Внесённые наличные средства закончились!")
                session_balance -= tariff

            # Расходуем ресурсы
            if mode == ResourceType.FOAM:
                self.current_foam -= consumption
            elif mode == ResourceType.WAX:
                self.current_wax -= consumption

            seconds_passed += 1

            # Условие завершения для APP
            if payment_type == PaymentType.APP and seconds_passed >= max_seconds:
                break
            # Для CASH выход только по исключению (когда закончатся деньги или ресурсы)
    except ValueError as error:
        print(f"[ТЕРМИНАЛ БОКСА №{self.box_number}]: {error}")
        final_price = seconds_passed * tariff
        if self.box_status == BoxStatus.BUSY:
            self.box_status = BoxStatus.FREE
        if final_price > 0:
            if payment_type == PaymentType.APP:
                self.process_payment(amount=final_price, payment_type=PaymentType.APP, user=user)
            else:
                self.process_payment(amount=final_price, payment_type=PaymentType.CASH, user=None)
        return {
            "message": "Мойка принудительно остановлена",
            "box_number": self.box_number,
            "status": self.box_status,
            "time": seconds_passed,
            "total_price": round(final_price, 2),
            "remaining_balance": round(user.balance, 2) if user else None
        }

    # Успешное завершение
    final_price = seconds_passed * tariff
    if payment_type == PaymentType.APP:
        self.process_payment(amount=final_price, payment_type=PaymentType.APP, user=user)
        remaining_balance = round(user.balance, 2)
    else:
        self.process_payment(amount=final_price, payment_type=PaymentType.CASH, user=None)
        remaining_balance = None

    self.box_status = BoxStatus.FREE
    return {
        "message": "Мойка успешно завершена",
        "box_number": self.box_number,
        "status": self.box_status,
        "time": seconds_passed,
        "total_price": round(final_price, 2),
        "remaining_balance": remaining_balance
    }