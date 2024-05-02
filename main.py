import discord
from discord.ext import commands
import dotenv
import nest_asyncio
import os
nest_asyncio.apply()
dotenv.load_dotenv()
from bot import Bot


class Server:
    def __init__(self, client: discord.Client, *argv):
        self.__args = [x for x in argv]

        if not any([isinstance(x, str) for x in self.__args]):
            raise TypeError

        self.__args_values = [[] for x in self.__args] 
        self.__client = client 

        global temp_array 
        temp_array = self.__args_values

        for index, arg in enumerate(self.__args):
            gen_function_code_getter = f'''def get{arg.capitalize()}():
            return self._Server__args_values[{index}]'''

            gen_function_code_setter = f'''def set{arg.capitalize()}(value):
            if not isinstance(value, list):
                raise TypeError
            self._Server__args_values[{index}] = value 
            '''

            gen_function_code_add = f'''def add{arg.capitalize()}(value):
            self._Server__args_values[{index}].append(value)'''

            gen_function_code_remove = f'''def remove{arg.capitalize()}(*args):
            if len(args) > 1:
                raise TypeError("remove{arg.capitalize()} only takes one positional agrument but " + str(len(args)) + " were given")
            if args:
                del self._Server__args_values[{index}][args[0]]
            else:
                del self._Server__args_values[{index}][-1]'''

            gen_function_code_remove_index = f'''def removeIndex{arg.capitalize()}(index):
            del self._Server__args_values[{index}][index]'''
            
            exec(gen_function_code_getter, {'self':self}, globals())
            exec(gen_function_code_setter, {'self':self}, globals())
            exec(gen_function_code_add, {'self':self}, globals())
            exec(gen_function_code_remove, {'self':self}, globals())
        

    def take_snapshot(self):
        pass


b = Bot(command_prefix='/', intents=discord.Intents.all())
server = Server(b, "data")
#b.run()
setData(["dataset"]) 
addData('added')
print(getData())
removeData(1) 
print(getData())

