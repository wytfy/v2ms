from flask import Blueprint, url_for, redirect
from flask import render_template, request
from forms.form import ServerForm, UserForm
from models.Host import Host
from utils.util import verify_host, get_count, info_remote_server,\
    host_sync, get_host_name, config, get_settings
from models.Inbound import Inbound
from configs.db import db
from dateutil.relativedelta import relativedelta
from datetime import datetime
from flask_login import login_required
v2ms_bp = Blueprint('v2ms_bp', __name__, url_prefix='/v2ms')


# 用户分页（重构）
@v2ms_bp.route('/user_list', methods=['GET', 'POST'])
@login_required
def user_list():
    page =request.args.get('page', type=int)
    if not page:
        page = 1
    inbounds = Inbound.query.order_by(Inbound.id.asc()).paginate(page=page, per_page=8)
    hosts = Host.query.all()
    server_form = ServerForm()
    user_form = UserForm()
    user_form.host.choices = get_host_name()
    # 增加服务器
    if server_form.validate_on_submit():
        host = Host(host=server_form.host.data, addr=server_form.addr.data, port=server_form.port.data,
                    manager=server_form.manager.data, password=server_form.password.data)
        host.user_num = get_count(host)
        if verify_host(host):
            db.session.add(host)
            db.session.commit()
        return redirect(url_for('v2ms_bp.user_list'))
    # 增加用户
    if user_form.validate_on_submit():
        inbound = Inbound(port=user_form.port.data, listen=config['listen'], protocol=config['protocol']
                          , settings=get_settings(), stream_settings=config['stream_settings'],
                          sniffing=config['sniffing'], remark=user_form.remark.data)
        inbound.host = user_form.host.choices[0][1]
        inbound.lease_month = user_form.lease_month.data
        db.session.add(inbound)
        db.session.commit()
        server_changed = Host.query.filter_by(host=inbound.host).first()
        host_sync(server_changed)
        info_remote_server(server_changed)
        return redirect(url_for('v2ms_bp.user_list'))
    return render_template('user_list.html', inbounds=inbounds, hosts=hosts, server_form=server_form, user_form=user_form)


# 删除服务器，只删除服务器数据不删除用户数据
@v2ms_bp.route('/del', methods=['GET'])
@login_required
def server_delete():
    uid = request.args.get('id', type=int)
    host = Host.query.filter_by(id=uid).first()
    db.session.delete(host)
    db.session.commit()
    return '{"del": "True"}'


# 删除用户配置
@v2ms_bp.route('/user_del')
@login_required
def user_del():
    uid = request.args.get('uid',type=int)
    user = Inbound.query.filter_by(id=uid).first()
    host = Host.query.filter_by(host=user.host).first()
    db.session.delete(user)
    db.session.commit()
    # 更新远程配置
    info_remote_server(host)
    # 同步用户数量
    host_sync(host)
    return '{"del": "True"}'


#  停用该用户
@v2ms_bp.route('/user_suspend')
@login_required
def user_suspend():
    uid = request.args.get('uid', type=int)
    user = Inbound.query.filter_by(id=uid).first()
    host = Host.query.filter_by(host=user.host).first()
    user.enable = not user.enable
    db.session.add(user)
    db.session.commit()
    info_remote_server(host)
    return str(user.enable)


# 续期
@v2ms_bp.route('/add_month')
@login_required
def add_month():
    uid = request.args.get('uid',type=int)
    inbound = Inbound.query.filter_by(id=uid).first()
    host = Host.query.filter_by(host=inbound.host).first()
    inbound.lease_month = inbound.lease_month + 1
    db.session.add(inbound)
    db.session.commit()
    info_remote_server(host)
    stop_date = inbound.start_data + relativedelta(months=inbound.lease_month)
    stop_date = stop_date.strftime('%Y-%m-%d')
    return '{"lease_month"' + ':' + '"' + str(inbound.lease_month) + '"' + ',' + '"stop_date": ' + '"' + stop_date + '"}'


# 更新配置
@v2ms_bp.route('/update')
@login_required
def update():
    uid = request.args.get('uid', type=int)
    inbound = Inbound.query.filter_by(id=uid).first()
    host = Host.query.filter_by(host=inbound.host).first()
    inbound.settings = get_settings()
    db.session.add(inbound)
    db.session.commit()
    info_remote_server(host)
    uuid = get_uuid(inbound.settings)
    return '{"uuid" : "' + uuid + '"}'


# 重置
@v2ms_bp.route('/reset')
@login_required
def reset():
    uid = request.args.get('uid', type=int)
    inbound = Inbound.query.filter_by(id=uid).first()
    inbound.start_data = datetime.now()
    inbound.lease_month = 0
    db.session.add(inbound)
    db.session.commit()
    stop_date = inbound.start_data + relativedelta(months=inbound.lease_month)
    stop_date = stop_date.strftime('%Y-%m-%d')
    return '{"lease_month"' + ':' + '"' + str(inbound.lease_month) + '"' + ',' + '"stop_date": ' + '"' + stop_date + '"}'


# 开启定时扫描任务
@v2ms_bp.route('/scanf')
def scanf():
    from utils.aps import start_jobs
    start_jobs()
    return redirect(url_for('v2ms_bp.server_user_list'))


# 404处理
@v2ms_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 500处理
@v2ms_bp.errorhandler(500)
def internal_server_error(e):
    return 'internal server error', 500


# 过滤器：日期加上月份
@v2ms_bp.app_template_filter('add_to_months')
def add_to_months(datetime, months):
    return datetime + relativedelta(months=months)


# 过滤器：只显示日期
@v2ms_bp.app_template_filter('date')
def only_show_date(datetime):
    return datetime.strftime('%Y-%m-%d')


# 过滤器：启用状态转化
@v2ms_bp.app_template_filter('status')
def show_status(enable):
    if enable:
        return '是'
    else:
        return '否'


# 过滤器：获取UUID
@v2ms_bp.app_template_filter('uuid')
def get_uuid(settings):
    return settings.lstrip('{"clients":[{"id":"').rstrip('","alterId":64}],"disableInsecureEncryption":false}')
