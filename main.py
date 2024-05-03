import discord
from discord.ext import commands
import dotenv
import nest_asyncio
import os
import asyncio
nest_asyncio.apply()
dotenv.load_dotenv()
from bot import Bot

class Server:
    def __init__(self, client: discord.Client, guild: discord.Guild, *argv):
        self.__args = [x for x in argv]

        if not any([isinstance(x, str) for x in self.__args]):
            raise TypeError

        self.__args_values = [[] for x in self.__args] 
        self.__client = client 
        self.guild = guild

        self.options = {'members': False, 'messages': False}

        if 'members' in self.__args:
            self.options['members'] = True
        if 'messages' in self.__args:
            self.options['messages'] = True

        for index, arg in enumerate(self.__args):

            gen_function_code_getter = f'''async def get{arg.capitalize()}():
            return self._Server__args_values[{index}]'''

            gen_function_code_setter = f'''async def set{arg.capitalize()}(value):
            if not isinstance(value, list):
                raise TypeError("value is supposed to be type list not " + str(type(value)))
            self._Server__args_values[{index}] = value 
            '''

            gen_function_code_add = f'''async def add{arg.capitalize()}(value):
            self._Server__args_values[{index}].append(value)'''

            gen_function_code_remove = f'''async def remove{arg.capitalize()}(*args):
            if len(args) > 1:
                raise TypeError("remove{arg.capitalize()} only takes one positional agrument but " + str(len(args)) + " were given")
            if args:
                del self._Server__args_values[{index}][args[0]]
            else:
                del self._Server__args_values[{index}][-1]'''

            
            exec(gen_function_code_getter, {'self':self}, globals())
            exec(gen_function_code_setter, {'self':self}, globals())
            exec(gen_function_code_add, {'self':self}, globals())
            exec(gen_function_code_remove, {'self':self}, globals())

    async def __generic_function(self):
        print("Taking Snapshot of Server . . .")
    
    def take_snapshot(self, func=None):
        async def take_snapshot_wrapper():

            self.guild_names = [x.name for x in self.__client.guilds]

            self.guild_obj = self.__client.guilds[self.guild_names.index(self.guild)]
        
            if self.options['members']:
                for member in self.guild_obj.members:
                    await addMembers(member)

            if self.options['messages']:
                for channel in self.guild_obj.channels:
                    try:
                        async for message in channel.history(limit=None):
                            print(message.content)
                            await addMessages(message.content)
                    except:
                        pass

            if func is None:
                await self.__generic_function() 
            else:    
                await func()

        if func is None:
            return take_snapshot_wrapper()
        return take_snapshot_wrapper

                

bot = Bot(command_prefix='/', intents=discord.Intents.all())
server = Server(bot, "monolith", "messages")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    #await server.add('hel')
    await server.take_snapshot()

    messages = await getMessages()
    print(messages)
    
    '''
    @server.take_snapshot
    async def w():
        pass
    await w()
    
    members = await getMembers() 
    print(members)
    '''

@bot.command()
async def answer(ctx):
    await ctx.send("hello")

bot.run()


