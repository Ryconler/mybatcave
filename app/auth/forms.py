#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField,SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class RegistrationForm(FlaskForm):
    username=StringField('用户名',validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          '用户名只能包含字母、数字、 '
                                          '点、或下划线！且至少含有一个英文！')])
    password = PasswordField('密码', validators=[
        Required(), EqualTo('password2', message='两次密码不相同！')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用！')

class LoginForm(FlaskForm):
    username=StringField('用户名',validators=[Required()])
    password = PasswordField('密码', validators=[Required()])
    remember_me=BooleanField("记住我")
    submit = SubmitField('登录')

class ShareForm(FlaskForm):
    title=StringField('标题',validators=[Required(), Length(1, 128)])
    url=TextAreaField('链接地址',validators=[Required(),Length(1,128)])
    theme=SelectField('资源种类',validators=[Required()],choices=[('资源链接','资源链接'),('视频网站','视频网站'),('直播网站','直播网站'),('游戏网站','游戏网站'),('购物网站','购物网站'),
                                                              ('漫画网站', '漫画网站'),('小说网站','小说网站'),('社区网站','社区网站'),('教学网站','教学网站'),('技术论坛','技术论坛'),
                                                              ('素材网站','素材网站'),('招聘网站','招聘网站'),('旅游网站','旅游网站'),('搜索网站', '搜索网站'),('其他','其他')])
    submit=SubmitField('提交')


class ManageForm(FlaskForm):
    id=StringField('id',validators=[Required()])
    title=StringField('title',validators=[Required(),Length(1,128)])
    url = StringField('url', validators=[Required(), Length(1, 128)])
    theme=StringField('theme',validators=[Required()])



class EditForm(FlaskForm):
    input=StringField('新内容',validators=[Required()])
    submit = SubmitField('保存')

class EditThemeForm(FlaskForm):
    input = SelectField('新主题', choices=[('资源链接', '资源链接'), ('视频网站', '视频网站'), ('直播网站', '直播网站'), ('游戏网站', '游戏网站'),
                                              ('购物网站', '购物网站'),
                                              ('漫画网站', '漫画网站'), ('小说网站', '小说网站'), ('社区网站', '社区网站'), ('教学网站', '教学网站'),
                                              ('技术论坛', '技术论坛'),
                                              ('素材网站', '素材网站'), ('招聘网站', '招聘网站'), ('旅游网站', '旅游网站'), ('搜索网站', '搜索网站'),
                                              ('其他', '其他')])
    submit = SubmitField('保存')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='两次密码不相同！')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('保存更改')