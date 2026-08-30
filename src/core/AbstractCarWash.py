from abc import ABC, abstractmethod
from src.config.Enums import BoxStatus, PaymentType 
from src.User_Class import User

class AbstractCarWash(ABC): 
    def __init__(self, id: int, address: str, box_number: int): 
        
        self.car_wash_Id = id 
        self.car_wash_address = address
        self.box_number = box_number
        self.box_status = BoxStatus.FREE
        self.cash_box = 0.0
        self.total_revenue = 0.0
        self.total_washes = 0
        self.pay_history_log = {}
        self.statistics_log = {}
        self.error_history_log = []

    @abstractmethod
    def get_resources(self):
        pass

    @abstractmethod
    def get_error_history_log(self):
        pass

    # Метод получения статистики по боксу
    def get_statistics(self) -> dict:
        return {
            "box_number": self.box_number,
            "address": self.car_wash_address,
            "cash_box": self.cash_box,
            "total_revenue": self.total_revenue,
            "total_washes": self.total_washes,
            "resources": self.get_resources(),
            "errors": self.get_error_history_log()
        }
    
    # Метод добавления ошибки в историю логов
    def add_error_history_log(self, error: str) -> None:
        self.error_history_log.append(error)

    # Метод добавления оплаты в иторию логов
    def add_pay_history_log(self, total_price: float, time_passed: int) -> None:
        if self.box_number not in self.pay_history_log:
            self.pay_history_log[self.box_number] = []
        self.total_washes += 1
        self.pay_history_log[self.box_number].append((total_price, time_passed))

    # Метод получения истории оплат
    def get_pay_history_log(self) -> dict:
        return self.pay_history_log
    
    # Метод получение текущего состояния бокса
    def get_status_report(self) -> dict[str, any] :
        return {
            "box_number": self.box_number,
            "cash_box": self.cash_box,
            "status": self.box_status
        }
    # Метод перевода бокса в состояние ремонта
    def set_maintenance_status(self) -> dict[str, any] :
        self.box_status = BoxStatus.MAINTENANCE
        return{
            "box_number": self.box_number,
            "status": self.box_status
        }
    # Метод перевода бокса в состояние свободен
    def finish_maintenance_status(self) -> dict[str, any] :
        self.box_status = BoxStatus.FREE
        return{
            "box_number": self.box_number,
            "box_status": self.box_status
        }
    # Метод оплаты
    def process_payment(self, amount: float, payment_type: PaymentType, user: User) -> bool:
        if payment_type == PaymentType.CASH:
            self.cash_box += amount
        if payment_type == PaymentType.APP:
            if user.balance < amount:
                raise ValueError(f"недостаточно средств на балансе! Стоимость {amount}.руб , на балансе {user.balance}.руб")
            user.balance -= amount

        self.total_revenue += amount
        return True
