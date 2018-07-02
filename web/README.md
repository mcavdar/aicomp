## Requirements:

**postgresql** 

`sudo apt-get install postgresql postgresql-contrib`<br/>
**pip** 

`sudo apt-get install python-pip`<br/>
**django** 1.1.3 

`pip install django==1.1.3`<br/>
**psycopg2** 

`pip install psycopg2`<br/>

And copy **[smart_if.py](https://raw.githubusercontent.com/mcavdar/aicomp/master/web/smart_if.py)** file to your django templatetags folder.

**`~/.local/lib/python2.7/site-packages/django/templatetags/`** <br/>
or <br/>
**`~/anaconda2/lib/python2.7/site-packages/django/templatetags/`** <br/>

## Installation & Run Steps:

Create a database schema using your database client, for example: 

**`psql> create database djangology;`**<br/>

Populate the database schema used by the application: 

**`python manage.py syncdb`**<br/>

To run web application:

**`python manage.py runserver`**<br/>

(You can create an administrator account by running:

**`python manage.py createsuperuser`**)
