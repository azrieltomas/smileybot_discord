import discord
import imgurpython
import asyncio
import imgurpython
import json
import time, datetime
import random
import urllib.parse, urllib.error, urllib.request

from discord.ext import commands

#imgur
client_id = "aec4adccb968389"
client_secret = "741f26d732eb750314ec4c1e6065a2a061951fff"
#discord
DTOKEN = "MzA1MjcxNzI0NjU4Nzg2MzA0.C9yzuw.KHUFIf9W6rUk2FDfOC4hwl8Bd2Q"

client = imgurpython.ImgurClient(client_id, client_secret)
dclient = discord.Client()

description='''Smilebot, for euphoria, now for Discord!
Original euphoria bot by Lyn. Discord port by crabmatic#2250.
Command Syntax:
    !add <name> <url>
    !info user <user name>
    !info image <image name>
    !listall
    !top
    !random
    !me_irl
Code available on request.
'''

class Image:
    def __init__(self, bot):
        self.bot = bot
        self.imgur = imgurpython.ImgurClient(client_id, client_secret)
        self.times = []
        self.open_list()

    #returns a smiley
    @commands.command(pass_context=True, no_pm=True)
    async def s(self, ctx, key: str):
        key = '!' + key
        if key in self.list:
            await self.bot.say(self.list[key].get('imgur_url'))
            self.record_data(key)

    #returns bot info / help
    @commands.command()
    async def botinfo(self):
        await self.bot.say(description)

    #returns info on an image or user
    @commands.command(pass_context=True, no_pm=True)
    async def info(self, ctx, option: str=None, key: str=None):
        if not option:
            await self.bot.say('''Syntax error, try:
                !info user <user>
                !info image <image>
                ''')
        elif not key:
            await self.bot.say('''Syntax error, try:
                !info user <user>
                !info image <image>
                ''')

        if option == 'user':
            count = 0
            for image in self.list:
                if self.list[image].get('user', None) == key:
                    count += 1
            await self.bot.say('User ' + key + ' has added ' + str(count) + ' images.')

        if option == 'image':
            if ' ' in key:
                return
            if key.startswith('"') or key.startswith('<'):
                key = key[1:-1]
            if not key[0] == '!':
                key = '!' + key
            key = key.casefold()
            if not key in self.list:
                await self.bot.say('No image named "' + key + '" exists.')
            else:
                await self.bot.say('Info for smiley "' + key +
                           '"\nImgur URL: ' + self.list[key].get('imgur_url', '') +
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
            message = message + ' ' + key
        #character limits means we gotta do a thing
        uplimit = len(message) + 2000 // 2 // 2000
        await self.bot.say('List of all Smileys:')
        for i in range(1,uplimit):
            await self.bot.say(message[(i*2000-2000):(i*2000)])

    #lists top smileys
    @commands.command()
    async def top(self):
        top = []
        for key in self.list:
            top.append((int(self.list[key]['count']), key))
        top.sort()
        message = 'Top 10 Smileys:'
        for i in range(1,11):
            message = message + '\n' + str(i) + '. ' + top[-i][1] + ' (' + str(top[-i][0]) + ')'
        await self.bot.say(message)

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
