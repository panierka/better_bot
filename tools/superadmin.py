from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()


async def predicate(ctx: commands.Context):
    can_proceed = str(ctx.author.id) == os.getenv('SUPERADMIN_ID')
    return can_proceed


superadmin = commands.check(predicate)
