// 通用函數

// 顯示通知
function showNotification(message, type = 'info') {
    // 創建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 添加到頁面
    const container = document.querySelector('.container');
    container.insertBefore(notification, container.firstChild);
    
    // 自動關閉
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// 格式化卡牌值顯示
function formatCardValue(value) {
    if (!value) return '';
    value = parseInt(value);
    if (value === 1) return 'A';
    if (value === 11) return 'J';
    if (value === 12) return 'Q';
    if (value === 13) return 'K';
    return value.toString();
}

// 計算百家樂點數
function calculateBaccaratPoint(cards) {
    if (!cards || !cards.length) return 0;
    
    let sum = 0;
    for (const card of cards) {
        if (!card) continue;
        const value = parseInt(card);
        if (value >= 10) {
            sum += 0;
        } else {
            sum += value;
        }
    }
    
    return sum % 10;
}

// 更新牌靴信息
function updateShoeInfo(shoeInfo) {
    if (shoeInfo) {
        document.getElementById('current-shoe-id').textContent = shoeInfo.shoe_id;
        document.getElementById('current-round').textContent = shoeInfo.current_round;
        document.getElementById('max-rounds').textContent = shoeInfo.max_rounds;
    }
}