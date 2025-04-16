import json
import os

def ensure_file_exists(file_path, default_content=None):
    """確保文件存在，如果不存在則創建"""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            if default_content is not None:
                json.dump(default_content, f)
            else:
                f.write('[]')

def format_card_value(value):
    """格式化卡牌值顯示"""
    if value == 1:
        return 'A'
    elif value == 10:
        return '10'
    elif value == 11:
        return 'J'
    elif value == 12:
        return 'Q'
    elif value == 13:
        return 'K'
    else:
        return str(value)