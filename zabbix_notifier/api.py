# -*- coding: utf-8 -*-

# Zabbix Notifier
# Copyright (C) 2010-2012 Grid Dynamics Consulting Services, Inc
# All Rights Reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.


import logging
import os
import json

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, Response
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound

from zabbix_notifier import app
from zabbix_notifier import database
from zabbix_notifier import poller
from zabbix_notifier.database import db
from sqlalchemy.exc import *


class ContentType(object):
    JSON = "application/json"


def to_json_response(obj):
    return Response(json.dumps(obj) + "\n",
                    mimetype=ContentType.JSON,
                    headers={"Pragma": "no-cache", "Expires": "0"})


def ajax_persistent_create(PersistentClass):
    obj_json = request.json
    try:
        del obj_json["id"]
    except KeyError:
        pass
    obj = PersistentClass(**obj_json)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as intErr:
        return Response("Integrity error\n", status=400)
    except Exception as ex:
        return Response("Exception: %s\n" % ex, status=400)
    return to_json_response(obj.to_json())


def ajax_persistent_get(PersistentClass, **filter_by):
    values = []
    query = PersistentClass.query
    if filter_by:
        query = query.filter_by(**filter_by)
    for obj in query.all():
        values.append(obj.to_json())
    return to_json_response({"values": values})


def ajax_persistent_update(PersistentClass, id):
    obj = PersistentClass.query.filter_by(id=id).first()
    if not obj:
        abort(404)
    obj_json = request.json
    obj.update(obj_json)
    db.session.merge(obj)
    db.session.commit()
    return to_json_response(obj.to_json())


def get_filter_parameters(fields):
    return dict(((key, request.args[key])
                 for key in fields
                 if key in request.args))


def ajax_persistent_delete(PersistentClass, id):
    obj = PersistentClass.query.filter_by(id=id).first()
    if not obj:
        abort(404)
    db.session.delete(obj)
    db.session.commit()
    return Response(status=204)


def add_ajax_rules(cls, rules):
    """
    Create a set of URLs, i.e.:
    * GET /parameter?<id=ID&name=NAME>
    * POST /parameter
    * PUT /parameter/<id>
    * DELETE /parameter/<id>
    """
    cls_name = cls.__tablename__
    if "PUT" in rules:
        app.add_url_rule("/%s/<int:id>" % cls_name,
                         "%s_update" % cls_name,
                         lambda id, cls=cls: ajax_persistent_update(cls, id),
                         methods=["PUT"])
    if "DELETE" in rules:
        app.add_url_rule("/%s/<int:id>" % cls_name,
                         "%s_delete" % cls_name,
                         lambda id, cls=cls: ajax_persistent_delete(cls, id),
                         methods=['DELETE'])
    if "POST" in rules:
        app.add_url_rule("/%s" % cls_name,
                         "%s_create" % cls_name,
                         lambda cls=cls: ajax_persistent_create(cls),
                         methods=['POST'])
    if "GET" in rules:
        app.add_url_rule(
            "/%s" % cls_name,
            "%s_get" % cls_name,
            lambda cls=cls:
            ajax_persistent_get(
                cls, **get_filter_parameters(cls.fields)),
            methods=['GET'])


add_ajax_rules(database.Parameter, ("GET", "PUT"))
add_ajax_rules(database.ItemInfo, ("GET", "PUT"))


@app.route("/item_info", methods=["POST"])
def item_info_create():
    obj_json = request.json
    try:
        del obj_json["id"]
    except KeyError:
        pass
    try:
        key_ = obj_json["key_"]
    except KeyError:
        raise BadRequest(description="key_ is required")
    obj = database.ItemInfo(**obj_json)
    db.session.add(obj)
    for is_email in 0, 1:
        obj = database.Parameter(key_=key_, is_email=is_email, is_notified=1)
        db.session.add(obj)
    db.session.commit()
    return to_json_response(obj.to_json())


@app.route("/item_info/<id_or_key>", methods=["DELETE"])
def item_info_delete(id_or_key):
    query = database.ItemInfo.query
    if id_or_key.isdigit():
        obj = query.filter_by(id=id_or_key).first()
    else:
        obj = query.filter_by(key_=id_or_key).first()
    if not obj:
        abort(404)
    database.Parameter.query.filter_by(key_=obj.key_).delete()
    db.session.delete(obj)
    db.session.commit()
    return Response(status=204)


@app.route("/item")
def items_get():
    fields = ("key_", "name", "description")
    field_filter = get_filter_parameters(fields)
    client = poller.get_zabbix_client()
    item_list = client.item.get({"output": "extend"})

    def is_acceptable(item):
        for key, value in field_filter.iteritems():
            if item.get(key) != value:
                return False
        return True

    return to_json_response([dict(((key, item[key])
                                   for key in fields))
                             for item in item_list
                             if is_acceptable(item)])
