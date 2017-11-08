#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 J. Manrique Lopez de la Fuente
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# Authors:
#     J. Manrique Lopez <jsmanrique@bitergia.com>

import argparse
import configparser

from sortinghat.db.database import Database
import sortinghat.api
from sortinghat.db.model import MIN_PERIOD_DATE, MAX_PERIOD_DATE,\
    UniqueIdentity, Identity, Profile, Organization, Domain,\
    Country, Enrollment, MatchingBlacklist

from flask import Flask, request, render_template

import logging
logging.basicConfig(level=logging.INFO)

def parse_args(args):
    """
    If provided, it parses address for Sorting Hat database settings
    """
    parser = argparse.ArgumentParser(description = 'Start Sorting Hat web data manager')
    parser.add_argument('-f', '--file', dest = 'sh_db_cfg', default='shdb.cfg', help = 'Sorting Hat data base server settings')

    return parser.parse_args()

def parse_shdb_config_file(filename):
    """
    Returns SortingHat database settings (user, password, name, host) to
    connect to it later
    """
    shdb_config = configparser.ConfigParser()
    shdb_config.read(filename)
    shdb_user = shdb_config.get('SHDB_Settings', 'user')
    shdb_pass = shdb_config.get('SHDB_Settings', 'password')
    shdb_name = shdb_config.get('SHDB_Settings', 'name')
    shdb_host = shdb_config.get('SHDB_Settings', 'host')

    return shdb_user, shdb_pass, shdb_name, shdb_host

def sortinghat_db_conn(filename):
    """
    Returns Sorting Hat database object to work with
    """
    shdb_user, shdb_pass, shdb_name, shdb_host = parse_shdb_config_file(filename)
    db = Database(user=shdb_user, password=shdb_pass, database=shdb_name, host=shdb_host)

    return db

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profiles', methods =['GET', 'POST'])
def profiles():
    if request.method == 'POST':
        print(request.form.getlist('uuid'))
        unique_identities = []
        with db.connect() as session:
            for u_identity in session.query(UniqueIdentity):
                unique_identities.append(u_identity.to_dict())
        return render_template('profiles.html', uids=unique_identities)
    else:
        unique_identities = []
        with db.connect() as session:
            for u_identity in session.query(UniqueIdentity):
                unique_identities.append(u_identity.to_dict())
        return render_template('profiles.html', uids=unique_identities)

@app.route('/profiles/<profile_uuid>')
def profile(profile_uuid):
    with db.connect() as session:
        profile_info = session.query(UniqueIdentity).filter(UniqueIdentity.uuid == profile_uuid).first()

        return render_template('profile.html', profile=profile_info.to_dict())

if __name__ == '__main__':
    import sys
    args = parse_args(sys.argv[1:])
    logging.info("Args: {}".format(args.sh_db_cfg))
    db = sortinghat_db_conn(args.sh_db_cfg)
    app.run(debug=True)
