from flask import Flask
from config import config
import os

def create_app(config_name):
    """創建 Flask 應用實例"""
    app = Flask(__name__)
    
    # 從配置字典中獲取配置類
    config_class = config[config_name]
    app.config.from_object(config_class)
    
    # 確保數據目錄存在
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(app.config['MODEL_DIR'], exist_ok=True)
    
    # 註冊藍圖
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app