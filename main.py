import discord
from discord.ext import commands
import dotenv
import nest_asyncio
import os
import pandas as pd
from bot import Bot
import sys
from Hub import Hub

nest_asyncio.apply()
dotenv.load_dotenv()


intents=discord.Intents.all()
intents.typing = True
intents.messages = True
intents.message_content = True
bot = Bot(command_prefix='/', intents=intents)
base = Hub(bot, "messages", 'members')

'''
server = Server(bot, "monolith", "messages", "members", "test")
server2 = Server(bot, "monolith2", "messages", "members", "test")
'''

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    #await server.add('hel')
    #await server.take_snapshot()
    @base.intialize
    async def new():
        print("no snaps")
    
    await new()
    #await base.intialize()

    #print(globals())
    '''
    @server.take_snapshot
    async def w():
        await MonolithSetTest([1, 2])
        
    await w()
    '''
    #await server2.take_snapshot()
    '''
    print(id)
    print(Monolith)

    #await server.export()
           

    messages = await MonolithGetMessages()
    print(messages)    

    messages = await Monolith2GetMessages()
    print(messages)     
    
    
    members = await MonolithGetMembers() 
    print(members)
    '''
@bot.command()
async def answer(ctx):
    await ctx.send("hello")

bot.run()


