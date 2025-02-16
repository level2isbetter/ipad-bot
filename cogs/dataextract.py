import discord
from discord.ext import commands
import csv

class DataExtraction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def extractmsg(self, ctx, user_id: int, limit: int = 100):
        """Extract messages from a specified user across all channels."""
        user = self.bot.get_user(user_id)
        if not user:
            await ctx.send("User not found.")
            return

        messages = []
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                try:
                    async for message in channel.history(limit=limit):
                        if message.author.id == user_id:
                            messages.append({
                                "channel": channel.name,
                                "author": message.author.name,
                                "content": message.content,
                                "timestamp": str(message.created_at)
                            })
                except discord.Forbidden:
                    # Skip channels where the bot does not have access
                    continue

        # Save to a CSV file
        with open('user_messages.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["channel", "author", "content", "timestamp"])
            writer.writeheader()
            writer.writerows(messages)

        await ctx.send(f'Extracted {len(messages)} messages from {user.name}.')

async def setup(bot):
    await bot.add_cog(DataExtraction(bot))