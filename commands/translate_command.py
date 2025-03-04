import emoji
import requests
import csv, configparser
import os

from langdetect import detect
from datetime import datetime, timedelta

DEEPLAPIKEY = os.getenv('DEEPL_API_KEY')

# Logging function for translation requests
def log(user, server, channel, source_lang, target_lang, translateMe, result):
    with open('./log.csv', 'a', encoding='UTF8', newline='') as f:
        now = datetime.now() - timedelta(hours=5)
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        row = [
            now, user, server, channel, source_lang, target_lang, translateMe, result
        ]
        writer = csv.writer(f)
        writer.writerow(row)

def add_translate_command(bot):
    # Translate command, only from JP to EN for now
    @bot.command(name="translate", aliases=["tl"])
    async def translate(ctx, *args):
        channel = ctx.channel.name
        server = ctx.guild.name
        user = ctx.author

        # Checks to see if the first argument is a language code
        if len(args) > 0 and args[0].startswith('-'):
            target_lang = args[0][1:].upper()
            translateMe = " ".join(args[1:])
        else:
            target_lang = 'EN' # Japanese default
            translateMe = " ".join(args)

        print("Translation request: ", translateMe)
        if translateMe == "":
            translateMe = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            translateMe = translateMe.content

        try:
            source_lang = detect(translateMe).upper()
        except:
            source_lang = 'EN'
        #if(emoji.demojize(translateMe).isascii()): #Checks if the message is ASCII, will set source lang to english
            #source_lang = 'EN'
        #else: #otherwise, japanese
            #source_lang = 'JA'
        
        # my DeepL API key (im stupid and cant get configs to work) UPDATE: I GOT THEM TO WORK
        url = f"https://api-free.deepl.com/v2/translate?auth_key={DEEPLAPIKEY}"

        params = {
            'text': translateMe,
            'source_lang': source_lang,
            'target_lang': target_lang
        }

        response = requests.get(url, params=params)
        responseJSON = response.json()
    
        try:
            result = responseJSON['translations'][0]['text']
            print("Translated result: ", result)
            await ctx.reply(result)
            log(user, server, channel, source_lang, target_lang, translateMe, result)
        except:
            errMsg = "Translation failed. Error code: {}".format(response.status_code)
            print("Error: ", errMsg)
            await ctx.reply(errMsg)
            log(user, server, channel, source_lang, target_lang, translateMe, errMsg)