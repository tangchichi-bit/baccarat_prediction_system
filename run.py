import os
from app import create_app

# 從環境變量獲取配置類型，默認為開發環境
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)