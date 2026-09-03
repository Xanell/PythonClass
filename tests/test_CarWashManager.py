import pytest
from src.CarWash.Manager import CarWashManager
from src.CarWash.Boxes import AbstractCarWash
from src.CarWash.Utils import BoxStatus

# Заглушка бокса для тестирования менеджера
class DummyBox(AbstractCarWash):
    def __init__(self, box_number, box_status=BoxStatus.FREE, total_revenue=0.0, cash_box=0.0,
                 total_washes=0, error_history_log=None, address="dummy"):
        super().__init__(id=1, address=address, box_number=box_number)
        self.box_status = box_status
        self.total_revenue = total_revenue
        self.cash_box = cash_box
        self.total_washes = total_washes
        self.error_history_log = error_history_log if error_history_log is not None else []

    def get_resources(self):
        return {"water": 100, "foam": 50}

    def get_error_history_log(self):
        return self.error_history_log

    def get_statistics(self):
        return {
            "box_number": self.box_number,
            "address": self.car_wash_address,
            "cash_box": self.cash_box,
            "total_revenue": self.total_revenue,
            "total_washes": self.total_washes,
            "resources": self.get_resources(),
            "errors": self.get_error_history_log(),
        }


# Вторая независимая заглушка
class AnotherDummyBox(AbstractCarWash):
    def __init__(self, box_number, box_status=BoxStatus.FREE, total_revenue=0.0, cash_box=0.0,
                 total_washes=0, error_history_log=None, address="dummy2"):
        super().__init__(id=2, address=address, box_number=box_number)
        self.box_status = box_status
        self.total_revenue = total_revenue
        self.cash_box = cash_box
        self.total_washes = total_washes
        self.error_history_log = error_history_log if error_history_log is not None else []

    def get_resources(self):
        return {"water": 200, "shampoo": 10}

    def get_error_history_log(self):
        return self.error_history_log

    def get_statistics(self):
        return {
            "box_number": self.box_number,
            "address": self.car_wash_address,
            "cash_box": self.cash_box,
            "total_revenue": self.total_revenue,
            "total_washes": self.total_washes,
            "resources": self.get_resources(),
            "errors": self.get_error_history_log(),
        }

@pytest.fixture
def manager():
    return CarWashManager()


@pytest.fixture
def dummy_box_free():
    return DummyBox(box_number=1, box_status=BoxStatus.FREE, total_revenue=100.0, cash_box=50.0,
                    total_washes=3, error_history_log=["err1"])


@pytest.fixture
def dummy_box_busy():
    return DummyBox(box_number=2, box_status=BoxStatus.BUSY, total_revenue=200.0, cash_box=70.0,
                    total_washes=5, error_history_log=["err2"])


@pytest.fixture
def dummy_box_maintenance():
    return DummyBox(box_number=3, box_status=BoxStatus.MAINTENANCE, total_revenue=300.0, cash_box=90.0,
                    total_washes=7, error_history_log=[])


# --- Тесты add_wash_box ---
def test_add_wash_box(manager, dummy_box_free):
    manager.add_wash_box(dummy_box_free)
    assert len(manager.wash_boxes) == 1
    assert manager.wash_boxes[0] == dummy_box_free


# --- Тесты remove_wash_box ---
def test_remove_wash_box_existing(manager, dummy_box_free, dummy_box_busy):
    manager.add_wash_box(dummy_box_free)
    manager.add_wash_box(dummy_box_busy)
    manager.remove_wash_box(box_number=1)
    assert len(manager.wash_boxes) == 1
    assert manager.wash_boxes[0].box_number == 2


def test_remove_wash_box_not_existing(manager, dummy_box_free):
    manager.add_wash_box(dummy_box_free)
    manager.remove_wash_box(box_number=999)
    assert len(manager.wash_boxes) == 1


# --- Тесты фильтрации по статусу ---
def test_get_free_boxes(manager, dummy_box_free, dummy_box_busy, dummy_box_maintenance):
    manager.add_wash_box(dummy_box_free)
    manager.add_wash_box(dummy_box_busy)
    manager.add_wash_box(dummy_box_maintenance)
    free = manager.get_free_boxes()
    assert len(free) == 1
    assert free[0].box_number == 1


def test_get_busy_boxes(manager, dummy_box_free, dummy_box_busy, dummy_box_maintenance):
    manager.add_wash_box(dummy_box_free)
    manager.add_wash_box(dummy_box_busy)
    manager.add_wash_box(dummy_box_maintenance)
    busy = manager.get_busy_boxes()
    assert len(busy) == 1
    assert busy[0].box_number == 2


def test_get_maintenance_boxes(manager, dummy_box_free, dummy_box_busy, dummy_box_maintenance):
    manager.add_wash_box(dummy_box_free)
    manager.add_wash_box(dummy_box_busy)
    manager.add_wash_box(dummy_box_maintenance)
    maint = manager.get_maintenance_boxes()
    assert len(maint) == 1
    assert maint[0].box_number == 3


# --- Тесты агрегации ---
def test_get_total_revenue(manager, dummy_box_free, dummy_box_busy, dummy_box_maintenance):
    manager.add_wash_box(dummy_box_free)
    manager.add_wash_box(dummy_box_busy)
    manager.add_wash_box(dummy_box_maintenance)
    assert manager.get_total_revenue() == 100.0 + 200.0 + 300.0


def test_get_total_cash(manager, dummy_box_free, dummy_box_busy, dummy_box_maintenance):
    manager.add_wash_box(dummy_box_free)
    manager.add_wash_box(dummy_box_busy)
    manager.add_wash_box(dummy_box_maintenance)
    assert manager.get_total_cash() == 50.0 + 70.0 + 90.0


def test_get_total_wash(manager, dummy_box_free, dummy_box_busy, dummy_box_maintenance):
    manager.add_wash_box(dummy_box_free)
    manager.add_wash_box(dummy_box_busy)
    manager.add_wash_box(dummy_box_maintenance)
    assert manager.get_total_wash() == 3 + 5 + 7


# --- Тест get_all_statistics ---
def test_get_all_statistics(manager, dummy_box_free, dummy_box_busy):
    manager.add_wash_box(dummy_box_free)
    manager.add_wash_box(dummy_box_busy)
    stats = manager.get_all_statistics()
    assert len(stats) == 2
    assert stats[0]["box_number"] == 1
    assert stats[1]["box_number"] == 2
    assert "resources" in stats[0]
    assert "errors" in stats[1]


# --- Тест get_all_errors ---
def test_get_all_errors(manager, dummy_box_free, dummy_box_busy, dummy_box_maintenance):
    manager.add_wash_box(dummy_box_free)      # есть ошибка "err1"
    manager.add_wash_box(dummy_box_busy)      # есть ошибка "err2"
    manager.add_wash_box(dummy_box_maintenance)  # ошибок нет
    errors = manager.get_all_errors()
    assert errors == {
        1: ["err1"],
        2: ["err2"]
    }


# --- Тест get_boxes_by_type ---
def test_get_boxes_by_type(manager):
    box1 = DummyBox(box_number=1)
    box2 = AnotherDummyBox(box_number=2)
    manager.add_wash_box(box1)
    manager.add_wash_box(box2)

    # Фильтрация по DummyBox должна вернуть только box1
    dummy_boxes = manager.get_boxes_by_type(DummyBox)
    assert len(dummy_boxes) == 1
    assert dummy_boxes[0] is box1

    # Фильтрация по AnotherDummyBox должна вернуть только box2
    another_boxes = manager.get_boxes_by_type(AnotherDummyBox)
    assert len(another_boxes) == 1
    assert another_boxes[0] is box2