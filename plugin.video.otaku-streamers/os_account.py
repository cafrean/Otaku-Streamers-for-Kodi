import os
import urllib
import urllib2
import md5
import cookielib
import sys
from kodi_controls import KodiControls


def _get_cookie_path(data_root):
    return os.path.join(data_root, 'oscookie')


def _build_post_data(username, password):
    password_md5 = md5.md5(password).hexdigest()
    payload = {'vb_login_username': username, 's': '', 'securitytoken': 'guest', 'do': 'login',
               'vb_login_md5password': password_md5, 'vb_login_md5password_utf': password_md5}

    return urllib.urlencode(payload)


def _is_logged_in(cookie_jar, cookie):
    try:
        cookie_jar.load(cookie, ignore_discard=True)
        response = urllib2.urlopen('https://otaku-streamers.com/community/faq.php')
        html = response.read()

        return 'class="welcomelink"' in html
    except IOError as e:
        print('Caught IOError: {}').format(e)
        return False


def _perform_login(kodi, cookie_jar):
    login_url = 'https://otaku-streamers.com/community/login.php?do=login'

    credentials = kodi.get_credentials()
    username = credentials['username']
    post_data = _build_post_data(username, credentials['password'])

    response = urllib2.urlopen(login_url, post_data)
    html = response.read()

    if not 'Thank you for logging in, {}.'.format(username) in html:
        kodi.display_notification('Login failed', 'Please try again!')
        print('Login failed.')

        return False

    cookie_jar.save(_get_cookie_path(kodi.get_data_root()), ignore_discard=True)

    kodi.display_notification('Login successful', 'Welcome to Otaku-Streamers!')
    kodi.set_current_user(username)

    print('Logged in to Otaku-Streamers as {}.'.format(username))

    return True


def log_in(kodi):
    print('Trying to log in user...')

    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    cookie_file = _get_cookie_path(kodi.get_data_root())

    return _is_logged_in(cj, cookie_file) or _perform_login(kodi, cj)


def log_out(argv):
    kodi = KodiControls(argv[0], argv[1])
    data_root = kodi.get_data_root()
    cookie_path = _get_cookie_path(data_root)

    if not os.path.exists(cookie_path):
        print('No cookie was found.')
        kodi.display_notification('Not logged in', 'No cookie has been set.')
        return

    os.remove(cookie_path)

    print('Cookie was deleted.')
    kodi.display_notification('Logged out', 'Cookie was deleted.')


# This part will run if called from add-on settings.
command = sys.argv[1]

if command == 'log_out':
    log_out(sys.argv)

