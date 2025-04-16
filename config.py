import os

class Config:
    """基本配置類"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    
    # 數據存儲路徑
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    GAME_HISTORY_FILE = os.path.join(DATA_DIR, 'game_history.json')
    MODEL_DIR = os.path.join(DATA_DIR, 'models')
    
    # 確保目錄存在
    @classmethod
    def init_app(cls, app):
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.MODEL_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    
class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}