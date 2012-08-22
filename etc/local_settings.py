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


import datetime

PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=2)
SESSION_COOKIE_NAME = "zabbix_notifier"
SECRET_KEY = '\xc0\xdd\x1e\xff+/>3\xec\xacn\xfc\x06\x9b\x07\x8e,\xe2\xd4\x14\xe7\xbc?\xe6'
SQLALCHEMY_DATABASE_URI = 'sqlite:////var/lib/zabbix-notifier/zabbix-notifier.sqlite'

ZABBIX_CONNECTION = {
    "server": "http://localhost/zabbix",
    "user": "admin",
    "password": "zabbix"
}

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587 
MAIL_USE_TLS = True
MAIL_USERNAME = 'altai-test@griddynamics.com'
MAIL_PASSWORD = ''
MAIL_USE_TLS = True
DEFAULT_MAIL_SENDER = ('robot', MAIL_USERNAME)
