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


def report_summary_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Today summary",
                    callback_data="report:today",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📆 This week",
                    callback_data="report:this_week",
                ),
                InlineKeyboardButton(
                    text="🗓 This month",
                    callback_data="report:this_month",
                ),
            ],
        ]
    )
