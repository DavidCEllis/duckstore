=========
Structure
=========

The basic idea of the project is to have a sqlite file and an associated archive.
The sqlite database is there to provide details and metadata about the documents
contained in the archive, or other documents that have not been digitized.

Duckstore can be launched from either an archive .7z file or a folder, the expected
structure of such an archive or folder is as follows:

Archive/
├─ duckstore/
│  ├─ <Stored Documents>
├─ duckstore.sql
