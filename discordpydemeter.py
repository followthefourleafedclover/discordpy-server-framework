import discord 
import pandas as pd 
import os 

class Hub():
    def __init__(self, client: discord.Client, *args):
        self.args = [x for x in args]
        self.client = client
        self.servers = [] 

    async def default_initialize(self):
        for server in self.servers:
            await server.take_snapshot()


    def intialize(self, func=None):
        async def take_snapshot_wrappper():
            for guild in self.client.guilds:
                server = _Server(self.client, str(guild), *self.args)
                self.servers.append(server)
            
            if func is None:
                return await self.default_initialize()
            else:
                await func()
        if func is None:
            return take_snapshot_wrappper()
        return take_snapshot_wrappper

class _Server:
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

            gen_function_code_getter = f'''async def {self.guild.capitalize()}Get{arg.capitalize()}():
            return self._Server__args_values[{index}]'''

            gen_function_code_setter = f'''async def {self.guild.capitalize()}Set{arg.capitalize()}(value):
            if not isinstance(value, list):
                raise TypeError("value is supposed to be type list not " + str(type(value)))
            self._Server__args_values[{index}] = value 
            '''

            gen_function_code_add = f'''async def {self.guild.capitalize()}Add{arg.capitalize()}(value):
            self._Server__args_values[{index}].append(value)'''

            gen_function_code_remove = f'''async def {self.guild.capitalize()}Remove{arg.capitalize()}(*args):
            if len(args) > 1:
                raise TypeError("{self.guild.capitalize()}Remove{arg.capitalize()} only takes one positional agrument but " + str(len(args)) + " were given")
            if args:
                del self._Server__args_values[{index}][args[0]]
            else:
                del self._Server__args_values[{index}][-1]'''

            
            exec(gen_function_code_getter, {'self':self}, globals())
            exec(f"import __main__; __main__.{self.guild.capitalize()}Get{arg.capitalize()} = {self.guild.capitalize()}Get{arg.capitalize()}")
            exec(gen_function_code_setter, {'self':self}, globals())
            exec(f"import __main__; __main__.{self.guild.capitalize()}Set{arg.capitalize()} = {self.guild.capitalize()}Set{arg.capitalize()}")
            exec(gen_function_code_add, {'self':self}, globals())
            exec(f"import __main__; __main__.{self.guild.capitalize()}Add{arg.capitalize()} = {self.guild.capitalize()}Add{arg.capitalize()}")
            exec(gen_function_code_remove, {'self':self}, globals())
            exec(f"import __main__; __main__.{self.guild.capitalize()}Remove{arg.capitalize()} = {self.guild.capitalize()}Remove{arg.capitalize()}")

        self.server_dir = f"{os.getcwd()}/{self.guild.capitalize()}"


    async def __generic_function(self):
        print(f"Taking Snapshot of {self.guild.capitalize()} . . .")

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

            global_guild_exec_code1 = f"global {self.guild.capitalize()}"
            global_guild_exec_code2  = f"{self.guild.capitalize()} = self.guild_obj"
            
            exec(global_guild_exec_code1, {'self':self}, globals())
            exec(global_guild_exec_code2, {'self':self}, globals())
            exec(f"import __main__; __main__.{self.guild.capitalize()} = {self.guild.capitalize()}")

            self.guild_attrs = self.__get_guild_attrs()

            for attr in self.guild_attrs:
                code = f'{self.guild.capitalize()}{attr.capitalize()} = self.guild_obj.{attr}'
                exec(code, {'self':self}, globals())
                exec(f"import __main__; __main__.{self.guild.capitalize()}{attr.capitalize()} = {self.guild.capitalize()}{attr.capitalize()}")
        
            if self.options['members']:
                for member in self.guild_obj.members:
                    await eval(f"{self.guild.capitalize()}AddMembers('{str(member)}')", globals())

            if self.options['messages']:
                for channel in self.guild_obj.channels:
                    try:
                        async for message in channel.history(limit=None):
                            await eval(f"{self.guild.capitalize()}AddMessages('{message.content}')", globals())
                    except AttributeError:
                        pass

            if func is None:
                await self.__generic_function() 
            else:    
                await func()

        if func is None:
            return take_snapshot_wrapper()
        return take_snapshot_wrapper

    def file_type_manager(self, file_type, frame, text):
        if file_type ==  'csv':
            return frame.to_csv(os.path.join(self.server_dir, f'{text}.csv'), index=False)

        if file_type == 'excel':
            return frame.to_excel(os.path.join(self.server_dir, f'{text}.xlsx'), sheet_name=f"{text}", index=False)
        raise NotImplementedError


    async def export(self, file_type='csv'):
        print(self.server_dir)
        if not os.path.isdir(self.server_dir):
            os.mkdir(self.server_dir)
        self.__args_zipped = dict(zip(self.__args, self.__args_values))

        async def merge():
            lengths = [len(x) for x in self.__args_zipped.values()] 
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

        to_merge = await merge() 
    
        if to_merge:
            df_dict = {} 
            for index, group in enumerate(to_merge): 
                for item in group: 
                    df_dict.update({item: self.__args_zipped[item]})

                print(df_dict)
                df = pd.DataFrame(df_dict)
                self.file_type_manager(file_type, df, f"{'&'.join(group)}") 
                #df.to_csv(f"{'&'.join(group)}.csv")

            flatten = [y for y in [x for x in to_merge]][0]
            rest = [x for x in self.__args if not x in flatten]
            
            for item in rest:
                df = pd.DataFrame({item: self.__args_zipped[item]})
                self.file_type_manager(file_type, df, f"{item}")

        else:
            for zipped in self.__args_zipped:
                df = pd.DataFrame({zipped: self.__args_zipped[zipped]})
                self.file_type_manager(file_type, df, f"{zipped}") 
                #df.to_csv(f"{zipped}.csv")
