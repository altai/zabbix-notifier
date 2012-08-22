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
import socket

import jinja2
import flask
from flaskext import mail

from zabbix_notifier import app


LOG = logging.getLogger(__name__)

mail_obj = mail.Mail(app)


def process_changed(host, item, parameter, satisfied):
    if not parameter.addressees or not isinstance(parameter.addressees, list):
        LOG.debug(
            "nothing is sent: parameter.addressees is empty or not a list")
        return
    try:
        msg = mail.Message("Zabbix Notification",
                           recipients=parameter.addressees,
                           sender=app.config.get("DEFAULT_MAIL_SENDER"))
        template_filename = ("/etc/zabbix-notifier/notification-%s.txt" %
                             ("email" if parameter.is_email else "sms"))
        template = jinja2.Template(open(template_filename, "r").read())
        msg.body = template.render(
            host=host,
            item=item,
            parameter=parameter)
        mail_obj.send(msg)
    except socket.error, e:
        LOG.error("unable to send notification emails")
