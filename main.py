import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

from base_cog import BaseCog


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot = commands.Bot(command_prefix='!', help_command=None)

    bot.add_cog(BaseCog(bot))

    bot.run(token)
