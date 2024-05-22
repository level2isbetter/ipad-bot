import emoji
import requests
import csv

from datetime import datetime, timedelta

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
            target_lang = 'JA' # Japanese default
            translateMe = " ".join(args)

        print("Translation request: ", translateMe)
        if translateMe == "":
            translateMe = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            translateMe = translateMe.content

        if(emoji.demojize(translateMe).isascii()): #Checks if the message is ASCII, will set source lang to english
            source_lang = 'EN'
        else: #otherwise, japanese
            source_lang = 'JA'
        
        # my DeepL API key (im stupid and cant get configs to work)
        url = "https://api-free.deepl.com/v2/translate?auth_key={DEEL_API_KEY}"

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