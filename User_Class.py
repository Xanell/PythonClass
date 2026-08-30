class User():
    def __init__(self, user_id: int, user_name: str, initial_balance: float = 0.0):
        self.user_id = user_id
        self.user_name = user_name
        self.balance = initial_balance

    # Метод получения информации о пользователе
    def get_profile_report(self) -> dict[str, any]:
        return {
            "user_id": self.user_id,
            "customer_name": self.user_name,
            "current_balance": round(self.balance, 2)
        }

    # Метод добавления (пополнения) баланса к счету
    def deposit_money(self, amount: float) -> dict[str, any]:
        if amount <= 0:
            raise ValueError(f"Ошибка пополнения: Сумма зачисления ({amount} руб.) должна быть больше нуля!")
            
        self.balance += amount
        print(f"[БЭКЭНД]: Пользователь {self.name} пополнил счет на +{amount} руб.")
        
        return {
            "success": True,
            "new_balance": round(self.balance, 2)
        }