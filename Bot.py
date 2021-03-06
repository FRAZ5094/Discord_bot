import discord
from discord.ext import commands, tasks
from secrets import discord_bot_token
from twitch_notifications import *
import os
from datetime import datetime


client = commands.Bot(command_prefix="!")


async def authorized(ctx):
    if ctx.author.id in [145272316778119170]:
        return True
    else:
        return False


def get_settings():
    with open("settings.json", "r") as f:
        return json.load(f)


def get_setting_value(setting):
    settings = get_settings()
    return settings[setting]


@client.event
async def on_ready():
    streamer_live_check.start()
    await client.change_presence(status=discord.Status.online, activity=discord.Game(get_setting_value("status")))
    print("Bot online")


@client.command()
async def hello(ctx):
    await ctx.send("hello")


@client.command()
async def clear(ctx, amount):
    if amount == "all":
        await ctx.channel.purge(limit=999999)
    await ctx.channel.purge(limit=int(amount)+1)


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify and amount of messages to delete")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command doesn't exist")
    if isinstance(error, commands.CheckFailure):
        await ctx.send("you dont have permission for this command")


@client.command()
async def ping(ctx):
    await ctx.send("{}ms".format(round(client.latency*1000)))


@tasks.loop(minutes=get_setting_value("refresh-time"))
async def streamer_live_check():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    print("Live check at:", current_time)
    subs = read_json()
    streamers_to_check = list(subs.keys())
    if len(streamers_to_check) == 0:
        return
    # get lists of offline/offline streamers
    online_streamer_data = get_streams(streamers_to_check)
    online_list, offline_list = streamer_lists(online_streamer_data)

    # increment the offline streamers offline-time
    increment_offline_time(offline_list, get_setting_value("refresh-time"))

    # sort data into dict: {"message":[list to send message to]}
    messages = {}
    for stream in online_streamer_data:
        user_name = stream["user_name"]
        messages[user_name] = {}
        title = stream["title"]
        message = f"{user_name} is live!\nTitle: {title}\nLink: https://www.twitch.tv/{user_name}"
        messages[user_name] = {"message": message,
                               "send_to": subs[user_name]["subs"]}

    notifications = check_offline_time(
        online_list, messages, get_setting_value("maxoffline-time"))

    for message_info in notifications.values():
        for user_id in message_info["send_to"]:
            await dm(user_id, message_info["message"])


@client.command()
async def check_online(ctx):
    user_id = ctx.author.id
    subbed_list = get_subbed_list(user_id)
    if len(subbed_list) == 0:
        await ctx.send("Your not subbed to anyone")
        return
    online_streamer_data = get_streams(subbed_list)
    online_list, offline_list = streamer_lists(online_streamer_data)
    message = ""
    for streamer in online_list:
        message += f":white_check_mark: {streamer}--> <https://www.twitch.tv/{streamer}>\n"
    subs = read_json()
    for streamer in offline_list:
        offline_time = subs[streamer]["offline-time"]
        if offline_time >= 9999999999999:
            time_phrase = "unknown"
        else:
            mins = int(offline_time % 60)
            offline_time /= 60
            offline_time = int(offline_time)
            time_phrase = time_formatting(offline_time, mins)
        message += f":x: {streamer}--> last live: {time_phrase}\n"
    await ctx.send(message)


@client.command()
async def channel(channel_id, message):
    channel = client.get_channel(int(channel_id))
    await channel.send(message)


async def dm(user_id, message):
    target = await client.fetch_user(user_id)
    await target.send(message)


@client.command()
async def sub_list(ctx):
    user_id = ctx.author.id
    subbed_list = get_subbed_list(user_id)
    if len(subbed_list) == 0:
        await ctx.send("Your not subbed to anyone")
    else:
        await ctx.send("Your subscribed list:\n   "+"\n   ".join(subbed_list))


@client.command()
async def add_streamer(ctx, streamer):
    user_id = ctx.author.id
    subs = read_json()
    all_streamers = list(subs.keys())
    streamer = get_correct_user_name(streamer)
    if streamer == "not a valid user name":
        await ctx.send("not a valid user name, try again")
    else:
        if streamer in all_streamers:
            if user_id in subs[streamer]["subs"]:
                await ctx.send(f"You are already subscibed to {streamer}")
                await sub_list(ctx)
            else:
                subs[streamer]["subs"].append(user_id)
                await ctx.send(f"Successfully subscribed to {streamer}")
                write_to_json(subs)
                await sub_list(ctx)

        else:
            subs[streamer] = {"subs": [user_id], "offline-time": 9999999999999}
            await ctx.send(f"Successfully subscribed to {streamer}")
            write_to_json(subs)
            await sub_list(ctx)


@client.command()
async def remove_streamer(ctx, streamer):
    subs = read_json()
    user_id = ctx.author.id
    if streamer in subs.keys():
        if user_id in subs[streamer]["subs"]:
            subs[streamer]["subs"].remove(user_id)
            await ctx.send(f"{streamer} removed from your subbed list")
            write_to_json(subs)
            await sub_list(ctx)
        else:
            await ctx.send(f"You are not subbed to {streamer}")
            await sub_list(ctx)

    else:
        await ctx.send("invalid streamer name, this command is case sensitive")


@client.command()
async def pi_temp(ctx):
    temp = os.popen("vcgencmd measure_temp").read()
    await ctx.send(f"pi {temp}")


@client.command()
async def settings(ctx):
    settings = get_settings()
    response = ""
    for setting, value in settings.items():
        response += f"{setting}: {value}\n"
    await ctx.send(response)


@client.command()
@commands.check(authorized)
async def change_setting(ctx, setting, value):
    already_added = False
    settings = get_settings()
    if setting in settings.keys():
        old_value = settings[setting]
        if setting == "refresh-time":
            settings[setting] = int(value)
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            already_added = True
            streamer_live_check.change_interval(minutes=float(value))
            streamer_live_check.restart()
        if setting == "status":
            await client.change_presence(status=discord.Status.online, activity=discord.Game(value))
        if setting == "maxoffline-time":
            settings[setting] = int(value)
            already_added = True
        if not already_added:
            settings[setting] = value
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)

        await ctx.send(f"{setting}: {old_value}-->{value}")
    else:
        await ctx.send(f"setting: \"{setting}\" not found")


@client.command()
async def next_refresh(ctx):
    next_iter = int(streamer_live_check.next_iteration.timestamp())
    now = int(datetime.now().timestamp())

    delta_time = next_iter-now

    await ctx.send(f"Next refresh is in {delta_time} seconds")


client.run(discord_bot_token)
