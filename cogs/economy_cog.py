from discord.ext import commands
from tools import database_wrapper as db


class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='test_read')
    async def test_read(self, ctx, table_name: str = ""):
        if table_name == "":
            await ctx.send('missing table name')
            return

        items = db.read_tables(table_name)
        await ctx.send(', '.join(map(str, items)))

    @commands.command(name='test_write')
    async def test_write(self, ctx, name: str = ""):
        if name == "":
            await ctx.send('missing item name')
            return

        item = db.TestTabl1()
        item.name = name
        db.write_to_table(item)

    @commands.command(name='wallet')
    async def wallet(self, ctx: commands.context.Context):
        items = db.get_user_data(10, 5)
        await ctx.send(items[0])
