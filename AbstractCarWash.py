from Enums import BoxStatus, PaymentType 
from User_Class import User

class AbstractCarWash: 
    def __init__(self, id: int, address: str, box_number: int): 
        
        self.car_wash_Id = id 
        self.car_was_address = address
        self.box_number = box_number
        self.box_status = BoxStatus.FREE
        self.cash_box = 0.0
        self.total_revenue = 0.0
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
