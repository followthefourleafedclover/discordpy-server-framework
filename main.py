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


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    #await server.add('hel')s
    #await server.take_snapshot()
    await hub.intialize(database_config={'host': 'localhost', 'dbname': 'postgres', 'user' :'postgres', 'password': 'sreevar', 'port': 5432})
    #print(globals())
    '''
    @hub.intialize
    async def w():
        print("initilatize?")
    '''
    #await w()

    #await MonolithAddMessages("works")
    await MonolithSetMessages(["lets", 'make', 'art'])
    
    messages = await MonolithGetMessages() 
    print(messages)
    
    await MonolithRemoveMessages()

    messages = await MonolithGetMessages() 
    print(messages)

    print(hub.servers[0].database_to_pd_dataframe(table='monolith_messages'))

    #print(globals())
    '''
    @server.take_snapshot
    async def w():
        await MonolithSetTest([1, 2])
        
    await w()
    '''
    #await server2.take_snapshot()
    '''
    print(MonolithId)
    print(Monolith)

    #await server.export()
    await MonolithSetTest([1, 2])
    #await hub.servers[0].export()

    messages = await MonolithGetMessages()
    print(messages)    

    messages = await Monolith2GetMessages()
    print(messages)     
    
    
    members = await MonolithGetMembers() 
    print(members)

    l = ServerStatistics(hub.servers[0])

    #await hub.export()
    '''
@bot.command()
async def answer(ctx):
    await ctx.send("hello")

bot.run()


