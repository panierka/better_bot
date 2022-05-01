from discord.ext import commands


class BaseCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name='on_ready')
    async def on_ready(self):
        print('bot is ready')
        servers_overview = ', '.join(map(str, self.bot.guilds))
        print('bound servers:', servers_overview)
        self.bot.get_cog('RewardsCog').award_voicechatters.start()

    @commands.command(name='ping', description='checks connection')
    async def ping(self, ctx: commands.context.Context):
        reaction_time_ms = round(self.bot.latency * 1000)
        await ctx.send(f'pong *time={reaction_time_ms}ms*')

    @commands.command(name='help', description='shows all commands')
    async def help(self, ctx, p=""):
        if p != "":
            p = p.lower()
            if p in self.bot.all_commands.keys():
                description = self.bot.all_commands[p].description
                if description == "":
                    await ctx.send(f'*`{p}` has no description yet, sorry*')
                    return
                await ctx.send(f'`{p}`: {description}')
                return

        message = '<:POLSKAGUROM:845746986841145355> **list of available commands:** ```'
        for command in self.bot.all_commands.values():
            command: commands.Command
            message += f'\n - !{command.name}'
            if command.description != "":
                message += f' ({command.description})'

        await ctx.send(message + '```')
