from models.Inbound import Inbound
from models.Host import Host
from utils.util import user_check, info_remote_server
from configs.db import db
from utils.util import create_app


# 用于定时监控用户是否过期
def user_monitor():
    app = create_app()
    with app.app_context():
        print('start jobs')
        change = False
        inbounds = Inbound.query.filter_by(enable=True).all()
        if inbounds is not None:
            for inbound in inbounds:
                if not user_check(inbound):
                    inbound.enable = False
                    db.session.add(inbound)
                    change = True
            db.session.commit()
        if change:
            hosts = Host.query.all()
            for host in hosts:
                info_remote_server(host)


def test():
    print("test")