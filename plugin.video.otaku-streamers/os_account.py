import os
import xbmc
import xbmcaddon
import urllib
import urllib2
import md5
import cookielib
import sys


# --- Define variables ---

__addon__        = xbmcaddon.Addon()
__addonname__    = __addon__.getAddonInfo('id')

# ------------------------


# --- Define functions ---

# Returns the path to the cookie, translated for the OS/platform used.
def get_cookie_path():
    cookiepath = 'oscookie'
    dataroot = xbmc.translatePath('special://profile/addon_data/%s' % __addonname__ ).decode('utf-8')

    # Create addon_data folder if it doesn't exist.
    if not os.path.exists(dataroot):
        os.makedirs(dataroot)

    return os.path.join(dataroot, cookiepath)


# Used to log in the user and loading/saving cookies.
# Big thanks to t0mm0 (https://github.com/t0mm0) for helping with this function!
def log_in():
    print 'Trying to log in user...'

    login_url = 'https://otaku-streamers.com/community/login.php?do=login'

    #create cookiejar
    cj = cookielib.LWPCookieJar()

    #tell urllib2 to handle cookies
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    cookie_file = get_cookie_path()

    #try to load existing cookies
    try:
        #ignore_discard=True loads session cookies too

        cj.load(cookie_file, ignore_discard=True)

        print 'cookies loaded, checking if they are still valid...'

        #check to see if login cookies still valid
        response = urllib2.urlopen('https://otaku-streamers.com/community/faq.php')
        html = response.read()

        if 'class="welcomelink"' in html:
            print 'Cookie is valid. No need to log in.'
            #lets get out of here!
            return True

    #if cookie file does not exist we just keep going...
    except IOError:
        print 'Caught IOError!'
        pass

    # Get settings and user credentials.
    settings = xbmcaddon.Addon(id=__addonname__)
    username = settings.getSetting('username')
    password = settings.getSetting('password')

    #the onsubmit() javascript does this bit
    password_md5 = md5.md5(password).hexdigest()

    #build POST data (including hidden form fields)
    post_data = urllib.urlencode({'vb_login_username': username,
                                  's': '',
                                  'securitytoken': 'guest',
                                  'do': 'login',
                                  'vb_login_md5password': password_md5,
                                  'vb_login_md5password_utf': password_md5,
                                  })

    #POST to login page
    response = urllib2.urlopen(login_url, post_data)

    #check for login string
    html = response.read()

    if 'Thank you for logging in, %s.' % username in html:
        print 'logged in to otaku-streamers as %s.' % username
        xbmc.executebuiltin("XBMC.Notification(Login successful, Welcome to Otaku-Streamers!, 4000)")

        # Save cookies to disk (ignore_discard=True saves session cookies)
        cj.save(get_cookie_path(), ignore_discard=True)

        # Perform changes to add-on settings.
        settings.setSetting(id="current_user", value=username)

        return True
    else:
        xbmc.executebuiltin("XBMC.Notification(Login failed, Please try again!, 4000)")
        print 'login failed'
        return False


# Logs out the user by deleting any set cookies. This is called from the add-on settings.
def log_out():
    print 'User requested cookie to be deleted.'

    if(os.path.exists(get_cookie_path())):
        os.remove(get_cookie_path())

        print "Cookie was deleted."
        xbmc.executebuiltin("XBMC.Notification(Logged out, Cookie was deleted., 4000)")

    else:
        print "No cookie was found."
        xbmc.executebuiltin("XBMC.Notification(Not logged in, No cookie has been set., 4000)")

def user_is_logged_in():
        if log_in():
            return True
        else:
            return False

# -------------------------



# ------------------------------------------
# Execution of the script starts here.
# ------------------------------------------

# This part will run if called from add-on settings.
command = sys.argv[1]

if command == 'log_out':
    log_out()



