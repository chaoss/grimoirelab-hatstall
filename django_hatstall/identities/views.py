import configparser
import json

import sortinghat.api

from sortinghat.db.database import Database
from sortinghat.db.model import UniqueIdentity

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

#
# VIEWS
#


def index(request):
    return HttpResponse("Hello, world. You're at the profiles index.")

def list(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    sh_db_cfg = "shdb.cfg"
    sh_db = sortinghat_db_conn(sh_db_cfg)
    # uuids = render_profiles(sh_db, request)
    # return HttpResponse("Listing all profiles: " + json.dumps(uuids))
    return HttpResponse(render_profiles(sh_db, request))

def identity(request, identity_id):
    return HttpResponse("Showing the profile: " + str(identity_id))


#
# HELPER METHODS FOR VIEWS
#


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


def render_profiles(db, request, err=None):
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
    template = loader.get_template('profiles/profiles.html')
    context = {
        "uids":unique_identities, "err":err
    }
    return template.render(context, request)
    # return unique_identities
    # return render(request, 'profiles.html', {})
    # return render_template('profiles.html', uids=unique_identities, err=err)
