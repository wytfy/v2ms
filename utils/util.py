from configs.db import db
from requests import post, get
from sqlalchemy import func
from models.Inbound import Inbound
from models.Host import Host
from uuid import uuid1
from json import load
from dateutil.relativedelta import relativedelta
from datetime import datetime


# 验证服务器是否连接成功
def verify_host(host):
    if get_cookies(host):
        return True
    else:
        return False


# 获取服务器cookies
def get_cookies(host):
    if host.port == 80:
        url = 'http://' + host.addr + '/login'
    else:
        url = 'http://' + host.addr + ':' + str(host.port) + '/login'
    params = {'username': host.manager, 'password': host.password}
    r = post(url, data=params)
    return r.cookies


# 统计服务器中的用户数量
def get_count(host):
    count = db.session.query(func.count(Inbound.id)).filter(Inbound.host == host.host).scalar()
    return count


# 通知远程服务器配置发生变化
def info_remote_server(host):
    cookies = get_cookies(host)
    if host.port == 80:
        api = 'http://' + host.addr + '/v2ray/api/conf_change'
    else:
        api = 'http://' + host.addr + ':' + str(host.port) + '/v2ray/api/conf_change'
    r = get(api, cookies=cookies).text
    return r


# 同步服务器用户数量
def host_sync(host):
    host.user_num = get_count(host)
    db.session.add(host)
    db.session.commit()


# 返回服务器选项
def get_host_name():
    fields = []
    hosts = Host.query.all()
    for host in hosts:
        fields.append(host.to_select_field())
    return fields


# 辅助数据，用于存储默认的配置
config = {'listen': '0.0.0.0',
          'protocol': 'vmess',
          'stream_settings': '{"network":"ws","security":"none","wsSettings":{"path":"/","headers":{}}}',
          'sniffing': '{"enabled":true,"destOverride":["http","tls"]}'
          }


# 用于产生uuid配置
def get_settings():
    return '{"clients":[{"id":"' + str(uuid1()) + '","alterId":64}],"disableInsecureEncryption":false}'


# 用于读取json文件
def open_json(path):
    f = open(path, encoding='utf-8')
    content = load(f)
    return content


# 用于检查用户是否过期
def user_check(inbound):
    stop_date = inbound.start_data + relativedelta(months=inbound.lease_month)
    if stop_date.__le__(datetime.now()):
        return False
    else:
        return True


# 创建动态应用
def create_app():
    from flask import Flask
    app = Flask(__name__)
    db.init_app(app)
    return app
