import discord,asyncio,random,TOKENS,youtube_dl,json
from discord.ext import commands
from discord.ext.commands import Bot, CommandNotFound
from discord.utils import get #it's importnat don't forget about it!
from discord import utils,FFmpegPCMAudio
from youtubesearchpython.__future__ import VideosSearch
import pafy #the best I luv u super simple library when working with youtube videos❤

intents = discord.Intents.default()
intents.members = True #making it possible for the bot to collect data about users that join or leave a server
intents.guilds = True

prefix = input("What is the prefix for the bot's commands?")
TOKEN = input("What's your bot token?(You can find it on https://discord.com/developers/applications)") 

client = commands.Bot(command_prefix=prefix,intents=intents) #setting the prefix for the bot's commands
 
FFmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}
g_list = {}
status = ["Sleeping","Eating my dev's ram :3",'Searching for friends <3','For help type &h!']

ydl_opts = {'format': 'bestaudio'}

@client.event
async def on_ready():
    print("Bot loaded succesfully!")
    print(f"-------\n{client.user.name}\n-------")
    global usrs_bal
    usrs_bal = json.load(open('economy_data_base.json','r')) #loading the users balances
    global wrnd_user
    wrnd_user = json.load(open('wrnd.json','r')) #getting the warned users 
    global g_words
    g_words = json.load(open('words.json','r')) #getting the censored words on specific servers 
    while True:
        await client.change_presence(activity=discord.Game(random.choice(status))) 
        await asyncio.sleep(600)

