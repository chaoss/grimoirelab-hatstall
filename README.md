# Hatstall

Hatstall is a web interface for [SortingHat](http://github.com/grimoirelab/sortinghat) databases developed mainly with [Flask](http://flask.pocoo.org/)

According to [Harry Potter Wiki](http://harrypotter.wikia.com/wiki/Hatstall) **Hatstall** is defined as:

> A Hatstall was an archaic term for a student of Hogwarts School of Witchcraft and Wizardry whose sorting took more than five minutes because the Sorting Hat found them to have a personality equally suited to different Hogwarts Houses. The Sorting Hat sometimes took the student's personal preference into consideration in order to break such a tie.

## Installation

Currently requirements are defined in the [requirements.txt](requirements.txt) file. They are mostly:

* Flask
* grimoire-elk
* grimoirelab-toolkit
* sortinghat

## Usage

Once you have the requirements installed (I recommend using a Python virtual environment), you would need a configuration file.

You can change [the one provided](shdb.cfg) (the app uses it by default), or create your own one.

The parameters in the file are:
* `user` stands for your username for the SortingHat database
* `password` stands for the password for your SortingHat database's user
* `name` stands for the name of the SortingHat database you want to manage
* `host` stands for the address where the SortingHat database is hosted

Once you have it, you can launch the web app using the command line:

```
$  python3 app.py [-f <your configuration file>]
```

There is more documentation is [docs/README.md](under development).

# Contributing

We are sure it is full of issues, so don't hesitate on blaming us and submitting the ones you find!

Feel free to fork it and submit merge requests. We are sure it can be improved in many ways.

Thre is more information in the [CONTRIBUTING](CONTRIBUTING.md) file

# License

[GPL v3](LICENSE)

## Logo

Logo is based in a combination of [Bitergia](http://bitergia.com)'s owl logo and [Wizard's white hat](https://openclipart.org/detail/245968/wizards-white-hat) from [Thewizardplusplus](https://openclipart.org/user-detail/thewizardplusplus)