# pyright: reportOptionalMemberAccess=false
"""

This is the server of SelfbotV2. It's not recommended to host this as well when creating a fork of Selfbot, but if you do:
- Replace `server` in modules\\globals with your new server ip/link.
- Ask the owner of Chat (Jona) if he can add a POST in api/<version>/group-message to your server/new with new message's content,
  or create a redirect to my server which will already has that implemented.

"""

# Test stuff
import os, subprocess, threading, sys
def run_test_script():
    time.sleep(2)
    print("Starting test.py!")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, "test.py"], cwd=script_dir)

# Server
import requests, random, string, time, requests_cache, dotenv
from flask import Flask, request, jsonify
from modules.globals import *

requests_cache.install_cache("http_cache", expire_after=60, allowable_methods=["GET"]) # 1 minute requests cache
dotenv.load_dotenv("sensitive.env")

app = Flask(__name__)

secret = os.getenv("SECRET")
access_token = os.getenv("ACCESS_TOKEN")

connected_clients = {}

# Methods
def get_token(auth: str) -> str|None:
    # add auto refresh later
    collection = connected_clients.get(auth)
    if collection:
        return collection.get("token")

# Endpoints
@app.route("/c", methods=["POST"])
def connect():
    # This endpoint is used by selfbots to connect with the server
    token = request.form.get('token')
    if token:
        if token.__class__ != str:
            return jsonify(success=False, reason=f"'token' must be a string!"), 400

        data = {
            "grant_type": "authorization_code",
            "code": token,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": secret
        }
        response = requests.post(url=token_url, data=data)
        if response.status_code < 400:
            jsonr = response.json()
            token = jsonr.get('access_token')
            ttl = jsonr.get('expires_in')
            if token and ttl:
                user_token = None
                while not user_token or connected_clients.get(user_token):
                    user_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(token_size))

                connected_clients[user_token] = {
                    "token": token,
                    "ttl": round(time.time()) + ttl
                }

                return jsonify(success=True, token=user_token), 200
            else:
                return jsonify(success=False, reason="Jona seems to have updated the Chat API, please reach out to Bjarnos on Chat"), 500
        elif response.status_code == 401:
            # auto refresh?
            return jsonify(success=False, reason="Token must be refreshed!"), 400
        else:
            return jsonify(success=False, reason="Token appears to be invalid"), 400
    else:
        return jsonify(success=False, reason="Missing argument 'token'"), 400
    
allowed_methods = ["post", "get", "put", "delete"]
@app.route("/r", methods=["POST"])
def incoming_request():
    # This endpoint is used by selfbots to make requests to the Chat API
    data = request.get_json(silent=False)
    if not isinstance(data, dict):
        return jsonify(success=False, reason="Data must be valid json!"), 400
    
    auth = data.get('auth')
    method = data.get('method')
    endpoint = data.get('endpoint')
    data = data.get('data')
    if auth.__class__ != str and auth != None:
        return jsonify(success=False, reason=f"'auth' must be a string or null!"), 400
    if method.__class__ != str:
        return jsonify(success=False, reason=f"'method' must be a string!"), 400
    if endpoint.__class__ != str:
        return jsonify(success=False, reason=f"'endpoint' must be a string!"), 400
    if data.__class__ != dict:
        return jsonify(success=False, reason=f"'data' must be a dict!"), 400

    method = method.lower()
    if method not in allowed_methods:
        return jsonify(success=False, reason=f"Method must be in {allowed_methods} (case insensitive)!"), 400
        
    token = auth and get_token(auth) or access_token
    if token:
        full_url = f"{api_url}/{endpoint}"
        method = getattr(requests, method.lower())
        response = None
        if method == requests.get:
            response = method(full_url, params=data, headers={"Authorization":f"Bearer {token}"})
        else:
            response = method(full_url, data=data, headers={"Authorization":f"Bearer {token}"})

        if response.status_code < 400:
            try:
                return jsonify(success=True, json=response.json()), 200
            except ValueError:
                return jsonify(success=False, reason="Response wasn't in json"), 400
        else:
            return jsonify(success=False, reason="Endpoint failed (is your token correct and not expired?). " \
            "This may be an internal error"), 500
    else:
        return jsonify(success=False, reason="Invalid auth"), 401
    
@app.route("/new", methods=["POST"])
def new_message():
    # This endpoint is used internally by Chat for new group messages
    data = request.get_json(silent=False)
    if not isinstance(data, dict):
        return jsonify(success=False, reason="Data must be valid json!"), 400
    
    auth = data.get('auth')
    method = data.get('method')
    endpoint = data.get('endpoint')
    data = data.get('data')
    if auth.__class__ != str and auth != None:
        return jsonify(success=False, reason=f"'auth' must be a string or null!"), 400
    if method.__class__ != str:
        return jsonify(success=False, reason=f"'method' must be a string!"), 400
    if endpoint.__class__ != str:
        return jsonify(success=False, reason=f"'endpoint' must be a string!"), 400
    if data.__class__ != dict:
        return jsonify(success=False, reason=f"'data' must be a dict!"), 400

    method = method.lower()
    if method not in allowed_methods:
        return jsonify(success=False, reason=f"Method must be in {allowed_methods} (case insensitive)!"), 400
        
    token = auth and get_token(auth) or access_token
    if token:
        full_url = f"{api_url}/{endpoint}"
        method = getattr(requests, method.lower())
        response = None
        if method == requests.get:
            response = method(full_url, params=data, headers={"Authorization":f"Bearer {token}"})
        else:
            response = method(full_url, data=data, headers={"Authorization":f"Bearer {token}"})

        if response.status_code < 400:
            try:
                return jsonify(success=True, json=response.json()), 200
            except ValueError:
                return jsonify(success=False, reason="Response wasn't in json"), 400
        else:
            return jsonify(success=False, reason="Endpoint failed (is your token correct and not expired?). " \
            "This may be an internal error"), 500
    else:
        return jsonify(success=False, reason="Invalid auth"), 401

if __name__ == "__main__":
    threading.Thread(target=run_test_script, daemon=True).start()
    app.run(debug=False)