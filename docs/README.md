# Intro

![Intro page](img/intro.jpg)

Hatstall is a web UI to manage part of [SortingHat](https://github.com/grimoirelab) data. It uses basically [DataTables JQuery plug-in](https://datatables.net/) to *search* and *order* data.

## Understanding SortingHat database

SortingHat stores and manages data about *community members*.

Community members are identified by the *identities* they are using in the different data sources (*git*, *github*, *bugzilla*, *slack*, etc.).

By default, each *identity* defines a *unique identity profile*. SortingHat is able to merge different *profiles* under a single one.

SortingHat is also able to manage community member *enrollments* information.

# Managing community profiles

`Profiles` page lists community profiles:

![Profiles list page](img/profiles.jpg)

Profiles list page shows every profile existing in the SortingHat database, showing for each community member information like:
* profile name
* profile email
* organizations where the member has been enrolled
* boolean to check if member is a bot or not
* profile country
* number of different identities used by the profile in the project

User is able to merge already existing profiles using `Merge` button.

The `edit` link allows Hatstall's user to see and manage unique profile info:

![Profile page](img/profile.jpg)

The `Edit` button allows Hatstall's user to modify profile main information:

![Edit profile information](img/profile-edit.jpg)

Using **Enrollments** `Add` button, the user is able to *enroll* the profile to existing organizations in the database:

![Add enrollment](img/profile-enroll.jpg)

It's also possible to *un-enroll* a profile from an organization.

*Still under-development*: User *shall* be able to edit enrollment initial and final date.

![Edit enrollments information](img/profile-enrollments-edit.jpg)

Using **Profile Identities** `Add` it's possible to add identities to the profile from the list of existing ones:

![Add identity to community member profile](img/profile-add-identity.jpg)

# Managing organizations

`Organizations` link shows a list of existing organizations:

![Organizations list](img/organizations.jpg)

It's possible to add new organizations to the database:

![Addingg organizations](img/organizations-add.jpg)

*Under development*: User *shall* be able to add and edit  organizations' *domains*.