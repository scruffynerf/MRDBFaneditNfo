# MRDBFaneditNfo
uses MRDB api to create NFO files for Fanedits
Should work with Kodi, Jellyfin, Emby, and other media players that recognize .nfo files and poster.jpg
Use GUI for picking the right fanedit, but needs to be run from command line (for now)

# Still in early Beta, there are bugs, you have been warned.

Thanks to MoviesRemastered for adding the api, so we can avoid scraping.

## Bug reports/Patches welcomed
ideas/discussion welcomed at MRDB Discord: https://discord.gg/uaUz5PgNKj

Please feel free to write actual metadata plugins for Kodi, Jellyfin, Emby, Plex, etc... 
this python code is a proof of concept and standalone
Tech team came back with this but it's like another language to me:

This is quick and dirty but might give you what you want (I've just taken the main query and used a convert to JSON, it does not query other tables like ratings etc as thats a bit of a pain, for search results you can increment the page number until it runs out)...  


## Currently requires a login to access the API endpoints.
Get your account at https://www.moviesremastered.com
## Please donate to help them continue this service...

# API examples
## movieinfo:
```
https://www.moviesremastered.com/apimovieinfo.php?moviename=Batman:%20The%20Dark%20Knight
https://www.moviesremastered.com/apimovieinfo.php?id=523
```

## search: 
### (mirrors choices found on website form)
```
https://www.moviesremastered.com/apisearch.php?searchtype=Faneditor&genre=&franchise=&certificate=U&award=fanedit&language=&fanedittype=&searchterm=moviesremastered
https://www.moviesremastered.com/apisearch.php?searchtype=Faneditor&language=&fanedittype=&certificate=U&award=fanedit&genre=&sort=&franchise=&searchterm=moviesremastered&pagenum=2
```

# Program usage:

```MRDB_fanedit_nfo_maker.py [-h] [--auto] [--username USERNAME] [--password PASSWORD] [--poster {normal,hd}] media_root```

## Tag fanedits with .nfo and poster using MRDb API

```
positional arguments:
  media_root            Path to top-level media directory

options:
  -h, --help            show this help message and exit
  --auto                Auto-fetch if only one match is found
  --username USERNAME   MoviesRemastered username/email (optional, will ask if not given)
  --password PASSWORD   MoviesRemastered password (optional, will ask if not given)
  --poster {normal,hd}  Choose poster resolution to save (defaults to normal)
```