@client.event
async def on_member_join(member):
    pass #empty for now but you can use it for greeting a new member like sending them a dm or creating a greetings channel and maybe add verfication etc.

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound): 
        await ctx.send("Command not found for help type &h!")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You lack the permission to use that command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("There is a missing argument in the command!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("There is a mistake in the arguments of the coammand,check it and try again!")

@client.command(name='say',help='Make me say something!')
async def say(ctx, *,msg):
    await ctx.send(msg)

@client.listen('on_message')
async def msg_filter(message):
    msg = message.content
    if isinstance(message.channel, discord.channel.DMChannel):
        pass
    else:
        if message.guild.id in g_words and any(word in msg.split() for word in g_words[message.guild.id]):
            if msg.startswith(f'{prefix}badwordadd') or msg.startswith(f'{prefix}badwordremove') or msg.startswith(f'{prefix}bwadd') or msg.startswith(f'{prefix}bwrem'):
                pass  
            else:
                await message.channel.send("A bad word was censored!")
                await message.delete()
        else:
            pass

@client.command(name='ping', help='Retruns the clinet latency',aliases=['p'])
async def ping(ctx):
    await ctx.send(f"{ctx.author.mention}Ping:{round(client.latency * 1000)}ms")

@client.command(name='hello', help='This command returns a random welcome message')
async def hello(ctx):
    responses = ['***grumble*** Why did you wake me up?', 'Top of the morning to you lad!', 'Hello, how are you?', 'Hi',
                 '**Wasssuup!**','**Whadya doin?**']
    await ctx.send(random.choice(responses))

@client.command(name='die', help='Well goodbye cruel world')
async def die(ctx):
    responses = ["why have you brought my short life to an end", "i could have done so much more",
                 "i have a family, kill them instead","why have you forsaken me?","It's,it's getting darker..."
                 "you are so cruel!","I wanted to do so much!"]
    await ctx.send(random.choice(responses)) 

@client.command(name='clear',help='Clears the given number of messages',aliases=['cl'])
async def clear(ctx,*,amount):
    r_amount = int(amount) + 1
    if int(amount) == 1:
        await ctx.channel.purge(limit=int(r_amount))
        await ctx.send(f"Succesfully deleted {amount} message!")
    elif int(amount) > 30:   
        await ctx.send(f"Woah slow down you get to delete only 30 messages at a time!")
    else:
        await ctx.channel.purge(limit=int(r_amount))
        await ctx.send(f"Succesfully deleted {amount} messages!")

def search(arg):
    if arg.startswith('https://www.youtube.com'):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(arg, download=False)
    else:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        
    return {'audio_source': info['formats'][0]['url'], 'video_url' : info['webpage_url']}

def play_next(ctx):
    if ctx.guild.id in g_list and len(g_list.get(ctx.guild.id)[0]) >= 1:
        data = g_list.get(ctx.guild.id)
        sauces = data[0]
        links = data[1]
        del sauces[0]
        del links[0]
        voice = get(client.voice_clients, guild=ctx.guild)
        if len(sauces) >= 1:
            voice.play(discord.FFmpegPCMAudio(source = sauces[0], **FFmpeg_opts), after=lambda e: play_next(ctx))
            voice.is_playing()
        else:
            return
    else:
        pass

@client.command(name='join',help='This command makes the bot join the voice channel',pass_context=True,aliases=['j'])
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel!")
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()

@client.command(name='playt',help='Plays a video from youtube you can a link or keywords to find the video!',aliases=['plyt'])
async def playt(ctx, *,arg = None):
    if not ctx.message.author.voice:
        await ctx.send("Join a voice channel first!")
    elif ctx.message.author.voice:
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)
        song = search(arg)
        sauce = song['audio_source']
        link = song['video_url']
        if ctx.guild.id in g_list:
            data = g_list.get(ctx.guild.id)
            sauc = data[0]
            links = data[1]
            sauc.append(sauce)
            links.append(link)
        else:
            sauc = []
            sauc.append(sauce)
            links = []
            links.append(link)
            gid = []
            gid.append(sauc)
            gid.append(links)
            g_list[ctx.guild.id] = gid

        data = g_list.get(ctx.guild.id)
        sauces = data[0]
        video = pafy.new(link)
        rating = video.rating
        rating = str(rating)[:4]
        embed=discord.Embed(title= str(video.author), color=0x23a5dc)
        embed.set_thumbnail(url= str(video.bigthumbhd))
        embed.add_field(name=str(video.title),          value='Great choice!',            inline=False)
        embed.add_field(name=":eye:View count:",        value=str(video.viewcount),        inline=True)
        embed.add_field(name=":clock9:Video duration:", value=str(video.duration),         inline=True)
        embed.add_field(name=":star2:Overall rating: ", value=f"{rating}:star:/5.00:star:",inline=True)
        embed.add_field(name='Postion in queue: ',      value=len(sauces),                 inline=True)
        embed.set_footer(text=f"Requested by: {ctx.message.author}")
        await ctx.send(embed=embed)
        
        if voice and voice.is_connected():
            await voice.move_to(channel)
        elif voice == ctx.message.author.voice:
            return
        else: 
            voice = await channel.connect()

        if not voice.is_playing():
            voice.play(discord.FFmpegPCMAudio(source = sauce, **FFmpeg_opts),after=lambda e: play_next(ctx))
            while voice.is_playing():
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(300)
                if voice.is_playing():
                    return
                elif voice.is_connected():
                    data = g_list.get(ctx.guild.id)
                    sauces = data[0]
                    links = data[1]
                    for i in range(len(sauces)):
                        del sauces[0]
                        del links[0]
                    embed=discord.Embed(title=':musical_note: The bot was innactive for quite some time!', description='The bot disconnected beacause of innactivity!')
                    await ctx.send(embed=embed)
                    await voice.disconnect()
        else:
            await ctx.send(f"*{str(video.title)}* was added to the queue!")
    else:
        await ctx.send("Join a voice channel first!")

def check(ctx):
    author = ctx.author
    def inner_check(message): 
        if message.author != author:
            return False
        try:
            int(message.content)
            return True
        except ValueError:
            return False
    return inner_check

