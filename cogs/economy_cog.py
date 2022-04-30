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

    #kuba moment
    def changeBalance(self, userid, guid, amount):
        current_amount = db.read_from_table('wallet', userid, guid).money

        # break if amount becomes <0
        if current_amount + amount < 0:
            return False

        db.update_table('wallet', userid, guid, 'money', current_amount + amount)
        return True

    def checkBalance(self, userid, guid):
        balance = db.read_from_table('wallet', userid, guid).money
        return balance

    @commands.command(name='pay', description='transfer money between users')
    async def pay(self, ctx: commands.context.Context, recipient: str = '', amount: str = ''):
        if recipient == '' or amount == '':
            return

        recipient_id = recipient.lstrip('<@').rstrip('>')

        if not recipient_id.isnumeric() or amount.isnumeric():
            return

        senderid = ctx.author.id
        guid = ctx.guild.id
        amount = int(amount)
        recipientName: Member = await ctx.guild.fetch_member(int(recipient_id))

        # take money from sender
        if self.changeBalance(senderid, guid, -abs(amount)):

            # give money to recipient
            self.changeBalance(recipient_id, guid, amount)
            await ctx.send(f'Transfered {amount} from {senderid} to {recipientName.nick}')

        await ctx.send(f'Transfer failed')