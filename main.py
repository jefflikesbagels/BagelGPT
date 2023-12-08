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
DISCORD_API_KEY = os.environ.get('DISCORD_API_KEY')
DISCORD_GENERAL_CHANNEL = os.environ.get('DISCORD_GENERAL_CHANNEL')
DISCORD_GENERAL_MODEL = os.environ.get('DISCORD_GENERAL_MODEL')
DISCORD_RAP_BOT_CHANNEL = os.environ.get('DISCORD_RAP_BOT_CHANNEL')
DISCORD_RAP_BOT_MODEL = os.environ.get('DISCORD_RAP_BOT_MODEL')
DISCORD_GPT4_BOT_CHANNEL = os.environ.get('DISCORD_GPT4_BOT_CHANNEL')
DISCORD_GPT4_BOT_MODEL = os.environ.get('DISCORD_GPT4_BOT_MODEL')
DISCORD_JOE_BOT_CHANNEL = os.environ.get('DISCORD_JOE_BOT_CHANNEL')
DISCORD_JOE_BOT_MODEL = os.environ.get('DISCORD_JOE_BOT_MODEL')

# Initialize the gpt class in the bagelgpt library
gpt_general = bagelgpt(api_key=OPENAI_API_KEY, model=DISCORD_GENERAL_MODEL)
gpt_rap = bagelgpt(api_key=OPENAI_API_KEY, model=DISCORD_RAP_BOT_MODEL)
gpt_4 = bagelgpt(api_key=OPENAI_API_KEY, model=DISCORD_GPT4_BOT_MODEL)
gpt_joe = bagelgpt(api_key=OPENAI_API_KEY, model=DISCORD_JOE_BOT_MODEL)

# Set up the Discord Bot
intents = discord.Intents.default()  # getting default intents for Discord API
intents.message_content = True  # enabling message content intent for Discord API
bot = commands.Bot(command_prefix='/', intents=intents)
history_limit = 10
conversation_history = {}

class UpdateCommand(Exception):
    pass

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
    general_channel = bot.get_channel(int(DISCORD_GENERAL_CHANNEL))
    rap_channel = bot.get_channel(int(DISCORD_RAP_BOT_CHANNEL))
    gpt4_channel = bot.get_channel(int(DISCORD_GPT4_BOT_CHANNEL))
    joe_channel = bot.get_channel(int(DISCORD_JOE_BOT_CHANNEL))

    print(f"Received message: {message.content}")
    await bot.process_commands(message)

    # Ignore messages from the bot
    if message.author == bot.user: return

    if message.channel == general_channel:
        await general_bot(general_channel, message, gpt_general)

    elif message.channel == rap_channel:
        await rap_bot(rap_channel, message, gpt_rap)

    elif message.channel == gpt4_channel:
        await gpt4_bot(gpt4_channel, message, gpt_4)

    elif message.channel == joe_channel:
        await gpt4_bot(joe_channel, message, gpt_joe)
   
async def general_bot(channel, message, gpt):
    if message.content.startswith('/update'):
        await update_command()
        return

async def rap_bot(channel, message, gpt):
    # Set a default topic if the channel topic is empty.
    if not channel.topic:
        channel_topic = "Your name is BagelGPT and you only answer in rap battles."
    else:
        channel_topic = channel.topic

    # Send a message to the channel to indicate that the chatbot is processing the message
    attempt_message = await channel.send("Attempting to create response...")

    gpt_response = gpt.get_chat_completion(message.content, channel_topic)
    print(f"Got response from GPT:", gpt_response)

    # Delete the original attempting to create response message and insert the final response
    await attempt_message.delete()
    await channel.send(gpt_response)

async def gpt4_bot(channel, message, gpt):
    global history_limit

    # Set a default topic if the channel topic is empty.
    if not channel.topic:
        channel_topic = "You are a helpful assistant."
    else:
        channel_topic = channel.topic

    # Check if the message starts with the command prefix
    if message.content.startswith('/history='):
        await history_command(message)
        return
    
    # Send a message to the channel to indicate that the chatbot is processing the message
    attempt_message = await channel.send("Attempting to create response...")

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
    response = gpt.get_chat_completion(message.content, channel_topic, context)
    print(f"Got response from GPT:", response)

    # Delete the original attempting to create response message and insert the final response
    await attempt_message.delete()

    # Check if the response is split
    if isinstance(response, list):
        for split_response in response:
            await channel.send(split_response)
    else:
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
    raise UpdateCommand()

async def send_final_message():
    await bot.wait_until_ready()
    channel = bot.get_channel(int(DISCORD_GENERAL_CHANNEL))
    await channel.send("Bite my shiny metal ass!")

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
    except UpdateCommand:
        print("Exiting with code 1001")
    finally:
        print(f"Logging {bot.user} out of Discord!")
        await logout()

# Run the main coroutine using asyncio.run()
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Detected SIGINT, closing process!")