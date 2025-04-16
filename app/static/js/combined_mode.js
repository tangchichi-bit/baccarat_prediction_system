// 綜合預測模式頁面腳本

document.addEventListener('DOMContentLoaded', function() {
    // 訓練模型按鈕事件
    document.getElementById('btn-train-model').addEventListener('click', function() {
        trainModel();
    });
    
    // 預測按鈕事件
    document.getElementById('btn-predict').addEventListener('click', function() {
        predictNextResult();
    });
    
    // 訓練模型
    function trainModel() {
        document.getElementById('training-status').textContent = '訓練中...';
        
        fetch('/train_model', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('training-status').textContent = '訓練完成';
                document.getElementById('model-accuracy').textContent = `${(data.accuracy * 100).toFixed(2)}%`;
                showNotification(data.message, 'success');
            } else {
                document.getElementById('training-status').textContent = '訓練失敗';
                showNotification(`訓練模型失敗: ${data.message}`, 'danger');
            }
        })
        .catch(error => {
            console.error('訓練模型失敗:', error);
            document.getElementById('training-status').textContent = '訓練失敗';
            showNotification('訓練模型失敗，請稍後再試', 'danger');
        });
    }
    
    // 預測下一局結果
    function predictNextResult() {
        // 獲取卡牌值
        const playerCards = [
            document.getElementById('player-card-1').value,
            document.getElementById('player-card-2').value,
            document.getElementById('player-card-3').value
        ].filter(Boolean);
        
        const bankerCards = [
            document.getElementById('banker-card-1').value,
            document.getElementById('banker-card-2').value,
            document.getElementById('banker-card-3').value
        ].filter(Boolean);
        
        // 發送預測請求
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'combined',
                player_cards: playerCards,
                banker_cards: bankerCards
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPredictionResult(data);
                displayPredictionDetails(data);
            } else {
                showNotification(`預測失敗: ${data.reason}`, 'warning');
            }
        })
        .catch(error => {
            console.error('預測失敗:', error);
            showNotification('預測失敗，請稍後再試', 'danger');
        });
    }
    
    // 顯示預測結果
    function displayPredictionResult(data) {
        const resultContainer = document.getElementById('prediction-result');
        resultContainer.innerHTML = '';
        
        const predictionClass = data.prediction === 'banker' ? 'prediction-banker' : 
                               data.prediction === 'player' ? 'prediction-player' : 'prediction-tie';
        
        const predictionText = data.prediction === 'banker' ? '莊家' : 
                              data.prediction === 'player' ? '閒家' : '和局';
        
        const resultDiv = document.createElement('div');
        resultDiv.className = `prediction-result ${predictionClass}`;
        resultDiv.innerHTML = `
            <h3>預測結果: ${predictionText}</h3>
            <p>置信度: ${Math.round(data.confidence * 100)}%</p>
            <div class="confidence-bar">
                <div class="confidence-level" style="width: ${Math.round(data.confidence * 100)}%">
                    ${Math.round(data.confidence * 100)}%
                </div>
            </div>
        `;
        
        resultContainer.appendChild(resultDiv);
    }
    
    // 顯示預測詳情
    function displayPredictionDetails(data) {
        document.getElementById('ai-prediction').textContent = data.ai_result ? 
            (data.ai_result === 'banker' ? '莊家' : data.ai_result === 'player' ? '閒家' : '和局') : '-';
        
        document.getElementById('ai-confidence').textContent = data.ai_result ? 
            `${Math.round(data.confidence * 100)}%` : '-';
        
        document.getElementById('formula-prediction').textContent = data.formula_result ? 
            (data.formula_result === 'banker' ? '莊家' : data.formula_result === 'player' ? '閒家' : '和局') : '-';
        
        document.getElementById('formula-score').textContent = data.formula_score ? 
            data.formula_score.toFixed(2) : '-';
        
        document.getElementById('prediction-reason').textContent = data.reason || '-';
    }
});