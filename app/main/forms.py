#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,SelectField,SubmitField,TextAreaField,BooleanField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileRequired
from ..models import User

class SearchForm(FlaskForm):
    search=StringField('',validators=[Required()])
    submit=SubmitField('搜索')


class UploadForm(FlaskForm):
    myfile=FileField('选择文件',validators=[FileRequired()])
    filename=StringField('给你的文件取个名字',validators=[Required()])
    describe=TextAreaField('描述一下你的文件（可选）',validators=[Length(0,128)])
    auth=BooleanField('仅自己可见')
    submit=SubmitField('上传')
