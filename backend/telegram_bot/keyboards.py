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


def manager_start_keyboard() -> InlineKeyboardMarkup:
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
                    text="🟢 Now",
                    callback_data="now",
                ),
                InlineKeyboardButton(
                    text="⏭ Next",
                    callback_data="next_placeholder",
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


def barber_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 My bookings today",
                    callback_data="barber_bookings:today",
                ),
                InlineKeyboardButton(
                    text="📅 My bookings tomorrow",
                    callback_data="barber_bookings:tomorrow",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🟢 Now",
                    callback_data="now",
                ),
                InlineKeyboardButton(
                    text="⏭ Next",
                    callback_data="next_placeholder",
                ),
            ],
        ]
    )


def report_summary_keyboard() -> InlineKeyboardMarkup:
    return manager_start_keyboard()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Menu",
                    callback_data="manager_menu",
                ),
            ],
        ]
    )
