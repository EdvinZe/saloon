import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from telegram_bot.api_client import BackendAPIError, complete_booking, mark_booking_no_show
from telegram_bot.handlers.common import get_authorized_context
from telegram_bot.keyboards import back_to_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)


def _parse_booking_id(callback_data: str | None) -> int | None:
    if not callback_data:
        return None
    try:
        return int(callback_data.rsplit(":", 1)[1])
    except (IndexError, ValueError):
        return None


async def _handle_action(callback: CallbackQuery, action: str) -> None:
    ctx = await get_authorized_context(callback)
    if ctx is None:
        return

    # TODO: for barber actions, verify booking.master_id before allowing action.
    if ctx.role != "manager":
        await callback.answer("This action is available for managers only.", show_alert=True)
        return

    booking_id = _parse_booking_id(callback.data)
    if booking_id is None:
        await callback.answer("Invalid booking action.", show_alert=True)
        return

    try:
        if action == "complete":
            await complete_booking(booking_id)
            confirmation = "Booking marked as completed."
        else:
            await mark_booking_no_show(booking_id)
            confirmation = "Booking marked as no-show."
    except BackendAPIError as exc:
        logger.warning("Could not update booking %s: %s", booking_id, exc)
        detail = str(exc) or "Could not update booking. Please try again."
        await callback.answer(detail, show_alert=True)
        return
    except Exception:
        logger.exception("Unexpected error while updating booking %s", booking_id)
        await callback.answer("Could not update booking. Please try again.", show_alert=True)
        return

    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(confirmation, reply_markup=back_to_menu_keyboard())
    await callback.answer(confirmation)


@router.callback_query(F.data.startswith("manager_booking_complete:"))
async def complete_booking_callback(callback: CallbackQuery) -> None:
    await _handle_action(callback, "complete")


@router.callback_query(F.data.startswith("manager_booking_no_show:"))
async def no_show_booking_callback(callback: CallbackQuery) -> None:
    await _handle_action(callback, "no_show")


@router.callback_query(F.data.startswith("admin_booking_complete:"))
async def legacy_complete_booking_callback(callback: CallbackQuery) -> None:
    await _handle_action(callback, "complete")


@router.callback_query(F.data.startswith("admin_booking_no_show:"))
async def legacy_no_show_booking_callback(callback: CallbackQuery) -> None:
    await _handle_action(callback, "no_show")
