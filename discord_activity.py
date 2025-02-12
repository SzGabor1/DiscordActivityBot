import discord
from discord.ext import commands
import requests
from datetime import datetime, timedelta
from Session import Session
from Reports import Reports
import os 


intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!",intents=intents)

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

sessions = {}
rep = Reports()


def send_webhook_message(content):
    data = {"content": content}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Failed to send message to webhook. Status code: {response.status_code}")
        


def online_time_message(times_online_dict):
    message = ""
    for user,time in times_online_dict:
        hours, remainder = divmod(time, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
        message+=f"**{user}** spent **{duration}** on the server\n"
    return message

def session_time_message(times_online_dict):
    message = ""
    for user,time in times_online_dict:
        hours, remainder = divmod(time, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
        message+=f"**{user}** spent **{duration}** in this session\n"
    return message
        
    


@bot.command(help="Save and create sessions for each user in a channel.", usage="!save")
async def save(ctx):
    sessions.clear()
    for member in ctx.guild.members:
        if member.voice:
            sessions[member.name] = Session(member)
            if member.voice.self_mute:
                sessions[member.name].handle_mic_state("muted")
    
    await ctx.send(f"Sessions have been saved for all users in voice channels.")


@bot.command(help="Time of current session of users on the server.", usage="!uptime")
async def uptime(ctx,*args):
    message : str = ""

    times_online_dict = Session.calculate_time_spent_in_session(sessions,ctx.author.guild.id)
    times_online_dict= sorted(times_online_dict.items(), key = lambda x:x[1])
    message +=  session_time_message(times_online_dict)

    if message:
        await ctx.send(message)
    else:
        await ctx.send("No user is online")



@bot.command(help="Send a Gantt chart showing user activity for today or for a specific date (in yyyy.mm.dd format).", usage="!gant")
async def gant(ctx,*args):
    
    
    if len(args) == 0:
        date = datetime.now() + timedelta(hours=1)
        report_file = rep.makeReport(ctx.guild.id, datetime(date.year, date.month, date.day), sessions)
        
        await ctx.send("Here's the Gantt chart for today's activity:", 
                    file=discord.File(report_file))
        
    elif(args[0] == "mic"):
        date = datetime.now() + timedelta(hours=1)
        report_file = rep.generateGanttReportMic(ctx.guild.id, datetime(date.year, date.month, date.day), sessions)
        
        await ctx.send("Here's the Gantt chart for today's activity:", 
                    file=discord.File(report_file))
    
    else:
        date_parts = args[0].split('.')
        date = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
        report_file = rep.makeReport(ctx.guild.id, date, sessions)
        
        await ctx.send("Here's the Gantt chart for today's activity:", 
                    file=discord.File(report_file))
        


@bot.command(help="Time of all users spent on this server.", args="!uptime\n!uptime <discord_username1> <discord_username2>")
async def alltime(ctx,*args):
    message : str = ""
    if len(args) == 0:
        times_online_dict = Session.calculate_time_spent_online(sessions,ctx.author.guild.id)
        
        times_online_dict= sorted(times_online_dict.items(), key = lambda x:x[1])
    
        
        message +=  online_time_message(times_online_dict)
        
    else:
        for username in args:
            times_online_dict = Session.calculate_time_spent_online(sessions, ctx.author.guild.id, username)
            message += online_time_message(times_online_dict)

    
    await ctx.send(message)

@bot.event
async def on_voice_state_update(member, before, after):
    

    if before.self_mute != after.self_mute:
        mic_state = "muted" if after.self_mute else "unmuted"
        sessions[member.name].handle_mic_state(mic_state)
    
    
    if before.channel is None and after.channel is not None:
        #joining channel
        sessions[member.name] = (Session(member))
        
        if before.self_mute:
            sessions[member.name].handle_mic_state("muted")
        
    elif before.channel is not None and after.channel is None:
        #leaving channel

        if sessions.get(member.name,None):
            sessions[member.name].channel = before.channel.name
            
            start = sessions[member.name].session_start
            end = datetime.now()+timedelta(hours=1)
            time_spent = end-start
            time_spent = int(time_spent.total_seconds())
            
            hours, remainder = divmod(time_spent, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
            
            message = f"**{member.name}** left **{before.channel.name}** after spending **{duration}**\n"
            
            sessions.pop(member.name)
            
            send_webhook_message(message)
    

    elif before.channel != after.channel:
        #channel change
        if sessions.get(member.name,None):
            sessions[member.name].channel = before.channel.name
            
            start = sessions[member.name].session_start
            end = datetime.now()+timedelta(hours=1)
            time_spent = end-start
            time_spent = int(time_spent.total_seconds())
            
            hours, remainder = divmod(time_spent, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
            
            message = f"**{member.name}** left **{before.channel.name}** after spending **{duration}**\n"
    
            sessions.pop(member.name)
            send_webhook_message(message)

        sessions[member.name] = (Session(member))
        
        if before.self_mute:
            sessions[member.name].handle_mic_state("muted")



bot.run(BOT_TOKEN)

