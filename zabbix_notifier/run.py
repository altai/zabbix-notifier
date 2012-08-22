#!/usr/bin/python2
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


import argparse
import logging
import os
import sys
import thread


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--sync-db", default=False,
                            action="store_true", help="synchronize database")
    arg_parser.add_argument("--reloader", "-r", default=False,
                            action="store_true", help="start with reloader")
    arg_parser.add_argument("host:port", nargs="?",
                            default="127.0.0.1:18080", help="host:port")
    args = arg_parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    if args.sync_db:
        from zabbix_notifier import database
        return

    if not args.reloader or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from zabbix_notifier import poller
        thread.start_new_thread(poller.poller_thread, ())

    listen = getattr(args, "host:port").split(':')
    from zabbix_notifier import app
    app.debug = True
    app.run(host=listen[0], port=int(listen[1]),
            use_reloader=args.reloader)


if __name__ == "__main__":
    main()
