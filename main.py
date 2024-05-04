import discord
from discord.ext import commands
import dotenv
import nest_asyncio
import os
import pandas as pd
import warnings
from bot import Bot

nest_asyncio.apply()
dotenv.load_dotenv()


class Server:
    def __init__(self, client: discord.Client, guild: discord.Guild, *args):
        self.__args = [x for x in args]

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

    def __get_guild_attrs(self):
        guild_attrs = dir(discord.Guild)
        start_index = 0
        for index, attrs in enumerate(guild_attrs):
            if not '_' in attrs:
                start_index = index 
                break 
        return guild_attrs[start_index:]
    
    def take_snapshot(self, func=None):
        async def take_snapshot_wrapper():

            self.guild_names = [x.name for x in self.__client.guilds]

            self.guild_obj = self.__client.guilds[self.guild_names.index(self.guild)]

            global Guild 
            Guild  = self.guild_obj  

            self.guild_attrs = self.__get_guild_attrs()

            for attr in self.guild_attrs:
                code = f'{attr} = self.guild_obj.{attr}'
                exec(code, {'self':self}, globals())
        
            if self.options['members']:
                for member in self.guild_obj.members:
                    await addMembers(member)

            if self.options['messages']:
                for channel in self.guild_obj.channels:
                    try:
                        async for message in channel.history(limit=None):
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


    async def export(self, file_type='csv'):
        self.__args_zipped = dict(zip(self.__args, self.__args_values))

        def merge():
            lengths = [len(x) for x in self.__args_zipped.values()] 
            print(lengths)
            lengths_zipped = list(zip(self.__args, lengths))
            sorted(lengths_zipped, key=lambda x: x[1])
            to_merge = [] 
            temp = []
            for i in range(len(lengths_zipped) - 1):
                if lengths_zipped[i][1] == lengths_zipped[i+1][1]:
                    if not lengths_zipped[i][0] in temp:
                        temp.append(lengths_zipped[i][0])
                    if not lengths_zipped[i+1][0] in temp:
                        temp.append(lengths_zipped[i+1][0])         
                else:
                    if temp:
                        to_merge.append(temp) 
                        temp = [] 
            if temp:
                to_merge.append(temp)    
            return to_merge

        to_merge = merge() 
        print(to_merge)
    

        if to_merge:
            df_dict = {} 
            for index, group in enumerate(to_merge): 
                for item in group: 
                    df_dict.update({item: self.__args_zipped[item]})

                print(df_dict)
                df = pd.DataFrame(df_dict)
                df.to_csv(f"{'&'.join(group)}.csv")

            flatten = [y for y in [x for x in to_merge]][0]
            rest = [x for x in self.__args if not x in flatten]
            
            for item in rest:
                df = pd.DataFrame({item: self.__args_zipped[item]})
                df.to_csv(f"{item}.csv")

        else:
            for zipped in self.__args_zipped:
                df = pd.DataFrame({zipped: self.__args_zipped[zipped]})
                df.to_csv(f"{zipped}.csv")

bot = Bot(command_prefix='/', intents=discord.Intents.all())
server = Server(bot, "monolith", "messages", "members", "test")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    #await server.add('hel')
    #await server.take_snapshot()
    @server.take_snapshot
    async def w():
        await setTest([1, 2])
        
    await w()
    print(id)
    print(Guild)

    await server.export()

    '''
    messages = await getMessages()
    print(messages)z
    '''

    
    
    
    members = await getMembers() 
    print(members)

@bot.command()
async def answer(ctx):
    await ctx.send("hello")

bot.run()


