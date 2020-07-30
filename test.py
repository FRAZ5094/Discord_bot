from twitch_notifications import read_json
import json

subs=read_json()

new_subs={}
for key,item in subs.items():
    if len(item["subs"])>0:
        new_subs[key]=item

with open("test.json","w") as f:
    json.dump(new_subs,f,indent=4)