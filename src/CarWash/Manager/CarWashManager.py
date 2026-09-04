from CarWash.Boxes import AbstractCarWash
from CarWash.Utils import BoxStatus

class CarWashManager:
    def __init__(self):
        self.wash_boxes: list[AbstractCarWash] = []

    # Метод добавления бокса
    def add_wash_box(self, box: AbstractCarWash) -> None:
        self.wash_boxes.append(box)

    # Метод удаления бокса по номеру бокса
    def remove_wash_box(self, box_number: int) -> None:
        new_boxes = []
        for box in self.wash_boxes :
            if box.box_number != box_number:
                new_boxes.append(box)
        self.wash_boxes = new_boxes

    # Метод получения свободных боксов
    def get_free_boxes(self) -> list:
        free_boxes = []
        for box in self.wash_boxes:
            if box.box_status == BoxStatus.FREE:
                free_boxes.append(box)
        return free_boxes

    # Метод получения занятых боксов
    def get_busy_boxes(self) -> list:
        busy_boxes = []
        for box in self.wash_boxes:
            if box.box_status == BoxStatus.BUSY:
                busy_boxes.append(box)
        return busy_boxes

    # Метод получения боксов находящихся на обслуживании
    def get_maintenance_boxes(self) -> list:
        maintenance_boxes = []
        for box in self.wash_boxes:
            if box.box_status == BoxStatus.MAINTENANCE:
                maintenance_boxes.append(box)
        return maintenance_boxes
    
    # Метод получения общей выручки боксов
    def get_total_revenue(self) -> float:
        total = 0
        for box in self.wash_boxes:
            total += box.total_revenue
        return total

    # Метод получения наличных всех боксов
    def get_total_cash(self) -> float:
        total_cash = 0
        for box in self.wash_boxes:
            total_cash += box.cash_box
        return total_cash

    # Метод получения общего кол-ва моек всех боксов
    def get_total_wash(self) -> int:
        total_washes = 0
        for box in self.wash_boxes:
            total_washes += box.total_washes
        return total_washes

    # Метод получение статистики по всем боксам
    def get_all_statistics(self) -> list[dict]:
        total_statistics = []
        for box in self.wash_boxes:
            total_statistics.append(box.get_statistics())
        return total_statistics

    # Метод получения ошибок по всем боксам
    def get_all_errors(self) -> dict:
        errors = {}
        for box in self.wash_boxes:
            if box.error_history_log:
                errors[box.box_number] = box.error_history_log
        return errors

    # Метод получения боксов по типу Робо или Ручная
    def get_boxes_by_type(self, box_type: type) -> list:
        boxes_by_type = []
        for box in self.wash_boxes:
            if isinstance(box, box_type):
                boxes_by_type.append(box)
        return boxes_by_type
