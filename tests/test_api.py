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


"""
Tests for zabbix_notifier.api
"""

import os
import sys
import json
import datetime
import unittest
import stubout
import tempfile

import routes
import webob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tests


from zabbix_notifier import app
from zabbix_notifier import api
from zabbix_notifier import database


class TestCase(tests.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.db_fd, self.db_filename = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            "sqlite:////%s" % self.db_filename)
        app.config['TESTING'] = True
        self.app_client = app.test_client()
        database.db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_filename)
        super(TestCase, self).tearDown()

    def assertSuccess(self, res):
        self.assertEqual(res.status_code / 100, 2)

    def test_parameter_get(self):
        res = self.app_client.get("/parameter")
        self.assertSuccess(res)
        res = self.app_client.get("/parameter?id=1")
        self.assertSuccess(res)

    def test_parameter_update(self):
        param = database.db.session.merge(
            database.Parameter(is_notified=False))
        database.db.session.commit()
        res = self.app_client.put(
            "/parameter/%s" % param.id,
            data=json.dumps({"is_notified": True}),
            content_type=api.ContentType.JSON)
        self.assertSuccess(res)

    def test_item_info_get(self):
        res = self.app_client.get("/item_info")
        self.assertSuccess(res)
        res = self.app_client.get("/item_info?id=1")
        self.assertSuccess(res)

    def test_item_info_update(self):
        item_info = database.db.session.merge(
            database.ItemInfo(is_notified=False))
        database.db.session.commit()
        res = self.app_client.put(
            "/item_info/%s" % item_info.id,
            data=json.dumps({"is_minimized": True}),
            content_type=api.ContentType.JSON)
        self.assertSuccess(res)

    def test_item_info_create(self):
        res = self.app_client.post(
            "/item_info",
            data=json.dumps({"key_": "a_key", "is_minimized": True}),
            content_type=api.ContentType.JSON)
        self.assertSuccess(res)

    def test_item_info_delete(self):
        res = self.app_client.post(
            "/item_info",
            data=json.dumps({"key_": "a_key", "is_minimized": True}),
            content_type=api.ContentType.JSON)
        res = self.app_client.delete(
            "/item_info/a_key")
        self.assertSuccess(res)
