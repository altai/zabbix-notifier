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
Tests for zabbix_notifier.poller
"""

import os
import sys
import json
import datetime
import unittest
import stubout
import tempfile
import subprocess

import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tests


from zabbix_notifier import app
from zabbix_notifier import poller
from zabbix_notifier import database
from zabbix_notifier import notifier


class FakeClientField(object):
    get_res = []

    def get(self, *args, **kwargs):
        return self.get_res


class FakeClient(object):
    host = FakeClientField()
    item = FakeClientField()


class TestCase(tests.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.db_fd, self.db_filename = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            "sqlite:////%s" % self.db_filename)
        database.db.create_all()

    def populate_db(self):
        INITIAL_DATA_SCRIPT = (
            "%s/data/data.sql" %
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for cmd in open(INITIAL_DATA_SCRIPT, "rt").read().split(";"):
            database.db.session.execute(cmd)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_filename)
        super(TestCase, self).tearDown()

    def test_must_notify(self):
        test_data = self.json_load_from_file("test_poller_must_notify.in.js")
        all_answers = []
        for test_unit in test_data:
            condition_state = {}
            unit_answers = []
            for curr_value, now in test_unit["changes"]:
                unit_answers.append({
                    "notify":  poller.must_notify(
                        curr_value, now,
                        condition_state,
                        test_unit["bound"], test_unit["hysteresis"],
                        test_unit["threshold"],
                        test_unit["is_minimized"]),
                    "sat": condition_state["sat"]
                })
            all_answers.append(unit_answers)
        self.json_check_with_file(
            all_answers,
            "test_poller_must_notify.out.js")

    def test_alarm_handler(self):
        self.populate_db()
        fake_client = FakeClient()
        fake_client.host.get_res = [
            {
                "hostid": "10001",
            }
        ]
        fake_time = 0
        all_notifications = []
        unit_notifications = []

        def fake_process_changed(host, item, parameter, satisfied):
            unit_notifications.append({
                "hostid": host["hostid"],
                "key_": item["key_"],
                "satisfied": satisfied
            })

        self.stubs.Set(notifier, "process_changed", fake_process_changed)
        self.stubs.Set(poller, "get_zabbix_client", lambda: fake_client)
        self.stubs.Set(time, "time", lambda: fake_time)

        test_data = self.json_load_from_file("test_poller_alarm_handler.in.js")
        for test_unit in test_data:
            fake_client.item.get_res = test_unit["item_list"]
            fake_time = test_unit["now"]
            poller.alarm_handler()
            all_notifications.append(unit_notifications)
            unit_notifications = []
        self.json_check_with_file(
            all_notifications,
            "test_poller_alarm_handler.out.js")
        self.stubs.UnsetAll()
