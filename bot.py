import discord
from discord import app_commands
from discord.ext import commands
import pandas as pd
import logging
from dotenv import load_dotenv
import os
from processing import datamanager as datman
from api import client
import requests as req
import json
from datetime import datetime

dm = datman.Datamanager()
cl = client.APIManager()

load_dotenv()
API_TOKEN = os.getenv("COC_API_TOKEN")
header = {"Authorization" : f"Bearer {API_TOKEN}"}
token = os.getenv('DISCORD_TOKEN')
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding='utf-8', mode='w')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
ALLOWED_GUILDS = {491691533461094416, 573374059052531712}

class CrewManager(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="/", intents=intents)
        self.members = dm.readFile("Tracked Members")
        self.clans = dm.readFile("Tracked Clans")
    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands synced with Discord")
        
bot = CrewManager()

@bot.event
async def on_ready():
    print(f"We are ready to go")

def search_clan(eingabe):
        eingabe = eingabe.strip()
        eingabe = eingabe.replace("#", "%23")
        url = f"{cl.baseUrl}clans?name={eingabe}"
        response = req.get(url, headers= header)
        if response.status_code == 200:
            data = response.json()
            clans = data["items"]
            return clans
        else:
            return []
        
async def clan_autocomplete(interaction: discord.Interaction, clan: str):
    if clan:
        clans = search_clan(clan)
        choices = []
        for clan in clans[:10]:
            choices.append(app_commands.Choice(name = f"{clan['name']} | {clan['tag']} | Lvl. {clan['clanLevel']}", value = f"{clan["tag"]}"))
        return choices
    return []
            
async def clan_remove_autocomplete(interaction: discord.Interaction, clan: str):
    clans = bot.clans
    print(clans)
    choices = []
    for idx, row in clans.iterrows():
        if row["clanname"].lower().startswith(clan.lower()):
            choices.append(app_commands.Choice(name = f"{row['clanname']} | {row['clantag']}", value = f"{row["clantag"]}"))
    return choices[:15]

#disable commands on unknown servers
@bot.check
async def only_in_allowed_guilds(ctx):
    return ctx.guild and ctx.guild.id in ALLOWED_GUILDS


#clan adder
@bot.tree.command(name = "trackclan", description="Füge einen Clan zur liste getrackter Clans hinzu")
@app_commands.describe(clan = "Clan der getrackt werden soll.")
@app_commands.autocomplete(clan = clan_autocomplete)
async def trackclan(interaction: discord.Interaction, clan: str):
    clandata = search_clan(clan)[0]
    clanname = clandata["name"]
    tag = clandata["tag"]
    existing = bot.clans[bot.clans["clantag"].astype(str) == tag]
    if existing.empty:
        bot.clans.loc[len(bot.clans)] = [clanname, tag]
        print(bot.clans)
        dm.saveToFile(bot.clans, "Tracked Clans")
        await interaction.response.send_message(f"✅{clanname} wird jetzt getrackt", ephemeral=True)
    else:
        await interaction.response.send_message(f"{clanname} wird schon getrackt.", ephemeral=True)

#clan remover
@bot.tree.command(name="untrackclan", description="Entfernt einen Clan von der Liste der getrackten Clans")
@app_commands.describe(clan= "Clan der nichtmehr getrackt werden soll")
@app_commands.autocomplete(clan = clan_remove_autocomplete)
async def untrackclan(interaction:discord.Interaction, clan: str):
    clanname = bot.clans.loc[bot.clans["clantag"].astype(str) == clan, "clanname"].iloc[0]
    bot.clans = bot.clans[bot.clans["clantag"].astype(str) != clan]
    print(bot.clans)
    dm.saveToFile(bot.clans, "Tracked Clans")
    await interaction.response.send_message(f"{clanname}|{clan} wird nichtmehr getrackt.", ephemeral=True)

#member adder
@bot.tree.command(name = "addmember",description = "adds a new member to the tracked list")
@app_commands.describe(member = "New members discord tag",playertags = "List of Members Account Tags seperated by ,")
async def addmember(interaction: discord.Interaction, member: discord.Member, playertags: str):
    tag_list = [t.strip() for t in playertags.split(",") if t.strip()]
    user_id = member.id
    username = member.name

    existing = bot.members[bot.members["user_id"].astype(int) == user_id]
    if existing.empty:
        bot.members.loc[len(bot.members)] = [user_id, username, tag_list]
        print(bot.members)
        dm.saveToFile(bot.members, "Tracked Members")
        await interaction.response.send_message(f"✅{tag_list} von {username} wird jetzt getrackt", ephemeral=True)
    else:
        await interaction.response.send_message(f"{member.mention} wird schon getrackt, wenn du die account tags ändern willst benutze das edittags kommando", ephemeral=True)
    
    

