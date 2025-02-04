import discord
from discord.ext import commands
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os

genai.configure(api_key="AIzaSyAiQksvTv_AZU-gmjC2IMzh7ME0Oq6GvAM")

model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              safety_settings={
                                  HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                                  HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                                  HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                                  HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                              }
                              )

class adventure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_state = None  # Initialize game state

    async def get_ai_response(self, prompt):
        # Function to send prompt to AI API and get response
        pass

    @commands.command()
    async def adv(self, ctx):
        # Start a new adventure
        initial_prompt = "Your adventure begins... (can you keep your response to less than 2000 characters please)"
        response = model.generate_content(initial_prompt)
        await ctx.send(response.text)
        self.game_state = "started"  # Update game state

    async def present_choices(self, ctx, choices):
        # Present choices to users and collect votes
        message = await ctx.send("Choose your path:\n" + "\n".join(choices))
        # Add reactions for voting
        for emoji in ['1️⃣', '2️⃣', '3️⃣']:
            await message.add_reaction(emoji)
        # Wait for votes (simplified, implement timing and vote counting)

    async def continue_adventure(self, ctx, choice):
        # Continue the adventure based on the chosen option
        next_prompt = f"Based on choice {choice}, what happens next? (can you keep your response to less than 2000 characters please)"
        response = await self.generate_content(next_prompt)
        await ctx.send(response.text)
        # Update game state and present next choices

    @commands.command()
    async def gpt(self, ctx: commands.Context, *, prompt: str):
        response = model.generate_content(prompt + " (can you keep your response to less than 2000 characters please)")

        await ctx.reply(response.text)
    
    #@commands.Cog.listener()
    #async def on_message(self, message):
        #if message.author == self.bot.user:
            #return
        
        #if message.reference and message.reference.resolved:
            #replied_message = message.reference.resolved
            #if replied_message.author == self.bot.user:
                #prompt = replied_message.content

                #combined_prompt = f"{prompt}\n{message.author.display_name}: {message.content}"

                #response = model.generate_content(combined_prompt + " (can you keep your response to less than 2000 characters please)")
                #await message.channel.send(response.text)

async def setup(bot):
    await bot.add_cog(adventure(bot))