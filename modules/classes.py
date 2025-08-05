## Imports ##
import inspect
from datetime import datetime
from modules.functions import *

## Shared ##
# Note that type checking usually isn't needed in class __init__
class Session(): # bot session
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.event_registry = {}
        self.command_registry = {}
        self.token = None

class ProfileConnection():
    def __init__(self, key: str, username: str, url: str):
        self.platform = key
        self.username = username
        self.url = url

class Trophy():
    def __init__(self, background: str, description: str, foreground: str, title: str):
        self.background_url = f"{url}{background}"
        self.description = description
        self.foreground = f"{url}{foreground}"
        self.title = title

def build_profile(self, username: str = None, userid: int = None, api_response: dict = None):
    if not api_response:
        data = {
            "auth": None,
            "method": "get",
            "endpoint": "profile",
            "data": {}
        }

        if username:
            data["data"] = {"user": username}
        else:
            data["data"] = {"userId": userid}

        success, response = server_request(type="post", data=data)
        if not success:
            reason = "<response isn't in json>"
            try:
                reason = response.json().get('reason')
            except Exception as e:
                reason = f"<json parsing error: {e}>"
            show_message(
                f"Error in .{inspect.currentframe().f_code.co_name}(): {reason}", "Error")
        
            self._success = False
            return
        else:
            api_response = response.json()['json']

    if api_response.get('error'):
        self._success = False
        return

    self.banner_id = api_response.get('banner')
    self.description = api_response.get('description')
    self.followers = api_response.get('followers')
    self.follows = api_response.get('follows')
    self.friend_status = api_response.get('follow')
    self.id = api_response.get('id')
    self.likes = api_response.get('likes')
    self.made_unix = api_response.get('made')
    self.online_unix = api_response.get('online')
    self.picture_id = api_response.get('picture')
    self.status = api_response.get('status')
    self.unseen_dms = api_response.get('unseen')
    self.user = api_response.get('user')
    self.verified = api_response.get('verified')

    self.banner_url = f"{url}/uploads/{self.banner_id}"
    self.following = self.friend_status != "none"
    self.made = datetime.fromtimestamp(self.made_unix or 0)
    self.online = datetime.fromtimestamp(self.online_unix or 0)
    self.picture_url = f"{url}/uploads/{self.picture_id}"
    self.url = f"https://chat.jonazwetsloot.nl/users/{self.user}"
    self.username = self.user

    connections = {}
    collection = api_response.get('connections')
    if isinstance(collection, dict):
        for key, item in collection.items():
            connections[key] = ProfileConnection(key, item['username'], item['url'])
    self.connections = connections

    trophies = []
    for trophy in api_response.get('trophies'):
        trophies.append(Trophy(trophy.get('background'), trophy.get('description'), trophy.get('foreground'), trophy.get('title')))
    self.trophies = trophies

    self._success = True

class Profile():
    def __init__(self, username: str = None, userid: int = None, api_response: dict = None):
        if not username and not api_response and not userid:
            self._success = False
            return
        
        if username:
            build_profile(self, username=username)
        elif userid:
            build_profile(self, userid=userid)
        else:
            build_profile(self, api_response=api_response)

    def refresh(self):
        return build_profile(self, self.user)._success
    
