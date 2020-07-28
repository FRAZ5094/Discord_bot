import json
import requests
import os
import time

json_file_name="streamers.json"
default_streamer_timeout=43200

async def twitch_streamer_notifications():
    streamers_to_check=get_streamers_to_check()
    if len(streamers_to_check)==0:
        #print("no streamers to check")
        return

    subs=read_json()
    messages=get_streams(streamers_to_check)
    notification_dict={}
    for streamer,message in messages.items():
        user_ids=subs[streamer]["subs"]
        notification_dict[message]=user_ids
        timeout_streamer(streamer)
    return notification_dict

def get_streamers_to_check():
    subs=read_json()
    streamers_to_check=[]
    epoch=int(time.time())
    for streamer in subs.keys():
        if subs[streamer]["timeout_until"]<=epoch:
            streamers_to_check.append(streamer)
    return streamers_to_check

def get_header(expired=False):

    if os.path.exists("header.json") and not expired:
        with open("header.json","r") as f:
            header=json.load(f)
            return header
    else:
        from secrets import client_id,secret_id
        payload={
            "client_id":client_id,
            "client_secret":secret_id,
            "grant_type":"client_credentials"}

        r=requests.post("https://id.twitch.tv/oauth2/token", data=payload)
        if r.ok:
            AuthData=json.loads(r.text)

            access_token=AuthData["access_token"]

            header={"client-id":client_id,"Authorization": f"Bearer {access_token}"}

            with open("header.json","w") as f:
                json.dump(header,f,indent=4)

            return header
        else:
            print("problem getting token")

def get_streams(channel_id_list):

    payload={
        "user_login":channel_id_list
    }

    header=get_header()

    r=requests.get("https://api.twitch.tv/helix/streams",params=payload,headers=header)
    if r.ok:
        data=json.loads(r.text)["data"]
        messages={}
        for stream in data:
            user_name=stream["user_name"]
            title=stream["title"]
            messages[user_name]=f"{user_name} is live!\nTitle: {title}\nLink: https://www.twitch.tv./{user_name}"
    else:  
        print("request error,getting new key")
        header=get_header(expired=True)
        messages=get_streams(channel_id_list)
        return messages
    return messages

def read_json():
    if os.path.exists(json_file_name):
        with open(json_file_name,"r") as f:
            subs=json.load(f)
        return subs
    else:
        return {}

def write_to_json(to_write):
    with open(json_file_name,"w") as f:
        json.dump(to_write,f,indent=4)

def get_correct_user_name(streamer):
    payload={
        "login":streamer
    }

    header=get_header()

    r=requests.get("https://api.twitch.tv/helix/users",params=payload,headers=header)

    if r.ok:
        data=json.loads(r.text)["data"]
        if len(data)>0: 
            display_name=data[0]["display_name"]
            return display_name
        else:
            return "not a valid user name"
       
    else:
        if r.status_code==400:
            return "not a valid user name"
        elif r.status_code==401:
            print("request error,getting new key")
            header=get_header(expired=True)
            messages=get_correct_user_name(streamer)
            return messages

def get_subbed_list(user_id):
    subs=read_json()
    user_subbed_list=[]
    for streamer in subs.keys():
        if user_id in subs[streamer]["subs"]:
            user_subbed_list.append(streamer)
    return user_subbed_list

def timeout_streamer(streamer):
    subs=read_json()
    epoch=int(time.time())
    subs[streamer]["timeout_until"]=epoch+default_streamer_timeout
    write_to_json(subs)
    