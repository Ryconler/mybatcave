#!/usr/bin/python
# -*- coding: UTF-8 -*-
from . import api
from ..models import User,UrlResource
from flask import jsonify




@api.route('/resources/<int:id>')
def get_resource(id):
    resource=UrlResource.query.get_or_404(id)
    return jsonify(resource.to_json())