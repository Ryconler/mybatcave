#!/usr/bin/python
# -*- coding: UTF-8 -*-
from . import api
from ..models import User,UrlResource
from flask import jsonify


@api.route('/users/<int:id>')
def get_user(id):
    user=User.query.get_or_404(id)
    return jsonify(user.to_json())