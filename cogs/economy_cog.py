from discord import User, Member
from discord.ext import commands
from tools import database_wrapper as db


class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='wallet', description='cash check')
    async def wallet(self, ctx: commands.context.Context, user: str = ''):
        if user == "":
            balance = self.balance_check(ctx.author.id, ctx.guild.id)
            await ctx.send(f'{ctx.author.nick} has {balance}$')
            return

        user_id = self.strip_id(user)
        nick = await self.id_to_nick(ctx, user_id)
        balance = self.balance_check(user_id, ctx.guild.id)

        await ctx.send(f'{nick} has {balance}$')

    @commands.command(name='test')
    async def test(self, ctx: commands.context.Context, user: str = ''):
        if user == '':
            return

        raw_id = user.lstrip('<@').rstrip('>')

        if not raw_id.isnumeric():
            return

        member: Member = await ctx.guild.fetch_member(int(raw_id))
        await ctx.send(f'{member.nick}, id = {raw_id}')

    # kuba moment
    @staticmethod
    def balance_change(user_id, guild_id, amount):
        current_amount = EconomyCog.balance_check(user_id, guild_id)

        # break if amount becomes <0
        if current_amount + amount < 0:
            return False

        db.update_table('wallet', user_id, guild_id, 'money', current_amount + amount)
        return True

    @staticmethod
    def balance_check(user_id, guild_id):
        balance = db.read_from_table('wallet', user_id, guild_id).money
        return balance

    @staticmethod
    def strip_id(nick):
        return nick.lstrip('<@').rstrip('>')

    @staticmethod
    async def id_to_nick(ctx, user_id):
        user: Member = await ctx.guild.fetch_member(int(user_id))
        return user.nick

    @commands.command(name='pay', description='transfer money between users')
    async def pay(self, ctx: commands.context.Context, recipient: str = '', amount: str = ''):
        if recipient == '' or amount == '':
            return

        recipient_id = self.strip_id(recipient)

        if not recipient_id.isnumeric() or not amount.isnumeric():
            return

        sender_id = ctx.author.id
        amount = int(amount)
        recipient_name = await self.id_to_nick(ctx, recipient_id)

        # take money from sender
        if self.balance_change(sender_id, ctx.guild.id, -abs(amount)):

            # give money to recipient
            self.balance_change(recipient_id, ctx.guild.id, amount)
            await ctx.send(f'Transfered {amount}$ '
                           f'from {ctx.author.nick} ({self.balance_check(sender_id, ctx.guild.id)}$) '
                           f'to {recipient_name} ({self.balance_check(recipient_id, ctx.guild.id)}$)')
            return

        await ctx.send(f'Transfer failed')
