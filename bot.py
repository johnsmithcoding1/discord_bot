import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import discord
from discord.ext import commands
import os
import json
import logging
from dotenv import load_dotenv
import asyncio

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bot')

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Load config
with open('config.json', 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.CONFIG = CONFIG

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    # Load cogs
    cogs = [
        'cogs.moderation',
        'cogs.roles',
        'cogs.tickets',
        'cogs.training',
        'cogs.logging',
        'cogs.troll',
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"Loaded cog: {cog}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog}: {e}")
    # Sync global slash commands
    synced = await bot.tree.sync()
    logger.info(f"Synced {len(synced)} global slash commands.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"You are on cooldown. Try again in {error.retry_after:.2f}s")
    else:
        logger.error(f"An error occurred: {error}")
        await ctx.send("An error occurred while processing the command.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

async def main():
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main()) 