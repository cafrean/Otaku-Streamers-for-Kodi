import requests

import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import re
import os
import sys
import urllib
import urllib2
import account
from BeautifulSoup import BeautifulSoup

# --- Define functions ---

def resolve(web_url):
    response = urllib2.urlopen(web_url)
    html = response.read()

    video_url = re.findall('"file", "(http.+?.mp4)', html)
    return video_url[0]

def build_url(query):
    return addon_base_url + '?' + urllib.urlencode(query)

def build_tree(url):
    page = requests.get(url)

    # This fixes some of the issues with parsing malformed tags on OS.
    data= page.text.replace("<!-oscontent>", "").replace("<!-oscontentend>", "")
    return BeautifulSoup(data)

def user_is_logged_in():
        if account.log_in():
            return True
        else:
            return False

# ------------------------



# ------------------------------------------
# Execution of the script starts here.
# ------------------------------------------

addon_base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'episodes')
mode = args.get('mode', None)

# Build file path to the plugins addon_data folder, and image folder.
__addon__        = xbmcaddon.Addon()
__addonname__    = __addon__.getAddonInfo('id')
dataroot = xbmc.translatePath('special://profile/addon_data/%s' % __addonname__).decode('utf-8')

imagefolder = os.path.join(dataroot, "images")

# Create image folder if it doesn't exist.
if not os.path.exists(imagefolder):
    os.makedirs(imagefolder)

# Create list of categories
if mode is None:

    # Performs the first attempt to log in.
    # Categories are only displayed if user is successfully logged in, to avoid confusion.
    if user_is_logged_in():

        # Create the file paths to the folder art.
        folder_art_base = xbmc.translatePath('special://home/addons/{0}/resources/images/folder_art'.format(__addonname__)).decode('utf-8')
        drama_folder = os.path.join(folder_art_base, 'dramafolder.png')
        anime_folder = os.path.join(folder_art_base, 'animefolder.png')

        url = build_url({'mode': 'category', 'categoryname': "anime"})
        li = xbmcgui.ListItem("Anime", iconImage=anime_folder)
        li.setProperty('fanart_image', __addon__.getAddonInfo('fanart'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

        url = build_url({'mode': 'category', 'categoryname': "drama"})
        li = xbmcgui.ListItem("Drama", iconImage= drama_folder)
        li.setProperty('fanart_image', __addon__.getAddonInfo('fanart'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(addon_handle)

# Create list of available letters
elif mode[0] == 'category':
    category_name = args['categoryname'][0]

    # Load page of selected category.
    category_url = 'http://otaku-streamers.com/{0}/'.format(category_name)
    tree = build_tree(category_url)

    # Get all letters
    letters = tree.findAll('h1')

    # Build the list containing folders for each category/letter.
    for entry in letters:
        url = build_url({'mode': 'letter', 'selectedletter': entry.text, 'categoryurl': category_url})
        li = xbmcgui.ListItem(entry.text, iconImage='DefaultFolder.png')
        li.setProperty('fanart_image', __addon__.getAddonInfo('fanart'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)


    xbmcplugin.endOfDirectory(addon_handle)

# Show the selected list of series.
elif mode[0] == 'letter':
    category_url = args['categoryurl'][0]
    selected_letter = args['selectedletter'][0]

    # Get name and URL of all series starting with the letter of the chosen folder.
    tree = build_tree(category_url)

    series = tree.findAll('span', attrs={'class': 'title_link'})

    for entry in series:

        if selected_letter != "0":
            tag = entry.find('a', text=re.compile("^" + selected_letter + ".+?"))
        else:
            tag = entry.find('a', text=re.compile("^[0-9].+?"))

        if tag is not None:
            # Since some titles and URLs contain incompatible unicode characters.
            seriesName = entry.text.encode("ascii", "ignore")
            seriesUrl = entry.find('a')['href'].encode("ascii", "ignore")

            # Check if cover-art/thumbnail is available
            imageName = seriesName.replace("/", "")
            imageUri = os.path.join(imagefolder, imageName + ".jpg")

            # If an image exists for this particular series; store the URI.
            if os.path.exists(imageUri):
                icon = imageUri
            else:
                icon = "DefaultVideo.png"

            url = build_url({'mode': 'series', 'seriesname': seriesName, 'seriesurl': seriesUrl, 'seriesicon': icon})
            li = xbmcgui.ListItem(seriesName, iconImage=imageUri)
            li.setProperty('fanart_image', __addon__.getAddonInfo('fanart'))
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

# Show the list of episodes for the selected series.
elif mode[0] == 'series':

    series_name = args['seriesname'][0]
    series_url = args['seriesurl'][0]
    series_icon = args['seriesicon'][0]

    tree = build_tree(series_url)

    rows = tree.findAll('a', text=re.compile("Episode [0-9]|Full Movie"))

    for entry in rows:
        # Since some URLs contain incompatible unicode characters.
        cleanUrl = entry.parent['href'].encode("ascii", "ignore")

        url = build_url({'mode': 'episode', 'episodename': entry.parent.text, 'episodeurl': cleanUrl})
        li = xbmcgui.ListItem(entry.parent.text, iconImage=series_icon)
        li.setProperty('fanart_image', __addon__.getAddonInfo('fanart'))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                            listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)

# If an episode has been chosen
elif mode[0] == 'episode':

    # Perform an additional login-check, in order to properly load the cookie.
    if user_is_logged_in():

        episode_url = args['episodeurl'][0]

        # Check if a "mature content"-warning is displayed.
        response = urllib2.urlopen(episode_url)
        html = response.read()
        warnings = re.findall('warning.jpg', html)

        # If warnings are found: Follow the redirect URL to access the actual video.
        if len(warnings) > 0:
            new_url = re.findall('"../..(/watch.+?)">', html)
            episode_url = "http://otaku-streamers.com/{0}".format(new_url[0])

        xbmc.Player().play(resolve(episode_url))

        xbmcplugin.endOfDirectory(addon_handle)



