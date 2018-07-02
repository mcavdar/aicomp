Installation Instructions:

Install Django by following the Django Installation Guide: http://docs.djangoproject.com/en/dev/intro/install/

Create a directory for the djangology web application: mkdir djangology

Go into the djangology directory: cd djangology 

Check-out the the latest version of djangology into the current directory: svn co https://djangology.svn.sourceforge.net/svnroot/djangology  .

Edit settings.py to configure your database (DATABASE_ENGINE, DATABASE_NAME, DATABASE_USER, etc)

Create a database schema using your database client, for example: mysql> create database djangology;

Make sure the default encoding is "utf-8", for example: mysql> alter database djangology CHARACTER SET = utf8;

Populate the database schema used by the application: python manage.py syncdb

(You will have the option to create an administrator account during this step. Or you can create an administrator account by running: python manage.py createsuperuser)

Start the application: python manage.py runserver

You should be able to connect to the application at http://localhost:8000/. Login with the credentials created in the previous step.

For a full list of the Django manager options run: python manage.py help or consult the Django documentation.


Note:

The system has been tested with Python 2.5 and  Django 1.1. 