#member updater
@bot.tree.command(name = "updatemember",description = "updates the accounttags of a member")
@app_commands.describe(member = "New members discord tag",playertags = "List of Members Account Tags seperated by \",\"")
@app_commands.choices(mode = [app_commands.Choice(name="Add Tags", value=1),
                              app_commands.Choice(name="Remove Tags", value=0)])
async def updatemember(interaction: discord.Interaction, member: discord.Member, mode: app_commands.Choice[int], playertags: str):
    tag_list = [t.strip() for t in playertags.split(",") if t.strip()]
    user_id = member.id
    username = member.name

    existing = bot.members[bot.members["user_id"].astype(int) == user_id]
    if not existing.empty:
        old_tags = existing.iloc[0]["tags"]
        print(old_tags)
        if mode.value == 1:
            print(old_tags)
            new_tags = list(set(old_tags + tag_list))
            print(new_tags)
            bot.members = dm.upsert(bot.members, pd.DataFrame({"user_id": user_id, "username": username, "tags": [new_tags]}), "user_id")
            dm.saveToFile(bot.members, "Tracked Members")
            await interaction.response.send_message(f"```✅ Tags zur List von {member.name} hinzugefügt\n\ngetrackte Tags: {new_tags}```", ephemeral=True)
        else:
            new_tags = [tag for tag in old_tags if tag not in tag_list]
            print(new_tags)
            bot.members = dm.upsert(bot.members, pd.DataFrame({"user_id": user_id, "username": username, "tags": [new_tags]}), "user_id")
            dm.saveToFile(bot.members, "Tracked Members")
            await interaction.response.send_message(f"```✅ Tags aus List von {member.name} entfernt\n\ngetrackte Tags: {new_tags}```", ephemeral=True)
    else:
        await interaction.response.send_message(f"```❌ Member wird noch nicht getrackt\nBenutze addmember um {member.name} zu tracken```", ephemeral=True)
    print(bot.members)
    
#member remover
@bot.tree.command(name = "removemember", description = "removes a member from the tracked list")
@app_commands.describe(member = "member to remove")
async def removemember(interaction: discord.Interaction, member: discord.Member):
    user_id = member.id
    bot.members = bot.members[bot.members["user_id"].astype(int) != user_id]
    print(bot.members)
    dm.saveToFile(bot.members, "Tracked Members") 
    await interaction.response.send_message(f"```✅ removed {member.name} from List.```", ephemeral=True)

#display functions

#shows wich clans are currently tracked
@bot.tree.command(name = "trackedclans", description="Zeigt an welche Clans aktuell getrackt werden")
async def trackedclans(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Getrackte Clans",
        description="*Die folgenden Clans werden aktuell getrackt.*",
        color= discord.Color.random(),
        timestamp= discord.utils.utcnow()
    )
    clantext = ""
    tagtext = ""
    print(bot.clans)
    for i, row in bot.clans.iterrows():
       clantext += f"`{row['clanname']}`\n"
       tagtext += f"`{row['clantag']}`\n"
    embed.add_field(name="Clan", value=f"{clantext}")
    embed.add_field(name="Tag", value= f"{tagtext}")
    await interaction.response.send_message(embed=embed)

#shows wich players are currently tracked
@bot.tree.command(name = "trackedplayers", description="Zeigt an welche Spieler aktuell getrackt werden")
async def trackedplayers(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Getrackte Spieler",
        description="*Die folgenden Spieler werden aktuell getrackt.*",
        color= discord.Color.random(),
        timestamp= discord.utils.utcnow()
    )
    playertext = ""
    tagtext = ""
    print(bot.members)
    for i, row in bot.members.iterrows():
       playertext += f"`{row['username']}`\n"
       tagtext += f"`{row['tags']}`\n"
    embed.add_field(name="Discord member", value=f"{playertext}")
    embed.add_field(name="Tags", value= f"{tagtext}")
    print(bot.members)
    await interaction.response.send_message(embed=embed)

bot.run(token)