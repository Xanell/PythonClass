from Enums import BoxStatus,PaymentType 

class AbstractCarWash: 
    def __init__(self, id: int, adress: str, box_number: int, cash_box: float, balance: float): 

        self.car_wash_Id = id 
        self.car_was_Adress = adress
        self.box_number = box_number
        self.box_status = BoxStatus.FREE
        self.cash_box = cash_box
        self.balance = balance
    # Метод получение текущего состояния бокса
    def get_status_report(self) -> dict[str, any] :
            return {
                "Box_Number": self.box_number,
                "Current_Foam": self.current_foam,
                "Current_Wax": self.current_wax,
                "Status": self.box_status
            }
    # Метод перевода бокса в состояние ремонта
    def set_maintance_status(self) -> dict[str, any] :
            self.box_status = BoxStatus.MAINTANCE
            return{
                "Box_Number": self.box_number,
                "Status": self.box_status
            }
    # Метод перевода бокса в состояние свободен
    def finish_maintance_status(self) -> dict[str, any] :
            self.box_status = BoxStatus.FREE
            return{
                "Box_Number": self.box_number,
                "Box_Status": self.box_status
            }
    # Метод пополнения баланса
    def add_balance(self,balance: float, amount: float, payment_type: PaymentType) -> dict[str, any]:
          if amount <= 0 :
                raise ValueError(f"amount: {amount},не может быть меньше или равно нулю")
          if payment_type == PaymentType.CASH:
                self.cash_box += amount
          balance += amount 
          return{
                "New_Balance:": balance,
                "Success": True
          }
    # Метод оплаты
    def process_payment(self, amount: float, payment_type: PaymentType, balance: float) -> bool:
          if payment_type == PaymentType.CASH:
                self.cash_box += amount
          if payment_type == PaymentType.TERMINAL:
                self.cash_box += amount
          if payment_type == PaymentType.APP:
                if balance < amount:
                    raise ValueError(f"недостаточно средств на балансе! Стоимость {amount}.руб , на балансе {balance}.руб")
                balance -= amount
          return{
                "New_Balance:": balance,
                "Success": True
          }
