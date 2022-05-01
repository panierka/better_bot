from discord import Guild, VoiceChannel
from discord.ext import commands, tasks
from tools.superadmin import superadmin
from tools.database_wrapper import read_all_rows_from_table, RegisteredChannel, write_to_table


class RewardsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.award_voicechatters.start()

    @tasks.loop(seconds=10)
    async def award_voicechatters(self):
        rows = read_all_rows_from_table(RegisteredChannel)
        for row in rows:
            row: RegisteredChannel

    @superadmin
    @commands.command(name='register_channel', description='enables money gain on given vc')
    async def register_channel(self, ctx, channel_name: str = ''):
        channel_name = channel_name.lstrip('<#').rstrip('>')

        if channel_name == '' or not channel_name.isnumeric():  # or channel nie istnieje
            await ctx.send('invalid channel name')
            return

        channel_id = int(channel_name)
        channel = self.bot.get_channel(channel_id)

        if channel is None:
            await ctx.send('invalid channel name')
            return

        if not isinstance(channel, VoiceChannel):
            await ctx.send('only voice channels can be registered')
            return

        registered_channel = RegisteredChannel()
        registered_channel.id = str(channel.id)
        write_to_table(registered_channel)
        await ctx.send('channel registered successfuly')