@client.command(name='ytsearch',help='Use this command to search for videos on youtube!',aliases=['ytsrc'])
async def ytsearch(ctx,*,msg=None):
    if msg == None:
        await ctx.send("You aren't searching for anything try to type in te key words!")
    else:
        t = []
        l = []
        src = VideosSearch(msg, limit = 5)
        src = await src.next()
        results = src.get('result')
        embed=discord.Embed(title=f"Results for {msg}!", color=0xff8000)
        for i in range(len(results)):
            embed.add_field(name=f"Video №{i+1}:{results[i].get('title')}, author:{results[i].get('channel').get('name')}",value=f"Link: {results[i].get('link')}", inline=False)
            t.append(results[i].get('title'))
            l.append(results[i].get('link'))
        embed.set_footer(text="Type a number ex:1,2,3 etc. to choose from the list!")
        await ctx.send(embed=embed)
        
        try:
            mesg = await client.wait_for('message', check=check(ctx),timeout=(35))
            n = mesg.content
        except asyncio.TimeoutError:
            await ctx.send("Timed out!")
            return False

        if not ctx.message.author.voice:
            await ctx.send("Join a voice channel first!")
        elif ctx.message.author.voice:
            voice = get(client.voice_clients, guild=ctx.guild)
            song = search(l[int(n)-1])
            sauce = song['audio_source']
            link = song['video_url']
            if ctx.guild.id in g_list:
                data = g_list.get(ctx.guild.id)
                sauc = data[0]
                links = data[1]
                sauc.append(sauce)
                links.append(link)
            else:
                sauc = []
                sauc.append(sauce)
                links = []
                links.append(link)
                gid = []
                gid.append(sauc)
                gid.append(links)
                g_list[ctx.guild.id] = gid

            data = g_list.get(ctx.guild.id)
            sauces = data[0]
            video = pafy.new(link)
            rating = video.rating
            rating = str(rating)[:4]
            embed=discord.Embed(title= str(video.author), color=0x23a5dc)
            embed.set_thumbnail(url= str(video.bigthumbhd))
            embed.add_field(name=str(video.title),          value='Great choice!',            inline=False)
            embed.add_field(name=":eye:View count:",        value=str(video.viewcount),        inline=True)
            embed.add_field(name=":clock9:Video duration:", value=str(video.duration),         inline=True)
            embed.add_field(name=":star2:Overall rating: ", value=f"{rating}:star:/5.00:star:",inline=True)
            embed.add_field(name='Postion in queue: ',      value=len(sauces),                 inline=True)
            embed.set_footer(text=f"Requested by: {ctx.message.author}")
            await ctx.send(embed=embed)
            channel = ctx.message.author.voice.channel
            if voice and voice.is_connected():
                await voice.move_to(channel)
            elif voice == ctx.message.author.voice:
                return
            else: 
                voice = await channel.connect()

            if not voice.is_playing():
                voice.play(discord.FFmpegPCMAudio(source = sauce, **FFmpeg_opts),after=lambda e: play_next(ctx))
                while voice.is_playing():
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(300)
                    if voice.is_playing():
                        return
                    elif voice.is_connected():
                        data = g_list.get(ctx.guild.id)
                        sauces = data[0]
                        links = data[1]
                        for i in range(len(sauces)):
                            del sauces[0]
                            del links[0]
                        embed=discord.Embed(title=':musical_note: The bot was innactive for quite some time!', description='The bot disconnected beacause of innactivity!')
                        await ctx.send(embed=embed)
                        await voice.disconnect()
            else:
                await ctx.send(f"*{str(video.title)}* was added to the queue!")
        else:
            await ctx.send("Join a voice channel first!")

@client.command(name='skip',help='Skips the current song!')
async def skip(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.author.mention}Connect to a voice channel first!")
        return
    else:
        server = ctx.message.guild.voice_client
        if ctx.guild.id in g_list and len(g_list.get(ctx.guild.id)[0]) > 1:
            data = g_list.get(ctx.guild.id)
            links = data[1]
            video = pafy.new(links[0])
            await ctx.send(f"{video.title} was skipped by {ctx.author.mention}")
            await server.stop()
            play_next(ctx)
        else:
            await ctx.send("Hey there are no more songs! Add some more to the queue to skip!")

