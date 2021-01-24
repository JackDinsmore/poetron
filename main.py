import discord, os, sys
import poetrylib as pl

COLOR=discord.Colour.light_gray()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    pl.init()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!poetron '):
        command = message.content[9:].lower().split(' ')
        while '' in command:
            command.remove('')
        if len(command) == 0:
            await message.channel.send(embed=discord.Embed(color=COLOR, description="What's up, chief? Type `!poetron help` for documentation."))
        
        elif command[0] == 'help' and len(command) == 1:
            await message.channel.send(embed=discord.Embed(color=COLOR, description="""Hiya, chief. Have some documentation.
This bot reads your messages and points out any accidental poetry you write.
It expresses short syllables as `u` and long ones as `-`.
- `!poetron stresses [args]`: give the stress pattern on each word in args.
- `!poetron ls`: list the meters available to Poetron
- `!poetron rm`: (reversibly) remove an item from the list of meters Poetron understands
- `!poetron add`: reinstate an item from the list of meters Poetron understands
- `!poetron help [meter]`: explain the meter [meter] (see `!poetron ls` for meter types)
- `!poetron example [meter]`: give an example of the meter [meter] (see `!poetron ls` for meter types)
- `!poetron shutdown`: shut down Poetron."""))
        
        elif command[0] == 'help':
            if command[1] in pl.DESCRIPTION.keys():
                await message.channel.send(embed=discord.Embed(color=COLOR, description='**'+command[1]+'**: ' + pl.DESCRIPTION[command[1]]))
            else:
                await message.channel.send(embed=discord.Embed(color=COLOR, description="Don't know that meter, chief."))

        elif command[0] == 'stresses':
            if len(command) == 1:
                await message.channel.send(embed=discord.Embed(color=COLOR, description="Whatcha doin, chief? You gotta name at least one word to get stresses for!"))
            text = ""
            for word in command[1:]:
                text+="**"+word+"**: "
                try:
                    patterns = pl.getPatterns(word)
                    print(patterns)
                except:
                    await message.channel.send(embed=discord.Embed(color=COLOR, description="Don't know that word, chief."))
                    return
                if len(patterns) == 1:
                    text += patterns[0]
                else:
                    if len(command) > 2: text += '('
                    for p in patterns:
                        text += p + ' or '
                    text = text[:-4]
                    if len(command) > 2: text += ')'
                text += '\n'
            await message.channel.send(embed=discord.Embed(color=COLOR, description=text[:-1]))


        elif command[0] == 'ls':
            text = 'Heya, chief! Use `rm` and `add` to remove and add meters to this list! You can only add ones that are struck out.\n'
            for meter, state in pl.enabled.items():
                if state:
                    text += meter + "\n"
                else:
                    text += "~~" + meter + "~~\n"
            await message.channel.send(embed=discord.Embed(color=COLOR, description=text))


        elif command[0] == 'rm':
            if len(command) == 1:
                await message.channel.send(embed=discord.Embed(color=COLOR, description="Whatcha doin, chief? You gotta name a meter to remove!"))
            else:
                for c in command[1:]:
                    if c in pl.enabled:
                        pl.enabled[c] = False
                        await message.channel.send(embed=discord.Embed(color=COLOR, description=c + " successfully removed."))
                    else:
                        await message.channel.send(embed=discord.Embed(color=COLOR, description="Whoa there chief! `"+c+"` is not a meter!"))
                pl.saveEnabled()
                pl.makeMeters()

        elif command[0] == 'add':
            if len(command) == 1:
                await message.channel.send(embed=discord.Embed(color=COLOR, description="Whatcha doin, chief? You gotta name a meter to add!"))
            else:
                for c in command[1:]:
                    if c in pl.enabled:
                        pl.enabled[c] = True
                        await message.channel.send(embed=discord.Embed(color=COLOR, description=c + " successfully added."))
                    else:
                        await message.channel.send(embed=discord.Embed(color=COLOR, description="Whoa there chief! `"+c+"` is not a meter!"))
                pl.saveEnabled()
                pl.makeMeters()

        elif command[0] == 'example':
            if len(command) == 1:
                await message.channel.send(embed=discord.Embed(color=COLOR, description="Whatcha doin, chief? You gotta name a meter to get an example for!"))
            else:
                if command[1] in pl.EXAMPLES:
                    await message.channel.send(embed=discord.Embed(color=COLOR, description='**'+command[1]+'**: ' + pl.EXAMPLES[command[1]]))
                else:
                    await message.channel.send(embed=discord.Embed(color=COLOR, description="Don't know that meter, chief."))

        elif command[0] == 'shutdown' and len(command) == 1:
            await message.channel.send(embed=discord.Embed(color=COLOR, description="Bye, chief!"))
            sys.exit()

        else:
            await message.channel.send(embed=discord.Embed(color=COLOR, description="Whoa there, chief! `"+command[0]+"` isn't a command!"))

        

    else:
        try:
            meter, text = pl.fitToMeter(message.content)
        except:
            return
        if meter != None:
            name = message.author.nick
            await message.channel.send(embed=discord.Embed(color=COLOR, description="_"+text+"_\n--"+name+" ("+meter+")"))

#client.run(os.getenv('TOKEN'))
client.run("ODAxMjU4NjIxOTgzOTE2MDYz.YAeEPg.erPGz0NIzViYm6X9QD9IMFa1H_g")