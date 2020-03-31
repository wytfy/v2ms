from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired


class ServerForm(FlaskForm):
    host = StringField('新增域名：',validators=[DataRequired()])
    addr = StringField('后台地址：', validators=[DataRequired()])
    port = IntegerField('后台端口：', default=80)
    manager = StringField('管理员账号：', validators=[DataRequired()])
    password = PasswordField('管理员密码：', validators=[DataRequired()])
    submit = SubmitField('提交', validators=[DataRequired()])


# 用户添加表格
class UserForm(FlaskForm):
    remark = StringField('备注：',validators=[DataRequired()])
    port = IntegerField('端口：',validators=[DataRequired()])
    host = SelectField('服务器：', validators=[DataRequired('选择服务器')], coerce=int,
                       render_kw={'id': 'host'}, choices='')
    lease_month = IntegerField('租用期(月)：', validators=[DataRequired()])
    submit = SubmitField('新增', validators=[DataRequired()])


# root 登录表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')
