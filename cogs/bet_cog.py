from discord.ext import commands


class BetCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.current_betting_sessions = {}

