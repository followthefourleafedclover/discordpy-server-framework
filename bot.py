import discord
import os
from discord.ext import commands

class Bot(commands.Bot):
    async def on_ready(self): # override the on_ready event
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)

    def run(self):
        super().run(os.getenv('TOKEN'))


#wrapper -> intents, and command prefix 


    

    

    