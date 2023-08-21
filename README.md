# Duckstore #

Document store to manage important documents

Inspired by: https://github.com/alexwlchan/docstore

## How do I launch this again? ##
Install via pip for development 
`pip install -e .`
Run `duckstore` in the terminal.
This will run on the flask test server and that's enough for the purpose of this project.
This is not intended to be run across the internet, just on a local network.

Make sure ghostscript is installed for the PDF compression.

## Why remake this ##

* Needed to brush up on/relearn python/flask
* Upload/Download from web interface
  * I don't really want to mess around with a CLI if I don't need to
* Store data in an encrypted format so it can be kept in cloud storage
* SQLAlchemy/SQL backend instead of plain JSON, I just prefer the structure

## Dependencies ##

* alembic - Managing changes to database structure / not currently used
* bootstrap-flask - Making the page look barely acceptable
* click - CLI for app runner
* flask - web framework
* flask-pretty - Make the HTML from flask readable
* flask-wtf & wtforms - Web forms
* py7zr - 7zip compression
* sqlalchemy - SQL Toolkit/Database ORM
* Select2 (JS) - Better select dialogs

Ghostscript is used via subprocess in order to reduce the size of PDFs
