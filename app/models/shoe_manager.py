class ShoeManager:
    def __init__(self):
        self.current_shoe_id = 1
        self.current_shoe_rounds = 0
        self.max_rounds_per_shoe = 80  # 一般一個牌靴約有80局
    
    def record_round(self):
        """記錄一局遊戲"""
        self.current_shoe_rounds += 1
        if self.current_shoe_rounds >= self.max_rounds_per_shoe:
            self.new_shoe()
    
    def new_shoe(self):
        """更換新牌靴"""
        self.current_shoe_id += 1
        self.current_shoe_rounds = 0
        return self.current_shoe_id
    
    def get_current_shoe_info(self):
        """獲取當前牌靴信息"""
        return {
            "shoe_id": self.current_shoe_id,
            "current_round": self.current_shoe_rounds,
            "max_rounds": self.max_rounds_per_shoe
        }