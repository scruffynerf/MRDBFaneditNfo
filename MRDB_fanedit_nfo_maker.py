
import os
import re
import sys
import argparse
import requests
from urllib.parse import urljoin
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
from bs4 import BeautifulSoup

SUPPORTED_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.wmv', '.flv', '.mov', '.iso', '.vob'}

def is_video_file(file_path):
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS

def safe_filename(name):
    return re.sub(r'[^\w\-_\. ]', '_', name).strip().replace(' ', '_')

def minutes_from_runtime(runtime):
    try:
        return int(runtime)
    except:
        return 0

def clean_title_for_fuzzy(name):
    name = re.sub(r'\b(19|20)\d{2}\b', '', name)
    name = re.sub(r'\d{3,4}p', '', name)
    name = re.sub(r'_', ' ', name)
    name = re.sub(r'\b(BluRay|WEBRip|HDRip|x264|x265|HEVC|AAC|DVDRip|HDTV|Edition|The|Of|An)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\W+', ' ', name)
    return name.strip()


def login_to_moviesremastered(session, username=None, password=None):
    """
    Login to MoviesRemastered with enhanced debugging and multiple approaches
    """
    login_url = "https://www.moviesremastered.com/users/login.php"
    
    # Configure session with proper settings
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    })
    
    print("🌐 Step 1: Getting login page...")
    
    # First, visit the main site to establish session
    main_resp = session.get("https://www.moviesremastered.com/")
    main_resp.raise_for_status()
    print(f"🏠 Main page status: {main_resp.status_code}")
    
    # Now get the login page
    login_resp = session.get(login_url)
    login_resp.raise_for_status()
    print(f"🔑 Login page status: {login_resp.status_code}")
    print(f"🍪 Session cookies: {dict(session.cookies)}")
    
    # Parse the login page
    soup = BeautifulSoup(login_resp.text, "html.parser")
    
    # Find CSRF token
    csrf_token = None
    csrf_input = soup.find("input", {"name": "csrf"})
    if csrf_input:
        csrf_token = csrf_input.get("value")
    
    if not csrf_token:
        print("❌ Could not find CSRF token")
        # Print form HTML for debugging
        form = soup.find("form", {"id": "login-form"})
        if form:
            print("📋 Form HTML:")
            print(form.prettify())
        raise ValueError("CSRF token not found")
    
    print(f"🔐 CSRF token: {csrf_token}")
    
    # Get credentials if not provided
    if not username or not password:
        def prompt_login():
            root = tk.Tk()
            root.title("Login to MoviesRemastered")
            root.geometry("350x250")
            
            tk.Label(root, text="Username or Email:", font=("Arial", 10)).pack(pady=5)
            uname_entry = tk.Entry(root, width=30, font=("Arial", 10))
            uname_entry.pack(pady=5)
            
            tk.Label(root, text="Password:", font=("Arial", 10)).pack(pady=5)
            pwd_entry = tk.Entry(root, show="*", width=30, font=("Arial", 10))
            pwd_entry.pack(pady=5)
            
            result = {}
            
            def on_submit():
                result["username"] = uname_entry.get()
                result["password"] = pwd_entry.get()
                root.destroy()
            
            def on_enter(event):
                on_submit()
            
            root.bind('<Return>', on_enter)
            uname_entry.bind('<Return>', on_enter)
            pwd_entry.bind('<Return>', on_enter)
            
            submit_btn = tk.Button(root, text="Login", command=on_submit, font=("Arial", 10))
            submit_btn.pack(pady=10)
            
            uname_entry.focus()
            root.mainloop()
            
            return result.get("username"), result.get("password")
        
        username, password = prompt_login()
        
        if not username or not password:
            raise ValueError("Username and password required")
    
    print("🚀 Step 2: Submitting login form...")
    
    # Prepare form data exactly as the browser would
    form_data = {
        'csrf': csrf_token,
        'username': username,
        'password': password,
        'redirect': ''
    }
    
    print(f"📋 Form data: {form_data}")
    
    # Update headers for form submission
    session.headers.update({
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.moviesremastered.com',
        'Referer': login_url,
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
    })
    
    # Submit the form
    login_submit_resp = session.post(login_url, data=form_data)
    login_submit_resp.raise_for_status()
    
    print(f"📊 Login submit status: {login_submit_resp.status_code}")
    print(f"📍 Final URL: {login_submit_resp.url}")
    print(f"🍪 Cookies after login: {dict(session.cookies)}")
    
    # Save response for debugging
    with open('login_debug.html', 'w', encoding='utf-8') as f:
        f.write(login_submit_resp.text)
    print("💾 Response saved to login_debug.html")
    
    # Check for success indicators
    response_text = login_submit_resp.text
    
    # NEW: Check for JavaScript redirect (this is the key indicator!)
    js_redirect = re.search(r'window\.location\.href\s*=\s*["\']([^"\']+)["\']', response_text)
    if js_redirect:
        redirect_url = js_redirect.group(1)
        print(f"🔄 Found JavaScript redirect to: {redirect_url}")
        
        # Follow the redirect manually
        if redirect_url.startswith('/'):
            redirect_url = 'https://www.moviesremastered.com' + redirect_url
        
        print(f"🔄 Following redirect to: {redirect_url}")
        redirect_resp = session.get(redirect_url)
        redirect_resp.raise_for_status()
        
        print(f"✅ Redirect successful! Status: {redirect_resp.status_code}")
        print(f"🍪 Final cookies: {dict(session.cookies)}")
        
        # Update response_text to the redirected page for final verification
        response_text = redirect_resp.text
        
        # Save the final page for debugging
        with open('final_page_debug.html', 'w', encoding='utf-8') as f:
            f.write(response_text)
        print("💾 Final page saved to final_page_debug.html")
    
    # Multiple ways to check for successful login
    success_checks = [
        ('JavaScript redirect found', js_redirect is not None),
        ('Contains logout', 'logout' in response_text.lower()),
        ('Contains Logout', 'Logout' in response_text),
        ('No "Please Log In"', 'Please Log In' not in response_text),
        ('No login form', 'id="login-form"' not in response_text),
        ('Has user menu', 'user-menu' in response_text.lower() or 'profile' in response_text.lower()),
        ('Dashboard/home', 'dashboard' in response_text.lower() or 'welcome' in response_text.lower()),
    ]
    
    print("\n🔍 Login success checks:")
    login_success = False
    for check_name, result in success_checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}: {result}")
        if result and check_name in ['JavaScript redirect found', 'Contains logout', 'Contains Logout']:
            login_success = True
    
    # Additional check: look for error messages
    error_indicators = [
        'Invalid username or password',
        'Login failed',
        'incorrect',
        'Please try again'
    ]
    
    found_errors = [error for error in error_indicators if error.lower() in response_text.lower()]
    if found_errors:
        print(f"❌ Found error messages: {found_errors}")
        login_success = False
    
    # Final determination
    if login_success:
        print("\n✅ Login successful!")
        return session
    else:
        print("\n❌ Login failed")
        
        # Print part of response for debugging
        if len(response_text) > 1000:
            print(f"📄 Response preview: {response_text[:500]}...{response_text[-500:]}")
        else:
            print(f"📄 Full response: {response_text}")
        
        raise ValueError("Login failed - check credentials and debug files for details")


