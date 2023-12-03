from bagelgpt import bagelgpt
import discord
from discord.ext import tasks
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import subprocess

# loading environment variables from .env file
load_dotenv()

# Getting API keys from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL')
DISCORD_API_KEY = os.environ.get('DISCORD_API_KEY')
DISCORD_GENERAL_CHANNEL = os.environ.get('DISCORD_GENERAL_CHANNEL')
DISCORD_RAP_BOT_CHANNEL = os.environ.get('DISCORD_RAP_BOT_CHANNEL')

# Initializing the gpt class in the bagelgpt library
gpt = bagelgpt(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)

# Setting up Discord Bot
intents = discord.Intents.default()  # getting default intents for Discord API
intents.message_content = True  # enabling message content intent for Discord API
bot = commands.Bot(command_prefix='/', intents=intents)
history_limit = 10
conversation_history = {}

# Defining event handler for when the Discord Bot is ready
@bot.event
async def on_ready():
    # Printing a message to the console to confirm that the Bot is ready
    print(f'{bot.user} has connected to Discord!')
      
    channel = bot.get_channel(int(DISCORD_GENERAL_CHANNEL))  # Get the Discord channel object for Chit-Chat
    await channel.send("I'm back baby!")

# Defining a task to run GPT-3.5 chatbot in channel 0Z every 10 seconds
@bot.event
async def on_message(message):
    global history_limit

    print(f"Received message: {message.content}")
    await bot.process_commands(message)

    channel = bot.get_channel(int(DISCORD_RAP_BOT_CHANNEL))

    # Ignore messages from the bot or other channels
    if message.author == bot.user or message.channel != channel:
        return

    # Check if the message starts with the command prefix
    if message.content.startswith('/history='):
        await history_command(message)
        return

    # Send a message to the channel to indicate that the chatbot is processing the message
    response_message = await channel.send("Attempting to create response...")
    print(f"Attempting to create response...")

    # Get or initialize conversation history for the channel
    channel_id = message.channel.id
    if channel_id not in conversation_history:
            conversation_history[channel_id] = []

    # Append the latest message to the conversation history
    conversation_history[channel_id].append(message.content)

    # Limit conversation history to a certain number of messages (e.g., last 10 messages)
    conversation_history[channel_id] = conversation_history[channel_id][-history_limit:]

    # Use conversation history for context when getting a response
    context = "\n".join(conversation_history[channel_id])
    print(f"Context:", context)
    response = gpt.get_chat_completion(message.content, context)
    print(f"Got response from GPT:", response)

    await response_message.delete()
    await channel.send(response)

async def history_command(message):
    global history_limit

    try:
        new_limit = int(message.content.split('=')[1])
        history_limit = new_limit

        channel_id = message.channel.id
        if channel_id not in conversation_history:
            conversation_history[channel_id] = []

        conversation_history[channel_id] = conversation_history[channel_id][-history_limit:]

        await message.channel.send(f"Updated conversation history limit to {history_limit}.")
    except ValueError:
        await message.channel.send("Invalid command format. Use '/history=<limit>'.")


"""
# Defining a task to update the Discord bot script every 10 seconds
@tasks.loop(seconds=10)
async def respond_update_bot():
   await bot.wait_until_ready()  # Wait for the client to be ready before starting the task

   channel = bot.get_channel(int(SERVER_UPDATES_CH_ID))  # Get the Discord channel object for channel 0Z

   while not bot.is_closed():  # Loop until the client is closed
       message = await bot.wait_for('message')  # Wait for a new message in the channel

       if message.author == bot.user or message.channel != channel:  # Ignore messages from the bot or other channels
           return

       if message.content.startswith("!update"):
           channel = bot.get_channel(int(CHIT_CHAT_CH_ID))  # Get the Discord channel object for Chit-Chat
           await channel.send("Updating Discord bot script, please stand by...")
           process = subprocess.Popen([SCRIPT_BIN,SCRIPT_PATH])
           process.wait()
"""

async def send_final_message():
    await bot.wait_until_ready()
    channel = bot.get_channel(int(DISCORD_GENERAL_CHANNEL))  # Choose your channel ID
    await channel.send("Bite my shiny metal ass!")  # Your final message

async def logout():
    try:
        await send_final_message()
    finally:
        await bot.close()

async def main():
    try:
        await bot.start(DISCORD_API_KEY)
    except KeyboardInterrupt:
        print("Detected SIGINT, closing process!")
    finally:
        print(f"Logging {bot.user} out of Discord!")
        await logout()

# Run the main coroutine using asyncio.run()
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Detected SIGINT, closing process!")