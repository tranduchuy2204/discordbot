import asyncio
from bot.bot import create_bot
import config


async def main():
    bot = create_bot()
    await bot.start(config.TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
