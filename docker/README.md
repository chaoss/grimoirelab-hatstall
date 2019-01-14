# Hatshall Docker Environment

## Quick execution

In order to start using Hatshall docker containers you just need to have Docker
installed in your host and execute:

```
django-hatstall/docker $ docker-compose up -d kibiter
django-hatstall/docker $ docker-compose up -d hatstall
django-hatstall/docker $ docker-compose up -d mordred
```

## Intro

Hatstall Docker containers will help you to deploy the Hatstall service with the
Bitergia Analytics dashboard using a set of configuration files.

The different files we will have to modify are:
- setup.cfg: Mordred's configuration file
- projects.json: JSON file with projects and its repositories
- orgs_file.json: a Sorting Hat file format with companies/organizations and domains
- docker-compose.yml: easy, the file where the container is specified with some variables that can be added

Let's start hacking!.


## docker-compose variables

These are the variables that you can define in the docker-compose file:

- `DATABASE_DIR`: path where the database is defined. If this variable is not defined, you will have to configure django-hatstall in order to connect to the db.
- `ADMIN_USER`: username of the admin user that will be on the django-hatstall app. If this variable is not defined, you will have to configure django creating a superuser.
- `ADMIN_PASS`: password of the admin user that will be on the django-hatstall app. If this variable is not defined, you will have to configure django creating a superuser.
- `APACHE_LOG_DIR`: path where the `access` and `error` logs of Apache2 are going to be stored. If this variable is not defined, you will have the `access` and `error` log in the default path of Apache2.


## setup.cfg

The Mordred's configuration file have several sections but don't panic, it is
easier than you may think at a glance.

First, we define the project name. The only thing you need to modify here is
the "short_name".
```
[general]
short_name = Hatstall
update = true
# seconds between collect+enrich rounds
min_update_delay = 120
debug = false
logs_dir = logs
kibana = "5"  
```

The "projects" section  specifies where the projects file is

```
[projects]
projects_file = /home/bitergia/conf/projects.json
```

The following two sections are used to store the 'raw' information we will
collect from the different data sources and to produce the 'enriched' data
we will create based on the 'raw' plus Sorting Hat information. In our example
we simply use the ElasticSearch started from docker-compose.

```
[es_collection]
url = http://bitergia:bitergia@172.17.0.1:9200

[es_enrichment]
url = http://bitergia:bitergia@172.17.0.1:9200
autorefresh = true
studies = false
```

One of the key pieces of the Bitergia Analytics dashboard is Sorting Hat. In
the following example it is running in a container named 'mariadb'. If you have
it, don't need to modify anything for the demo.

The parameters 'matching' and 'autoprofile' are a essential part of Sorting Hat
functionality, if you wanna to learn more go to its command line help after
installing it or to https://github.com/MetricsGrimoire/sortinghat

```
[sortinghat]
host = mariadb
user = root
password =
database = shdb
load_orgs = true
orgs_file = home/grimoirelab/conf/orgs_file
# see: sortinghat unify --help
unify_method =
affiliate = false
unaffiliated_group = Unknown
autoprofile = [customer,git,github]
matching = [email]
# Every 10s identities will be checked to refresh
sleep_for = 10
bots_names = [Beloved Bot]
```

For builidng the dashboard, mordred configures Kibiter. No config is needed
by default but sometimes is useful to change the default time frame is shown.

```
[panels]
kibiter_time_from="now-90d"
kibiter_default_index="git"
```

We can also enable of disable the different phases. Let's start will all of
them enabled.

```
[phases]
collection = true
identities = true
enrichment = true
panels = true
```

Last but not least, for every data source Bitergia Analytics supports, it is
needed to include the name of both the raw and enriched indices. These will
be use to contain the information in the Elastic Search server.

```
[git]
raw_index = git_test-raw
enriched_index = git_test
```

## projects.json and orgs_file

The projects.json file contains a list of projects and the data source associated
to it. In the example below git and github repositories associated to the project
named 'grimoirelab'.

```
{
    "grimoirelab": {
        "git": [
            "https://github.com/grimoirelab/perceval",
            "https://github.com/grimoirelab/sortinghat",
            "https://github.com/grimoirelab/GrimoireELK"
        ]
    }
}
```

The orgs file contains a list of internet domains and organizations in
Sortinghat format.

## execute it

So, now we have the input Mordred needs, let's set up its containers.

It is recommend that first, you start kibiter with:

```
(acs@dellx) (mordred *+%) ~/devel/django-hatstall/docker $ docker-compose up -d kibiter
```

Once kibiter and elasticsearch are ready, you can check it accessing http://localhost:5601,
you can continue.

Next you need to start hatstall service:

```
(acs@dellx) (mordred *+%) ~/devel/django-hatstall/docker $ docker-compose up -d hatstall
```

And as a last step, yo start the mordred service to fill the Sortinghat
information which will be managed from Hatstall Web interface.

```
(acs@dellx) (mordred *+%) ~/devel/django-hatstall/docker $ docker-compose up -d mordred
```

You can check the mordred activities with:

```
(acs@dellx) (mordred *+%) ~/devel/django-hatstall/docker $ tail -f logs/all.log
```


Bitergia 2018. Software metrics for your peace of mind.
