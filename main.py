# Importing necessary libraries
from refikigpt import gpt  # importing custom library "refikigpt" openaai API wrapper
import discord  # importing discord API wrapper library
from discord.ext import tasks  # importing tasks module for Discord Bot tasks
import os  # importing OS module for accessing environment variables
import asyncio  # importing asyncio for asynchronous execution
from dotenv import load_dotenv  # importing dotenv for loading environment variables from .env file
import subprocess # importing subprocess for calling update script

load_dotenv()  # loading environment variables from .env file

# Getting API keys from environment variables
RG_KEY = os.environ.get('RG_KEY')  # API key for refikigpt library
GPT_35_CH_0Z_ID = os.environ.get('GPT_35_CH_0Z_ID')  # Discord channel ID for GPT-3.5 chat
GPT_35_CH_CT_ID = os.environ.get('GPT_35_CH_CT_ID')  # Discord channel ID for GPT-3.5 chatbot (conversation tracking)
GPT_DAV_CH_0Z_ID = os.environ.get('GPT_DAV_CH_0Z_ID')  # Discord channel ID for GPT-3.5 chatbot (David's version)
DALLE_2 = os.environ.get('DALLE_2_CH_ID')  # Discord channel ID for DALLE-2 image generation model
CHIT_CHAT_CH_ID = os.environ.get('CHIT_CHAT_CH_ID') # Discord channel ID for Chit-Chat channel
SERVER_OS = os.environ.get('SERVER_OS') # Set to True if running on Windows, False if running on Linux
if SERVER_OS == "Linux":
      SERVER_UPDATES_CH_ID = os.environ.get('SERVER_UPDATES_CH_ID') # Discord channel for bot update script
      SCRIPT_BIN = os.environ.get('SCRIPT_BIN') # Location of bin file for executing update script
      SCRIPT_PATH = os.environ.get('SCRIPT_PATH') # Location of Discord Bot update script

# Initializing the gpt class in the refikigpt library
gpt = gpt()

# Setting up Discord Bot
intents = discord.Intents.default()  # getting default intents for Discord API
intents.message_content = True  # enabling message content intent for Discord API
client = discord.Client(intents=intents)  # creating Discord Bot client with the specified intents

# Defining event handler for when the Discord Bot is ready
@client.event
async def on_ready():
    # Printing a message to the console to confirm that the Bot is ready
    print(f'{client.user} has connected to Discord!')
      
    channel = client.get_channel(int(CHIT_CHAT_CH_ID))  # Get the Discord channel object for Chit-Chat
    await channel.send("I'm back baby!")

    # Starting background tasks for various chatbots using Discord.py's Task object
    # 'respond_gpt_35_turbo_0Z', 'respond_gpt_35_turbo_chat', 'respond_gpt_dav_0Z', 'respond_dalle_2'
    respond_gpt_35_turbo_0Z.start()  # Starting task for GPT-3.5 chatbot in channel 0Z
    respond_gpt_35_turbo_chat.start()  # Starting task for GPT-3.5 chatbot with conversation tracking
    respond_gpt_dav_0Z.start()  # Starting task for David's version of GPT-3.5 chatbot in channel 0Z
    respond_dalle_2.start()  # Starting task for DALLE-2 image generation model
    if SERVER_OS == "Linux":
       respond_update_bot.start() # Starting task for bot update script

# Defining a task to run GPT-3.5 chatbot in channel 0Z every 10 seconds
@tasks.loop(seconds=3)
async def respond_gpt_35_turbo_0Z():
    await client.wait_until_ready()  # Wait for the client to be ready before starting the task

    channel = client.get_channel(int(GPT_35_CH_0Z_ID))  # Get the Discord channel object for channel 0Z

    while not client.is_closed():  # Loop until the client is closed
        message = await client.wait_for('message')  # Wait for a new message in the channel

        if message.author == client.user or message.channel != channel:  # Ignore messages from the bot or other channels
            return

        #await channel.send("Attempting to create response...")  # Send a message to the channel to indicate that the chatbot is processing the message

        response = gpt.get_chat_completion(message.content)  # Get a response from the chatbot based on the input message

        if gpt.generate_chat_completion_fail:  # Check if there was an error generating the chatbot's response
            await channel.send(response + "\n\nChat completion failed. Please try again.")  # If there was an error, send a message to the channel with the error message
        else:
            if isinstance(response, list):  # Check if the response is a list of messages
                for item in response:  # If so, iterate through the list and send each message to the channel
                    await channel.send(item)
            else:  # If the response is a single message
                await channel.send(response)  # Send the message to the channel