@client.command(name='queue',help='Shows the list of the song that will be played',aliases=['q'])
async def queue(ctx):
    if ctx.guild.id in g_list and len(g_list.get(ctx.guild.id)[0]) >= 1:
        data = g_list.get(ctx.guild.id)
        links = data[1]
        embed=discord.Embed(title="The list of songs to be played:",color=0x00ff40)
        for i in range(len(links)):
            link = links[i]
            video = pafy.new(link)
            embed.add_field(name=f'**{i+1}.**', value=video.title,inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Add some songs first to see the queue!')

@client.command(name='queue_clear',help='Clears the current queue of songs!',aliases=['qcl'])
async def qclear(ctx):
    if ctx.guild.id in g_list and len(g_list.get(ctx.guild.id)[0]) >= 1:
        data = g_list.get(ctx.guild.id)
        sauces = data[0]
        links = data[1]
        for i in range(len(sauces)):
            del sauces[0]
            del links[0]
        await ctx.send(f"Cleared {len(sauces) + 1} songs from queue!")
    else:
        await ctx.send('There are no songs that can be cleared from the queue!')

@client.command(name='queue_remove',help="Removes a song from the queue by specifiyng it's position in queue!",aliases=['qrem'])
async def qremove(ctx,*,q_pos):
    q_pos = int(q_pos) - 1
    if ctx.guild.id in g_list and len(g_list.get(ctx.guild.id)[0]) >= 1:
        if q_pos < 0:
            await ctx.send("Invalid queue postion! (Don't set the postion of the song that you want to remove to 0 or below)")
        elif q_pos == 0:
            await ctx.send("Hey you can't remove the song that is being played now!") 
        else:
            data = g_list.get(ctx.guild.id)
            sauces = data[0]
            links = data[1]
            link = links[q_pos] 
            video = pafy.new(link)
            del links[q_pos]
            del sauces[q_pos]
            await ctx.send(f"Succesfully removed {video.title} - on the position {int(q_pos) + 1} from the queue!")
    else:
        await ctx.send("There are no songs in the queue,add some first to manipulate the queue!")
        
@client.command(name='leave',help='This command makes the bot leave the channel',pass_context=True,aliases=['l'])
async def leave(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await ctx.send(f"The bot isn't connected to a vc!")
    else:
        await voice.disconnect()

@client.command(name='pause',help='This command makes the bot pause the audio',pass_context=True,aliases=['pa'])
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await ctx.send("The bot isn't connected to a vc!")
    elif voice.is_playing():
        await voice.pause()
    else:
        await ctx.send("The bot isn't playing anything!")

@client.command(name='resume',help='This command makes the bot resume playing the audio',pass_context=True,aliases=['re'])
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await ctx.send("The bot isn't connected to a vc!")
    elif not voice.is_playing():
        await voice.resume()
    else:
        await ctx.send("The bot is already playing smthing or isn't connected to a vc!")

@client.command(name='stop',help='This command makes the bot stop playing the audio',pass_context=True)
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await ctx.send("The bot isn't connected to a vc!")
    elif voice.is_playing():
        await voice.stop()
    else:
        await ctx.send("The bot isn't playing anything!")

@client.command(name='playing',help='Shows the song that is currnetly being played!',aliases=['plng'])
async def playing(ctx):
    if ctx.guild.id in g_list and len(g_list.get(ctx.guild.id)[0]) >= 1:
        data = g_list.get(ctx.guild.id)
        links = data[1]
        video = pafy.new(links[0])
        await ctx.send(f"Currnetly playing *{video.title}*!")
    else:
        await ctx.send("The song queue is empty!")

def wrnsave():
    json.dump(wrnd_user, open('wrnd.json','w'))

@client.command(name='warn',help='Warning if a user has done smthing wrong,if the user gets 3 warns he gets kicked automaticaly',aliases=['wr'])
async def warn(ctx, user: discord.Member, *, reason='the user was warned'):
    usr_gld = str(ctx.guild.id) + str(user.id)
    if usr_gld in wrnd_user:
        if wrnd_user[usr_gld] == 1:
            wrnd_user[usr_gld] = 2
            await ctx.send(f"The user {user.mention} has been warned by {ctx.author.mention},reason: {reason}!")
        elif wrnd_user[usr_gld] == 2:
            await ctx.send(f"The user {user.mention} has been warned by {ctx.author.mention},reason: {reason}!")
            await ctx.send(f"The user {user.mention} got 3 warns kicking this bastard from the server...")
            await user.kick(reason="You got 3 warns so you got kicked!")
            del wrnd_user[usr_gld]
    else:
        wrnd_user[usr_gld] = 1
        await ctx.send(f"The user {user.mention} has been warned by {ctx.author.mention},reason: {reason}!")
    wrnsave()

def words_save():
    json.dump(g_words, open('words.json','w'))

@client.command(name='badwordadd',help='Add a word that will be automaticaly deleted!',aliases=['bwadd'])
async def badwordadd(ctx,*,word):
    gd = str(ctx.guild.id)
    if gd in g_words:
        data = g_words.get(gd)
        data.append(word)
    else:
        g_id = []
        g_id.append(word)
        g_words[gd] = g_id
    await ctx.send("The list of forbidden words has been updated!")
    words_save()

@client.command(name='badwordremove',help='Remove a word from the list of censored words!',aliases=['bwrem'])
async def badwordremove(ctx,*,word):
    gd = str(ctx.guild.id)
    if gd in g_words:
        data = g_words.get(gd)
        if word in data:
            print(3)
            for i in range(len(data)):
                if data[i] == word:
                    del data[i]
                    await ctx.send(f'The word {word} has been succesfully removed!')
                    break
                else:
                    pass
        else:
            await ctx.send(f"The word {word} is not in the list of forbidden words!")
    else:
        await ctx.send("The list of forbidden words is empty, add some words first to interact with the list!")
    words_save()

@client.command(name='badwordslist',help='The bot will dm you displaying the list of forbidden words on the server!',aliases=['bwl'])
async def badwordslist(ctx):
    gd = str(ctx.guild.id)
    if gd in g_words and len(g_words.get(gd)) >= 1:
        await ctx.author.send(f"The list of words forbidden on {ctx.guild.name}:")
        for item in g_words.get(gd):
            await ctx.author.send(f"'{item}'")
    else:
        await ctx.send("There are no forbidden words on this server!")

@client.command(name='badwordslistclear',help='Clears the current list of censored words on a server!',aliases=['bwlc'])
async def badwordslistclear(ctx):
    gd = str(ctx.guild.id)
    if gd in g_words and len(g_words.get(gd)) >= 1:
        for i in range(len(g_words.get(gd))):
            del g_words.get(gd)[0]
        await ctx.send(f"Succesfully cleared {i} words from the list!")
    else:
        await ctx.send("There are no forbidden words on this server!")
    words_save()

@client.command(name='pardon',help='Removes all the warns from a user,if he has any!')
async def pardon(ctx, user: discord.Member):
    usr = str(ctx.guild.id) + str(user.id)
    if usr in wrnd_user:
        await ctx.send(f"Lucky you {user.mention} you've been pardoned by {ctx.author.mention}!\nPreviously {user.mention} had {wrnd_user.get(usr)} warn/warns!")
        del wrnd_user[usr]
    else:
        await ctx.send(f"Hey {ctx.author.mention} dumbass {user.mention} doesn't have any warns!")
    wrnsave()

@client.command(name='kick', help='Kicks a member just mention him/her specify a reason if you want!',aliases=['kk'])
async def kick(ctx, user: discord.Member, *, reason="You have been kicked!"):
    await ctx.send(f"User {user.mention} has been succesfully kicked by {ctx.author.mention},reason: {reason}!")
    await user.kick(reason=reason)
    usr = str(ctx.guild.id) + str(user.id)
    if usr in wrnd_user:
        del wrnd_user[usr]
    else:
        pass
    wrnsave()

@client.command(name='ban', help="Bans a member you can specify a reason (optional) just don't forget to mention him/her")
async def ban(ctx, user: discord.Member, *,reason="The ban hammer has spoken"):
    await ctx.send(f"The member {user.mention} has been banned by {ctx.author.mention},reason: {reason}!")
    await user.ban(reason=reason)
    usr = str(ctx.guild.id) + str(user.id)
    if usr in wrnd_user:
        del wrnd_user[usr]
    else:
        pass
    wrnsave()

def save():
    json.dump(usrs_bal, open('economy_data_base.json','w'))

def open_account(user):
    if user in usrs_bal:
        pass
    else:
        usrs_bal[user] = '150'
    save()

def open_account2(user,user2):
    if user and user2 in usrs_bal:
        pass
    elif user in usrs_bal and user2 not in usrs_bal:
        usrs_bal[user2] = '150'
    elif user2 in usrs_bal and user not in usrs_bal:
        usrs_bal[user] = '150'
    else:
        usrs_bal[user] = '150'
        usrs_bal[user2] = '150'
    save()

@client.command(name='balance',help='See how much money do you,or your friends have!',aliases=['bal'])
async def balance(ctx,user: discord.Member=None):
    if user == None:
        user = ctx.author
    else:
        pass
    usr = str(user.id) + str(ctx.guild.id)
    open_account(usr)
    bal = usrs_bal.get(usr)
    embed=discord.Embed(title=f'{user.name} has got {bal}₽!',color=0x23a5dc)
    embed.set_author(name="Balance", icon_url=user.avatar_url)
    embed.set_thumbnail(url="https://i.imgur.com/apq7TAO.png")
    await ctx.send(embed=embed)
    save()

@client.command(name='give',help='Do you feel generous today?You can give some money to a user!')
async def give(ctx, user:discord.Member, amount):
    usr = str(ctx.author.id) + str(ctx.guild.id)
    usr_gv = str(user.id) + str(ctx.guild.id)
    open_account2(usr,usr_gv)
    usr_bal = usrs_bal.get(usr)
    usr2_bal = usrs_bal.get(usr_gv)
    if user.id == ctx.author.id:
        await ctx.send("You can't give money to urself!")
    elif user.id == TOKENS.BOT_ID:
        await ctx.send("Really nice of you,but you can't give money to me!")
    else:
        if int(amount) > int(usr_bal):
            await ctx.send("You don't have enough money!")
        elif int(amount) <= 0:
            await ctx.send("You have to give at least smthing,enter a valid amount of money!")
        else:
            usrs_bal[usr] = int(usr_bal) - int(amount)
            usrs_bal[usr_gv] = int(usr2_bal) + int(amount)
            await ctx.send(f"You gave {amount}$ to {user}!")
    save()

@client.command(name='fish',help='Fish for some money!',aliases=['fi'])
async def fish(ctx):
    usr = str(ctx.author.id) + str(ctx.guild.id)
    open_account(usr)
    bal = usrs_bal.get(usr)
    amount = random.randrange(1,100)
    usrs_bal[usr] = int(bal) + amount
    await ctx.send(f"You got {amount}$ from fishing!")
    save()

@client.command(name='bet',help='I flip a coin,you bet on what will it land (heads or tails) if you win you get double the money you have bet!If you lose I get the amount of money you have bet:3')
async def bet(ctx,guess,amount):
    usr = str(ctx.author.id) + str(ctx.guild.id)
    open_account(usr)
    bal = usrs_bal.get(usr)
    if int(amount) > int(bal):
        await ctx.send("You are too poor for this!")
    else:
        randomize = random.randrange(1,3)
        if randomize == 1:
            rand = 'heads'
        else:
            rand = 'tails' 
        if rand == str(guess):
            usrs_bal[usr] = bal + int(amount)*2
            await ctx.send(f"Yay the coin landed on the {rand}!")
        else:
            usrs_bal[usr] = bal - int(amount)
            await ctx.send(f"Sorry the coin landed on the {rand}!")
    save()

@client.command(name='roll',help='Rolls a random number beetween 6 or 8 or 10 or 12',aliases=['r'])
async def roll(ctx,rols):
    num = random.randrange(1,int(rols)+1)
    if num == 1 or num == 8 or num == 11:
        a = 'an'
    else:
        a = 'a'
    await ctx.send(f"{ctx.author.mention} rolled {a} {num}!")

@client.command(name='kiss',help='Kiss someone!',aliases=['ks'])
async def kiss(ctx, user: discord.Member):
    if user.id == TOKENS.BOT_ID:
        await ctx.send(f"{ctx.author.mention} thx I really liked that!")
        await ctx.send(random.choice(TOKENS.e_kiss))
    elif user.id == ctx.author.id:
        await ctx.send(f"You kissed yourself to much self-loving here!")
        await ctx.send(random.choice(TOKENS.e_kiss))
    else:
        await ctx.send(f"{ctx.author.mention} just kissed {user.mention}!")
        await ctx.send(random.choice(TOKENS.e_kiss))

@client.command(name='kill',help="Hey it's bad to kill people!",aliases=['kl'])
async def kill(ctx, user: discord.Member):
    rr = [f"{ctx.author.mention} just wiped out {user.mention}'s soul from this universe!",f"{ctx.author.mention} is going on a rampage killing {user.mention}!",f"{ctx.author.mention} dezintegrated {user.mention}!"]
    if user.id == TOKENS.BOT_ID:
        await ctx.send(f"{ctx.author.mention} is this the end of my robotic life?")
        await ctx.send(random.choice(TOKENS.e_kill))
    elif user.id == ctx.author.id:
        await ctx.send(f"{ctx.author.mention} suicide is bad!")
        await ctx.send(random.choice(TOKENS.e_kill))
    else:
        await ctx.send(random.choice(rr))
        await ctx.send(random.choice(TOKENS.e_kill))

@client.command(name='roleadd', help='Adds a role to a member', aliases=['rlad'], pass_context = True)
async def rladd(ctx, user: discord.Member, *,role):
    r = discord.utils.get(ctx.guild.roles, name=str(role))
    if str(user) == str(client.user):
        await ctx.send(f"Hey you can't manage my roles!")
    else:
        if r in ctx.guild.roles:
            if r in user.roles:
                await ctx.send(f"{ctx.author.mention} the user:{user} already has the '{role}' role!")
            else:
                await user.add_roles(r)
                await ctx.send(f"{user.mention} got the role {role} from {ctx.author.mention}")
        else:
            await ctx.send(f"{ctx.author.mention},the role '{role}' doesn't exist!")

@client.command(name='roleremove', help='Removes a role from a member', aliases=['rlrem'],pass_context = True)
async def rlremove(ctx, user: discord.Member, *,role):
    r = discord.utils.get(ctx.guild.roles, name=str(role))
    if str(user) != str(client.user):
        if r in ctx.guild.roles:
            if r in user.roles:
                await user.remove_roles(r)
                await ctx.send(f"{user.mention} haha you lost the role '{role}',because of {ctx.author.mention}!")
            else:
                await ctx.send(f"{ctx.author.mention},you dummy :{user} does not posses the role '{role}',stop wasting my time!")
        else:
            await ctx.send(f"The role '{role}' does not exist!\n{ctx.author.mention} use your fingers and type what you meant properly!")
    else:
        await ctx.send(f"Hey arsehole {ctx.author.mention} are you stupid or what? You can't manage my roles you creep!")

@client.command(name='h',help='Shows a detalized list of commands and their purpose')
async def h(ctx):
    embed=discord.Embed(title="The list of working commands for the bot  page:1/2",                                                                                                                                       color=0xdd1d1d)
    embed.add_field(name=f"{prefix}join",       value="Makes the bot join the voice channel!",                                                                                                                            inline=False) 
    embed.add_field(name=f"{prefix}playt",      value="Plays a video from youtube from a given link or keywords!",                                                                                                        inline=False)
    embed.add_field(name=f"{prefix}ytsearch",   value="Shows a list of videos from given keywords choose something by typing 1,2,3 etc. in chat, use it:'&ytsrc keywords here',for direct play we recommend using playt!",inline=False)
    embed.add_field(name=f"{prefix}playing",    value="Shows the title of the song that is being played!",                                                                                                                inline=False)
    embed.add_field(name=f"{prefix}skip",       value="Skips the currnet song and plays the next in the queue!",                                                                                                          inline=False)
    embed.add_field(name=f"{prefix}queue",      value="Shows the list of the song that will be played soon!",                                                                                                             inline=False)
    embed.add_field(name=f"{prefix}qclear",     value="Clears the currnet queue of songs - Sometimes a bug may occur when playing an audio to fix it make the bot leave the voice channel then clear the queue!",         inline=False)
    embed.add_field(name=f"{prefix}leave",      value="Makes the bot leave the voice channel that it's connected to!",                                                                                                    inline=False)
    embed.add_field(name=f"{prefix}ping",       value="Shows the client latency!",                                                                                                                                        inline=False)
    embed.add_field(name=f"{prefix}warn",       value="Warns a user if he gets 3 warns he gets automaticaly kicked,you can specify the warn reason(optional)",                                                            inline=False)
    embed.add_field(name=f"{prefix}pardon",     value="Pardons a user by removing all of his current warns!",                                                                                                             inline=False)
    embed.add_field(name=f"{prefix}kick",       value="Kicks a user from the server!",                                                                                                                                    inline=False)
    embed.add_field(name=f"{prefix}ban",        value="Bans a user from the server!",                                                                                                                                     inline=False)
    embed.add_field(name=f"{prefix}say",        value="What do I say?",                                                                                                                                                   inline=False)
    embed.set_footer(text="For page 2 of commands type &h2!")
    await ctx.send(embed=embed)

@client.command(name='h2',help='Shows the 2nd sheet of the list of commands and their purpose!')
async def h2(ctx):
    embed=discord.Embed(title="The list of working commands for the bot page:2/2",                                                                                                                                                    color=0xdd1d1d)
    embed.add_field(name=f"{prefix}clear",            value="Use '&clear (number of messages you want to delete)' to clear this number of messages!",                                                                                  inline=False)
    embed.add_field(name=f"{prefix}balance",          value="Check how money do you have in your purse!",                                                                                                                              inline=False)
    embed.add_field(name=f"{prefix}fish",             value="Go fishing and maybe you'll find some sweet money!",                                                                                                                      inline=False)
    embed.add_field(name=f"{prefix}bet",              value="Use $bet (head or talis) (amount of money) to flip a coin that can land on heads or tails if your guess is correct you get double the amount of money that you have bet!",inline=False)
    embed.add_field(name=f"{prefix}give",             value="You can give some money to a user using &give (user) (amount of money)!",                                                                                                 inline=False)
    embed.add_field(name=f"{prefix}roll",             value="Use '&roll (6,8,10,12)' to roll a random number from 1 to the chosen number!",                                                                                            inline=False)
    embed.add_field(name=f"{prefix}help",             value="Shows the list of commands and their functions in a less detalized variant then &h!",                                                                                     inline=False)
    embed.add_field(name=f"{prefix}kiss",             value="Shows a random anime kiss gif! ",                                                                                                                                         inline=False)
    embed.add_field(name=f"{prefix}kill",             value="Sends some kinda anime kill gif!",                                                                                                                                        inline=False)
    embed.add_field(name=f"{prefix}roleadd",          value="Use this command and then mention an user and a role to add a role to an user!",                                                                                          inline=False)
    embed.add_field(name=f"{prefix}roleremove",       value="Use this command and then mention an user and a role to remove a role from an user!",                                                                                     inline=False)
    embed.add_field(name=f"{prefix}badwordadd",       value="Adds a word/expression to a list.that will be automatically removed from chat!",                                                                                          inline=False)
    embed.add_field(name=f"{prefix}badwordremove",    value="Removes a word/expression from the list.Warning the word/expression will no longer be automaticaly removed from chat!",                                                   inline=False)
    embed.add_field(name=f"{prefix}badwordslist",     value="Dms the author of the message,displaying the current list of forbidden words on the server!",                                                                             inline=False)
    embed.add_field(name=f"{prefix}badwordslistclear",value="Warning deletes the wholes list of words/expressions from the general database.So these words/expressions will no longer be auto deleted from chat!",                     inline=False)
    embed.set_footer(text="To see shortcuts of all the commands type &s!")
    await ctx.send(embed=embed)

@client.command(name='s',help='Shows shortcuts for the commands that are available')
async def s(ctx): 
    embed=discord.Embed(title="The list of working shortcuts for the commands!", color=0xff8000)
    embed.add_field(name=f"{prefix}ping",             value="&p",        inline=True)
    embed.add_field(name=f"{prefix}join",             value="&j",        inline=True)
    embed.add_field(name=f"{prefix}playt",            value="&plyt",     inline=True)
    embed.add_field(name=f"{prefix}ytsearch",         value="&ytsrc",    inline=True)
    embed.add_field(name=f"{prefix}playing",          value="&plyng",    inline=True)
    embed.add_field(name=f"{prefix}leave",            value="&l",        inline=True)
    embed.add_field(name=f"{prefix}queue",            value="&q",        inline=True)
    embed.add_field(name=f"{prefix}qclear",           value="&qcl",      inline=True)
    embed.add_field(name=f"{prefix}qremove",          value="&qrem",     inline=True)
    embed.add_field(name=f"{prefix}pause",            value="&pa",       inline=True)
    embed.add_field(name=f"{prefix}resume",           value="&re",       inline=True)
    embed.add_field(name=f"{prefix}stop",             value="&st",       inline=True)
    embed.add_field(name=f"{prefix}warn",             value="&wr",       inline=True)
    embed.add_field(name=f"{prefix}kick",             value="&kk",       inline=True)
    embed.add_field(name=f"{prefix}balance",          value="&bal",      inline=True)
    embed.add_field(name=f"{prefix}fish",             value="&fi",       inline=True)
    embed.add_field(name=f"{prefix}roll",             value="&r",        inline=True)
    embed.add_field(name=f"{prefix}clear",            value="&cl",       inline=True)
    embed.add_field(name=f"{prefix}kiss",             value="&ks",       inline=True)
    embed.add_field(name=f"{prefix}kill",             value="&kl",       inline=True)
    embed.add_field(name=f"{prefix}rladd",            value="&rlad",     inline=True)
    embed.add_field(name=f"{prefix}rlremove",         value="&rlrem",    inline=True)
    embed.add_field(name=f"{prefix}badwordadd",       value="&bwadd",    inline=True)
    embed.add_field(name=f"{prefix}badwordremove",    value="&bwrem",    inline=True)
    embed.add_field(name=f"{prefix}badwordslist",     value="&bwl",      inline=True)
    embed.add_field(name=f"{prefix}badwordslistclear",value="&bwlc",     inline=True)
    embed.set_footer(text="For help type &h!")
    await ctx.send(embed=embed)

client.run(TOKEN)