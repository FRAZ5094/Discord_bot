import json
import requests

json_file_name="streamers.json"
"""
with open("streamers.json","r") as f:
    streamers=json.load(f)
"""
subs={
    "xqcow":[1,2,3,145272316778119170],
    "lirik":[3,4,5,145272316778119170]
    }



def twitch_streamer_notifications():
 
    streamer_names=all_streamers_in_json() #list of all streamers registered in the json

    header=get_header() #gets auth token from twitch api and creates a header
    
    for streamer in streamer_names:
        is_live,message=get_stream_details(streamer,header)
        print(is_live)
        if is_live:
            for sub in subs[streamer]:
                print("message {} with \"{}\"".format(sub,message))
            
def all_streamers_in_json():
    subs=read_json()
    streamer_names=list(subs.keys())
    return streamer_names

def get_header():
    from secrets import client_id,secret_id
    payload={
        "client_id":client_id,
        "client_secret":secret_id,
        "grant_type":"client_credentials"}

    r=requests.post("https://id.twitch.tv/oauth2/token", data=payload)

    AuthData=json.loads(r.text)

    access_token=AuthData["access_token"]

    header={"client-id":client_id,"Authorization": "Bearer {}".format(access_token)}

    return header

def get_stream_details(streamer,header):
    payload={"query":streamer,"live_only": True}

    r=requests.get("https://api.twitch.tv/helix/search/channels",params=payload,headers=header)
    data=json.loads(r.text)["data"]
    for result in data:
        if result["display_name"]==streamer:
            display_name=result["display_name"]
            title=result["title"]
            return True,"{0} is live!\nTitle: {1}\nLink: https://www.twitch.tv/{0}".format(display_name,title)

    return False," "


def remove_id_from_streamer(id,streamer):
    subs=read_json()

def read_json():
    with open(json_file_name,"r") as f:
        subs=json.load(f)
    return subs


def write_to_json(to_write):
    with open(json_file_name,"w") as f:
        json.dump(to_write,f,indent=4)

write_to_json(subs)