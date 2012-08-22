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


import json

from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

from zabbix_notifier import app

import sqlalchemy
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy import types as sql_types


db = SQLAlchemy(app)


class JsonBlob(sql_types.TypeDecorator):

    impl = sqlalchemy.Text

    def process_bind_param(self, value, dialect):
        return ((value
                 if isinstance(value, basestring)
                 else json.dumps(value))
                if value
                else None)

    def process_result_value(self, value, dialect):
        try:
            return json.loads(value) if value else None
        except:
            return None


class BaseEntity(object):
    prohibit = set(["id"])

    @classmethod
    def ensure_fields(cls):
        if hasattr(cls, "fields"):
            return
        fields = []
        for key, value in cls.__dict__.iteritems():
            if isinstance(value, QueryableAttribute):
                fields.append(key)
        cls.fields = fields

    def __init__(self, **obj_json):
        self.update(obj_json, prohibit=set("id"))

    def update(self, obj_json, prohibit=None):
        if prohibit is None:
            prohibit = self.prohibit
        for field in (set(self.fields) & set(obj_json.iterkeys())
                      - prohibit):
            setattr(self, field, obj_json[field])

    def to_json(self):
        json = {}
        for field in self.fields:
            json[field] = getattr(self, field)
        return json


class Parameter(BaseEntity, db.Model):
    __tablename__ = "parameter"
    prohibit = set(["id", "key_", "is_email"])
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_ = db.Column(db.String(8))
    is_email = db.Column(db.Boolean)
    is_notified = db.Column(db.Boolean)
    addressees = db.Column(JsonBlob())

    bound = db.Column(db.Float)
    hysteresis = db.Column(db.Integer)  # seconds
    threshold = db.Column(db.Integer)   # percent


class ItemInfo(BaseEntity, db.Model):
    prohibit = set(["id", "key_", "condition_state"])
    __tablename__ = "item_info"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_ = db.Column(db.String(8))
    condition_state = db.Column(JsonBlob())
    is_minimized = db.Column(db.Boolean)


db.create_all()

for cls in BaseEntity.__subclasses__():
    cls.ensure_fields()
