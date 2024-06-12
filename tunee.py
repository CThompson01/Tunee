# Discord Bot
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio

# Audio Formatting Junk
import subprocess
import youtube_dl

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
	if (video is None):
		await ctx.send("To play a song you must either provide a YouTube link or text to search.\nFor example, try typing \n```-play moan bark fart``` or ```-play https://www.youtube.com/watch?v=n5YHJMdN9FE```")
		return

	# Actually add the song to queue
	print(f"Adding to queue: {video}")
	if (not play_queue):
		if (ctx.author.voice):
			channel = ctx.message.author.voice.channel
			voice = None
			if (not ctx.voice_client):
				voice = await channel.connect()
			else:
				voice = ctx.message.guild.voice_client
			play_queue.append(f"test_audio/{video}.wav")
			await run_through_queue(voice, channel)
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
	if (ctx.voice_client):
		await ctx.guild.voice_client.disconnect()
	else:
		await ctx.send("I am not in a voice channel!")
	# Empty out the play_queue
	while play_queue:
		print(f"Removing from queue: {play_queue.pop(0)}")

async def run_through_queue(voice, channel):
	"""
	Enters a while loop that continues until the play queue is empty.
	This allows for users to add more videos to the queue without disrupting the current video.
	"""
	while play_queue:
		play_file = play_queue[0]
		file_length = get_length(play_file)
		print(f"Now playing: {play_file}({file_length} seconds)")
		source = FFmpegPCMAudio(play_file)
		player = voice.play(source)
		await asyncio.sleep(file_length) # wait for audio to finish before moving on to next audio
		play_queue.pop(0) # Probably fix this eventually but because of the while loop can't pop 0 without it exiting
	return

def dl_video(url_search):
	ytdl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
		'outtmpl': 'queue/%(title)s.%(ext)s',
	}
	with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
		meta_data = ytdl.extract_info(url_search, download=True)
		return meta_data.get('title', None)

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

tunee.run(tunee_token)