# Defining a task to run GPT-3.5 chatbot with conversation tracking every 10 seconds
@tasks.loop(seconds=3)
async def respond_gpt_35_turbo_chat():
    await client.wait_until_ready()  # Wait for the client to be ready before starting the task

    channel = client.get_channel(int(GPT_35_CH_CT_ID))  # Get the Discord channel object for the conversation tracking channel

    while not client.is_closed():  # Loop until the client is closed
        message = await client.wait_for('message')  # Wait for a new message in the channel

        if message.author == client.user or message.channel != channel:  # Ignore messages from the bot or other channels
            return

        #await channel.send("Attempting to create response...")

        message_history = [message async for message in channel.history(limit=100)]  # Get the last 100 messages in the channel

        user_history = []
        assistant_history = []

        # Separate the message history into user messages and assistant messages
        for msg in message_history:
            if msg.author == client.user:
                assistant_history.append(msg.content)
            else:
                user_history.append(msg.content)

        # Get a response from the chatbot based on the input message and the conversation history
        response = gpt.get_ongoing_chat_completion(message.content, user_history, assistant_history)

        if gpt.generate_chat_completion_fail:  # Check if there was an error generating the chatbot's response
            await channel.send(response + "\n\nChat completion failed. Please try again.")  # If there was an error, send a message to the channel with the error message
        else:
            if isinstance(response, list):  # Check if the response is a list of messages
                for item in response:  # If so, iterate through the list and send each message to the channel
                    await channel.send(item)
            else:  # If the response is a single message
                await channel.send(response)  # Send the message to the channel

# Defining a task to run David's version of GPT-3.5 chatbot in channel 0Z every 10 seconds
@tasks.loop(seconds=3)
async def respond_gpt_dav_0Z():
    await client.wait_until_ready()  # Wait for the client to be ready before starting the task

    channel = client.get_channel(int(GPT_DAV_CH_0Z_ID))  # Get the Discord channel object for David's version of the chatbot in channel 0Z

    while not client.is_closed():  # Loop until the client is closed
        message = await client.wait_for('message')  # Wait for a new message in the channel

        if message.author == client.user or message.channel != channel:  # Ignore messages from the bot or other channels
            return

        await channel.send("Attempting to create response...")  # Send a message to the channel to indicate that the chatbot is processing the message

        response = gpt.get_completion(message.content)  # Get a response from the chatbot based on the input message

        if gpt.generate_completion_fail:  # Check if there was an error generating the chatbot's response
            await channel.send(response + "\n\nChat completion failed. Please try again.")  # If there was an error, send a message to the channel with the error message
        else:
            if isinstance(response, list):  # Check if the response is a list of messages
                for item in response:  # If so, iterate through the list and send each message to the channel
                    await channel.send(item)
            else:  # If the response is a single message
                await channel.send(response)  # Send the message to the channel

# Defining a task to run the DALLE-2 image generation model every 10 seconds
@tasks.loop(seconds=3)
async def respond_dalle_2():
    await client.wait_until_ready()  # Wait for the client to be ready before starting the task

    channel = client.get_channel(int(DALLE_2))  # Get the Discord channel object for the DALLE-2 image generation model

    while not client.is_closed():  # Loop until the client is closed
        message = await client.wait_for('message')  # Wait for a new message in the channel

        if message.author == client.user or message.channel != channel:  # Ignore messages from the bot or other channels
            return

        if message.content.startswith('https://') or message.attachments:  # Check if the message contains an image URL
            await channel.send("Attempting to create Image Variation...")  # Send a message to the channel to indicate that the image variation is being generated

            if message.attachments:
                image_response = gpt.get_image_variation(message.attachments[0].url)  # Generate an image variation based on the attatched image's URL
            else:
                image_response = gpt.get_image_variation(message.content) # Generate an image variation based on the input URL

            if gpt.generate_image_variation_fail:  # Check if there was an error generating the image variation
                await channel.send(image_response + "\n\nImage variation failed. Please try again.")  # If there was an error, send a message to the channel with the error message
            else:
                file = discord.File(image_response, filename=image_response)  # Create a file object for the image variation
                await channel.send(file=file)  # Send the image variation to the channel

        else:
            await channel.send("Attempting to create Image...")  # Send a message to the channel to indicate that the image is being generated

            image_response = gpt.get_image(message.content)  # Generate an image based on the input text

            if gpt.generate_image_fail:  # Check if there was an error generating the image
                await channel.send(image_response + "\n\nImage completion failed. Please try again.")  # If there was an error, send a message to the channel with the error message
            else:
                file = discord.File(image_response, filename=image_response)  # Create a file object for the image variation
                await channel.send(file=file)  # Send the image variation to the channel

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

#Starts the discord client using the API key
try:
    client.run(RG_KEY)
except KeyboardInterrupt:
    print(f'Detected SIGINT, closing process!')
finally:
    print(f'Logging {client.user} out of Discord!')
    client.close()