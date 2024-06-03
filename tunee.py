# Discord Bot
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio

# Audio Formatting Junk
import subprocess

# Dev Environment
from dotenv import load_dotenv
import os

# Get env variables
load_dotenv()
tunee_token = os.getenv("TUNEE_TOKEN")

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize Tunee and empty play_queue
tunee = commands.Bot(command_prefix = "-", intents=intents)
play_queue = []

@tunee.event
async def on_ready():
	print("Tunee is online and ready to receive requests!")

@tunee.command(pass_context=True)
async def play(ctx, args):
	print(f"Adding to queue: {args}")
	if (not play_queue):
		if (ctx.author.voice):
			channel = ctx.message.author.voice.channel
			voice = None
			if (not ctx.voice_client):
				voice = await channel.connect()
			else:
				voice = ctx.message.guild.voice_client
			play_queue.append("test_audio/mbf.wav")
			await run_through_queue(voice, channel)
		else:
			await ctx.send("You are not in a voice channel, you must be in a voice channel to play audio!")
	else:
		play_queue.append("mbf.wav")

@tunee.command(pass_context=True)
async def stop(ctx):
	# Disconnect from voice client
	if (ctx.voice_client):
		await ctx.guild.voice_client.disconnect()
	else:
		await ctx.send("I am not in a voice channel!")
	# Empty out the play_queue
	while play_queue:
		print(f"Removing from queue: {play_queue.pop(0)}")

def get_length(input_video):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

async def run_through_queue(voice, channel):
	while play_queue:
		print(f"Now playing: {play_queue[0]}")
		source = FFmpegPCMAudio(play_queue[0])
		player = voice.play(source)
		# sleep and wait for audio to finish before repeating and moving on to the next audio
		await asyncio.sleep(3) # TODO make this the actual length of the audio
		play_queue.pop(0)
	return

tunee.run(tunee_token)