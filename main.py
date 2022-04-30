import os
from dotenv import load_dotenv
from discord.ext import commands

from cogs.base_cog import BaseCog
from cogs.economy_cog import EconomyCog


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot = commands.Bot(command_prefix='!', help_command=None)

    bot.add_cog(BaseCog(bot))
    bot.add_cog(EconomyCog(bot))

    bot.run(token)
