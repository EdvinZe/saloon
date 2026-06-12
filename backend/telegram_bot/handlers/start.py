from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from telegram_bot.formatters import format_welcome_message
from telegram_bot.handlers.common import get_authorized_context
from telegram_bot.keyboards import barber_start_keyboard, manager_start_keyboard

router = Router()


async def send_main_menu(target: Message | CallbackQuery) -> None:
    ctx = await get_authorized_context(target)
    if ctx is None:
        return

    if ctx.role == "barber":
        reply_markup = barber_start_keyboard()
    else:
        reply_markup = manager_start_keyboard()

    text = format_welcome_message(ctx)

    if isinstance(target, CallbackQuery):
        if target.message is not None:
            await target.message.answer(text, reply_markup=reply_markup)
        else:
            await target.answer(text[:200], show_alert=True)
            return
        await target.answer()
        return

    await target.answer(text, reply_markup=reply_markup)


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    await send_main_menu(message)


@router.message(Command("menu"))
async def menu_command(message: Message) -> None:
    await send_main_menu(message)


@router.callback_query(F.data == "manager_menu")
async def manager_menu_callback(callback: CallbackQuery) -> None:
    await send_main_menu(callback)
