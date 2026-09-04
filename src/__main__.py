from CarWash.Boxes import StandartWashBox, RobotWashStation
from CarWash.User import User
from CarWash.Manager import CarWashManager
from CarWash.Utils import ResourceType, PaymentType, WashMode

testUser1 = User(1, "Саша", 1000)
testUser2 = User(2, "Маша", 1600)

manual_box1 = StandartWashBox(1, "Тестовая, д. 5", 1)
manual_box2 = StandartWashBox(2, "Тестовая, д. 5", 2)
robo_box1 = RobotWashStation(1, "Тестовая, д. 5", 1)
robo_box2 = RobotWashStation(2, "Тестовая, д. 5", 2)

manager = CarWashManager()
boxes = [manual_box1, manual_box2, robo_box1, robo_box2]

for box in boxes:
    manager.add_wash_box(box)

print(manual_box1.get_resources())
print(manual_box2.get_resources())
print(robo_box1.get_resources())
print(robo_box2.get_resources())

print(manual_box1.start_wash_session(ResourceType.WATER, PaymentType.CASH, None, 0, 100))
print(manual_box1.start_wash_session(ResourceType.FOAM, PaymentType.APP, testUser1, 100, 0))

print(manual_box1.get_resources())

print(robo_box1.start_wash_session(WashMode.EXPRESS, PaymentType.CASH, None, 300))
print(robo_box2.start_wash_session(WashMode.PREMIUM, PaymentType.APP, testUser2, 0))

print(manager.get_all_statistics())
print(manager.get_free_boxes())
print(manager.get_total_revenue())
print(manager.get_total_cash())
print(manager.get_total_wash())
print(manager.get_boxes_by_type(StandartWashBox))