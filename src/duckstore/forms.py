from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    StringField,
    MultipleFileField,
    SelectMultipleField,
    SelectField,
    SubmitField,
    BooleanField,
)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class MultipleTagField(SelectMultipleField):
    def pre_validate(self, form):
        # Override pre_validate so new tags can be added in-line
        # While I want to provide tags that already exist
        # It's going to be much easier just to add new tags while making the document
        pass


class SearchForm(FlaskForm):
    title = StringField("Title")
    source = SelectField("Source")
    tags = SelectMultipleField("Tags")
    search = SubmitField("Search")


class DocumentForm(FlaskForm):
    id = HiddenField("ID")  # This hidden field is used to update if needed
    date_added = DateField("Date Added")

    title = StringField("Title", validators=[DataRequired()])
    date_received = DateField("Date Received", validators=[DataRequired()])
    location = StringField("Physical Copy Location")
    tags = MultipleTagField("Tags")
    sources = MultipleTagField("Sources")
    files = MultipleFileField("Files")
    compress_pdf = BooleanField("Compress PDFs")
    submit = SubmitField()
