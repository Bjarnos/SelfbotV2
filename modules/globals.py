## Imports ##
import dotenv, os
dotenv.load_dotenv()

## Shared ##
# Dev/production mode
version = "Selfbot V2.0.0"
show_http = True

# OAUTH info
client_id = "E5F3304E-41BF-4793-A4CD-A36C04FD4B5C"
redirect_uri = "https://bjarnos.dev/"

# Http urls (client)
base = "chat.jonazwetsloot.nl"
url = f"https://{base}"
login_url = f"{url}/login"
actionlogin_url = f"{url}/actionlogin"
timeline_url = f"{url}/timeline"

api_url = f"{url}/api/v1"
approve_url = f"{api_url}/approve"
approve2_url = f"{api_url}/handle-permission"

server = "https://api.bjarnos.dev/chatselfbot" # "http://127.0.0.1:3000" if you localhost server.js
server_connect = f"{server}/connect"
server_question = f"{server}/request"
server_activity = f"{server}/active"

# Headers
standard_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8,application/json,text/plain,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Host": base,
    "Origin": url,
    "Referer": login_url,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Content-Type": "application/x-www-form-urlencoded",
}

auth_headers = {
    # I removed a lot of headers official requests do have, might cause trouble later
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "null",
    "Content-Type": "application/x-www-form-urlencoded",
    "Alt-Used": "chat.jonazwetsloot.nl",
    "TE": "trailers"
}