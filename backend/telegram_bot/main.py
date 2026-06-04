import asyncio
import logging

from aiogram import Bot, Dispatcher

from telegram_bot.config import load_config
from telegram_bot.handlers import actions, bookings, reports, start


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = load_config()

    bot = Bot(token=config.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(start.router)
    dispatcher.include_router(bookings.router)
    dispatcher.include_router(reports.router)
    dispatcher.include_router(actions.router)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
