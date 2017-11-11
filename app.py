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

import argparse
import configparser
from flask import Flask, request, redirect, url_for, render_template

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

def render_profiles(err=None):
    """
    Render profiles page
    """
    unique_identities = []
    with db.connect() as session:
        for u_identity in session.query(UniqueIdentity):
            uuid_dict = u_identity.to_dict()
            enrollments = []
            for enrollment in u_identity.enrollments:
                enrollments.append(enrollment.organization.name)
            uuid_dict['enrollments'] = enrollments
            unique_identities.append(uuid_dict)
    session.expunge_all()
    return render_template('profiles.html', uids=unique_identities, err=err)

def render_profile(profile_uuid, err=None):
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
         orgs=orgs, identities=remaining_identities, enrollments=profile_info.enrollments,\
         err=err)

def merge(uuids):
    """
    Merge a set of profiles given the list of uuids
    """
    if len(uuids) > 1:
        for uuid in uuids[:-1]:
            sortinghat.api.merge_unique_identities(db, uuid, uuids[-1])
            app.logger.info("%s merged into %s", uuid, uuids[-1])
    else:
        err = "You need at least 2 profiles to merge them"
        app.logger.info(err)
    return err

def update_profile(uuid, profile_data):
    """
    Update profile
    """
    try:
        sortinghat.api.edit_profile(db, uuid, name=profile_data['name'],\
            email=profile_data['email'], is_bot=profile_data['bot'] == 'True',\
            country=profile_data['country'])
        err = None
        app.logger.info("%s update with: name: %s, email: %s, bot: %s, country: %s",\
            uuid, profile_data['name'], profile_data['email'], profile_data['bot'],\
            profile_data['country'])
    except sortinghat.exceptions.NotFoundError as error:
        err = error
        app.logger.info("Update failed: %s", error)
    except sortinghat.exceptions.ValueError as error:
        err = error
        app.logger.info("Update failed: %s", error)
    return err

app = Flask(__name__)

@app.route('/')
def index(err=None):
    """
    Render index page
    """
    return render_template('index.html', err=err)

@app.route('/profiles', strict_slashes=False, methods=['GET', 'POST'])
def profiles(err=None):
    """
    Render profiles page
    Includes profiles merging functionallity
    """
    if request.method == 'POST':
        err = merge(request.form.getlist('uuid'))
    return render_profiles(err)

@app.route('/profiles/<profile_uuid>', methods=['GET', 'POST'])
def profile(profile_uuid, err=None):
    """
    Render profile page
    Includes profiles indentities unmerging
    """
    if request.method == 'POST':
        err = update_profile(profile_uuid, request.form)
    return render_profile(profile_uuid, err)

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
    try:
        sortinghat.api.add_enrollment(db, profile_uuid, organization)
        app.logger.info('Enrolled %s in %s', profile_uuid, organization)
        err = None
    except sortinghat.exceptions.AlreadyExistsError as error:
        err = error
        app.logger.info('Enrollment failed: %s', error)
    return redirect(url_for('profile', profile_uuid=profile_uuid, err=err))

@app.route('/profiles/<profile_uuid>/unenroll_from/<organization>')
def unenroll_profile(profile_uuid, organization):
    """
    Un-enroll a profile uuid from an organization
    """
    sortinghat.api.delete_enrollment(db, profile_uuid, organization)
    app.logger.info("Un-enrolled %s in %s", profile_uuid, organization)
    return redirect(url_for('profile', profile_uuid=profile_uuid))

@app.route('/profiles/<profile_uuid>/unmerge/<identity_id>')
def unmerge(profile_uuid, identity_id):
    """
    Unmerge a given identity from a unique identity, creating a new unique identity
    """
    sortinghat.api.move_identity(db, identity_id, identity_id)
    with db.connect() as session:
        edit_identity = session.query(Identity).filter(Identity.uuid == identity_id).first()
        uid_profile_name = edit_identity.name
        uid_profile_email = edit_identity.email
        sortinghat.api.edit_profile(db, identity_id, name=uid_profile_name, email=uid_profile_email)
        app.logger.info("Unmerged %s and created its unique indentity", identity_id)
    session.expunge_all()
    return redirect(url_for('profile', profile_uuid=profile_uuid))

@app.route('/organizations', methods=['GET', 'POST'])
def organizations():
    """
    Render organizations page
    """
    err = None
    orgs = sortinghat.api.registry(db)
    domains = sortinghat.api.domains(db)
    if request.method == 'POST':
        try:
            sortinghat.api.add_organization(db, request.form['name'])
            app.logger.info('%s added to Organizations', request.form['name'])
        except sortinghat.exceptions.AlreadyExistsError as error:
            err = error
            app.logger.info('Adding organization falied: %s', error)
    return render_template('organizations.html', orgs=orgs, domains=domains, err=err)

if __name__ == '__main__':
    import sys
    args = parse_args(sys.argv[1:])
    app.logger.info("Args: {}".format(args.sh_db_cfg))
    db = sortinghat_db_conn(args.sh_db_cfg)
    app.run(debug=True)
