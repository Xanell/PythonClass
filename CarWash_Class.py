from enum import Enum

class BoxStatus(Enum) :
    FREE = "Свободен"
    BUSY = "Занят"
    MAINTANCE = "На обслуживании"

class BoxWashMode(Enum) :
    WATER = "Мойка водой"
    FOAM = "Мойка пеной"
    WAX = "Защита воском"

class StandartWashBox :
    def __init__(self, id: int, adress: str, box_number: int, curr_foam: float = None, curr_wax: float = None):

        self.car_wash_Id = id 
        self.car_was_Adress = adress
        self.box_number = box_number
        self.box_status = BoxStatus.FREE

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

    # Метод получение текущего состояния бокса
    def get_status_report(self) -> dict[str, any] :
        return {
            "Box_Number": self.box_number,
            "Current_Foam": self.current_foam,
            "Current_Wax": self.current_wax,
            "Status": self.box_status
        }
    # Метод залития мыла в баки
    def restock_foam(self, foam_liters: float) -> dict[str, any] :
        self.current_foam += foam_liters
        self.box_status = BoxStatus.MAINTANCE

        if self.current_foam > self.MAX_FOAM:
            print("Ошибка, залито слишком много пены!")
            return

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
            print("Ошибка, залито слишком много воска!")
            return

        return{
            "Box_Number": self.box_number,
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
    # Метод начала мойки машины
    def start_wash_session(self, mode: BoxWashMode, duration_seconds: int) -> dict[str, any]:
        if mode == BoxWashMode.WATER : 
            self.box_status = BoxStatus.BUSY
            price = duration_seconds * self.TARIFF_WATER_PER_SEC
            return{
                "Box_Number": self.box_number,
                "Status": self.box_status,
                "Total_Price": round(price, 2)
            }
        elif mode == BoxWashMode.FOAM :
            self.box_status = BoxStatus.BUSY
            foam_consumption = duration_seconds * self.FOAM_CONSUMPTION_PER_SEC

            if self.current_foam < foam_consumption:
                self.box_status = BoxStatus.MAINTANCE
                print("Ошибка, недостаточно мыла для проведения мойки!")
                return

            self.current_foam -= foam_consumption
            price = duration_seconds * self.TARIFF_FOAM_PER_SEC
            return{
                "Box_Number": self.box_number,
                "Status": self.box_status,
                "Remaning_Foam": self.current_foam,
                "Total_Price": round(price, 2)
            }
        elif mode == BoxWashMode.WAX :
            self.box_status = BoxStatus.BUSY
            wax_consumption = duration_seconds * self.WAX_CONSUMPTION_PER_SEC

            if self.current_wax < wax_consumption :
                self.box_status = BoxStatus.MAINTANCE
                print("Ошибка, недостаточно воска для проведения мойки!")
                return

            self.current_wax -= wax_consumption
            price = duration_seconds * self.TARIFF_WAX_PER_SEC
            return{
                "Box_Number": self.box_number,
                "Status": self.box_status,
                "Remaning_Wax": self.current_wax,
                "Total_Price": round(price, 2)
            }