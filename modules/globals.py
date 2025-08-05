## Imports ##
import dotenv, os
dotenv.load_dotenv()

## Shared ##
# Dev/production mode
version = os.getenv("VERSION")
show_http = True

# OAUTH info
client_id = os.getenv("CLIENT_ID")
redirect_uri = os.getenv("REDIRECT_URI")

# Http urls (client)
base = os.getenv("BASE")
url = f"https://{base}"
login_url = f"{url}/login"
actionlogin_url = f"{url}/actionlogin"
timeline_url = f"{url}/timeline"

api_url = f"{url}/api/v1"
approve_url = f"{api_url}/approve"
approve2_url = f"{api_url}/handle-permission"

server = os.getenv("SERVER")
server_connect = f"{server}/c"
server_question = f"{server}/r"
server_read = f"{server}/d"

# Server
token_size = 24
token_url = f"{api_url}/token"

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