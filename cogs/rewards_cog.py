from discord import Guild, VoiceChannel
from discord.ext import commands, tasks
import requests
import regex as re
from cogs.economy_cog import EconomyCog
from tools.superadmin import superadmin
from tools.database_wrapper import read_all_rows_from_table, RegisteredChannel, write_to_table


class RewardsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @tasks.loop(seconds=514)
    async def award_voicechatters(self):
        rows = read_all_rows_from_table(RegisteredChannel)
        for row in rows:
            row: RegisteredChannel
            channel_id = int(row.id)
            channel: VoiceChannel = self.bot.get_channel(channel_id)

            members = list(filter(lambda x: not x.bot, channel.members))
            if len(members) >= 2:
                economy_cog = self.bot.get_cog('EconomyCog')
                economy_cog: EconomyCog
                for member in members:
                    minimal_wage = 2
                    current_time_multiplier = await RewardsCog.time_multiplier()
                    total_money = minimal_wage * current_time_multiplier
                    economy_cog.balance_change(member.id, channel.guild.id, total_money)

    @staticmethod
    async def time_multiplier() -> int:
        url = r'http://worldtimeapi.org/api/timezone/Europe/Warsaw'
        try:
            response = requests.get(url).json()
            matches = re.findall('(?<=T)..', response)
            match = matches[0] if matches else None
            match = int(match)

            if match == 2:
                return 64
            if match == 3:
                return 128
            if match in range(4, 6 + 1):
                return 16
            if match in range(7, 20 + 1):
                return 1
            if match in range(21, 22 + 1):
                return 2
            if match in range(22, 23 + 1):
                return 4
            if match in range(23, 24 + 1):
                return 8
            if match in range(24, 1 + 1):
                return 16
            return 1
        except requests.Timeout or requests.RequestException:
            print('time API error')
            return 1

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
