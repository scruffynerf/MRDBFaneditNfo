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

# For Python Newbies in Windows:

You can follow these steps, OR grab the zip and run the setup_and_run.bat

## 🖥️ How to Install and Run on Windows

This guide walks you through installing Python, setting up the environment, and running the script on Windows.

### 📦 Prerequisites

- Windows 10 or 11
- Internet connection
- Basic familiarity with the Command Prompt

---

### 1️⃣ Install Python

1. Download Python from: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Run the installer:
   - ✅ Check **"Add Python to PATH"**
   - Click **Install Now**
3. Verify installation in Command Prompt:
   ```bash
   python --version
   ```

### 2️⃣ (Optional) Install Git to clone the repository:
Download Git from: https://git-scm.com/download/win
Install with default options.

### 3️⃣ Download the Code
#### Option A (after step 2): Clone with Git
```bash
git clone https://github.com/scruffynerf/MRDBFaneditNfo.git
cd MRDBFaneditNfo
```

#### Option B (no git needed): Download ZIP

Go to `https://github.com/scruffynerf/MRDBFaneditNfo`

Click Code > Download ZIP

Extract the ZIP and open a terminal in the folder.

### 4️⃣ (Optional, recommended) Create a Virtual Environment
In the project folder:

```bash
python -m venv venv
venv\Scripts\activate
```

### 5️⃣ Install Required Python Packages
Make sure you're in the project directory, then run:

```bash
pip install -r requirements.txt
```

### 6️⃣ Run the Script
To run the script:

```bash
python MRDB_fanedit_nfo_maker.py --help
```

Refer to the rest of the README for usage.

# ✅ Done!
You are now set up to run MRDBFaneditNfo on Windows.

# ⚙️ ALTERNATIVELY: One-Click Setup Script
You can use the included setup_and_run.bat script to automatically:
- Create a virtual environment
- Install dependencies
- Run the program
Just double-click the .bat file or run from the Command Prompt
