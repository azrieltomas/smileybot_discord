#SmileBot, originally for Euphoria, and created by SillyLyn.
#Code forked and remade for Discord by crabmatic#2250
#There's a few things in here that are throwbacks to the old system
#I might fix them up but probably wont
import discord
import imgurpython
import asyncio
import json
import time, datetime
import random
import urllib.parse, urllib.error, urllib.request
import math

from discord.ext import commands

#imgur
client_id = ""
client_secret = ""
#discord
DTOKEN = ""
DISCORD_MAX_CHAR = 1850

client = imgurpython.ImgurClient(client_id, client_secret)

description = '''Smilebot, for euphoria, now for Discord!
Original euphoria bot by Lyn. Discord port by crabmatic#2250.
Command Syntax:
    &<smiley> --- calls the image
    !add <smiley> <url>
    !search <string> -- search through the database for similar / matching
    !info user <username>
    !info image <smiley>
    !listall --- lists all available smileys
    !top --- lists the top ten smileys
    !random -- displays a random smiley
    !me_irl --- displays your personal smiley
            --- create with !add me_irl <url>
    !remove <smiley> --- delete smiley from the database
Code available on request.
'''

adminlist = ()

class Image:
    def __init__(self, bot):
        self.bot = bot
        self.imgur = imgurpython.ImgurClient(client_id, client_secret)
        self.times = []
        self.open_list()

    #returns a smiley
    async def on_message(self, message):
        if message.content.startswith('&'):
            key = str(message.content)[1:].casefold()
            if key in self.list:
                await bot.send_message(message.channel, self.list[key].get('url'))
                self.record_data(key)
            else:
                msg = 'No smiley called ' + key + ' exists.'
                await bot.send_message(message.channel, msg)
        #    await bot.process_commands(message)

    #returns bot info / help
    @commands.command()
    async def botinfo(self):
        await self.bot.say(description)

    #returns me_irl smiley for specific user
    @commands.command(pass_context=True, no_pm=True)
    async def me_irl(self, ctx):
        #ctx.message.author > eg crabmatic#2250
        key = str(ctx.message.author).casefold().replace(" ", "_")
        if key in self.list:
            await self.bot.say(self.list[key].get('url'))
            self.record_data(key)
        else:
            await self.bot.say('''You don't have a me_irl!''')

    #returns info on an image or user
    @commands.command(pass_context=True, no_pm=True)
    async def info(self, ctx, option: str=None, key: str=None):
        if not option or not key:
            await self.bot.say('''Syntax error, try:
                !info user <user>
                !info image <image>
                ''')
            return

        if option == 'user':
            count = 0
            for image in self.list:
                if self.list[image].get('user', None) == key:
                    count += 1
            await self.bot.say('User ' + key + ' has added ' + str(count) + ' images.')

        if option == 'image':
            key = key.casefold()
            if key.startswith('"') or key.startswith('<'):
                key = key[1:-1]
            if not key in self.list:
                await self.bot.say('No image named "' + key + '" exists.')
            else:
                await self.bot.say('Info for smiley "' + key +
                           '"\nImgur URL: ' + self.list[key].get('url', '') +
                           '\nUsage count: ' + self.list[key]['count'] +
                           '\nAdded by: ' + self.list[key].get('user','') +
                           '\nTime added (UTC): ' + self.list[key].get('date',''))

    #returns a random image
    @commands.command()
    async def random(self):
        r = random.randint(0, len(list(self.list))-1)
        self.record_data(list(self.list)[r])
        await self.bot.say(list(self.list)[r] + ' ' + self.list[list(self.list)[r]]['url'])

    #lists all available images
    @commands.command()
    async def listall(self):
        message = ''
        for key in self.list:
            message = message + ' `' + key + '`'
        #character limits means we gotta do a thing
        uplimit = math.ceil((len(message) + DISCORD_MAX_CHAR) / 2 / DISCORD_MAX_CHAR)
        await self.bot.say('List of all Smileys:')
        for i in range(1,uplimit+1):
            await self.bot.say ('`' + message[(i*DISCORD_MAX_CHAR-DISCORD_MAX_CHAR):(i*DISCORD_MAX_CHAR)] + '`')

    #lists top smileys
    @commands.command()
    async def top(self):
        top = []
        for key in self.list:
            top.append((int(self.list[key]['count']), key))
        top.sort()
        if len(top) < 10:
            await self.bot.say('You need to have added 10 smileys first.')
        else:
            message = 'Top 10 Smileys:'
            for i in range(1,11):
                message =  message + '\n' + str(i) + '. ' + top[-i][1] + ' (' + str(top[-i][0]) + ')'
            await self.bot.say('```' + message + '```')

    #add a new smiley
    @commands.command(pass_context=True, no_pm=True)
    async def add(self, ctx, key: str=None, url: str=None):
        #get the format correct
        if not url:
            await self.bot.say('''~bad syntax puppies~ https://i.imgur.com/ieajOG4.jpg\nTry !add <name> <url>''')
            return
        if key.startswith('"') or key.startswith('<'):
            key = key[1:-1]
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        key = key.casefold()

        #handle me_irl adds
        if key == 'me_irl' or key == 'meirl':
            key = str(ctx.message.author).casefold().replace(" ", "_")

        #verify some error conditions
        if key in self.list:
            await self.bot.say('Name "' + key + '" already in use. Please choose a different name')
            return

        #if image is from imgur just add away
        if self.imgur_verification(url):
            self.list[key] = {'url': url, 'count': '0', 'user': str(ctx.message.author).replace(" ", "_"),
                              'date': str(datetime.datetime.utcnow()), 'deletehash': None}
            self.write_list()
            await self.bot.say('New smiley "' + key + '" added.')
        #if image not from imgur, try uploading it
        elif self.non_imgur_verification(url):
            if client.get_credits()['UserRemaining'] >= 10:
                try:
                    img = client.upload_from_url(url)
                    self.list[key] = {'url': img['link'], 'count': '0', 'user': str(ctx.message.author).replace(" ", "_"),
                                      'date': str(datetime.datetime.utcnow()), 'deletehash': None}
                    self.write_list()
                    await self.bot.say('New smiley "' + key + '" added.')
                except imgurpython.helpers.error.ImgurClientRateLimitError:
                    await self.bot.say('Error: Imgur Rate Limit Error. Unable to add smiley.')
            else:
                await self.bot.say('Not enough Imgur credits. Please reupload the image to imgur manually, or try again later.')
        else:
            await self.bot.say('Imgur error: possible error in image or url. Please check and retry.')

    #remove a smiley
    @commands.command(pass_context=True, no_pm=True)
    async def remove(self, ctx, key: str=None):
        if not key:
            await self.bot.say('Syntax error, try !remove <name>')
            return

        key = key.casefold()
        #handle me_irl adds
        if key == 'me_irl' or key == 'meirl':
            key = str(ctx.message.author).casefold().replace(" ", "_")

        if str(ctx.message.author).replace(" ", "_") in adminlist or str(ctx.message.author).replace(" ", "_") == self.list[key].get('user'):
            if not key in self.list:
                await self.bot.say('Unable to find smiley in list. Please try again')
            else:
                if key.startswith('"') or key.startswith('<'):
                    key = key[1:-1]
                try:
                    del self.list[key]
                except KeyError:
                    return
                else:
                    self.write_list()
                    await self.bot.say('Smiley "' + key +'" removed.')
        else:
            await self.bot.say('Insufficient privileges')

    #search for a smiley
    @commands.command(pass_context=True, no_pm=True)
    async def search(self, ctx, searchstr: str=None):
        message = ''
        if not searchstr:
            await self.bot.say('Syntax error, try !search <string>')
            return
        searchstr = searchstr.casefold()
        for key in self.list:
            if key.find(searchstr) >= 0:
                message = message + ' `' + key + '`'
        if message == '':
            await self.bot.say('No match for "' + searchstr + '"')
        else:
             await self.bot.say(message)

    def imgur_verification(self, url):
        if not 'imgur.com' in urllib.parse.urlparse(url).netloc:
            return False
        try:
            client.get_image(urllib.parse.urlparse(url).path.split('.')[0][1:])
        except imgurpython.helpers.error.ImgurClientError:
            return False
        else:
            return True

    def non_imgur_verification(self, url):
        try:
            valid_link= urllib.request.urlopen(url).info().get_content_type().startswith('image')
        except urllib.error.HTTPError:
            return False
        except urllib.error.URLError:
            return False
        else:
            if valid_link:
                return True
            else:
                return False

    def open_list(self):
        with open('list.json', 'r') as imagelist:
            self.list = json.load(imagelist)

    def write_list(self):
        with open('list.json', 'w') as imagelist:
            json.dump(self.list, imagelist)

    def record_data(self, key):
        self.times.append(time.time())
        self.list[key]['count'] = str(int(self.list[key]['count']) + 1)
        self.write_list()

bot = commands.Bot(command_prefix='!', description=description)
bot.add_cog(Image(bot))

@bot.event
async def on_ready():
    print("Bot logged in")
    print(bot.user.name)
    print(bot.user.id)

bot.run(DTOKEN)
