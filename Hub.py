import discord
from Server import Server

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
                server = Server(self.client, str(guild), *self.args)
                self.servers.append(server)
            
            if func is None:
                return await self.default_initialize()
            else:
                await func()
        if func is None:
            return take_snapshot_wrappper()
        return take_snapshot_wrappper
         