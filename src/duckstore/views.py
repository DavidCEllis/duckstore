from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for,
    flash,
    request,
    jsonify,
    current_app,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .forms import SearchForm, DocumentForm
from .database import db_session
from .database.models import Document, Tag, Source, File
from .util.filename_deduper import prepare_storepath
from .util.optimize_pdf import compress_pdf

duckstore = Blueprint(
    "duckstore", __name__, template_folder="templates", static_folder="static"
)


@duckstore.route("/", methods=["GET", "POST"])
def store_main():
    """
    Main page, shows a list of most recent documents + has a search form
    :return:
    """
    searchform = SearchForm()
    # Set up the choices for tags and sources
    tag_select = select(Tag).order_by(Tag.name)
    tags = [(item.Tag.name, item.Tag.name) for item in db_session.execute(tag_select)]
    searchform.tags.choices = tags

    source_select = select(Source).order_by(Source.name)
    sources = [("", "")]
    sources.extend(
        (item.Source.name, item.Source.name) for item in db_session.execute(source_select)
    )
    searchform.source.choices = sources

    results = None

    if searchform.validate_on_submit():
        title = f"%{searchform.title.data}%" if searchform.title.data else None
        tags = searchform.tags.data if searchform.tags.data else None
        source = searchform.source.data if searchform.source.data else None

        query = select(Document)

        if title:
            query = query.where(Document.title.ilike(title))
        if source:
            query = query.join(Document.sources).where(Source.name == source)
        if tags:
            for tag in tags:
                subquery = select(Document.id).join(Document.tags).where(Tag.name == tag)
                query = query.where(Document.id.in_(subquery))

        query = query.distinct().order_by(Document.date_received.desc())
        results = db_session.execute(query).scalars().all()

    return render_template("index.html", searchform=searchform, results=results)


@duckstore.route("/edit", methods=["GET", "POST"], strict_slashes=False)
def edit_document():
    doc_id = request.args.get("doc_id", None)

    docform = DocumentForm()
    source_select = select(Source).order_by(Source.name)
    sources = [
        (item.Source.name, item.Source.name) for item in db_session.execute(source_select)
    ]
    docform.sources.choices = sources

    tag_select = select(Tag).order_by(Tag.name)
    tags = [(item.Tag.name, item.Tag.name) for item in db_session.execute(tag_select)]
    docform.tags.choices = tags

    if docform.validate_on_submit():
        if doc_id:
            edit_type = "edit"
            query = select(Document).where(Document.id == doc_id)
            document = db_session.execute(query).scalars().one()
        else:
            edit_type = "new"
            document = Document()
            document.date_added = datetime.today()

        document.title = docform.title.data
        document.date_received = docform.date_received.data
        document.location = docform.location.data

        document.description = docform.description.data

        # TODO: rewrite so there's only 1 query for tags and 1 for sources
        #  rather than 1 per tag/source
        document.tags = []
        for tagname in docform.tags.data:
            tagname = tagname.strip()
            # Ignore empty tags
            if tagname == "":
                continue
            query = select(Tag).where(Tag.name == tagname)
            tag = db_session.execute(query).scalars().one_or_none()
            if not tag:
                tag = Tag(name=tagname)
                db_session.add(tag)
            document.tags.append(tag)

        document.sources = []
        for sourcename in docform.sources.data:
            sourcename = sourcename.strip()
            # Ignore empty sources
            if sourcename == "":
                continue
            query = select(Source).where(Source.name == sourcename)
            source = db_session.execute(query).scalars().one_or_none()
            if not source:
                source = Source(name=sourcename)
                db_session.add(source)
            document.sources.append(source)

        # Prepare the files here, but don't save them until the commit
        save_files = []
        folder = Path(current_app.config['STORE_PATH'], current_app.config['STORE_NAME'])

        # Check for 'files' which seems to actually always exist (why if no files are chosen!?)
        # Also check the first file has a filename
        # Flask seems to just get an empty file if no files are chosen
        if 'files' in request.files and request.files['files'].filename:
            for file in request.files.getlist('files'):
                safe_name = secure_filename(file.filename)
                outpath = prepare_storepath(folder / safe_name)

                store_filepath = str(outpath.relative_to(folder))
                db_file = File(path=store_filepath, original_name=safe_name)
                document.files.append(db_file)

                save_files.append((file, outpath))

        db_session.add(document)
        try:
            db_session.commit()
        except IntegrityError as exc:
            flash(f"Document addition failed: {exc}", 'danger')
            db_session.rollback()
        else:
            # Send them to the new document
            if edit_type == "new":
                success_message = f"Successfully added document: {document.title}"
            else:
                success_message = f"Successfully edited document: {document.title}"
            flash(success_message, 'success')

            for file, outpath in save_files:
                if docform.compress_pdf.data and outpath.suffix == '.pdf':
                    with TemporaryDirectory(prefix='temp_', dir=folder) as tmpdir:
                        tmp_file = Path(tmpdir) / Path(outpath).name
                        file.save(tmp_file)
                        result = compress_pdf(tmp_file, outpath)
                        if result.returncode == 0:
                            flash(f"Uploaded & Compressed {file.filename} as {outpath.name}")
                        else:
                            shutil.copyfile(tmp_file, outpath)
                            flash(f"Uploaded, Failed to Compress {file.filename} as {outpath.name}")

                else:
                    file.save(outpath)
                    flash(f"Uploaded {file.filename} as {outpath.name}")

            return redirect(url_for(".edit_document", doc_id=document.id))

    return render_template("edit_document.html", docform=docform, doc_id=doc_id)


@duckstore.route("/delete", strict_slashes=False)
def delete_document():
    doc_id = request.args.get("doc_id", None)
    if not doc_id:
        return redirect(url_for(".store_main"))

    doc = db_session.execute(select(Document).filter_by(id=doc_id)).scalars().one_or_none()
    if not doc:
        flash(f"Document with ID {doc_id} not found.")
        return redirect(url_for(".store_main"))

    # Delete the document, first clean up the files
    store_folder = Path(current_app.config['STORE_PATH'], current_app.config['STORE_NAME'])
    pending_deletion = [(file.original_name, file.full_path(store_folder)) for file in doc.files]

    # Remove the document
    db_session.delete(doc)
    db_session.commit()
    flash(f"Document: {doc.title} removed from the database.")

    # Clean up the associated files
    for fname, fpath in pending_deletion:
        try:
            fpath.unlink()
        except FileNotFoundError:
            flash(f"Could not delete: {fname}", 'error')
        else:
            flash(f"Deleted: {fname}")

    return redirect(url_for(".store_main"))


@duckstore.route("/docdata", methods=["POST"])
def get_data():
    docid = int(request.form.get("docid"))
    result = db_session.execute(select(Document).where(Document.id == docid))
    document = result.scalars().one_or_none()
    if document:
        data = document.to_dict()
        return jsonify(data)
    else:
        return "Document not found", 404


@duckstore.route("/download")
def download_file():
    file_id = request.args.get('file_id', None)
    if file_id:
        file = db_session.execute(select(File).where(File.id == file_id)).scalars().one_or_none()
        if file:
            folder = Path(current_app.config['STORE_PATH'], current_app.config['STORE_NAME'])
            result = send_from_directory(
                folder,
                file.path,
                download_name=file.original_name,
                as_attachment=True,
            )
            return result
        else:
            return "File not found", 404
    else:
        return "File not found", 404