class Contact():
    def __init__(self, username: str = None, api_response: dict = None):
        if not username and not api_response:
            self._success = False
            return
        
        if not api_response:
            data = {
                "auth": None,
                "method": "get",
                "endpoint": "contact",
                "data": {}
            }

            success, response = server_request(type="post", data=data)
            if not success:
                reason = "<response isn't in json>"
                try:
                    reason = response.json().get('reason')
                except Exception as e:
                    reason = f"<json parsing error: {e}>"
                    show_message(
                        f"Error in .{inspect.currentframe().f_code.co_name}(): {reason}", "Error")
        
                self._success = False
                return
            else:
                data = response.json()['json']
                for item in data:
                    if (item.get('user') or "").lower() == username.lower():
                        api_response = item
                
        if not api_response or api_response.get('error'):
            self._success = False
            return

        self.added = api_response.get('added')
        self.banner_id = api_response.get('banner')
        self.description = api_response.get('description')
        self.followers = api_response.get('followers')
        self.follows = api_response.get('follows')
        self.friend_status = api_response.get('follow')
        self.id = api_response.get('url')
        # there is api_response.get('last_message') for if a DMMessage object gets added
        self.likes = api_response.get('likes')
        self.made_unix = api_response.get('made')
        self.online_unix = api_response.get('online')
        self.picture_id = api_response.get('picture')
        self.status = api_response.get('status')
        self.unseen_dms = api_response.get('unseen')
        self.user = api_response.get('user')
        self.verified = api_response.get('verified')

        self.banner_url = f"{url}/uploads/{self.banner_id}"
        self.following = self.friend_status != "none"
        self.made = datetime.fromtimestamp(self.made_unix or 0)
        self.online = datetime.fromtimestamp(self.online_unix or 0)
        self.picture_url = f"{url}/uploads/{self.picture_id}"
        self.url = f"https://chat.jonazwetsloot.nl/users/{self.user}"
        self.username = self.user

        connections = {}
        collection = api_response.get('connections')
        if isinstance(collection, dict):
            for key, item in collection.items():
                connections[key] = ProfileConnection(key, item['username'], item['url'])
        self.connections = connections

        self._success = True

class Channel():
    def __init__(self, category, api_response: dict):
        self.category = category
        self.id = api_response.get('id')
        self.name = api_response.get('name')
        self.type = api_response.get('type')

    def send_message(self, message: str) -> tuple[bool, int]:
        if not check_type(message, str, 2): return
        bot_sessions = {} # silence, fix later

        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "post",
                "endpoint": "group-message",
                "data": {
                    "message": message
                }
            }
            success, response = server_request(type="post", data=data)
            if not success:
                reason = "<response isn't in json>"
                try:
                    reason = response.json().get('reason') or "<no reason provided>"
                except Exception as e:
                    reason = f"<json parsing error: {e}>"
                show_message(
                    f"Error in .{inspect.currentframe().f_code.co_name}(): {reason}", "Error")
                return False, None
            else:
                data = response.json()['json']
                return data.get('error') == None, data.get('id')
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return False, None
 
class Category():
    def __init__(self, group, name: str, api_response: dict):
        self.name = name
        self.group = group
        self.channels = {}
        for channel in api_response:
            self.channels[channel.get('name') or "<unknown>"] = Channel(self, channel)

    def get_channel(self, name: str) -> Channel | None:
        if not check_type(name, str, 2): return
        for cname, channel in self.channels.items():
            if cname.lower() == name.lower():
                return channel

class Group():
    def __init__(self, title: str = None, api_response: dict = None):
        if not title and not api_response:
            self._success = False
            return
        
        if not api_response:
            data = {
                "auth": None,
                "method": "get",
                "endpoint": "group",
                "data": {}
            }

            success, response = server_request(type="post", data=data)
            if not success:
                reason = "<response isn't in json>"
                try:
                    reason = response.json().get('reason')
                except Exception as e:
                    reason = f"<json parsing error: {e}>"
                    show_message(
                        f"Error in .{inspect.currentframe().f_code.co_name}(): {reason}", "Error")
        
                self._success = False
                return
            else:
                data = response.json()['json']
                for item in data:
                    if (item.get('title') or "").lower() == title.lower():
                        api_response = item
                
        if not api_response or api_response.get('error'):
            self._success = False
            return
        
        self.admin_ids = api_response.get('admins')
        # add a .get_admins() function that returns as Profile objects
        self.description = api_response.get('description')
        self.icon_id = api_response.get('icon')
        self.id = api_response.get('id')
        # there is api_response.get('last_message') for if a DMMessage object gets added
        self.title = api_response.get('title')
        self.user_ids = api_response.get('user_ids')
        # add a .get_members() function that returns as Profile objects

        self.categories = {}
        for category, data in api_response.get('channels').items():
            self.categories[category] = Category(self, category, data)

        self.icon_url = f"https://chat.jonazwetsloot.nl/uploads/{self.icon_id}"
        self.name = self.title

        self._success = True

    def is_admin(self, user: Profile) -> bool:
        if not check_type(user, Profile, 2): return
        return user.id in self.admin_ids