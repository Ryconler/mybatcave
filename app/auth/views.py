#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import render_template, redirect, request, url_for, flash,current_app
from flask_login import login_user, logout_user, login_required,current_user
from . import auth
from .. import db
from ..models import User,UrlResource
from .forms import RegistrationForm,LoginForm,ShareForm,ManageForm,EditForm,EditThemeForm,ChangePasswordForm
from datetime import datetime
from os import path,makedirs

@auth.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,
                  password=form.password.data,
                  register_date=datetime.utcnow())
        db.session.add(user)
        newuser = User.query.filter_by(username=form.username.data).first()
        basepath = path.abspath('.')
        upload_path1 = path.join(basepath, 'files', str(newuser.id), 'private')
        upload_path2 = path.join(basepath, 'files', str(newuser.id), 'public')
        makedirs(upload_path1)
        makedirs(upload_path2)
        flash('注册成功！')
        return redirect(request.args.get('next') or url_for('auth.login'))
    return render_template('auth/register.html',form=form)

@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            flash('登陆成功！')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误！')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出！')
    return redirect(url_for('main.index'))

@auth.route('/share',methods=['GET','POST'])
@login_required
def share():
    from sqlalchemy.exc import IntegrityError
    form = ShareForm()
    if form.validate_on_submit():
        if (form.url.data)[0:4] == 'http':
            url = form.url.data
        else:
            url ='http://' + form.url.data


        resource = UrlResource(title=form.title.data,
                                   theme=form.theme.data,
                                   url=url,
                                   like_num=0,
                                   author_id=current_user.id,
                                   post_date=datetime.utcnow())

        db.session.add(resource)
        flash('分享成功！')

        return redirect(request.args.get('next') or url_for('main.url_resources'))

    return render_template('auth/share.html',form=form)


@auth.route('/resources-manage',methods=['GET','POST'])
@login_required
def resources_manage():
    if current_user.username  not in current_app.config['ADMIN']:
        return redirect(url_for('main.index'))
    form=ManageForm()
    page = request.args.get('page', 1, type=int)
    pagination = UrlResource.query.order_by(UrlResource.post_date.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts=pagination.items
    return render_template('auth/resources_manage.html',pagination=pagination,posts=posts,form=form)

@auth.route('/edit-title/<int:id>',methods=['GET','POST'])
@login_required
def edit_title(id):
    if current_user.username  not in current_app.config['ADMIN']:
        return redirect(url_for('main.index'))
    post=UrlResource.query.get_or_404(id)
    form = EditForm()
    if form.validate_on_submit():
        post.title=form.input.data
        db.session.add(post)
        flash('更改成功！')
        return redirect(url_for('.resources_manage'))
    return render_template('auth/edit.html',form=form)

@auth.route('/edit-url/<int:id>',methods=['GET','POST'])
@login_required
def edit_url(id):
    if current_user.username  not in current_app.config['ADMIN']:
        return redirect(url_for('main.index'))
    post=UrlResource.query.get_or_404(id)
    form = EditForm()
    if form.validate_on_submit():
        post.url=form.input.data
        db.session.add(post)
        flash('更改成功！')
        return redirect(url_for('.resources_manage'))
    return render_template('auth/edit.html',form=form)

@auth.route('/edit-theme/<int:id>',methods=['GET','POST'])
@login_required
def edit_theme(id):
    if current_user.username  not in current_app.config['ADMIN']:
        return redirect(url_for('main.index'))
    post=UrlResource.query.get_or_404(id)
    form = EditThemeForm()
    if form.validate_on_submit():
        post.theme=form.input.data
        db.session.add(post)
        flash('更改成功！')
        return redirect(url_for('.resources_manage'))
    return render_template('auth/edit.html',form=form)

@auth.route('/delete/<int:id>',methods=['GET','POST'])
@login_required
def delete(id):
    if current_user.username  not in current_app.config['ADMIN']:
        return redirect(url_for('main.index'))
    resource = UrlResource.query.filter_by(id=id).first()
    if resource is None:
        flash('资源不存在！')
        return redirect(url_for('.resources_manage'))
    db.session.delete(resource)
    flash('删除成功！')
    return redirect(url_for('.resources_manage'))

@auth.route('/users-manage',methods=['GET','POST'])
@login_required
def users_manage():
    if current_user.username  not in current_app.config['ADMIN']:
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    users=pagination.items
    return render_template('auth/users_manage.html',pagination=pagination,users=users)

@auth.route('/manage-passowrd/<int:id>',methods=['GET','POST'])
@login_required
def manage_password(id):
    if current_user.username  not in current_app.config['ADMIN']:
        return redirect(url_for('main.index'))
    user=User.query.get_or_404(id)
    form = EditForm()
    if form.validate_on_submit():
        user.password= form.input.data
        db.session.add(user)
        flash('更改成功！')
        return redirect(url_for('.users_manage'))
    return render_template('auth/edit.html', form=form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('你的密码已更改！')
            return redirect(url_for('main.index'))
        else:
            flash('密码无效！')
    return render_template("auth/change_password.html", form=form)

