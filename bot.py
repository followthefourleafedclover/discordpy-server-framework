import discord
import os
from discord.ext import commands

class Bot(commands.Bot):

    def run(self):
        super().run(os.getenv('TOKEN'))


#wrapper -> intents, and command prefix 


    

    

    