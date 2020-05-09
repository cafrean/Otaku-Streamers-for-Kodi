import re
import os


def make_letter_entry(letter, category_url):
    letter_clean = letter.encode('ascii', 'ignore')

    return {'mode': 'letter', 'selected_letter': letter_clean, 'display_name': letter_clean, 'category_url': category_url, 'icon': 'DefaultFolder.png', 'is_folder': True}


def get_list_letters(soup, category_url):
    letters = [letter.text for letter in soup.findAll('h1') if all(ord(c) < 128 for c in letter)]

    return [make_letter_entry(letter, category_url) for letter in letters]


def get_categories(folder_art_base):
    base_url = 'https://otaku-streamers.com/{0}/'
    anime_url = base_url.format('anime')
    drama_url = base_url.format('drama')

    drama_folder = os.path.join(folder_art_base, 'dramafolder.png')
    anime_folder = os.path.join(folder_art_base, 'animefolder.png')

    return [_make_category_entry('anime', 'Anime', anime_url, anime_folder), _make_category_entry('drama', 'Drama', drama_url, drama_folder)]


def _make_category_entry(category_name, display_name, url, icon):
    return {'mode': 'category', 'category_name': category_name, 'category_url': url, 'display_name': display_name, 'icon': icon, 'is_folder': True}


def _make_series_entry(entry, img_provider):
    series_name = entry.text.encode('ascii', 'ignore')
    series_url = 'https:' + entry['href'].encode('ascii', 'ignore')
    icon = img_provider(series_name)

    return {'mode': 'series', 'display_name': series_name, 'series_url': series_url, 'icon': icon, 'is_folder': True}


def _make_content_entry(entry, series_name, img_provider):
    clean_url = 'https:' + entry['href'].encode('ascii', 'ignore')
    icon = img_provider(series_name)

    return {'mode': 'episode', 'display_name': entry.parent.text, 'series_name': series_name, 'episode_url': clean_url, 'icon': icon, 'is_folder': False}


def get_series_for_letter(soup, selected_letter, img_provider):
    letter = '0-9' if selected_letter == '0' else selected_letter
    series = soup.findAll('a', {'href': re.compile(r'\/\/otaku-streamers.com\/info\/\d+\/[{}].*'.format(letter), flags=re.IGNORECASE)})
    
    return [_make_series_entry(entry, img_provider) for entry in series]


def get_series_content(soup, series_name, img_provider):
    rows = soup.findAll('a', {'href': re.compile('//otaku-streamers.com/watch/')})

    return [_make_content_entry(entry, series_name, img_provider) for entry in rows]


def get_episode_redirect(soup):
    mature_content_warning = soup.findAll('img', {'src': re.compile('../../images/warning.jpg')})

    if not mature_content_warning:
        return None

    new_url = re.findall('../..(/watch.*)$', mature_content_warning[0].parent['href'])

    return 'https://otaku-streamers.com/{0}'.format(new_url[0])


def get_video_link(soup):
    return re.findall('"file", "(http.+?.mp4)', soup.text)[0]
