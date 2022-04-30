from discord.ext import commands
from tools import database_wrapper as db


class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='wallet', description='cash check')
    async def wallet(self, ctx: commands.context.Context):
        items = db.get_user_data(str(ctx.author.id), str(ctx.guild.id))
        # await ctx.send(' '.join(map(str, items)))
        wallet: db.Wallet = items['wallet']
        money = wallet.money

        await ctx.send(f'{ctx.author.nick} has {money}$')
