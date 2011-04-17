'''
    Subsonic XBMC Plugin
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import simplejson as json
import urllib, urllib2
import xbmc
import Addon

class Subsonic:
    def __init__(self, server, user, password):
        self.server = server
        self.user = user
        self.password = password
        self.api_version = '1.5.0'
        self.client_name='xbmc'
        
    def ping(self):
        Addon.logging.debug('ping')
        payload = self.__get_json('ping.view')
        return payload
        
    def get_music_folders(self):
        Addon.logging.debug('get_music_folders')
        payload = self.__get_json('getMusicFolders.view')
        folders = payload['musicFolders']['musicFolder']
        total = len(folders)
        for folder in folders:
            Addon.add_directory({'mode': 'list_indexes', 'folder_id': folder['id']}, 
                                folder['name'], total_items=total)
        Addon.end_of_directory()

    def get_indexes(self, folder_id):
        Addon.logging.debug('get_indexes')
        payload = self.__get_json('getIndexes.view', {'musicFolderId': folder_id})
        indexes = payload['indexes']['index']
        index = []
        [index.extend(i) for i in [i['artist'] for i in indexes]]
        [Addon.add_artist(i) for i in index if type(i) is dict]
        Addon.end_of_directory()
      
    def __get_json(self, url, queries={}):
        queries.update({'v': self.api_version, 
                        'c': self.client_name, 
                        'u': self.user, 
                        'p': self.password,
                        'f': 'json'})
        Addon.logging.debug('queries: ' + str(queries))
        json_response = None
        query = Addon.build_query(queries)
        url = '%s/rest/%s?%s' % (self.server, url, query) 
        Addon.logging.debug('getting ' + url)
        try:
            response = urllib2.urlopen(url)
            try:
                json_response = json.loads(response.read())
            except ValueError:
                Addon.show_error([Addon.get_string(30002)])
                return False
        except urllib2.URLError, e:
            Addon.show_error([Addon.get_string(30001), str(e.reason)])
            return False

        payload = json_response.get('subsonic-response', None)
        if payload.get('status', 'failed') == 'ok':              
            return payload
        else:
            Addon.show_error([payload['error']['message'], 
                       'json version: ' + payload['version']])  
            return False 

