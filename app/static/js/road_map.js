// 路單圖表管理
class RoadMap {
    constructor(containerId, rows = 6, cols = 12) {
        this.container = document.getElementById(containerId);
        this.rows = rows;
        this.cols = cols;
        this.history = [];
        this.currentPosition = { row: 0, col: 0 };
        
        this.init();
    }
    
    init() {
        // 清空容器
        this.container.innerHTML = '';
        
        // 創建網格
        for (let r = 0; r < this.rows; r++) {
            for (let c = 0; c < this.cols; c++) {
                const cell = document.createElement('div');
                cell.className = 'road-map-cell empty-cell';
                cell.dataset.row = r;
                cell.dataset.col = c;
                this.container.appendChild(cell);
            }
        }
        
        // 載入歷史數據
        this.loadHistory();
    }
    
    loadHistory() {
        fetch('/get_history')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.history) {
                    this.history = data.history;
                    this.renderRoadMap();
                }
            })
            .catch(error => {
                console.error('載入歷史數據失敗:', error);
            });
    }
    
    renderRoadMap() {
        // 清空所有單元格
        const cells = this.container.querySelectorAll('.road-map-cell');
        cells.forEach(cell => {
            cell.className = 'road-map-cell empty-cell';
            cell.textContent = '';
        });
        
        // 重置當前位置
        this.currentPosition = { row: 0, col: 0 };
        
        // 繪製歷史結果
        for (const result of this.history) {
            this.addResult(result);
        }
    }
    
    addResult(result) {
        // 檢查是否需要換列
        if (this.currentPosition.row >= this.rows) {
            this.currentPosition.row = 0;
            this.currentPosition.col++;
            
            // 檢查是否超出範圍
            if (this.currentPosition.col >= this.cols) {
                // 向左移動所有結果
                this.shiftRoadMapLeft();
                this.currentPosition.col = this.cols - 1;
            }
        }
        
        // 獲取當前單元格
        const cell = this.container.querySelector(
            `.road-map-cell[data-row="${this.currentPosition.row}"][data-col="${this.currentPosition.col}"]`
        );
        
        if (cell) {
            // 設置單元格樣式和內容
            cell.className = 'road-map-cell';
            
            if (result === 'banker') {
                cell.classList.add('banker-cell');
                cell.textContent = 'B';
            } else if (result === 'player') {
                cell.classList.add('player-cell');
                cell.textContent = 'P';
            } else if (result === 'tie') {
                cell.classList.add('tie-cell');
                cell.textContent = 'T';
            }
            
            // 更新位置
            this.currentPosition.row++;
        }
    }
    
    shiftRoadMapLeft() {
        // 將所有結果向左移動一列
        for (let c = 0; c < this.cols - 1; c++) {
            for (let r = 0; r < this.rows; r++) {
                const currentCell = this.container.querySelector(
                    `.road-map-cell[data-row="${r}"][data-col="${c}"]`
                );
                const nextCell = this.container.querySelector(
                    `.road-map-cell[data-row="${r}"][data-col="${c+1}"]`
                );
                
                if (currentCell && nextCell) {
                    currentCell.className = nextCell.className;
                    currentCell.textContent = nextCell.textContent;
                }
            }
        }
        
        // 清空最後一列
        for (let r = 0; r < this.rows; r++) {
            const cell = this.container.querySelector(
                `.road-map-cell[data-row="${r}"][data-col="${this.cols-1}"]`
            );
            
            if (cell) {
                cell.className = 'road-map-cell empty-cell';
                cell.textContent = '';
            }
        }
    }
}

// 顯示通知消息的函數
function showNotification(message, type) {
    // 查找通知容器
    let flashContainer = document.querySelector('.flash-messages');
    
    // 如果找不到容器，則在卡片內容區域的頂部創建一個
    if (!flashContainer) {
        // 查找當前頁面的卡片內容區域
        const cardBody = document.querySelector('.card-body');
        if (cardBody) {
            flashContainer = document.createElement('div');
            flashContainer.className = 'flash-messages mb-3';
            cardBody.insertBefore(flashContainer, cardBody.firstChild);
        } else {
            // 如果找不到卡片內容區域，則在頁面頂部創建一個
            flashContainer = document.createElement('div');
            flashContainer.className = 'flash-messages mb-3';
            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(flashContainer, container.firstChild);
            } else {
                // 最後的後備方案
                document.body.insertBefore(flashContainer, document.body.firstChild);
            }
        }
    }
    
    // 創建通知元素
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 添加到容器
    flashContainer.appendChild(alertDiv);
    
    // 5秒後自動關閉
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => {
            alertDiv.remove();
        }, 150);
    }, 5000);
}

