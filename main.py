import discord
from discord.ext import commands
import dotenv
import nest_asyncio
import os
import pandas as pd
from bot import Bot
import sys
from discordpydemeter import *


nest_asyncio.apply()
dotenv.load_dotenv()
s = "snake_case"
print(s.casefold())

intents=discord.Intents.all()
bot = Bot(command_prefix='/', intents=intents)
hub = Hub(bot, "messages", 'members', 'test')

#server = Server(bot, "monolith", 'messages', 'members')
def test__command():
    return 0 



async def custom_on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    #await server.add('hel')s
    #await server.take_snapshot()
    #await hub.intialize() 
    #await hub.intialize(database_config={'host': 'localhost', 'dbname': 'postgres', 'user' :'postgres', 'password': 'sreevar', 'port': 5432})
    
    #print(globals())



async def answer(ctx):
    await ctx.send("hello")

x = bot.command("answer")(answer)
setattr(bot, 'on_ready', custom_on_ready)
y = bot.event(custom_on_ready)

#d = Demeter()
bot.run()

