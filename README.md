# MRDBFaneditNfo
uses MRDB api to create NFO files for Fanedits

Still in Beta, there are bugs.

usage: MRDB_fanedit_nfo_maker.py [-h] [--auto] [--username USERNAME] [--password PASSWORD] [--poster {normal,hd}] media_root

Tag fanedits with .nfo and poster using MRDb API

positional arguments:
  media_root            Path to top-level media directory

options:
  -h, --help            show this help message and exit
  --auto                Auto-fetch if only one match is found
  --username USERNAME   MoviesRemastered username/email
  --password PASSWORD   MoviesRemastered password
  --poster {normal,hd}  Choose poster resolution to save
