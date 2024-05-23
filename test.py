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

intents=discord.Intents.all()
bot = Bot(command_prefix='/', intents=intents)

async def on_ready__event():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)

async def on_message__event(message):
    print('message')

async def test__command(ctx, desc="test for Demeter"):
    await ctx.send("cool")
    print('[200]')

zzz = bot.event(on_ready__event)

d = Demeter() 
print(globals())
bot.run()