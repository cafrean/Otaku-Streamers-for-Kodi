import urllib2
import urllib
import os
import re


def get_image_provider(poster_folder):
    def get_poster(series_name):
        image_name = series_name.replace('/', '')
        image_uri = os.path.join(poster_folder, image_name + '.jpg')

        return image_uri if os.path.exists(image_uri) else 'DefaultVideo.png'

    return get_poster


def download_poster_image(poster_folder, series_name, series_url):
    image_path = os.path.join(poster_folder, series_name + '.jpg')

    if os.path.exists(image_path):
        print('Image for {0} already exists').format(series_name)
        return

    response = urllib2.urlopen(series_url)
    image_url = re.findall(r'\/\/static.otaku-streamers.com\/aniencyclopedia\/images\/.+?.jpg', response.read())

    if len(image_url) < 1:
        print('No image could be found for {0} on Otaku-Streamers.').format(series_name)
        return

    if not os.path.exists(poster_folder):
        os.makedirs(poster_folder)

    image_url_full = 'https:' + image_url[0]
    urllib.urlretrieve(image_url_full, image_path)

    print('Fetched image for {0} from URL: {1}').format(series_name, image_url_full)
