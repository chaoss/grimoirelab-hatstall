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

def merge(uuids):
    """
    Merge a set of profiles given the list of uuids
    """
    if len(uuids) > 1:
        for uuid in uuids[:-1]:
            sortinghat.api.merge_unique_identities(db, uuid, uuids[-1])
            logging.info("{} merged into {}".format(uuid, uuids[-1]))
    else:
        logging.info("You need at least 2 profiles to merge them")

def unmerge(uuid):
    uid_target = '3e07ffee1f3dc6eac7be34d46b0423ab81e2eac7'
    sortinghat.api.move_identity(db, uid_target, uid_target)
    #sortinghat.api.edit_profile(db, uid_target)
    with db.connect() as sesion:
        edit_identity = sesion.query(Identity).filter(Identity.uuid == uid_target).first()
        uid_profile_uuid = edit_identity.id
        uid_profile_name = edit_identity.name
        uid_profile_email = edit_identity.email
        sortinghat.api.edit_profile(db, uid_target, name=uid_profile_name, email=uid_profile_email)
    print(edit_identity.to_dict())

def render_profiles():
    """
    Render profiles page
    """
    unique_identities = []
    with db.connect() as session:
        for u_identity in session.query(UniqueIdentity):
            unique_identities.append(u_identity.to_dict())
    return render_template('profiles.html', uids=unique_identities)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profiles', methods =['GET', 'POST'])
def profiles():
    if request.method == 'POST':
        merge(request.form.getlist('uuid'))
        return render_profiles()
    else:
        return render_profiles()

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
