import discord
from discord.ext import commands
from discord import app_commands
import wavelink
import config
from .events import setup_events
from .music import setup_music_commands
from ._global import setup_global_commands


def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.voice_states = True

    bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents)

    setup_events(bot)

    setup_music_commands(bot)

    setup_global_commands(bot)

    return bot
