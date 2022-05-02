from discord import User, Member
from discord.ext import commands
from tools import database_wrapper as db
from tools.superadmin import superadmin

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

    @commands.command(name='burn', description='throw away any amount of your cash')
    async def burn(self, ctx, amount: int = 0):
        if amount <= 0:
            return await ctx.send("can't burn less than 1$")

        uid = ctx.author.id
        guid = ctx.guild.id
        EconomyCog.balance_change(uid, guid, -amount)
        await ctx.send(f'successfully burned {amount}$')
        await self.wallet(ctx)

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
        target_amount = current_amount + amount

        # break if amount becomes <0
        if target_amount < 0:
            target_amount = 0

        db.update_table('wallet', user_id, guild_id, 'money', target_amount)

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

        current_balance = self.balance_check(sender_id, ctx.guild.id)

        if current_balance < amount:
            amount = current_balance

        return await self.transfer_money(amount, ctx, recipient_id, sender_id)

    @superadmin
    @commands.command(name='steal', description='gaming')
    async def steal(self, ctx, victim: str = '', amount: int = 0):
        if victim == '':
            return

        victim_id = self.strip_id(victim)

        if not victim_id.isnumeric():
            return

        thief_id = ctx.author.id
        current_balance = self.balance_check(victim_id, ctx.guild.id)

        if current_balance < amount:
            amount = current_balance

        return await self.transfer_money(amount, ctx, thief_id, victim_id)

    async def transfer_money(self, amount, ctx, recipient_id, sender_id):
        # take money from sender
        self.balance_change(sender_id, ctx.guild.id, -abs(amount))
        # give money to recipient
        self.balance_change(recipient_id, ctx.guild.id, amount)
        sender_name = await self.id_to_nick(ctx, sender_id)
        recipient_name = await self.id_to_nick(ctx, recipient_id)
        await ctx.send(f'Transfered {amount}$ '
                       f'from {sender_name} ({self.balance_check(sender_id, ctx.guild.id)}$) '
                       f'to {recipient_name} ({self.balance_check(recipient_id, ctx.guild.id)}$)')
        return

    # relative wealth status display logic
    @staticmethod
    def wealth_status(user_id, guild_id):
        user_wealth = EconomyCog.balance_check(user_id, guild_id)

        wallets = db.find_active_wallets(server_id=guild_id)
        max_wealth = max(map(lambda x: x.money, wallets))
        min_wealth = min(map(lambda x: x.money, wallets))

        normalized_wealth = (user_wealth - min_wealth) / (max_wealth - min_wealth)
        lvl = EconomyCog.check_relative_wealth(normalized_wealth)

        return EconomyCog.wealth_status_emoji(lvl)

    # compare user wealth to average wealth
    @staticmethod
    def check_relative_wealth(ratio):
        index = int(ratio * 8)
        return index

    @staticmethod
    def wealth_status_emoji(lvl):
        # list of 9 emojis, worst to best
        list_emojis = ['<:trollgan:840535942006833152>', '<:trollge:818968052388855868>', '<:sadge:778533708135137331>',
                       '<:weirdga:845369491793117234>', '<:trollsmile:843465720171855883>', '<:okayge:778544807257440277>',
                       '<:pogCaco:698831786230284318>', '<:knyga:947560578233294848>', '<:POLSKAGUROM:845746986841145355>']

        if len(list_emojis) >= lvl:
            return list_emojis[lvl]