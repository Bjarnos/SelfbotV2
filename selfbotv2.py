## Imports ##
import asyncio, inspect
from bs4 import BeautifulSoup
from datetime import datetime

import modules.enums as enums
from modules.globals import *
from modules.functions import *
from modules.classes import *

### TO-DO with endpoints
## Group messages
# ask Jona
# join group function?
# group messages endpoint
## Laatste endpoints
# adjust profile
# DELETE endpoints
## Public messages
# message list
## DM messages
# dm message list
## Image system (custom cdn)
# upload image
# view image
# image list
# file storage
## Attachments in general
## Profiles
# adjust profile
## Make everything refreshable

## Library ##
bot_sessions = {}
def f(): pass
function = f.__class__

## Main ##
class Bot():
    # Init
    def __init__(self, user: str, password: str):
        if not check_type(user, str, 2, True): return
        if not check_type(password, str, 3, True): return

        bot_sessions[self] = Session(user, password)

    # Standard methods
    def send_message(self, message: str) -> tuple[bool, int]:
        if not check_type(message, str, 2): return

        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "post",
                "endpoint": "message",
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
        
    def send_reaction(self, id: int, message: str) -> tuple[bool, int]:
        if not check_type(id, int, 2): return
        if not check_type(message, str, 3): return

        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "post",
                "endpoint": "message",
                "data": {
                    "message": message,
                    "id": id
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
        
    def like_message(self, id: int, unlike: bool = False) -> bool:
        if not check_type(id, int, 2): return
        if not check_type(unlike, bool, 3): return

        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "post",
                "endpoint": "like",
                "data": {
                    "id": id,
                    "like": unlike and 'false' or 'true'
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
                return False
            else:
                data = response.json()['json']
                return data.get('error') == None
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return False
        
    def edit_message(self, id: int, message: str) -> bool:
        if not check_type(id, int, 2): return
        if not check_type(message, str, 3): return

        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "put",
                "endpoint": "message",
                "data": {
                    "id": id,
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
                return False
            else:
                data = response.json()['json']
                return data.get('error') == None
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return False
        
    def get_contacts(self) -> dict[Contact]:
        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "get",
                "endpoint": "contact",
                "data": {}
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
                return {}
            else:
                data = response.json()['json']
                collection = {}
                for item in data:
                    collection[item.get('user') or "<unknown>"] = Contact(api_response=item)
                return collection
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return {}
        
    def get_contact(self, user: str) -> Contact | None:
        if not check_type(user, str, 2): return

        profile = Contact(username=user)
        if profile._success != False:
            return profile
        
    def add_contact(self, user: str) -> bool:
        if not check_type(user, str, 2): return

        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "post",
                "endpoint": "contact",
                "data": {
                    "user": user
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
                return False
            else:
                data = response.json()['json']
                return data.get('error') == None
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return False
        
    def send_dm(self, user: str, message: str) -> tuple[bool, int]:
        if not check_type(user, str, 2): return
        if not check_type(message, str, 3): return

        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "post",
                "endpoint": "direct-message",
                "data": {
                    "user": user,
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
        
    def edit_dm(self, id: int, message: str) -> tuple[bool, int]:
        if not check_type(id, int, 2): return
        if not check_type(message, str, 3): return

        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "put",
                "endpoint": "direct-message",
                "data": {
                    "id": id,
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
                return False
            else:
                data = response.json()['json']
                return data.get('error') == None
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return False
        
    def get_groups(self) -> dict[Group]:
        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "get",
                "endpoint": "group",
                "data": {}
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
                return {}
            else:
                data = response.json()['json']
                collection = {}
                for item in data:
                    collection[item.get('title') or "<unknown>"] = Group(bot_sessions[self], api_response=item)
                return collection
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return {}
        
    def get_group(self, title: str) -> Group | None:
        if not check_type(title, str, 2): return

        token = bot_sessions[self].token
        if token:
            data = {
                "auth": bot_sessions[self].token,
                "method": "get",
                "endpoint": "group",
                "data": {}
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
                return {}
            else:
                data = response.json()['json']
                for item in data:
                    if item.get('title').lower() == title.lower():
                        return Group(bot_sessions[self], api_response=item)
        else:
            show_message(
                f"Can't use .{inspect.currentframe().f_code.co_name}() before .run()!", "Error")
            return {}
        
    # @ methods
    def event(self, func: function) -> function:
        if not check_type(func, function, 2): return

        bot_session = bot_sessions.get(self)
        if not bot_session: return # creating bot had an error

        allowed = ["on_ready"]
        event_name = func.__name__
        if event_name not in allowed:
            show_message(
                f"{event_name} is not a valid event for @bot.event!", "Error")
            return

        if not callable(func):
            show_message("@bot.event should get a function passed!", "Error")
            return

        bot_session.event_registry[event_name] = func
        return func

    def command(self, name: str = None) -> function:
        # update this later
        def decorator(func):
            cmd_name = name or func.__name__
            bot_sessions[self].command_registry[cmd_name] = func
            return func
        return decorator

    # Main
    def run(self) -> bool:
        # Gather session
        bot_session = bot_sessions.get(self)
        if not bot_session: return # creating bot had an error

        username = bot_session.username
        password = bot_session.password

        session = requests.session()

        # Approve my API client
        data = {
            'user': username,
            'pass': password,
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri
        }
        response = session.post(url=approve_url, data=data)

        soup = BeautifulSoup(response.text, "html.parser")
        verifier = soup.find('input', id='api_login_verifier')
        if verifier:
            verifier = verifier.get('value')
        else:
            show_message("Couldn't find login verifier.\n Usually, this means your login info is incorrect.", "Error")
            return

        data = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'api_login_verifier': verifier
        }
        response = session.post(url=approve2_url, data=data, headers=auth_headers, allow_redirects=False)
        token = response.headers.get('Location')
        if token:
            token = token.split("#code=")[1]
        else:
            show_message("Failed to get Authorization code!", "Error")

        # Connect to my server
        data = {'token': token}
        response = requests.post(url=server_connect, data=data)
        if response.status_code < 400:
            token = response.json().get('token')
            if not token:
                show_message("Server didn't return token!", "Error")
                return

            bot_session.token = token
        else:
            show_message("Server had an error.", "Error")
            return
        
        # Set user attribute
        self.user = get_profile(username) # don't forget to refresh often when using :)

        # Run the on_ready event
        onr = bot_session.event_registry.get('on_ready')
        if onr:
            asyncio.run(onr())

        return True


## Main ##
def create_session(username: str, password: str) -> Bot:
    if not check_type(username, str, 1): return
    if not check_type(password, str, 2): return
    return Bot(username, password)


## Public methods ##
def is_username_available(username: str) -> bool:
    if not check_type(username, str, 1): return
    data = {
        "auth": None,
        "method": "get",
        "endpoint": "status-username",
        "data": {
            "user": username
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
    else:
        data = response.json()['json']
        return data.get('available')
    
def is_email_available(email: str) -> bool:
    if not check_type(email, str, 1): return

    data = {
        "auth": None,
        "method": "get",
        "endpoint": "status-mail",
        "data": {
            "mail": email
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
    else:
        data = response.json()['json']
        return data.get('valid') and data.get('available')
    
def is_email_verified(user: str) -> bool:
    if not check_type(user, str, 1): return

    data = {
        "auth": None,
        "method": "get",
        "endpoint": "status-mail-verified",
        "data": {
            "mail": user
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
    else:
        data = response.json()['json']
        return data.get('verified')
    
def get_profile(user: int|str) -> Profile | None:
    if not isinstance(user, (int, str)):
        show_message(
            f"Expected arg1 to be class str or int instead of {user.__class__.__name__} in get_profile(user: int | str) -> modules.classes.Profile | None", "Error")
        return

    if isinstance(user, int):
        profile = Profile(userid=user)
        if profile._success != False:
            return profile
    else:
        profile = Profile(username=user)
        if profile._success != False:
            return profile
    
def create_account(user: str, email: str, password: str) -> None:
    raise NotImplementedError("This function has not been added to the library, and never will be, for security and anti-spam reasons.")


__all__ = [
    create_session, is_username_available, is_email_available, is_email_verified,
    get_profile, create_account
    ] # shared by module