// 更新牌靴信息的函數
function updateShoeInfo(shoeInfo) {
    if (shoeInfo) {
        const shoeIdElement = document.getElementById('current-shoe-id');
        const currentRoundElement = document.getElementById('current-round');
        const maxRoundsElement = document.getElementById('max-rounds');
        
        if (shoeIdElement) shoeIdElement.textContent = shoeInfo.shoe_id;
        if (currentRoundElement) currentRoundElement.textContent = shoeInfo.current_round;
        if (maxRoundsElement) maxRoundsElement.textContent = shoeInfo.max_rounds;
    }
}

// 頁面載入時初始化路單
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('road-map')) {
        const roadMap = new RoadMap('road-map');
        
        // 添加結果按鈕事件
        document.getElementById('btn-banker').addEventListener('click', function() {
            addGameResult('banker');
        });
        
        document.getElementById('btn-player').addEventListener('click', function() {
            addGameResult('player');
        });
        
        document.getElementById('btn-tie').addEventListener('click', function() {
            addGameResult('tie');
        });
        
        // 清除歷史按鈕事件
        document.getElementById('btn-clear-history').addEventListener('click', function() {
            clearHistory();
        });
        
        // 更換牌靴按鈕事件
        document.getElementById('btn-new-shoe').addEventListener('click', function() {
            newShoe();
        });
        
        // 添加遊戲結果
        function addGameResult(result) {
            // 獲取卡牌值
            const playerCards = [
                document.getElementById('player-card-1')?.value || '',
                document.getElementById('player-card-2')?.value || '',
                document.getElementById('player-card-3')?.value || ''
            ].filter(Boolean);
            
            const bankerCards = [
                document.getElementById('banker-card-1')?.value || '',
                document.getElementById('banker-card-2')?.value || '',
                document.getElementById('banker-card-3')?.value || ''
            ].filter(Boolean);
            
            fetch('/add_result', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    result: result,
                    player_cards: playerCards,
                    banker_cards: bankerCards
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    roadMap.addResult(result);
                    roadMap.history.push(result);
                    
                    // 更新牌靴信息
                    if (data.shoe_info) {
                        updateShoeInfo(data.shoe_info);
                    }
                    
                    // 清空卡牌選擇
                    resetCardSelections();
                    
                    showNotification(`已添加 ${result === 'banker' ? '莊家' : result === 'player' ? '閒家' : '和局'} 結果`, 'success');
                } else {
                    showNotification(`添加結果失敗: ${data.error}`, 'danger');
                }
            })
            .catch(error => {
                console.error('添加結果失敗:', error);
                showNotification('添加結果失敗，請稍後再試', 'danger');
            });
        }
        
        // 清除歷史記錄
        function clearHistory() {
            if (confirm('確定要清除所有歷史記錄嗎？這將重置所有數據。')) {
                fetch('/clear_history', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        roadMap.history = [];
                        roadMap.renderRoadMap();
                        showNotification('歷史記錄已清除', 'success');
                        
                        // 重置牌靴信息
                        updateShoeInfo({shoe_id: 1, current_round: 0, max_rounds: 80});
                    } else {
                        showNotification(`清除歷史記錄失敗: ${data.error}`, 'danger');
                    }
                })
                .catch(error => {
                    console.error('清除歷史記錄失敗:', error);
                    showNotification('清除歷史記錄失敗，請稍後再試', 'danger');
                });
            }
        }
        
        // 更換新牌靴
        function newShoe() {
            fetch('/new_shoe', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    
                    // 更新牌靴信息
                    if (data.shoe_info) {
                        updateShoeInfo(data.shoe_info);
                    }
                } else {
                    showNotification(`更換牌靴失敗: ${data.error}`, 'danger');
                }
            })
            .catch(error => {
                console.error('更換牌靴失敗:', error);
                showNotification('更換牌靴失敗，請稍後再試', 'danger');
            });
        }
        
        // 重置卡牌選擇
        function resetCardSelections() {
            const cardSelects = document.querySelectorAll('select[id^="player-card-"], select[id^="banker-card-"]');
            cardSelects.forEach(select => {
                select.value = '';
            });
        }
    }
});