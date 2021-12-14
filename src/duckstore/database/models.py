from pathlib import Path

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date, DateTime, func, select
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


def add_repr(cls):
    def _repr(obj, **fields):
        classname = obj.__class__.__name__
        output_values = [f"{key!s}={value!r}" for key, value in fields.items()]
        output_base = " ".join(item for item in output_values)
        reprstring = f"<{classname} {output_base}>"
        return reprstring
    cls._repr = _repr
    return cls


def make_association_table(source1, source2):
    """
    Shortcut function for making association tables based on tablenames
    assuming that 'id' is the element needed for association

    :param source1: First table that makes part of the many-to-many relationship
    :param source2: Second table
    :return: An association table that connects the two
    """
    return Table(
        f"associate_{source1}_{source2}",
        Base.metadata,
        Column(f"{source1}_id", ForeignKey(f"{source1}.id"), primary_key=True),
        Column(f"{source2}_id", ForeignKey(f"{source2}.id"), primary_key=True),
    )


associate_document_source = make_association_table("document", "source")
associate_document_tag = make_association_table("document", "tag")


@add_repr
class File(Base):
    """
    The Actual File links for the documents.

    This is a separate table because 1 'document' could have more than one
    connected file
    """

    __tablename__ = "file"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('document.id'))
    path = Column(String)  # Relative to the store folder.
    original_name = Column(String)  # The original filename in case it got changed

    def __repr__(self):
        return self._repr(id=self.id, path=self.path, original_name=self.original_name)

    def to_dict(self):
        return {"id": self.id, "path": self.path, "original_name": self.original_name}

    def full_path(self, store_folder):
        return Path(store_folder, self.path)


@add_repr
class Source(Base):
    """
    Companies/People/Agencies that sent the document.

    One Document can come from multiple companies/agencies so this is a many to many.
    """

    __tablename__ = "source"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


@add_repr
class Tag(Base):
    """
    Other assorted tags that can be given to documents
    """

    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return self._repr(id=self.id, name=self.name)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


@add_repr
class Document(Base):
    """
    The Main Document Table
    """

    __tablename__ = "document"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    location = Column(String)  # If there's a physical copy where did I put it.
    date_added = Column(DateTime, server_default=func.now())
    date_received = Column(Date)

    files = relationship("File", backref="document", cascade="all, delete-orphan")
    sources = relationship("Source", secondary=associate_document_source, backref="documents")
    tags = relationship("Tag", secondary=associate_document_tag, backref="documents")

    def __repr__(self):
        if self.location:
            return self._repr(
                id=self.id,
                title=self.title,
                location=self.location,
                date_added=self.date_added.strftime("%Y-%m-%d"),
                sources=f"[{', '.join(s.name for s in self.sources)}]",
                tags=f"[{', '.join(t.name for t in self.tags)}]"
            )
        else:
            return self._repr(
                id=self.id,
                title=self.title,
                date_added=self.date_added.strftime("%Y-%m-%d"),
                sources=f"[{', '.join(s.name for s in self.sources)}]",
                tags=f"[{', '.join(t.name for t in self.tags)}]"
            )

    def to_dict(self):
        files = [file.to_dict() for file in self.files]
        sources = [source.to_dict() for source in self.sources]
        tags = [tag.to_dict() for tag in self.tags]
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "date_added": self.date_added.strftime("%Y-%m-%d"),
            "date_received": self.date_received.strftime("%Y-%m-%d"),
            "tags": tags,
            "sources": sources,
            "files": files,
        }


def merge_tags(main_tag, *tags):
    """
    Merge tags into main_tag, designed to be used from the shell

    If documents with any of the following tags are already in the main tag
    do nothing, otherwise place main_tag on any documents missing the tag.

    :param main_tag: Tag that should be kept
    :param tags: Tags that should be combined into the main tag
    :return main tag:
    """
    main_docs = [doc for doc in main_tag.documents]

    for tag in tags:
        pass


# noinspection DuplicatedCode,PyUnresolvedReferences
def clear_unused(db_session):
    # Clean up unused tags and unused sources
    used_tags = select(associate_document_tag.c.tag_id)
    unused_tags = db_session.execute(select(Tag).where(~Tag.id.in_(used_tags))).scalars()
    for tag in unused_tags:
        db_session.delete(tag)

    print(f"Marked {len(unused_tags)} unused tags for deletion.")
    used_sources = select(associate_document_source.c.source_id)
    unused_sources = db_session.execute(
        select(Source).where(~Source.id.in_(used_sources))
    ).scalars()

    for source in unused_sources:
        db_session.delete(source)

    print(f"Marked {len(unused_sources)} unused sources for deletion")

    db_session.commit()
    print("Sources and Tags removed.")
