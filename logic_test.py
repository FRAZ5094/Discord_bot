import json

with open("streamers.json","r") as f:
    streamers=json.load(f)


"""
with open("streamers.json","w") as f:
    json.dump(streamers,f,indent=4)
"""



def check_if_live(streamer):
    if streamer=="xQcOW":
        return True
    if streamer=="LIRIK":
        return False


def get_token():
    print("getting token")

def refresh_token():
    print("refreshing token")

def check_streamers_live(streamers):
    #live_streamers
    for streamer in streamers:
        if check_if_live(streamer):
            pass
            









