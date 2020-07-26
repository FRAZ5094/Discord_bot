import discord
from discord.ext import commands,tasks
from secrets import discord_bot_token
import time

client = commands.Bot(command_prefix="!")
#use client. because client is used
@client.event
async def on_ready():
    streamer_live_check.start()
    await client.change_presence(status=discord.Status.idle,activity=discord.Game("Fucking your mum"))
    print("serverpi_discord_bot online")

@client.command()
async def hello(ctx):
    await ctx.send("hello")

@client.command()
async def clear(ctx,amount):
    if amount=="all":
        await ctx.channel.purge(limit=999999)
    await ctx.channel.purge(limit=int(amount)+1)

@clear.error #only for an error with the "clear" function
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("Please specify and amount of messages to delete")
       

@client.command()
async def ping(ctx):
    await ctx.send("{}ms".format(round(client.latency*1000)))


@tasks.loop(seconds=2)
async def streamer_live_check():
    await dm()
    time.sleep(10)
#ch = client.get_channel(736949877237612544)
#await ch.send("xQcOW is live\nTitle: Fucking your mom")

@client.command()
async def dm():
    target=await client.fetch_user(145272316778119170)
    await target.send("Bruh")


@client.command()
async def channel(channel_id,message):
    channel = client.get_channel(int(channel_id))
    await channel.send(message)

client.run(discord_bot_token)
