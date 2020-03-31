from flask_bootstrap import Bootstrap
from datetime import timedelta
from flask_login import LoginManager
from utils.util import open_json
from flask_migrate import Migrate

# 数据库配置
conf = open_json('configs/setting.json')
db_addr = conf['db_addr']
# SQLALCHEMY_DATABASE_URI = 'postgresql://v2:123456@192.168.2.181:5432/v2_ui'
SQLALCHEMY_DATABASE_URI = db_addr
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

# 秘钥设置
SECRET_KEY = 'HARD TO GUSESS STRING'

# css调试立即生效
SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)

# bootstrap配置
bootstrap = Bootstrap()

# login manager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

# flask-migrate设置
migrate = Migrate()
