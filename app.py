#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 J. Manrique Lopez de la Fuente
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     J. Manrique Lopez <jsmanrique@bitergia.com>

import logging
import argparse
import configparser
from flask import Flask, request, redirect, url_for, render_template

logging.basicConfig(level=logging.INFO)

from sortinghat.db.database import Database
import sortinghat.api
from sortinghat.db.model import MIN_PERIOD_DATE, MAX_PERIOD_DATE,\
    UniqueIdentity, Identity, Profile, Organization, Domain,\
    Country, Enrollment, MatchingBlacklist

def parse_args(args):
    """
    If provided, it parses address for Sorting Hat database settings
    """
    parser = argparse.ArgumentParser(description='Start Sorting Hat web data manager')
    parser.add_argument('-f', '--file', dest='sh_db_cfg', default='shdb.cfg', \
        help='Sorting Hat data base server settings')

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
    sortinghat_db = Database(user=shdb_user, password=shdb_pass, database=shdb_name, host=shdb_host)

    return sortinghat_db

def render_profiles():
    """
    Render profiles page
    """
    unique_identities = []
    with db.connect() as session:
        for u_identity in session.query(UniqueIdentity):
            uuid_dict = u_identity.to_dict()
            enrollments = []
            for enrollment in u_identity.enrollments:
                print(enrollment.organization.name)
                enrollments.append(enrollment.organization.name)
            uuid_dict['enrollments'] = enrollments
            unique_identities.append(uuid_dict)
    session.expunge_all()
    return render_template('profiles.html', uids=unique_identities)

def render_profile(profile_uuid):
    """
    Render unique identity profile page
    It shows also sections to add enrollments and merge remaining
    identities
    """
    orgs = sortinghat.api.registry(db)
    remaining_identities = []
    profile_enrollments = []
    with db.connect() as session:
        profile_info = session.query(UniqueIdentity).\
            filter(UniqueIdentity.uuid == profile_uuid).first()
        profile_identities = [x.id for x in profile_info.identities]
        for identity in session.query(Identity).filter(Identity.id.notin_(profile_identities)):
            remaining_identities.append(identity)
        for enrollment in profile_info.enrollments:
            profile_enrollments.append(enrollment)
        session.expunge_all()
    return render_template('profile.html', profile=profile_info.to_dict(),\
         orgs=orgs, identities=remaining_identities, enrollments=profile_info.enrollments)

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

def update_profile(uuid, profile_data):
    """
    Update profile
    """
    sortinghat.api.edit_profile(db, uuid, name=profile_data['name'],\
        email=profile_data['email'], is_bot=profile_data['bot'] == 'True',\
        country=profile_data['country'])
    logging.info("{} update with: name: {}, email: {}, bot: {}, country: {}".\
        format(uuid, profile_data['name'], profile_data['email'], profile_data['bot'],\
        profile_data['country']))

app = Flask(__name__)

@app.route('/')
def index():
    """
    Render index page
    """
    return render_template('index.html')

@app.route('/profiles', strict_slashes=False, methods=['GET', 'POST'])
def profiles():
    """
    Render profiles page
    Includes profiles merging functionallity
    """
    if request.method == 'POST':
        merge(request.form.getlist('uuid'))
        return render_profiles()
    else:
        return render_profiles()

@app.route('/profiles/<profile_uuid>', methods=['GET', 'POST'])
def profile(profile_uuid):
    """
    Render profile page
    Includes profiles indentities unmerging
    """
    if request.method == 'POST':
        update_profile(profile_uuid, request.form)
        return render_profile(profile_uuid)
    else:
        return render_profile(profile_uuid)

@app.route('/profiles/<profile_uuid>/merge', methods=['POST'])
def merge_to_profile(profile_uuid):
    """
    Merge a list of unique profiles to the profile
    """
    uuids = request.form.getlist('uuid')
    uuids.append(profile_uuid)
    merge(uuids)
    return redirect(url_for('profile', profile_uuid=profile_uuid))

@app.route('/profiles/<profile_uuid>/enroll_in/<organization>')
def enroll_to_profile(profile_uuid, organization):
    """
    Enroll a profile uuid into an organization
    """
    sortinghat.api.add_enrollment(db, profile_uuid, organization)
    logging.info("Enrolled {} in {}".format(profile_uuid, organization))
    return redirect(url_for('profile', profile_uuid=profile_uuid))

@app.route('/profiles/<profile_uuid>/unenroll_from/<organization>')
def unenroll_profile(profile_uuid, organization):
    """
    Enroll a profile uuid into an organization
    """
    sortinghat.api.delete_enrollment(db, profile_uuid, organization)
    logging.info("Un-enrolled {} in {}".format(profile_uuid, organization))
    return redirect(url_for('profile', profile_uuid=profile_uuid))

@app.route('/unmerge/<identity_id>')
def unmerge(identity_id):
    """
    Unmerge a given identity from a unique identity, creating a new unique identity
    """
    sortinghat.api.move_identity(db, identity_id, identity_id)
    with db.connect() as session:
        edit_identity = session.query(Identity).filter(Identity.uuid == identity_id).first()
        uid_profile_name = edit_identity.name
        uid_profile_email = edit_identity.email
        sortinghat.api.edit_profile(db, identity_id, name=uid_profile_name, email=uid_profile_email)
        logging.info("Unmerged {} and created its unique indentity".format(identity_id))
    session.expunge_all()
    return redirect(url_for('profiles'))

@app.route('/organizations')
def organizations():
    """
    Render organizations page
    """
    orgs = sortinghat.api.registry(db)
    domains = sortinghat.api.domains(db)
    return render_template('organizations.html', orgs=orgs, domains=domains)

if __name__ == '__main__':
    import sys
    args = parse_args(sys.argv[1:])
    logging.info("Args: {}".format(args.sh_db_cfg))
    db = sortinghat_db_conn(args.sh_db_cfg)
    app.run(debug=True)
