from discord.ext import commands


class BettingSession:
    __pools = {
        'believers' : {},
        'doubters' : {}
    }

    def bet(self, uid: str, side, amount):
        if amount <= 0:
            return

        if uid in self.__pools.keys():
            self.__pools[side][uid] += amount
            return
        self.__pools[side][uid] = amount

    def get_resolve(self, side):
        data = {
            'winners' : self.__pools[side].keys(),
            'total_reward' : sum(self.__pools[side].values())
        }
        return data


class BetCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.current_betting_sessions = {}