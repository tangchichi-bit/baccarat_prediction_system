from flask import Blueprint

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# 導入路由處理函數
from . import main, api