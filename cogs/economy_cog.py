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
            status_emoji = EconomyCog.wealth_status(ctx.author.id, ctx.guild.id)
            await ctx.send(f'{ctx.author.nick} has {balance}$ {status_emoji}')
            return

        user_id = self.strip_id(user)
        nick = await self.id_to_nick(ctx, user_id)
        balance = self.balance_check(user_id, ctx.guild.id)
        status_emoji = EconomyCog.wealth_status(user_id, ctx.guild.id)

        await ctx.send(f'{nick} has {balance}$ {status_emoji}')

    @commands.command(name='test')
    async def test(self, ctx: commands.context.Context, user: str = ''):
        if user == '':
            return

        raw_id = user.lstrip('<@').rstrip('>')

        if not raw_id.isnumeric():
            return

        member: Member = await ctx.guild.fetch_member(int(raw_id))
        await ctx.send(f'{member.nick}, id = {raw_id}')

    # wallet and pay logic
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
        balance = db.read_userdata_from_table('wallet', user_id, guild_id).money
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


    # relative wealth status display logic

    @staticmethod
    def wealth_status(user_id, guild_id):
        user_wealth = EconomyCog.balance_check(user_id, guild_id)
        total_wealth, active_users_num = EconomyCog.guild_wealth(guild_id)
        lvl = EconomyCog.check_relative_wealth(user_wealth, total_wealth, active_users_num)
        return EconomyCog.wealth_status_emoji(lvl)

    # find all server users with >0$, calculate total server wealth
    @staticmethod
    def guild_wealth(guild_id):
        users = db.find_active_users(guild_id)
        total_wealth = 0

        for user in users:
            total_wealth += EconomyCog.balance_check(user.user_id, guild_id)

        return total_wealth, len(users)

    # compare user wealth to average wealth
    @staticmethod
    def check_relative_wealth(user_wealth, total_wealth, users_num):
        avg_wealth = total_wealth // users_num
        ratio = user_wealth / avg_wealth

        if ratio < 0.001:
            return 0
        if ratio < 0.01:
            return 1
        if ratio < 0.1:
            return 2
        if ratio < 0.5:
            return 3
        if ratio < 1.5:
            return 4
        if ratio < 10:
            return 5
        if ratio < 100:
            return 6
        if ratio < 1000:
            return 7
        if ratio > 1000:
            return 8

    @staticmethod
    def wealth_status_emoji(lvl):
        # list of 9 emojis, worst to best
        list_emojis = ['<:trollgan:840535942006833152>', '<:trollge:818968052388855868>', '<:sadge:778533708135137331>',
                       '<:weirdga:845369491793117234>', '<:trollsmile:843465720171855883>', '<:okayge:778544807257440277>',
                       '<:pogCaco:698831786230284318>', '<:knyga:947560578233294848>', '<:POLSKAGUROM:845746986841145355>']

        if len(list_emojis) >=lvl:
            return list_emojis[lvl]