def search_mrdb_api(session, searchterm, page=1):
    url = "https://www.moviesremastered.com/apisearch.php"
    params = {
        "searchtype": "Title",
        "searchterm": searchterm,
        "pagenum": page
    }
    print(f"🔍 Searching API (page {page}) for: {params['searchtype']} '{searchterm}'")
    resp = session.get(url, params=params)
    resp.raise_for_status()
    results = resp.json()
    return results

def gui_select_from_results(results, session, searchterm, poster_res, page, has_prev_page):
    selected = {'index': None}
    next_page_results = []

    def on_select(i):
        selected['index'] = i
        root.destroy()

    def on_next_page():
        nonlocal next_page_results
        next_page_results = search_mrdb_api(session, searchterm, page + 1)
        if next_page_results:
            selected['index'] = 'next'
            root.destroy()

    def on_prev_page():
        selected['index'] = 'prev'
        root.destroy()

    def on_skip():
        root.destroy()

    root = tk.Tk()
    width = 1000
    height = 1000
    root.geometry(f"{width}x{height}")
    root.title(f"Select Fanedit for {searchterm} - Page {page}")

    canvas = tk.Canvas(root)
    frame = tk.Frame(canvas)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    images = []
    for i, r in enumerate(results):
        try:
            thumb = r.get("posterarturl") or r.get("hiresposterart", "")
            if thumb.startswith("/"):
               thumb = urljoin("https://www.moviesremastered.com", thumb)
            img_data = session.get(thumb).content
            pil_img = Image.open(BytesIO(img_data)).resize(( int((width/8)) , int((width/8)*1.33) ))
            tk_img = ImageTk.PhotoImage(pil_img)
            images.append(tk_img)
            btn = tk.Button(frame, image=tk_img, text=r['editname'], compound="top",  wraplength=int(width/8),  justify="center",command=lambda i=i: on_select(i))
            btn.grid(row=i // 5, column=i % 5, padx=2, pady=2)
        except:
            continue

    nav_frame = tk.Frame(root)
    nav_frame.pack(side="bottom", pady=10)
    if has_prev_page:
        tk.Button(nav_frame, text="⬅ Prev", command=on_prev_page).pack(side="bottom")
    
    print(f"Result count = {len(results)}")
    if len(results) >= 20:
        tk.Button(nav_frame, text="➡ Next", command=on_next_page).pack(side="bottom")

    tk.Button(nav_frame, text="⏭ Skip", command=on_skip).pack(side="bottom")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", on_frame_configure)
    root.mainloop()

    if selected['index'] == 'next':
        return gui_select_from_results(next_page_results, session, searchterm, poster_res, page + 1, True)
    elif selected['index'] == 'prev':
        if page > 1:
            prev_results = search_mrdb_api(session, searchterm, page - 1)
            return gui_select_from_results(prev_results, session, searchterm, poster_res, page - 1, page > 2)
    else:
        return results[selected['index']] if selected['index'] is not None else None

def fetch_movie_info_api(movie, target_folder, session, poster_res):
    movie_id = movie["id"]
    info_url = f"https://www.moviesremastered.com/apimovieinfo.php?id={movie_id}"
    resp = session.get(info_url)
    resp.raise_for_status()
    data = resp.json()

    title = data.get("editname", f"Movie {movie_id}")
    safe_title = safe_filename(title)
    faneditor = data.get("FaneditorsName", "Unknown")
    runtime = minutes_from_runtime(data.get("FaneditRuntime", "0"))
    synopsis = data.get("Synopsis", "")
    intentions = data.get("Intentions", "")
    changelist = data.get("ChangeList", "")
    genres = data.get("Genre", "").replace("/", " / ")
    certificate = data.get("certificate", "")
    resolution = data.get("Resolution", "")
    language = data.get("language", "")
    franchise = data.get("Franchise", "")
    fanedit_type = data.get("FaneditType", "")
    release_date = data.get("FanediReleaseDate", "")[-4:]

    poster_url = data.get("hiresposterart") if poster_res == "hd" else data.get("posterarturl")
    if poster_url.startswith("/"):
       poster_url = urljoin("https://www.moviesremastered.com", poster_url)

    nfo_path = os.path.join(target_folder, "movie.nfo")
    poster_path = os.path.join(target_folder, "movie.jpg")

    if poster_url:
        img_data = session.get(poster_url).content
        with open(poster_path, "wb") as f:
            f.write(img_data)

    nfo_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
  <title>{title}</title>
  <originaltitle>{title}</originaltitle>
  <year>{release_date}</year>
  <plot>{synopsis}</plot>
  <runtime>{runtime}</runtime>
  <genre>{genres}</genre>
  <studio>Fanedit by {faneditor}</studio>
  <director>{faneditor}</director>
  <thumb>{Path(poster_path).name}</thumb>
  <fanedit_type>{fanedit_type}</fanedit_type>
  <certificate>{certificate}</certificate>
  <resolution>{resolution}</resolution>
  <language>{language}</language>
  <source>Unknown</source>
  <franchise>{franchise}</franchise>
  <intentions>{intentions}</intentions>
  <changelist>{changelist}</changelist>
  <url>{info_url}</url>
</movie>"""
    with open(nfo_path, "w", encoding="utf-8") as f:
        f.write(nfo_xml)
    print(f"✅ Saved NFO: {nfo_path}")
    print(f"🖼️ Saved Poster: {poster_path}")

def walk_and_process_media(root_path, session, auto_mode=False, poster_res="normal"):
    for root, dirs, files in os.walk(root_path):
        media_files = [f for f in files if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS]
        if not media_files:
            continue

        for file in media_files:
            folder_path = Path(root)
            name_guess = Path(file).stem
            if Path(file).suffix.lower() == '.vob':
                if name_guess.lower() == "video_ts":
                   name_guess = folder_path.parent.parent.name
                else:
                   continue

            existing_nfos = list(folder_path.glob("*.nfo"))
            if existing_nfos:
                print(f"⚠️ Skipping {file}, NFO already exists.")
                continue

            print(f"📦 Found: {file}")
            print(f"🔍 Guessing title: '{name_guess}'")

            results = search_mrdb_api(session, name_guess)
            #print(results)
           
            if not results or len(results) == 0:
                fuzzy = clean_title_for_fuzzy(name_guess)
                if fuzzy is not None:
                    print(f"🔁 Retrying with fuzzy: '{fuzzy}'")
                    results = search_mrdb_api(session, fuzzy)
                    name_guess = fuzzy
                    print(results)
                if not results or len(results) == 0:
                   manual = input("Manual search (or leave blank to skip): ").strip()
                   while manual:
                       results = search_mrdb_api(session, manual)
                       print(results)
                       if not results or len(results) == 0:
                          print("❌ No matches found.")
                          manual = input("Manual search (or leave blank to skip): ").strip()
                          continue
                       name_guess = manual
                       manual = False

            if auto_mode and len(results) == 1:
                fetch_movie_info_api(results[0], str(folder_path), session, poster_res)
                continue

            if len(results) > 1:
                selected = gui_select_from_results(results, session, name_guess, poster_res, 1, False)
                if selected:
                    fetch_movie_info_api(selected, str(folder_path), session, poster_res)
                else:
                    print("⏭️ Skipped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tag fanedits with .nfo and poster using MRDb API")
    parser.add_argument("media_root", help="Path to top-level media directory")
    parser.add_argument("--auto", action="store_true", help="Auto-fetch if only one match is found")
    parser.add_argument("--username", help="MoviesRemastered username/email")
    parser.add_argument("--password", help="MoviesRemastered password")
    parser.add_argument("--poster", choices=["normal", "hd"], default="normal", help="Choose poster resolution to save")
    args = parser.parse_args()

    session = requests.Session()
    session = login_to_moviesremastered(session, args.username, args.password)
    walk_and_process_media(args.media_root, session, auto_mode=args.auto, poster_res=args.poster)
