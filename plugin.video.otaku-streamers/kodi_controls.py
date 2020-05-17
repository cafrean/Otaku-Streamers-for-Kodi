import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib


class KodiControls:
    def __init__(self, addon_base_url, addon_handle):
        self.addon_base_url = addon_base_url
        self.addon_handle = addon_handle
        self.addon = xbmcaddon.Addon()
        self.addon_name = xbmcaddon.Addon().getAddonInfo('id')

    def __build_url(self, query):
        return self.addon_base_url + '?' + urllib.urlencode(query)

    def get_data_root(self):
        return xbmc.translatePath('special://profile/addon_data/{}'.format(self.addon_name)).decode('utf-8')

    def get_folder_art_base(self):
        return xbmc.translatePath('special://home/addons/{}/resources/images/folder_art'.format(self.addon_name)).decode('utf-8')

    def get_poster_art_base(self):
        return xbmc.translatePath('special://profile/addon_data/{}/images/posters'.format(self.addon_name)).decode('utf-8')

    def get_credentials(self):
        return {'username': self.addon.getSetting('username'), 'password': self.addon.getSetting('password')}

    def set_current_user(self, username):
        return self.addon.setSetting(id="current_user", value=username)

    def add_list_item(self, entry):
        li = xbmcgui.ListItem(entry['display_name'], iconImage=entry['icon'])
        li.setProperty('fanart_image', self.addon.getAddonInfo('fanart'))
        li.setThumbnailImage(entry['icon'])

        xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=self.__build_url(entry), listitem=li, isFolder=entry['is_folder'])

    def display_notification(self, header, subtitle):
        xbmc.executebuiltin('XBMC.Notification({},{}, 4000)'.format(header, subtitle))

    def get_user_input(self, label):  
        kb = xbmc.Keyboard('', label)
        kb.doModal()

        return kb.getText() if kb.isConfirmed() else ''

    def display_entries(self, entries):
        xbmcplugin.setContent(self.addon_handle, 'episodes')

        [self.add_list_item(entry) for entry in entries]

        xbmcplugin.endOfDirectory(self.addon_handle)

    def play_video(self, video_path, title, thumbnail):
        li = xbmcgui.ListItem(thumbnailImage=thumbnail)
        li.setInfo('video', {'title': title})

        xbmc.Player().play(video_path + '|verifypeer=false', li)

        xbmcplugin.endOfDirectory(self.addon_handle)
