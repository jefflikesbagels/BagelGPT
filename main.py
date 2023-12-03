from bagelgpt import bagelgpt
import discord
from discord.ext import tasks
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
DISCORD_PLC_BOT_CHANNEL = os.environ.get('DISCORD_PLC_BOT_CHANNEL')

# Initializing the gpt class in the bagelgpt library
gpt = bagelgpt(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)

# Setting up Discord Bot
intents = discord.Intents.default()  # getting default intents for Discord API
intents.message_content = True  # enabling message content intent for Discord API
client = discord.Client(intents=intents)  # creating Discord Bot client with the specified intents

# Defining event handler for when the Discord Bot is ready
@client.event
async def on_ready():
    # Printing a message to the console to confirm that the Bot is ready
    print(f'{client.user} has connected to Discord!')
      
    channel = client.get_channel(int(DISCORD_GENERAL_CHANNEL))  # Get the Discord channel object for Chit-Chat
    await channel.send("I'm back baby!")

    # Starting background tasks for various chatbots using Discord.py's Task object
    on_message.start()  # Starting task for GPT-3.5 chatbot in channel 0Z
    #if SERVER_OS == "Linux":
    #   respond_update_bot.start() # Starting task for bot update script


# Defining a task to run GPT-3.5 chatbot in channel 0Z every 10 seconds
@tasks.loop(seconds=3)
async def on_message():
    # Wait for the client to be ready before starting the task
    await client.wait_until_ready()

    
    channel = client.get_channel(int(DISCORD_PLC_BOT_CHANNEL))

    # Loop until the client is closed
    while not client.is_closed():

        # Wait for a new message in the channel
        message = await client.wait_for('message')

        # Ignore messages from the bot or other channels
        if message.author == client.user or message.channel != channel:
            return

        # Send a message to the channel to indicate that the chatbot is processing the message
        await channel.send("Attempting to create response...")

        # Get a response from the chatbot based on the input message
        response = gpt.get_chat_completion(message.content)

        # Check if there was an error generating the chatbot's response
        if gpt.generate_chat_completion_fail:
            await channel.send(response + "\n\nChat completion failed. Please try again.")
        else:
            # Check if the response is a list of messages
            if isinstance(response, list):
                # If so, iterate through the list and send each message to the channel
                for item in response:
                    await channel.send(item)
            # If the response is a single message
            else:
                # Send the message to the channel
                await channel.send(response)



"""
# Defining a task to update the Discord bot script every 10 seconds
@tasks.loop(seconds=10)
async def respond_update_bot():
   await client.wait_until_ready()  # Wait for the client to be ready before starting the task

   channel = client.get_channel(int(SERVER_UPDATES_CH_ID))  # Get the Discord channel object for channel 0Z

   while not client.is_closed():  # Loop until the client is closed
       message = await client.wait_for('message')  # Wait for a new message in the channel

       if message.author == client.user or message.channel != channel:  # Ignore messages from the bot or other channels
           return

       if message.content.startswith("!update"):
           channel = client.get_channel(int(CHIT_CHAT_CH_ID))  # Get the Discord channel object for Chit-Chat
           await channel.send("Updating Discord bot script, please stand by...")
           process = subprocess.Popen([SCRIPT_BIN,SCRIPT_PATH])
           process.wait()
"""

#Starts the discord client using the API key
try:
    client.run(DISCORD_API_KEY)
except KeyboardInterrupt:
    print(f'Detected SIGINT, closing process!')
finally:
    print(f'Logging {client.user} out of Discord!')
    client.close()