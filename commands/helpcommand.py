from discord import Embed
from discord.ext import commands

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = Embed(title="Bot Commands", color=0x00ff00)
        for cog, commands in mapping.items():
            if cog:
                cog_name = cog.qualified_name
                commands_desc = "\n".join([c.name for c in commands])
                if commands_desc:
                    embed.add_field(name=cog_name, value=commands_desc, inline=False)
        
        await self.context.send(embed=embed)