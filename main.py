from discord import Object as DiscordObject
from discord import (
    app_commands, 
    Client, 
    Intents, 
    Interaction, 
    Permissions, 
    PermissionOverwrite, 
    utils
)

from datetime import datetime

import traceback
import logging
import asyncio
import signal
import sys

from utilities.ConfigController import config, Secrets

str_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
handler = logging.FileHandler(filename=f'logs\\{str_time}.log', encoding='utf-8', mode='w')

@config
class BotConfig:
    GUILD_ID: int = 1121888564842610768

# Constants
MY_GUILD = DiscordObject(id=BotConfig.GUILD_ID)
TOKEN = Secrets.get("TOKEN")

# Permissions setup
permissions = Permissions()
permissions.value = 9194720066624 # Perhaps this should go in the config

# Intents setup
intents = Intents.default()
intents.message_content = True

# Creating the client instance
class MyClient(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')

    invite_url = utils.oauth_url(
        client_id = 1237848281946652672, # Perhaps this too should go in the config
        permissions=permissions
    )

    print(f'Invite URL: {invite_url}')

# Auxiliary functions
async def close_bot():
    print("Closing the bot...")
    await client.close()

async def main():
    try:
        await client.start(TOKEN)
    finally:
        await close_bot()
        print("Bot has shut down.")
        sys.exit()

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def handle_sigint():
        asyncio.create_task(close_bot())

    # Setting the SIGINT handler
    if sys.platform != 'win32':  # Signal handling does not work on Windows, fun.
        signal.signal(signal.SIGINT, lambda signum, frame: handle_sigint())
    
    asyncio.run(main())