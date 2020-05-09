from BeautifulSoup import BeautifulSoup
import urllib2


def build_tree(url):
    response = urllib2.urlopen(url)
    page = response.read()

    # This fixes some of the issues with parsing malformed tags on OS.
    data = page.replace("<!-oscontent>", "").replace("<!-oscontentend>", "")
    return BeautifulSoup(data)
