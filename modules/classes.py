## Imports ##
import inspect
from datetime import datetime
from modules.functions import *

## Shared ##
# Note that type checking usually isn't needed in class __init__
class Session(): # bot session
    def __init__(self, username: str, password: str):
        self.username: str = username
        self.password: str = password
        self.event_registry: dict = {}
        self.command_registry: dict = {}
        self.token: str = ""
        self.kill: bool = False

class ProfileConnection():
    def __init__(self, key: str, username: str, url: str):
        self.platform: str = key
        self.username: str = username
        self.url: str = url

class Trophy():
    def __init__(self, background: str, description: str, foreground: str, title: str):
        self.background_url: str = f"{url}{background}"
        self.description: str = description
        self.foreground: str = f"{url}{foreground}"
        self.title: str = title

class Profile():
    def __init__(self, username: str = None, userid: int = None, api_response: dict = None):
        self._success: bool = False
        if not username and not api_response and not userid:
            return
        
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
                    json = response.json()
                    reason = debug_response(json)
                except Exception as e:
                    reason = f"<json parsing error: {e}>"
                show_message(
                    f"Server error in .{inspect.currentframe().f_code.co_name}(): {reason}", "Error")
        
                return
            else:
                api_response = response.json()['json']

        if api_response.get('error'):
            return

        self.banner_id: str = api_response.get('banner')
        self.description: str = api_response.get('description')
        self.followers: int = api_response.get('followers')
        self.follows: int = api_response.get('follows')
        self.friend_status: str = api_response.get('follow')
        self.id: int = api_response.get('id')
        self.likes: int = api_response.get('likes')
        self.made_unix: int = api_response.get('made')
        self.online_unix: int = api_response.get('online')
        self.picture_id: str = api_response.get('picture')
        self.status: str = api_response.get('status')
        self.unseen_dms: int = api_response.get('unseen')
        self.user: str = api_response.get('user')
        self.verified: bool = api_response.get('verified')

        self.banner_url: str = f"{url}/uploads/{self.banner_id}"
        self.following: bool = self.friend_status != "none"
        self.made: datetime = datetime.fromtimestamp(self.made_unix or 0)
        self.online: datetime = datetime.fromtimestamp(self.online_unix or 0)
        self.picture_url: str = f"{url}/uploads/{self.picture_id}"
        self.url: str = f"https://chat.jonazwetsloot.nl/users/{self.user}"
        self.username: str = self.user

        connections = {}
        collection = api_response.get('connections')
        if isinstance(collection, dict):
            for key, item in collection.items():
                connections[key] = ProfileConnection(key, item['username'], item['url'])
        self.connections: dict[str, ProfileConnection] = connections

        trophies = []
        for trophy in api_response.get('trophies'):
            trophies.append(Trophy(trophy.get('background'), trophy.get('description'), trophy.get('foreground'), trophy.get('title')))
        self.trophies: list[Trophy] = trophies

        self._success: bool = True

    async def refresh(self):
        return Profile(userid=self.id)

class Contact():
    def __init__(self, username: str = None, api_response: dict = None):
        self._success: bool = False
        if not username and not api_response:
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
                    json = response.json()
                    reason = debug_response(json)
                except Exception as e:
                    reason = f"<json parsing error: {e}>"
                show_message(
                    f"Server error in .{inspect.currentframe().f_code.co_name}(): {reason}", "Error")
        
                return
            else:
                data = response.json()['json']
                for item in data:
                    if (item.get('user') or "").lower() == username.lower():
                        api_response = item
                
        if not api_response or api_response.get('error'):
            return

        self.added_unix: int = api_response.get('added')
        self.banner_id: str = api_response.get('banner')
        self.description: str = api_response.get('description')
        self.followers: int = api_response.get('followers')
        self.follows: int = api_response.get('follows')
        self.friend_status: str = api_response.get('follow')
        self.id: int = api_response.get('url')
        # there is api_response.get('last_message') for if a DMMessage object gets added
        self.likes: int = api_response.get('likes')
        self.made_unix: int = api_response.get('made')
        self.online_unix: int = api_response.get('online')
        self.picture_id: str = api_response.get('picture')
        self.status: str = api_response.get('status')
        self.unseen_dms: int = api_response.get('unseen')
        self.user: str = api_response.get('user')
        self.verified: bool = api_response.get('verified')

        self.banner_url: str = f"{url}/uploads/{self.banner_id}"
        self.following: bool = self.friend_status != "none"
        self.added: datetime = datetime.fromtimestamp(self.added_unix or 0)
        self.made: datetime = datetime.fromtimestamp(self.made_unix or 0)
        self.online: datetime = datetime.fromtimestamp(self.online_unix or 0)
        self.picture_url: str = f"{url}/uploads/{self.picture_id}"
        self.url: str = f"https://chat.jonazwetsloot.nl/users/{self.user}"
        self.username: str = self.user

        connections = {}
        collection = api_response.get('connections')
        if isinstance(collection, dict):
            for key, item in collection.items():
                connections[key] = ProfileConnection(key, item['username'], item['url'])
        self.connections: dict[str, ProfileConnection] = connections

        self._success: bool = True

