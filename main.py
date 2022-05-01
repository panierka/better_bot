import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

from cogs.base_cog import BaseCog
from cogs.economy_cog import EconomyCog
from cogs.rewards_cog import RewardsCog


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('DISCORD_BOT_TOKEN')
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

    bot.add_cog(BaseCog(bot))
    bot.add_cog(EconomyCog(bot))
    bot.add_cog(RewardsCog(bot))

    bot.run(token)
