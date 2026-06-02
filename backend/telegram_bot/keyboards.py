from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def booking_actions_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Complete",
                    callback_data=f"admin_booking_complete:{booking_id}",
                ),
                InlineKeyboardButton(
                    text="❌ No-show",
                    callback_data=f"admin_booking_no_show:{booking_id}",
                ),
            ]
        ]
    )