class Channel():
    def __init__(self, session, group, category, api_response: dict):
        self.session: Session = session
        self.category: Category = category
        self.group: Group = group
        self.id: int = api_response.get('id')
        self.name: str = api_response.get('name')
        self.type: str = api_response.get('type')

    async def send_message(self, message: str) -> tuple[bool, int|None]:
        if not check_type(message, str, 2): return False, None

        token = self.session.token
        if token:
            data = {
                "auth": self.session.token,
                "method": "post",
                "endpoint": "group-message",
                "data": {
                    "id": self.group.id,
                    "channel": self.name,
                    "message": message
                }
            }
            success, response = server_request(type="post", data=data)
            if not success:
                reason = "<response isn't in json>"
                try:
                    json = response.json()
                    reason = debug_response(json)
                except Exception as e:
                    reason = f"<json parsing error: {e}>"
                show_message(
                    f"Server error in .{inspect.currentframe().f_code.co_name}(): {reason}", "Error")
                return False, None
            else:
                data = response.json()['json']
                return data.get('error') == None, data.get('id')
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return False, None
 
class Category():
    def __init__(self, session, group, name: str, api_response: dict):
        self.session: Session = session
        self.name: str = name
        self.group: Group = group
        self.channels: dict[str, Channel] = {}
        for channel in api_response:
            self.channels[channel.get('name') or "<unknown>"] = Channel(session, self.group, self, channel)

    def get_channel(self, name: str) -> Channel | None:
        if not check_type(name, str, 2): return
        for cname, channel in self.channels.items():
            if cname.lower() == name.lower():
                return channel

class Group():
    def __init__(self, session, title: str = None, api_response: dict = None):
        self.session: Session = session
        self._success: bool = False
        if not title and not api_response:
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
                    json = response.json()
                    reason = debug_response(json)
                except Exception as e:
                    reason = f"<json parsing error: {e}>"
                show_message(
                    f"Server error in .{inspect.currentframe().f_code.co_name}(): {reason}", "Error")
        
                return
            else:
                data = response.json()['json']
                for item in data:
                    if (item.get('title') or "").lower() == title.lower():
                        api_response = item
                
        if not api_response or api_response.get('error'):
            return
        
        self.admin_ids: list[int] = api_response.get('admins')
        # add a .get_admins() function that returns as Profile objects
        self.description: str = api_response.get('description')
        self.icon_id: str = api_response.get('icon')
        self.id: int = api_response.get('id')
        # there is api_response.get('last_message') for if a DMMessage object gets added
        self.title: str = api_response.get('title')
        self.user_ids: list[int] = api_response.get('user_ids')
        # add a .get_members() function that returns as Profile objects

        self.categories: dict[str, Category] = {}
        for category, data in api_response.get('channels').items():
            self.categories[category] = Category(session, self, category, data)

        self.icon_url: str = f"https://chat.jonazwetsloot.nl/uploads/{self.icon_id}"
        self.name: str = self.title

        self._success: bool = True

    async def get_admins(self) -> list[Profile]:
        admins = []
        for id in self.admin_ids:
            admins.append(Profile(userid=id))
        return admins
    
    async def get_members(self) -> list[Profile]:
        members = []
        for id in self.user_ids:
            members.append(Profile(userid=id))
        return members

    def get_category(self, name: str) -> Category | None:
        if not check_type(name, str, 2): return
        for cname, category in self.categories.items():
            if cname.lower() == name.lower():
                return category

    def is_admin(self, user: Profile) -> bool | None:
        if not check_type(user, Profile, 2): return
        return user.id in self.admin_ids
    
    async def send_message(self, message: str) -> tuple[bool, int | None]:
        if not check_type(message, str, 2): return False, None

        token = self.session.token
        if token:
            data = {
                "auth": self.session.token,
                "method": "post",
                "endpoint": "group-message",
                "data": {
                    "id": self.id,
                    "message": message
                }
            }
            success, response = server_request(type="post", data=data)
            if not success:
                reason = "<response isn't in json>"
                try:
                    json = response.json()
                    reason = debug_response(json)
                except Exception as e:
                    reason = f"<json parsing error: {e}>"
                show_message(
                    f"Server error in .{inspect.currentframe().f_code.co_name}(): {reason}", "Error")
                return False, None
            else:
                data = response.json()['json']
                return data.get('error') == None, data.get('id')
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return False, None