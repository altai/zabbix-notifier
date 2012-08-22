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
import logging
import time

import flask

from zabbix import api as zabbix_api

from zabbix_notifier import app
from zabbix_notifier import notifier
from zabbix_notifier import database
from zabbix_notifier.database import db


LOG = logging.getLogger(__name__)


def get_zabbix_client():
    conn = app.config["ZABBIX_CONNECTION"]
    client = zabbix_api.ZabbixAPI(server=conn["server"])
    client.login(conn["user"], conn["password"], save=True)
    return client


def alarm_handler():
    LOG.debug("polling zabbix for new items")
    param_list = db.session.query(database.Parameter).filter_by(
        is_notified=1).all()
    item_info_by_key = dict(
        ((ii.key_, ii)
         for ii in db.session.query(database.ItemInfo).all()))
    client = get_zabbix_client()
    client.login()
    item_list = client.item.get({"output": "extend"})
    host_list = client.host.get({"output": "extend"})
    now = time.time()
    process_items(param_list, item_info_by_key, item_list, host_list, now)


def process_items(param_list, item_info_by_key, item_list, host_list, now):
    param_by_key = {}
    for param in param_list:
        param_by_key.setdefault(param.key_, []).append(param)
    host_by_id = dict(((host["hostid"], host) for host in host_list))
    for item in item_list:
        hostid = item["hostid"]
        if not hostid in host_by_id:
            continue
        try:
            curr_value = float(item["lastvalue"])
        except ValueError:
            continue
        key_ = item["key_"]
        try:
            params = param_by_key[key_]
            item_info = item_info_by_key[key_]
        except KeyError:
            continue
        if item_info.condition_state is None:
            item_info.condition_state = {}
        condition_state = item_info.condition_state.setdefault(str(hostid), {})
        if item_info.is_minimized:
            curr_value = -curr_value
        for par in params:
            par_condition_state = condition_state.setdefault(str(par.id), {})
            bound = par.bound or 0.0
            hysteresis = par.hysteresis or 0.0
            threshold = par.threshold or 0.0
            if item_info.is_minimized:
                bound = -bound
            threshold = abs(threshold * bound / 100.0)
            prev_satisfied = par_condition_state.setdefault("sat", True)
            prev_at = par_condition_state.setdefault("at", 0.0)
            if curr_value > bound + threshold:
                curr_satisfied = True
            elif curr_value < bound - threshold:
                curr_satisfied = False
            else:
                curr_satisfied = prev_satisfied
            LOG.debug("host %s, key %s, state %s -> %s" %
                      (hostid, key_, prev_satisfied, curr_satisfied))
            if curr_satisfied != prev_satisfied:
                par_condition_state["at"] = now
                par_condition_state["sat"] = curr_satisfied
                par_condition_state["sent"] = False
            if (now - prev_at > hysteresis and
                not par_condition_state.get("sent", False)):
                par_condition_state["sent"] = True
                notifier.process_changed(
                    host_by_id[hostid], item, par, curr_satisfied)

    for item_info in item_info_by_key.itervalues():
        # use json.dumps here since sqlalchemy usually cannot understand that
        # a JSON field was changed
        item_info.condition_state = json.dumps(item_info.condition_state)
        db.session.merge(item_info)

    db.session.commit()


def poller_thread():
    while True:
        alarm_handler()
        time.sleep(app.config.get("ZABBIX_POLLING_INTERVAL", 3))
