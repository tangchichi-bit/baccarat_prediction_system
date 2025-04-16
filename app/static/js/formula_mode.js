// 公式模式頁面腳本

document.addEventListener('DOMContentLoaded', function() {
    // 計算按鈕事件
    document.getElementById('btn-calculate').addEventListener('click', function() {
        calculatePrediction();
    });
    
    // 計算預測
    function calculatePrediction() {
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
        
        // 檢查是否有足夠的卡牌
        if (playerCards.length < 2 || bankerCards.length < 2) {
            showNotification('請至少輸入閒家和莊家的前兩張牌', 'warning');
            return;
        }
        
        // 發送預測請求
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'formula_only',
                player_cards: playerCards,
                banker_cards: bankerCards
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPredictionResult(data);
                displayCalculationDetails(data);
            } else {
                showNotification(`預測失敗: ${data.reason}`, 'danger');
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
    
    // 顯示計算詳情
    function displayCalculationDetails(data) {
        document.getElementById('advantage-value').textContent = data.formula_score ? data.formula_score.toFixed(2) : '-';
        
        // 計算閒家點數
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
        
        const playerPoint = calculateBaccaratPoint(playerCards);
        const bankerPoint = calculateBaccaratPoint(bankerCards);
        
        // 顯示頻率值
        let playerFrequency = 0;
        if ([7, 8, 9].includes(playerPoint)) {
            playerFrequency = 2;
        } else if ([0, 1, 3, 4].includes(playerPoint)) {
            playerFrequency = 1;
        } else if ([2, 5, 6].includes(playerPoint)) {
            playerFrequency = -5;
        }
        
        let bankerFrequency = 0;
        if ([7, 8, 9].includes(bankerPoint)) {
            bankerFrequency = 3;
        } else if ([0, 1, 3, 4, 6].includes(bankerPoint)) {
            bankerFrequency = 2;
        } else if ([2, 5].includes(bankerPoint)) {
            bankerFrequency = -5;
        }
        
        document.getElementById('player-frequency').textContent = playerFrequency;
        document.getElementById('banker-frequency').textContent = bankerFrequency;
        document.getElementById('hertz-result').textContent = data.formula_score ? data.formula_score.toFixed(2) : '-';
    }
});