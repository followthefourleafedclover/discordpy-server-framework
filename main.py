import discord
from discord.ext import commands
import dotenv
import nest_asyncio
import os
nest_asyncio.apply()
dotenv.load_dotenv()

APP_TOKEN = os.getenv('APP_TOKEN')

def run():

    client = commands.Bot(command_prefix="/", intents=discord.Intents.all())

    @client.event
    async def on_ready():
        print("ready")
    
    client.run(f"{APP_TOKEN}")


run()

