#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import render_template, redirect, url_for, request, current_app, flash, make_response, send_from_directory
from flask_login import login_required, current_user
from werkzeug import secure_filename
from .forms import SearchForm,UploadForm
from ..models import User,UrlResource,Permission,Like,Files
from .. import db
from . import main
from os import path,listdir,makedirs
from random import random
import subprocess




@main.route('/',methods=['GET','POST'])
def index():
    users = User()
    pagination = UrlResource.query.order_by(UrlResource.post_date.desc()).paginate()
    post=pagination.items
    posts=post[0:5]
    return render_template('index.html',posts=posts,users=users)

@main.route('/url-resources',methods=['GET','POST'])
@login_required
def url_resources():
    form=SearchForm()
    users=User()
    page = request.args.get('page', 1, type=int)
    hotpagination = UrlResource.query.order_by(UrlResource.like_num.desc()).all()

    sort_hot=False
    if current_user.is_authenticated:
        sort_hot=bool(request.cookies.get('sort_hot',''))
    if sort_hot:
        pagination = UrlResource.query.order_by(UrlResource.like_num.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
    else:
        pagination = UrlResource.query.order_by(UrlResource.post_date.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items

    if form.validate_on_submit():
        data = form.search.data
        key = '%' + data + '%'
        pagination1 = UrlResource.query.filter(UrlResource.title.ilike(key)).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        pagination2 = UrlResource.query.filter(UrlResource.theme.ilike(key)).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts1=pagination1.items
        posts2 = pagination2.items
        posts = sorted(set(posts1+posts2), key=(posts1+posts2).index)  #去掉重复项
    hots=hotpagination[0:6]
    return render_template('url_resources.html',posts=posts,users=users,pagination=pagination,hots=hots,form=form,sort_datetime=sort_datetime)

@main.route('/datetime')
@login_required
def sort_datetime():
    resp=make_response(redirect(url_for('.url_resources')))
    resp.set_cookie('sort_hot','',max_age=30*24*60*60)
    return resp

@main.route('/hot')
@login_required
def sort_hot():
    resp=make_response(redirect(url_for('.url_resources')))
    resp.set_cookie('sort_hot','1',max_age=30*24*60*60)
    return resp

@main.route('/like/<id>')
@login_required
def like(id):
    resource = UrlResource.query.filter_by(id=id).first()
    if resource is None:
        flash('资源不存在！')
        return redirect(url_for('.index'))
    if current_user.is_liking(resource):
        flash('已喜欢！')
        return redirect(url_for('.url_resources'))
    current_user.like(resource)
    resource.like_num=resource.like_num+1
    flash('你喜欢了 %s ！' % resource.title)
    return redirect(url_for('.url_resources'))
@main.route('/unlike/<id>')
@login_required
def unlike(id):
    resource = UrlResource.query.filter_by(id=id).first()
    if resource is None:
        flash('资源不存在！')
        return redirect(url_for('.index'))
    if not current_user.is_liking(resource):
        flash('未喜欢！')
        return redirect(url_for('.url_resources'))
    current_user.unlike(resource)
    resource.like_num = resource.like_num-1
    flash('你取消喜欢了 %s ！' % resource.title)
    return redirect(url_for('.url_resources'))



@main.route('/mylike', methods=['GET', 'POST'])
@login_required
def mylike():
    users = User()
    page = request.args.get('page', 1, type=int)
    query=current_user.liked_Resources
    pagination = query.order_by(UrlResource.post_date.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts=pagination.items
    return render_template('mylike.html',posts=posts,pagination=pagination,users=users)

@main.route('/likes/<id>')
@login_required
def likes(id):
    resource = UrlResource.query.filter_by(id=id).first()
    if resource is None:
        flash('资源不存在！')
        return redirect(url_for('.index'))
    if current_user.is_liking(resource):
        flash('已喜欢！')
        return redirect(url_for('.url_resources'))
    current_user.like(resource)
    resource.like_num=resource.like_num+1
    flash('你喜欢了 %s ！' % resource.title)
    return redirect(url_for('.mylike'))
@main.route('/unlikes/<id>')
@login_required
def unlikes(id):
    resource = UrlResource.query.filter_by(id=id).first()
    if resource is None:
        flash('资源不存在！')
        return redirect(url_for('.index'))
    if not current_user.is_liking(resource):
        flash('未喜欢！')
        return redirect(url_for('.url_resources'))
    current_user.unlike(resource)
    resource.like_num = resource.like_num-1
    flash('你取消喜欢了 %s ！' % resource.title)
    return redirect(url_for('.mylike'))
	
@main.route('/upload',methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        randnum = str(random())

        filename = secure_filename(form.myfile.data.filename)
        unifilename=randnum[-4:]+filename
        s=filename.split('.')
        uploadpath=path.join('/app/files', unifilename)
        form.myfile.data.save(uploadpath)


        afile = Files(title=form.filename.data,
                      url=unifilename,
                      describe=form.describe.data,
                      format=s[-1],
                      author_id=current_user.id,
                      is_private=form.auth.data)
        db.session.add(afile)
        flash('上传成功！')
    return render_template('upload.html',form=form)

@main.route('/myfiles',methods=['GET','POST'])
@login_required
def myfiles():
    page = request.args.get('page', 1, type=int)
    pagination0 = Files.query.filter_by(is_private=False,author_id=current_user.id).order_by(Files.upload_date.desc()).paginate(
        page, per_page=5,
        error_out=False)
    pagination1 = Files.query.filter_by(is_private=True,author_id=current_user.id).order_by(Files.upload_date.desc()).paginate(
        page, per_page=5,
        error_out=False)
    files0 = pagination0.items
    files1 = pagination1.items
    return render_template('myfiles.html', files0=files0, files1=files1,pagination0=pagination0, pagination1=pagination1,current_app=current_app)



@main.route('/file/<id>')
@login_required
def file(id):
    users=User()
    file = Files.query.filter_by(id=id).first()
    if file.is_private and file.author_id !=current_user.id:
        flash('你无权查看此文件！')
        return redirect(url_for('.index'))
    return render_template('file.html',file=file,users=users)

@main.route('/download/<id>')
@login_required
def download(id):
    file = Files.query.filter_by(id=id).first()
    file.download_num=file.download_num+1
    if file.is_private and file.author_id !=current_user.id:
        flash('你无权下载此文件！')
        return redirect(url_for('.index'))
    filename=Files.query.filter_by(id=id).first().url
    return send_from_directory('/app/files', filename, as_attachment=True)


@main.route('/showfiles',methods=['GET', 'POST'])
@login_required
def showfiles():
    if current_user.username  not in current_app.config['ADMIN']:
        return redirect(url_for('main.index'))
    allfiles=listdir('/app/files')
    return str(allfiles)

@main.route('/resetft',methods=['GET', 'POST'])
@login_required
def resetft():
    # if current_user.username  not in current_app.config['ADMIN']:
    #     return redirect(url_for('main.index'))
    # for i in range(1,11):
    #     file = Files.query.filter_by(id=i).first()
    #     if file is None:
    #         pass
    #     else:
    #         db.session.delete(file)
    return 'ok!!'
