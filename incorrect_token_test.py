import requests
import json
from twitch_notifications import get_header



with open("header.json","r") as f:
    header=json.load(f)


def get_request(channel_id_list):

    
    payload={
        "user_login":channel_id_list
    }

    header=get_header()

    r=requests.get("https://api.twitch.tv/helix/streams",params=payload,headers=header)
    if r.ok:
        print("request ok")
        data=json.loads(r.text)["data"]
        print(data)
    else:  
        print("request error, getting new key")
        header=get_header(expired=True)
        get_request(channel_id_list)


get_request(["timthetatman"])
