import os
import json
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
import logging

class BaccaratAIModel:
    def __init__(self, history_file):
        self.history_file = history_file
        self.model = None
        self.sequence_length = 5  # 減少序列長度，使用前5局預測下一局
        self.accuracy = 0.0
        self.model_file = os.path.join(os.path.dirname(history_file), 'baccarat_model.h5')
        
        # 確保歷史文件存在
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)
        
        # 嘗試加載已訓練的模型
        self.load_model()
    
    def load_model(self):
        """加載已訓練的模型"""
        if os.path.exists(self.model_file):
            try:
                self.model = load_model(self.model_file)
                logging.info("已加載訓練好的模型")
                return True
            except Exception as e:
                logging.error(f"加載模型失敗: {str(e)}")
        return False
    
    def save_model(self):
        """保存訓練好的模型"""
        if self.model:
            try:
                self.model.save(self.model_file)
                logging.info("模型已保存")
                return True
            except Exception as e:
                logging.error(f"保存模型失敗: {str(e)}")
        return False
    
    def _load_history(self):
        """載入遊戲歷史數據"""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_history(self, history):
        """保存遊戲歷史數據"""
        with open(self.history_file, 'w') as f:
            json.dump(history, f)
    
    def add_game_result(self, result, player_cards=None, banker_cards=None, shoe_id=None):
        """添加遊戲結果到歷史記錄
        
        Args:
            result: 'player', 'banker' 或 'tie'
            player_cards: 閒家牌值列表 (可選)
            banker_cards: 莊家牌值列表 (可選)
            shoe_id: 牌靴ID (可選)
        """
        history = self._load_history()
        
        game_record = {
            "result": result,
            "timestamp": tf.timestamp().numpy().tolist()
        }
        
        if player_cards:
            game_record["player_cards"] = player_cards
        if banker_cards:
            game_record["banker_cards"] = banker_cards
        if shoe_id:
            game_record["shoe_id"] = shoe_id
            
        history.append(game_record)
        self._save_history(history)
    
    def clear_history(self):
        """清除所有歷史數據"""
        self._save_history([])
        # 同時刪除模型文件
        if os.path.exists(self.model_file):
            try:
                os.remove(self.model_file)
                logging.info("模型文件已刪除")
            except Exception as e:
                logging.error(f"刪除模型文件失敗: {str(e)}")
        self.model = None
        self.accuracy = 0.0
    
    def _prepare_data(self):
        """準備訓練數據"""
        history = self._load_history()
        
        # 過濾掉 tie 結果，只使用 banker 和 player
        filtered_history = [game for game in history if game["result"] in ["banker", "player"]]
        
        if len(filtered_history) < self.sequence_length + 1:
            return None, None
        
        # 將結果轉換為數字: banker=0, player=1
        results = []
        for game in filtered_history:
            if game["result"] == "banker":
                results.append(0)
            else:  # player
                results.append(1)
        
        # 創建序列和標籤
        X, y = [], []
        for i in range(len(results) - self.sequence_length):
            X.append(results[i:i + self.sequence_length])
            y.append(results[i + self.sequence_length])
        
        # 轉換為 numpy 數組
        X = np.array(X)
        y = np.array(y)
        
        # 對標籤進行 one-hot 編碼
        y_encoded = tf.keras.utils.to_categorical(y, num_classes=2)
        
        return X, y_encoded
    
    def train_model(self):
        """訓練模型"""
        X, y = self._prepare_data()
        
        if X is None:
            return False, "訓練數據不足，請添加更多遊戲結果"
        
        if len(X) < 10:  # 降低訓練數據要求
            return False, f"訓練數據不足，當前有 {len(X)} 個序列，至少需要 10 個"
        
        logging.info(f"開始訓練模型，使用 {len(X)} 個序列")
        
        # 分割訓練集和測試集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 重塑數據為 LSTM 輸入格式
        X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
        
        # 創建一個更簡單的模型
        model = Sequential([
            LSTM(32, input_shape=(self.sequence_length, 1)),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(2, activation='softmax')  # 2個類別: banker, player
        ])
        
        # 編譯模型
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # 訓練模型
        model.fit(
            X_train, y_train,
            epochs=30,  # 減少訓練輪數
            batch_size=16,  # 減少批次大小
            validation_data=(X_test, y_test),
            verbose=0
        )
        
        # 評估模型
        _, accuracy = model.evaluate(X_test, y_test, verbose=0)
        self.accuracy = accuracy
        self.model = model
        
        # 保存模型
        self.save_model()
        
        return True, f"模型訓練完成，準確率: {accuracy:.2f}"
    
    def predict_next(self):
        """預測下一局結果"""
        if self.model is None:
            # 嘗試加載模型
            if not self.load_model():
                # 如果沒有模型，嘗試訓練一個
                success, _ = self.train_model()
                if not success:
                    # 如果訓練失敗，使用簡單統計預測
                    return self.predict_based_on_statistics()
        
        history = self._load_history()
        
        # 過濾掉 tie 結果
        filtered_history = [game for game in history if game["result"] in ["banker", "player"]]
        
        if len(filtered_history) < self.sequence_length:
            # 數據不足，使用簡單統計預測
            return self.predict_based_on_statistics()
        
        # 獲取最近的序列
        recent_results = []
        for game in filtered_history[-self.sequence_length:]:
            if game["result"] == "banker":
                recent_results.append(0)
            else:  # player
                recent_results.append(1)
        
        # 準備預測數據
        X_pred = np.array([recent_results])
        X_pred = X_pred.reshape(X_pred.shape[0], X_pred.shape[1], 1)
        
        # 預測
        try:
            prediction = self.model.predict(X_pred, verbose=0)[0]
            
            # 獲取最可能的結果
            pred_index = np.argmax(prediction)
            confidence = float(prediction[pred_index])
            
            result = "banker" if pred_index == 0 else "player"
            
            return result, confidence
        except Exception as e:
            logging.error(f"預測失敗: {str(e)}")
            return self.predict_based_on_statistics()
    
    def predict_based_on_statistics(self):
        """基於簡單統計進行預測"""
        history = self._load_history()
        
        if not history:
            # 如果沒有歷史數據，隨機預測
            import random
            return random.choice(["banker", "player"]), 0.51
        
        # 計算莊家和閒家的勝率
        banker_wins = sum(1 for game in history if game["result"] == "banker")
        player_wins = sum(1 for game in history if game["result"] == "player")
        
        total_games = banker_wins + player_wins
        if total_games == 0:
            import random
            return random.choice(["banker", "player"]), 0.51
        
        banker_rate = banker_wins / total_games
        player_rate = player_wins / total_games
        
        if banker_rate > player_rate:
            return "banker", banker_rate
        else:
            return "player", player_rate
    
    def get_accuracy(self):
        """獲取模型準確率"""
        return self.accuracy