from flask import render_template , jsonify, request, current_app
from app.routes import main_bp
from app.models.ai_model import BaccaratAIModel
from app.models.card_formula import CardFormula
from app.models.shoe_manager import ShoeManager
import json
import os

# 初始化模型和牌靴管理器
shoe_manager = ShoeManager()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/formula_mode')
def formula_mode():
    return render_template('formula_mode.html')

@main_bp.route('/combined_mode')
def combined_mode():
    return render_template('combined_mode.html')

@main_bp.route('/get_history')
def get_history():
    try:
        with open(current_app.config['GAME_HISTORY_FILE'], 'r') as f:
            history = json.load(f)
        return jsonify({"success": True, "history": history})
    except Exception as e:
        current_app.logger.error(f"讀取歷史記錄失敗: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@main_bp.route('/add_result', methods=['POST'])
def add_result():
    data = request.json
    result = data.get('result')
    player_cards = data.get('player_cards', [])
    banker_cards = data.get('banker_cards', [])
    
    if result not in ['player', 'banker', 'tie']:
        return jsonify({"success": False, "error": "無效的結果"})
    
    # 記錄牌靴信息
    shoe_manager.record_round()
    shoe_info = shoe_manager.get_current_shoe_info()
    
    # 添加到AI模型
    ai_model = BaccaratAIModel(current_app.config['GAME_HISTORY_FILE'])
    ai_model.add_game_result(result, player_cards, banker_cards, shoe_info['shoe_id'])
    
    return jsonify({
        "success": True, 
        "message": "結果已添加",
        "shoe_info": shoe_info
    })

@main_bp.route('/train_model', methods=['POST'])
def train_model():
    ai_model = BaccaratAIModel(current_app.config['GAME_HISTORY_FILE'])
    success, message = ai_model.train_model()
    
    return jsonify({
        "success": success,
        "message": message,
        "accuracy": ai_model.get_accuracy() if success else 0
    })

@main_bp.route('/predict', methods=['POST'])
def predict():
    data = request.json
    prediction_type = data.get('type', 'combined')
    player_cards = data.get('player_cards', [])
    banker_cards = data.get('banker_cards', [])
    
    # 記錄輸入數據
    current_app.logger.info(f"預測請求: type={prediction_type}, player_cards={player_cards}, banker_cards={banker_cards}")
    
    ai_model = BaccaratAIModel(current_app.config['GAME_HISTORY_FILE'])
    
    # AI預測
    ai_result, ai_confidence = ai_model.predict_next()
    current_app.logger.info(f"AI預測結果: {ai_result}, 置信度: {ai_confidence}")
    
    # 公式預測
    formula_result = None
    formula_score = 0
    if player_cards and banker_cards:
        try:
            formula_result, formula_score = CardFormula.hertz_formula(player_cards, banker_cards)
            current_app.logger.info(f"公式預測結果: {formula_result}, 分數: {formula_score}")
        except Exception as e:
            current_app.logger.error(f"公式預測失敗: {str(e)}")
    else:
        current_app.logger.warning("公式預測失敗: 玩家或莊家卡牌為空")
    
    # 綜合預測
    final_result = None
    confidence = 0
    reason = "無法預測，請確保提供足夠的數據"
    
    if prediction_type == 'combined':
        if formula_result and ai_result:
            # 如果AI和公式預測結果一致，使用該結果
            if formula_result == ai_result:
                final_result = formula_result
                confidence = ai_confidence
                reason = "AI模型和赫茲公式預測結果一致"
            # 如果不一致，根據AI的置信度決定
            elif ai_confidence > 0.7:  # 高置信度時使用AI結果
                final_result = ai_result
                confidence = ai_confidence
                reason = "AI模型預測置信度高"
            else:  # 否則使用公式結果
                final_result = formula_result
                confidence = abs(formula_score) / 10  # 將公式分數轉換為0-1之間的置信度
                reason = "使用赫茲公式預測結果"
        elif formula_result:
            final_result = formula_result
            confidence = abs(formula_score) / 10
            reason = "僅使用赫茲公式預測結果 (AI模型無法預測)"
        elif ai_result:
            final_result = ai_result
            confidence = ai_confidence
            reason = "僅使用AI模型預測結果 (公式無法預測)"
        else:
            reason = "AI模型和赫茲公式均無法預測"
    elif prediction_type == 'ai_only':
        if ai_result:
            final_result = ai_result
            confidence = ai_confidence
            reason = "僅使用AI模型預測"
        else:
            reason = "AI模型無法預測，請確保模型已訓練且有足夠的數據"
    elif prediction_type == 'formula_only':
        if formula_result:
            final_result = formula_result
            confidence = abs(formula_score) / 10
            reason = "僅使用赫茲公式預測"
        else:
            reason = "赫茲公式無法預測，請確保提供了有效的卡牌數據"
    
    current_app.logger.info(f"最終預測結果: {final_result}, 置信度: {confidence}, 原因: {reason}")
    
    return jsonify({
        "success": final_result is not None,
        "prediction": final_result,
        "confidence": confidence,
        "reason": reason,
        "ai_result": ai_result,
        "formula_result": formula_result,
        "formula_score": formula_score
    })
    data = request.json
    prediction_type = data.get('type', 'combined')
    player_cards = data.get('player_cards', [])
    banker_cards = data.get('banker_cards', [])
    
    ai_model = BaccaratAIModel(current_app.config['GAME_HISTORY_FILE'])
    
    # AI預測
    ai_result, ai_confidence = ai_model.predict_next()
    
    # 公式預測
    formula_result = None
    formula_score = 0
    if player_cards and banker_cards:
        formula_result, formula_score = CardFormula.hertz_formula(player_cards, banker_cards)
    
    # 綜合預測
    if prediction_type == 'combined' and formula_result and ai_result:
        # 如果AI和公式預測結果一致，使用該結果
        if formula_result == ai_result:
            final_result = formula_result
            confidence = ai_confidence
            reason = "AI模型和赫茲公式預測結果一致"
        # 如果不一致，根據AI的置信度決定
        elif ai_confidence > 0.7:  # 高置信度時使用AI結果
            final_result = ai_result
            confidence = ai_confidence
            reason = "AI模型預測置信度高"
        else:  # 否則使用公式結果
            final_result = formula_result
            confidence = abs(formula_score) / 10  # 將公式分數轉換為0-1之間的置信度
            reason = "使用赫茲公式預測結果"
    elif prediction_type == 'ai_only':
        final_result = ai_result
        confidence = ai_confidence
        reason = "僅使用AI模型預測"
    elif prediction_type == 'formula_only':
        final_result = formula_result
        confidence = abs(formula_score) / 10 if formula_result else 0
        reason = "僅使用赫茲公式預測"
    else:
        final_result = None
        confidence = 0
        reason = "無法預測，請確保提供足夠的數據"
    
    return jsonify({
        "success": final_result is not None,
        "prediction": final_result,
        "confidence": confidence,
        "reason": reason,
        "ai_result": ai_result,
        "formula_result": formula_result,
        "formula_score": formula_score
    })

@main_bp.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        ai_model = BaccaratAIModel(current_app.config['GAME_HISTORY_FILE'])
        ai_model.clear_history()
        # 重置牌靴
        global shoe_manager
        shoe_manager = ShoeManager()
        return jsonify({"success": True, "message": "歷史記錄已清除"})
    except Exception as e:
        current_app.logger.error(f"清除歷史記錄失敗: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@main_bp.route('/new_shoe', methods=['POST'])
def new_shoe():
    shoe_id = shoe_manager.new_shoe()
    return jsonify({
        "success": True,
        "message": f"已更換新牌靴 (ID: {shoe_id})",
        "shoe_info": shoe_manager.get_current_shoe_info()
    })