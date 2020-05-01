import xbmc
import xbmcaddon
import urllib2
import urllib
import os
import re

__addon__        = xbmcaddon.Addon()
__addonname__    = __addon__.getAddonInfo('id')
scrape_folder = xbmc.translatePath('special://profile/addon_data/{0}/images/posters'.format(__addonname__)).decode('utf-8')

if not os.path.exists(scrape_folder):
    os.makedirs(scrape_folder)

def get_poster_image(series_name):
    # Check if cover-art/thumbnail is available
    image_name = series_name.replace("/", "")
    image_uri = os.path.join(scrape_folder, image_name + ".jpg")

    # If an image exists for this particular series; store the URI.
    if os.path.exists(image_uri):
        icon = image_uri
    else:
        icon = "DefaultVideo.png"

    return icon


def download_poster_image(series_name, series_url):
    # If an image hasn't already been downloaded for this series...
    if not os.path.exists(os.path.join(scrape_folder, series_name + ".jpg")):
        response = urllib2.urlopen(series_url)
        html = response.read()

        image_url = re.findall('\/\/static.otaku-streamers.com\/aniencyclopedia\/images\/.+?.jpg', html)

        if len(image_url) < 1:
            print "No image could be found for {0} on Otaku-Streamers.".format(series_name)
        else:
            # Download the image
            imgage_url_full = 'https:' + image_url[0]
            print "Fetching image for {0} from URL: {1}".format(series_name, imgage_url_full)
            urllib.urlretrieve(imgage_url_full, "{0}/{1}{2}".format(scrape_folder, series_name, ".jpg"))
    else:
        print "Image for {0} already exists".format(series_name)