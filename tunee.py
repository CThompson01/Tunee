"""
This is a Discord bot that plays YouTube videos in voice channels.
"""

# Standard Imports
import subprocess
import asyncio
import random

# Dev Environment
import os
from dotenv import load_dotenv

# Discord Bot
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio

# Audio Formatting Junk
import youtube_dl

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
	"""
	Function called once the bot is logged in and ready to receive commands.
	Prints a message to the terminal letting the user know the bot is online.
	"""
	print("Tunee is online and ready to receive requests!")

@tunee.command(pass_context=True)
async def play(ctx, video=None):
	"""
	This command will play either the video from the YouTube link provided or if no
	link is provided, it will play the first search result using the text provided

	Parameters
	----------
	video : str, optional
		Either the link to a video or text used to search for a video
	"""
	# Send a warning message about using the command properly and exit
	if video is None:
		await ctx.send(
			"To play a song you must either provide a YouTube link or text to search.\n\n" +
			"For example, try typing\n" +
			"```-play moan bark fart``` or ```-play https://www.youtube.com/watch?v=n5YHJMdN9FE```")
		return

	# Actually add the song to queue
	print(f"Adding to queue: {video}")
	if not play_queue:
		if ctx.author.voice:
			channel = ctx.message.author.voice.channel
			voice = None
			if not ctx.voice_client:
				voice = await channel.connect()
			else:
				voice = ctx.message.guild.voice_client
			play_queue.append(f"test_audio/{video}.wav")
			await run_through_queue(voice)
		else:
			await ctx.send("You are not in a voice channel, you must be in a voice channel to play audio!")
	else:
		play_queue.append(f"test_audio/{video}.wav")

@tunee.command(pass_context=True)
async def stop(ctx):
	"""
	Disconnects Tunee from the call and clears the queue of videos
	"""
	# Disconnect from voice client
	if ctx.voice_client:
		await ctx.guild.voice_client.disconnect()
	else:
		await ctx.send("I am not in a voice channel!")
	# Empty out the play_queue
	while play_queue:
		print(f"Removing from queue: {play_queue.pop(0)}")

def get_length(input_video):
	"""
	Uses ffprobe to get the length in seconds of the current video.
	This is used by run_through_queue to properly wait until the current video
	is ended before starting the next one.
	"""
	result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
		'default=noprint_wrappers=1:nokey=1', input_video], stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT, check=True)
	return float(result.stdout)

async def run_through_queue(voice):
	"""
	Enters a while loop that continues until the play queue is empty.
	This allows for users to add more videos to the queue without disrupting the current video.
	"""
	while play_queue:
		play_file = play_queue[0]
		file_length = get_length(play_file)
		print(f"Now playing: {play_file}({file_length} seconds)")
		source = FFmpegPCMAudio(play_file)
		voice.play(source)
		await asyncio.sleep(file_length) # wait for audio to finish before moving on to next audio
		play_queue.pop(0) # Fix eventually can't pop 0 without it exiting
	return

def dl_video(url_search):
	identifier = random.randrange(0, 9)
	ytdl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
		'outtmpl': 'queue/%(title)s-' + str(identifier) + '.%(ext)s',
	}
	with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
		meta_data = ytdl.extract_info(url_search, download=True)
		return {
			'title': meta_data.get('title', None),
			'file_location': f'queue/{meta_data.get('title', None)}-{identifier}.mp3'
		}

def get_length(input_video):
	"""
	Uses ffprobe to get the length in seconds of the current video.
	This is used by run_through_queue to properly wait until the current video is ended before starting the next one.
	"""
	result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return float(result.stdout)

def is_url(url_str):
	"""
	Check whether the argument given is a URL or just a string to search
	"""
	return "https:" in url_str or "http:" in url_str # TODO: implement this better

if __name__ == "__main__":
	tunee.run(tunee_token)
