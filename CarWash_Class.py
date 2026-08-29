from AbstractCarWash import AbstractCarWash
from Enums import BoxStatus, BoxWashMode, PaymentType 
from User_Class import User

class StandartWashBox(AbstractCarWash) : 
    def __init__(self, id: int, adress: str, box_number: int, curr_foam: float = None, curr_wax: float = None):
        super().__init__(id, adress, box_number)
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
        self.box_status = BoxStatus.MAINTANCE

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
        self.box_status = BoxStatus.MAINTANCE

        if self.current_wax > self.MAX_WAX :
            print("Ошибка, залито слишком много воска! Излишки воска слиты через аварийный клапан.")
            self.current_wax = self.MAX_WAX

        return{
            "Box_Number": self.box_number,
            "Current_Wax": self.current_wax,
            "Status": self.box_status
        }
    # Метод начала мойки машины при оплате через приложение
    def start_wash_session_app_pay(self, mode: BoxWashMode, user: User = None, duration_seconds: int = 0) -> dict[str, any]:
        # Проверка на доступность бокса
        if self.box_status != BoxStatus.FREE :
            raise ValueError(f"Бокс №{self.box_number}, недоступен!")

        current_session_balance = 0.0
        # Проверка текущего баланса пользователя
        if user.balance <= 0 :
            raise ValueError("Пополните баланс!")
        
        current_session_balance = user.balance

        # Проверка выбраного режима мойки
        if mode == BoxWashMode.FOAM :
            tariff = self.TARIFF_FOAM_PER_SEC
            consumption = self.FOAM_CONSUMPTION_PER_SEC
        elif mode == BoxWashMode.WAX :
            tariff = self.TARIFF_WAX_PER_SEC
            consumption = self.WAX_CONSUMPTION_PER_SEC
        else :
            tariff = self.TARIFF_WATER_PER_SEC
            consumption = 0.0

        self.box_status = BoxStatus.BUSY
        seconds_passed = 0

        try:
            while True:
                # Проверяем баки с химией
                if mode == BoxWashMode.FOAM and self.current_foam < consumption:
                    self.set_maintance_status() # Уходим в ремонт
                    raise ValueError("Ресурсы в баке пены закончились!")
                    
                if mode == BoxWashMode.WAX and self.current_wax < consumption:
                    self.set_maintance_status()
                    raise ValueError("Ресурсы в баке воска закончились!")

                # Проверяем баланс пользователя
                if current_session_balance < tariff:
                    raise ValueError("Деньги на балансе приложения закончились!")

                # Списываем с баланса текущий тариф
                user.balance -= tariff
                current_session_balance = user.balance

                if mode == BoxWashMode.FOAM:
                    self.current_foam -= consumption
                elif mode == BoxWashMode.WAX:
                    self.current_wax -= consumption

                # Добавляем секунду работы для расчета финальной цены
                seconds_passed += 1

                if seconds_passed >= duration_seconds:
                    break

        except ValueError as error:
            # Мойка прервалась аварийно (закончились деньги или химия)
            print(f"[ТЕРМИНАЛ БОКСА №{self.box_number}]: {error}")
            
            # Считаем цену за то время, которое клиент УСПЕЛ отмыть
            final_price = seconds_passed * tariff
            
            # Если это была не поломка бака, возвращаем бокс в работу
            if self.box_status == BoxStatus.BUSY:
                self.box_status = BoxStatus.FREE
                
            # Проводим платеж в родительском классе (для учета выручки total_revenue)
            if final_price > 0:
                self.process_payment(amount=final_price, payment_type=PaymentType.APP, user=user)

            return {
                "Message": "Мойка принудительно остановлена",
                "Box_Number": self.box_number,
                "Status": self.box_status,
                "Time": seconds_passed,
                "Total_Price": round(final_price, 2),
                "Remaining_Balance": round(user.balance, 2)
            }
        final_price = seconds_passed * tariff
        self.process_payment(amount=final_price, payment_type=PaymentType.APP, user=user)
        self.box_status = BoxStatus.FREE
        return {
            "Message": "Мойка успешно завершена по таймеру!",
            "Time": seconds_passed,
            "Total_Price": round(final_price, 2)
        }
    # Метод начала мойки через оплату наличкой
    def start_wash_session_cash_pay(self, mode: BoxWashMode, cash_amount: float) -> dict[str, any]:
        # Проверка на доступность бокса
        if self.box_status != BoxStatus.FREE :
            raise ValueError(f"Бокс №{self.box_number}, недоступен!")

        self.cash_box += cash_amount
        current_session_balance = self.cash_box

        # Проверка выбраного режима мойки
        if mode == BoxWashMode.FOAM :
            tariff = self.TARIFF_FOAM_PER_SEC
            consumption = self.FOAM_CONSUMPTION_PER_SEC
        elif mode == BoxWashMode.WAX :
            tariff = self.TARIFF_WAX_PER_SEC
            consumption = self.WAX_CONSUMPTION_PER_SEC
        else :
            tariff = self.TARIFF_WATER_PER_SEC
            consumption = 0.0

        self.box_status = BoxStatus.BUSY
        seconds_passed = 0

        try:
            while True:
                # Проверяем баки с химией
                if mode == BoxWashMode.FOAM and self.current_foam < consumption:
                    self.set_maintance_status() # Уходим в ремонт
                    raise ValueError("Ресурсы в баке пены закончились!")
                    
                if mode == BoxWashMode.WAX and self.current_wax < consumption:
                    self.set_maintance_status()
                    raise ValueError("Ресурсы в баке воска закончились!")

                # Проверяем баланс пользователя
                if current_session_balance < tariff:
                    raise ValueError("Внесенные наличные средства полностью закончились!")

                # Списываем с баланса текущий тариф
                current_session_balance -= tariff

                if mode == BoxWashMode.FOAM:
                    self.current_foam -= consumption
                elif mode == BoxWashMode.WAX:
                    self.current_wax -= consumption

                # Добавляем секунду работы для расчета финальной цены
                seconds_passed += 1

        except ValueError as error:
            # Мойка прервалась аварийно (закончились деньги или химия)
            print(f"[ТЕРМИНАЛ БОКСА №{self.box_number}]: {error}")
            
            # Считаем цену за то время, которое клиент УСПЕЛ отмыть
            final_price = seconds_passed * tariff
            
            # Если это была не поломка бака, возвращаем бокс в работу
            if self.box_status == BoxStatus.BUSY:
                self.box_status = BoxStatus.FREE
                
            # Проводим платеж в родительском классе (для учета выручки total_revenue)
            if final_price > 0:
                self.process_payment(amount=final_price, payment_type=PaymentType.CASH, user=None)

            return {
                "Message": "Мойка принудительно остановлена",
                "Box_Number": self.box_number,
                "Status": self.box_status,
                "Time": seconds_passed,
                "Total_Price": round(final_price, 2),
            }