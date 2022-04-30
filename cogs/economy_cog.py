from discord import User, Member
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

    @commands.command(name='test')
    async def test(self, ctx: commands.context.Context, user: str = ''):
        if user == '':
            return

        raw_id = user.lstrip('<@').rstrip('>')

        if not raw_id.isnumeric():
            return

        member: Member = await ctx.guild.fetch_member(int(raw_id))
        await ctx.send(f'{member.nick}, id = {raw_id}')
