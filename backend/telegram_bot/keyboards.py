from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def booking_actions_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Complete",
                    callback_data=f"manager_booking_complete:{booking_id}",
                ),
                InlineKeyboardButton(
                    text="❌ No-show",
                    callback_data=f"manager_booking_no_show:{booking_id}",
                ),
            ]
        ]
    )


def report_summary_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Today bookings",
                    callback_data="manager_bookings:today",
                ),
                InlineKeyboardButton(
                    text="📅 Tomorrow bookings",
                    callback_data="manager_bookings:tomorrow",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 Today summary",
                    callback_data="manager_report:today",
                ),
                InlineKeyboardButton(
                    text="📊 Yesterday summary",
                    callback_data="manager_report:yesterday",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📆 This week summary",
                    callback_data="manager_report:this_week",
                ),
                InlineKeyboardButton(
                    text="📆 Last week summary",
                    callback_data="manager_report:last_week",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗓 This month summary",
                    callback_data="manager_report:this_month",
                ),
                InlineKeyboardButton(
                    text="🗓 Last month summary",
                    callback_data="manager_report:last_month",
                ),
            ],
        ]
    )
