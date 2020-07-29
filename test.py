import json 


settings={
    "refresh-time":5,
    "maxoffline-time":60,
    "bot-status":"Fucking you're mum"
}


with open("settings.json","w") as f:
    json.dump(settings,f,indent=4)