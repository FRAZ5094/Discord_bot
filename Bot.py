import discord
from discord.ext import commands,tasks
from secrets import discord_bot_token
from twitch_notifications import *
import os 
from datetime import datetime
client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    streamer_live_check.start()
    await client.change_presence(status=discord.Status.idle,activity=discord.Game("Fucking your mum"))
    print("Bot online")

@client.command()
async def hello(ctx):
    await ctx.send("hello")

@client.command()
async def clear(ctx,amount):
    if amount=="all":
        await ctx.channel.purge(limit=999999)
    await ctx.channel.purge(limit=int(amount)+1)

@clear.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("Please specify and amount of messages to delete")

@client.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):
        await ctx.send("Command doesn't exist")

@client.command()
async def ping(ctx):
    await ctx.send("{}ms".format(round(client.latency*1000)))

@tasks.loop(minutes=5)
async def streamer_live_check():
    now=datetime.now()
    current_time=now.strftime("%H:%M")
    print("Live check at:", current_time)
    messages=await twitch_streamer_notifications()
    for message,user_ids in messages.items():
        for user_id in user_ids:
            await dm(user_id,message)

@client.command()
async def check_online(ctx):
    user_id=ctx.author.id
    subbed_list=get_subbed_list(user_id)
    online_list=list(get_streams(subbed_list).keys())
    offline_list=[]
    for streamer in subbed_list:
        if streamer not in online_list:
            offline_list.append(streamer)
    message=""

    for streamer in online_list:
        message+=f":white_check_mark: {streamer}\n"

    for streamer in offline_list:
        message+=f":x: {streamer}\n"
    await ctx.send(message)

@client.command()
async def channel(channel_id,message):
    channel = client.get_channel(int(channel_id))
    await channel.send(message)

async def dm(user_id,message):
        target= await client.fetch_user(user_id)
        await target.send(message)

@client.command()
async def sub_list(ctx):
    user_id=ctx.author.id
    subbed_list=get_subbed_list(user_id)
    if len(subbed_list)==0:
        await ctx.send("Your not subbed to anyone")
    else:
        await ctx.send("Your subscribed list:\n   "+"\n   ".join(subbed_list))

@client.command()
async def add_streamer(ctx,streamer):
    user_id=ctx.author.id
    subs=read_json()
    all_streamers=list(subs.keys())
    streamer=get_correct_user_name(streamer)
    if streamer=="not a valid user name":
        await ctx.send("not a valid user name, try again")
    else:
        if streamer in all_streamers:
            if user_id in subs[streamer]["subs"]:
                await ctx.send(f"You are already subscibed to {streamer}")
            else:
                subs[streamer]["subs"].append(user_id)
                await ctx.send(f"Successfully subscribed to {streamer}")
                write_to_json(subs)
                sub_list(ctx)
                
        else:
            subs[streamer]={"subs": [user_id],"timeout_until": 0}
            await ctx.send(f"Successfully subscribed to {streamer}")
            write_to_json(subs)
            sub_list(ctx)

@client.command()
async def remove_streamer(ctx,streamer):
    subs=read_json()
    user_id=ctx.author.id
    if streamer in subs.keys():
        if user_id in subs[streamer]["subs"]:
            subs[streamer]["subs"].remove(user_id)
            await ctx.send(f"{streamer} removed from your subbed list")
            write_to_json(subs)
            subbed_list=get_subbed_list(user_id)
            await ctx.send(subbed_list)
        else:
            await ctx.send(f"You are not subbed to {streamer}")

    else:
        await ctx.send("invalid streamer name, this command is case sensitive")

@client.command()
async def pi_temp(ctx):
        temp=os.popen("vcgencmd measure_temp").read()
        await ctx.send(f"pi {temp}")

client.run(discord_bot_token)


#ch = client.get_channel(736949877237612544)
#await ch.send("xQcOW is live\nTitle: Fucking your mom")