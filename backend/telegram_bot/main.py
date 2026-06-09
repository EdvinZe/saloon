import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher

from telegram_bot.config import load_config
from telegram_bot.handlers import actions, bookings, next, now, reports, start
from telegram_bot.reminders import reminder_loop


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = load_config()

    bot = Bot(token=config.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(start.router)
    dispatcher.include_router(now.router)
    dispatcher.include_router(next.router)
    dispatcher.include_router(bookings.router)
    dispatcher.include_router(reports.router)
    dispatcher.include_router(actions.router)

    reminder_task = asyncio.create_task(reminder_loop(bot))
    try:
        await dispatcher.start_polling(bot)
    finally:
        reminder_task.cancel()
        with suppress(asyncio.CancelledError):
            await reminder_task


if __name__ == "__main__":
    asyncio.run(main())
