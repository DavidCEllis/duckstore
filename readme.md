# Duckstore #

Document store to manage important documents

Inspired by: https://github.com/alexwlchan/docstore

## Why remake this ##

* Needed to brush up on/relearn python/flask
* Upload/Download from web interface
  * I don't really want to mess around with a CLI if I don't need to
* Store data in an encrypted format so it can be kept in cloud storage
* SQLAlchemy/SQL backend instead of plain JSON, I just prefer the structure

## Dependencies ##

alembic - Managing changes to database structure / not currently used
bootstrap-flask - Making the page look barely acceptable
click - CLI for app runner
flask - web framework
flask-pretty - Make the HTML from flask readable
flask-wtf & wtforms - Web forms
py7zr - 7zip compression
select2 - Make the select fields actually usable
sqlalchemy - SQL Toolkit/Database ORM

Select2 - Better select dialogs

Ghostscript is used via subprocess in order to reduce the size of PDFs
