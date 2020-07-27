import json
import requests
import os
json_file_name="streamers.json"

#145272316778119170

subs={
    "TimTheTatman":{"subs":[145272316778119170],"timeout_until":0},
    "Faker":{"subs":[145272316778119170],"timeout_until":0},
    "HealthyGamer_GG":{"subs":[145272316778119170],"timeout_until":0},
    "GMHikaru":{"subs":[145272316778119170],"timeout_until":0}
}


async def twitch_streamer_notifications(client):
    all_streamers=all_streamers_in_json()
    subs=read_json()
    messages=get_streams(all_streamers)

    online_streamers=list(messages.keys())
    print(f"online streamers:{online_streamers}")
    for streamer in online_streamers:
        message=messages[streamer]
        send_to=subs[streamer]["subs"]
        await dm(client,message,send_to)
        print(f"sent for {streamer}")

            
def all_streamers_in_json():
    subs=read_json()
    streamer_names=list(subs.keys())
    return streamer_names

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

        AuthData=json.loads(r.text)

        access_token=AuthData["access_token"]

        header={"client-id":client_id,"Authorization": f"Bearer {access_token}"}

        with open("header.json","w") as f:
            json.dump(header,f,indent=4)

        return header

def get_streams(channel_id_list):

    payload={
        "user_login":channel_id_list
    }

    header=get_header()

    r=requests.get("https://api.twitch.tv/helix/streams",params=payload,headers=header)
    if r.ok:
        print("request ok")
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


def remove_id_from_streamer(id,streamer):
    subs=read_json()

def read_json():
    with open(json_file_name,"r") as f:
        subs=json.load(f)
    return subs


def write_to_json(to_write):
    with open(json_file_name,"w") as f:
        json.dump(to_write,f,indent=4)

async def dm(client,message,send_to):
    for recipient in send_to:
        target= await client.fetch_user(recipient)
        await target.send(message)


write_to_json(subs)
