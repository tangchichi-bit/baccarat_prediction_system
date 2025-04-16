class CardFormula:
    @staticmethod
    def calculate_advantage_value(card):
        """計算優勢牌值
        1、4、5、7、8 → +2
        2、3 → -3
        6、9 → -5
        10、J、Q、K → 0
        """
        # 確保卡牌值是整數
        if isinstance(card, str):
            try:
                card = int(card)
            except ValueError:
                # 處理 J、Q、K 等非數字字符
                if card.upper() in ['J', 'Q', 'K']:
                    return 0
                else:
                    # 默認返回0，或者根據需要處理其他情況
                    return 0
        
        if card in [1, 4, 5, 7, 8]:
            return 2
        elif card in [2, 3]:
            return -3
        elif card in [6, 9]:
            return -5
        else:  # 10, J, Q, K
            return 0
    
    @staticmethod
    def calculate_player_frequency(cards):
        """計算閒家頻率
        7、8、9 → +2
        0、1、3、4 → +1
        2、5、6 → -5
        """
        # 確保所有卡牌值都是整數
        int_cards = []
        for card in cards:
            if isinstance(card, str):
                try:
                    int_cards.append(int(card))
                except ValueError:
                    # 處理 J、Q、K 等非數字字符，它們的點數為0
                    if card.upper() in ['J', 'Q', 'K']:
                        int_cards.append(0)
                    else:
                        # 默認為0，或者根據需要處理其他情況
                        int_cards.append(0)
            else:
                int_cards.append(card)
        
        # 計算點數總和的個位數
        total = sum(int_cards) % 10
        
        if total in [7, 8, 9]:
            return 2
        elif total in [0, 1, 3, 4]:
            return 1
        else:  # 2, 5, 6
            return -5
    
    @staticmethod
    def calculate_banker_frequency(cards):
        """計算莊家頻率
        7、8、9 → +3
        0、1、3、4、6 → +2
        2、5 → -5
        """
        # 確保所有卡牌值都是整數
        int_cards = []
        for card in cards:
            if isinstance(card, str):
                try:
                    int_cards.append(int(card))
                except ValueError:
                    # 處理 J、Q、K 等非數字字符，它們的點數為0
                    if card.upper() in ['J', 'Q', 'K']:
                        int_cards.append(0)
                    else:
                        # 默認為0，或者根據需要處理其他情況
                        int_cards.append(0)
            else:
                int_cards.append(card)
        
        # 計算點數總和的個位數
        total = sum(int_cards) % 10
        
        if total in [7, 8, 9]:
            return 3
        elif total in [0, 1, 3, 4, 6]:
            return 2
        else:  # 2, 5
            return -5
    
    @staticmethod
    def hertz_formula(player_cards, banker_cards):
        """赫茲公式計算
        
        Args:
            player_cards: 閒家牌值列表
            banker_cards: 莊家牌值列表
            
        Returns:
            prediction: 預測結果 ("banker" 或 "player")
            score: 赫茲公式分數
        """
        # 計算優勢牌值總和
        advantage_value = sum(CardFormula.calculate_advantage_value(card) for card in player_cards + banker_cards)
        
        # 計算閒家頻率
        player_frequency = CardFormula.calculate_player_frequency(player_cards)
        
        # 計算莊家頻率
        banker_frequency = CardFormula.calculate_banker_frequency(banker_cards)
        
        # 赫茲結果
        hertz_result = advantage_value + player_frequency + banker_frequency
        
        # 結果為負數時，下一局選擇莊家；結果為正數時，下一局選擇閒家
        prediction = "banker" if hertz_result < 0 else "player"
        
        return prediction, hertz_result