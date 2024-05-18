import discord 
import pandas as pd 
import os 
import psycopg2

class Hub():
    def __init__(self, client: discord.Client, *args):
        self.args = [x for x in args]
        self.client = client
        self.servers = [] 

    async def default_initialize(self):
        for server in self.servers:
            await server.take_snapshot()

    async def default_export(self, file_type='csv'):
        for server in self.servers:
            await server.export(file_type=file_type)

    def export(self, func=None, file_type='csv'):
        async def export_wrapper():
            if func is None:
                return await self.default_export(file_type=file_type)
            else:
                return await func()

        if func is None:
            return export_wrapper()
        return export_wrapper

    def intialize(self, func=None, database_config={}):
        async def take_snapshot_wrappper():
            for guild in self.client.guilds:
                server = _Server(self.client, str(guild), *self.args, database_config=database_config)
                self.servers.append(server)
            
            if func is None:
                return await self.default_initialize()
            else:
                return await func()
        if func is None:
            return take_snapshot_wrappper()
        return take_snapshot_wrappper

class _Server:
    def __init__(self, client: discord.Client, guild: discord.Guild, *args, database_config={}):
        self.__client = client 
        self.guild = guild
        self.__args = [x for x in args]
        self.database_config = database_config

        if not any([isinstance(x, str) for x in self.__args]):
            raise TypeError
        
        # Options for setup -> pre-programed 
        self.options = {'members': False, 'messages': False}

        if 'members' in self.__args:
            self.options['members'] = True
        if 'messages' in self.__args:
            self.options['messages'] = True
        
        # PostgreSQL Database functions generation 
        if database_config:
            try: 
                self.connect = psycopg2.connect(**self.database_config)
                print('[200]')
                self.cur = self.connect.cursor()
            except psycopg2.Error as e:
                print(f"Error connecting to the database . . . {e}")

            for index, arg in enumerate(self.__args):
                gen_function_database_getter = f"""async def {self.guild.capitalize()}Get{arg.capitalize()}():
                self.cur.execute("SELECT {arg} FROM {self.guild}_{arg}")
                self.connect.commit()
                output = self.cur.fetchall()
                return [row[0] for row in output]"""

                gen_function_database_setter = f"""async def {self.guild.capitalize()}Set{arg.capitalize()}(value):
                if not isinstance(value, list):
                    raise TypeError("value is supposed to be type list not " + str(type(value)))
                self.cur.execute('''DELETE FROM {self.guild}_{arg}''')
                self.connect.commit()
                for item in value:
                    self.cur.execute(f'''INSERT INTO {self.guild}_{arg} ({arg})
                    VALUES ('{{item}}')''')
                    self.connect.commit()"""

                gen_function_database_add = f"""async def {self.guild.capitalize()}Add{arg.capitalize()}(value):
                self.cur.execute(f'''INSERT INTO {self.guild}_{arg} ({arg})
                VALUES ('{{value}}')''')
                self.connect.commit()"""

                gen_function_database_remove = f"""async def {self.guild.capitalize()}Remove{arg.capitalize()}():
                self.cur.execute('''DELETE FROM {self.guild}_{arg}
                WHERE id = (
                    SELECT id
                    FROM {self.guild}_{arg}
                    ORDER BY id DESC 
                    LIMIT 1
                );''')"""

                exec(gen_function_database_getter, {'self': self}, globals())
                exec(f"import __main__; __main__.{self.guild.capitalize()}Get{arg.capitalize()} = {self.guild.capitalize()}Get{arg.capitalize()}")
                exec(gen_function_database_setter, {'self': self}, globals())
                exec(f"import __main__; __main__.{self.guild.capitalize()}Set{arg.capitalize()} = {self.guild.capitalize()}Set{arg.capitalize()}")
                exec(gen_function_database_add, {'self': self}, globals())
                exec(f"import __main__; __main__.{self.guild.capitalize()}Add{arg.capitalize()} = {self.guild.capitalize()}Add{arg.capitalize()}")
                exec(gen_function_database_remove, {'self': self}, globals())
                exec(f"import __main__; __main__.{self.guild.capitalize()}Remove{arg.capitalize()} = {self.guild.capitalize()}Remove{arg.capitalize()}")

        else:
            self.__args_values = [[] for x in self.__args] 

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
            if self.database_config:
                
                for item in self.__args:
                    self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {self.guild.capitalize()}_{item} (
                        id SERIAL PRIMARY KEY
                        );""")
                    self.connect.commit()
                    self.cur.execute(f"""ALTER TABLE {self.guild.capitalize()}_{item}
                    ADD COLUMN IF NOT EXISTS {item} TEXT;
                    """)
                    self.connect.commit()
            
            else:
                self.guild_names = [x.name for x in self.__client.guilds]

                self.guild_obj = self.__client.guilds[self.guild_names.index(self.guild)] 

                global_guild_exec_code1 = f"global {self.guild.capitalize()}Guild"
                global_guild_exec_code2  = f"{self.guild.capitalize()} = self.guild_obj"

                exec(f"global {self.guild.capitalize()}")
                
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
                self.df = pd.DataFrame(df_dict)
                self.file_type_manager(file_type, self.df, f"{'&'.join(group)}") 
                #df.to_csv(f"{'&'.join(group)}.csv")

            flatten = [y for y in [x for x in to_merge]][0]
            rest = [x for x in self.__args if not x in flatten]
            
            for item in rest:
                self.df = pd.DataFrame({item: self.__args_zipped[item]})
                self.file_type_manager(file_type, self.df, f"{item}")

        else:
            for zipped in self.__args_zipped:
                self.df = pd.DataFrame({zipped: self.__args_zipped[zipped]})
                self.file_type_manager(file_type, self.df, f"{zipped}") 
                #df.to_csv(f"{zipped}.csv")

        self.file_type_manager(file_type, self.to_pd_dataframe(), "one-column")

    def to_pd_dataframe(self):
        combined_list_catagories = [] 
        combined_list_values = [] 
        for index, item in enumerate(self.__args):
            combined_list_catagories += [item] * len(self.__args_values[index])
            combined_list_values += self.__args_values[index]

        return pd.DataFrame({'Catagory': combined_list_catagories, "Value": combined_list_values})

    async def disconnect(self):
        self.cur.close() 
        self.connect.close() 
    
    def database_to_pd_dataframe(self, table=None):
        if table:
            self.cur.execute(f"SELECT {table.split('_')[-1]} FROM {table}")
            output = self.cur.fetchall() 
            return pd.DataFrame(output)
        else:
            combined_list_catagories = [] 
            combined_list_values  = []
            for item in self.__args:
               self.cur.execute(f"SELECT {item} FROM {self.guild}_{item}")
               output = self.cur.fetchall()
               output = [x[0] for x in output]
               combined_list_catagories += [item] * len(output)
               combined_list_values += output 

        return pd.DataFrame({'Catagory': combined_list_catagories, 'Value': combined_list_values})

class ServerStatistics:
    def __init__(self, server):
        self.server = server
        if server.database_config:
            self.df = self.server.database_to_pd_dataframe() 
        else:
            self.df = self.server.to_pd_dataframe()
        
        
