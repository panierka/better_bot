from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()


def predicate(ctx: commands.Context):
    return str(ctx.author.id) == os.getenv('SUPERADMIN_ID')


superadmin = commands.check(predicate)
