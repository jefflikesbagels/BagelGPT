import sys
import os
import asyncio
from dotenv import load_dotenv
from bagelgpt import bagelgpt
import discord
from discord.ext import commands

# Load environment variables from .env file
load_dotenv()

# Get API keys and channel IDs from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL')
DISCORD_API_KEY = os.environ.get('DISCORD_API_KEY')
DISCORD_GENERAL_CHANNEL = os.environ.get('DISCORD_GENERAL_CHANNEL')
DISCORD_RAP_BOT_CHANNEL = os.environ.get('DISCORD_RAP_BOT_CHANNEL')

# Initialize the gpt class in the bagelgpt library
gpt = bagelgpt(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)

# Set up the Discord Bot
intents = discord.Intents.default()  # getting default intents for Discord API
intents.message_content = True  # enabling message content intent for Discord API
bot = commands.Bot(command_prefix='/', intents=intents)
history_limit = 10
conversation_history = {}

# Define event handler for when the Discord Bot is ready
@bot.event
async def on_ready():
    # Printing a message to the console to confirm that the Bot is ready
    print(f'{bot.user} has connected to Discord!')
      
    # Get the Discord "General" channel object
    channel = bot.get_channel(int(DISCORD_GENERAL_CHANNEL))
    await channel.send("I'm back baby!")

# Define an event handler for responding to messages in the "Rap-Bot" channel
@bot.event
async def on_message(message):
    global history_limit

    print(f"Received message: {message.content}")
    await bot.process_commands(message)

    # Get the Discord "Rap-Bot" channel object
    channel = bot.get_channel(int(DISCORD_RAP_BOT_CHANNEL))

    # Ignore messages from the bot or other channels
    if message.author == bot.user or message.channel != channel:
        return

    # Check if the message starts with the command prefix
    if message.content.startswith('/history='):
        await history_command(message)
        return
    if message.content.startswith('/update'):
        await update_command()
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
    response = gpt.get_chat_completion(message.content, context, channel.topic)
    print(f"Got response from GPT:", response)

    # Delete the original attempting to create response message and insert the final response
    await response_message.delete()
    await channel.send(response)

async def history_command(message):
    global history_limit

    # Update the message history context with /history=<limit>
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

async def update_command():
    await logout()
    await asyncio.sleep(5)
    sys.exit(1001)

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