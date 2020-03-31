from flask import Flask
from configs.db import db
from configs.setting import bootstrap,login_manager, migrate
from routers.router import v2ms_bp
from routers.auth import auth
from flask_script import Manager, Server
from flask_migrate import MigrateCommand


v2ms = Flask(__name__)
v2ms.config.from_pyfile('configs/setting.py')
db.init_app(v2ms)
login_manager.init_app(v2ms)
migrate.init_app(v2ms, db)
v2ms.register_blueprint(v2ms_bp)
v2ms.register_blueprint(auth)
manager = Manager(v2ms)
# flask-script debug 模式
manager.add_command("runserver", Server(use_debugger=True))
# 增加migrate命令
manager.add_command('db', MigrateCommand)
bootstrap.init_app(v2ms)


@manager.command
def init():
    '''安装前初始化'''
    from utils.util import open_json
    from models.Rooter import Rooter
    db.drop_all()
    db.create_all()
    content = open_json('configs/setting.json')
    rooter = Rooter()
    rooter.username = content['username']
    rooter.password = content['password']
    db.session.add(rooter)
    db.session.commit()


@manager.command
def deploy():
    '''部署升级时数据库迁移'''
    from flask_migrate import upgrade
    upgrade()


if __name__ == '__main__':
    manager.run()
