import requests
import urlparse
import re
import os
import sys
import urllib2
import urllib
import os_account
import os_images
import os_content_provider
from os_link_scraper import build_tree
from kodi_controls import KodiControls

kodi = KodiControls(addon_base_url=sys.argv[0], addon_handle=int(sys.argv[1]))
args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
img_provider = os_images.get_image_provider(kodi.get_poster_art_base())


if not os_account.log_in(kodi):
    exit(0)

if mode is None:
    categories = os_content_provider.get_categories(kodi.get_folder_art_base())
    kodi.display_entries(categories)

elif mode[0] == 'category':
    category_name = args['category_name'][0]
    category_url = args['category_url'][0]

    soup = build_tree(category_url)
    letters = os_content_provider.get_list_letters(soup, category_url)

    kodi.display_entries(letters)

elif mode[0] == 'search':
    category_name = args['category_name'][0]
    category_url = args['category_url'][0]

    user_input = kodi.get_user_input('Search for anime/drama titles...')
    url = category_url.format(urllib.quote(user_input))

    soup = build_tree(url)
    titles = os_content_provider.get_search_results(soup, '.*', img_provider)

    kodi.display_entries(titles)

elif mode[0] == 'search_result':
    url = args['url'][0]
    pattern = args['pattern'][0]

    soup = build_tree(url)
    titles = os_content_provider.get_search_results(soup, pattern, img_provider)

    kodi.display_entries(titles)

elif mode[0] == 'series':
    series_name = args['display_name'][0]
    series_url = args['series_url'][0]

    soup = build_tree(series_url)
    poster_art_base = kodi.get_poster_art_base()
    os_images.download_poster_image(poster_art_base, series_name, series_url)
    content = os_content_provider.get_series_content(soup, series_name, img_provider)

    kodi.display_entries(content)

elif mode[0] == 'episode':
    episode_url = args['episode_url'][0]
    episode_nbr = args['display_name'][0]
    series_name = args['series_name'][0]

    thumbnail = img_provider(series_name)
    soup = build_tree(episode_url)
    redirect_url = os_content_provider.get_episode_redirect(soup)
    video_path = os_content_provider.get_video_link(build_tree(redirect_url) if redirect_url else soup)
    title = series_name if episode_nbr == 'Full Movie' else '{0} - {1}'.format(series_name, episode_nbr) 

    kodi.play_video(video_path, title, thumbnail)
