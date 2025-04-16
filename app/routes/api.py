from flask import jsonify, request, current_app
from app.routes import api_bp
from app.models.ai_model import BaccaratAIModel
from app.models.card_formula import CardFormula

@api_bp.route('/predict', methods=['POST'])
def api_predict():
    data = request.json
    
    if not data:
        return jsonify({"error": "無效的請求數據"}), 400
    
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
        if formula_result == ai_result:
            final_result = formula_result
            confidence = ai_confidence
            reason = "AI模型和赫茲公式預測結果一致"
        elif ai_confidence > 0.7:
            final_result = ai_result
            confidence = ai_confidence
            reason = "AI模型預測置信度高"
        else:
            final_result = formula_result
            confidence = abs(formula_score) / 10
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
        "prediction": final_result,
        "confidence": confidence,
        "reason": reason,
        "ai_result": ai_result,
        "formula_result": formula_result,
        "formula_score": formula_score
    })

@api_bp.route('/history', methods=['GET'])
def api_history():
    try:
        ai_model = BaccaratAIModel(current_app.config['GAME_HISTORY_FILE'])
        history = ai_model._load_history()
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/add_result', methods=['POST'])
def api_add_result():
    data = request.json
    
    if not data:
        return jsonify({"error": "無效的請求數據"}), 400
    
    result = data.get('result')
    player_cards = data.get('player_cards', [])
    banker_cards = data.get('banker_cards', [])
    
    if result not in ['player', 'banker', 'tie']:
        return jsonify({"error": "無效的結果"}), 400
    
    try:
        ai_model = BaccaratAIModel(current_app.config['GAME_HISTORY_FILE'])
        ai_model.add_game_result(result, player_cards, banker_cards)
        return jsonify({"message": "結果已添加"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500