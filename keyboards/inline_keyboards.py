from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PHOTO_OPTIONS = ["Природные", "Городские пейзажи", "Памятники", "Музеи"]
CUISINE_OPTIONS = [
    "Итальянская", "Русская", "Азиатская",
    "Фастфуд", "Вегетарианская", "Десерты",
    "Кофейни", "Bubble Tea"
]


def get_main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Главное меню бота.
    Если is_admin=True, добавляет кнопку «Команды админа».
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗺️ Построить маршрут",
                    callback_data="build_route"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💱 Найти ближайшие обменники",
                    callback_data="currency_exchange",
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Информация про бота",
                    callback_data="bot_info"
                )
            ],
        ]
    )
    # кнопка фидбека
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="📝 Обратная связь",
            callback_data="feedback"
        )
    ])
    # кнопка админа
    if is_admin:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="🛠️ Команды админа",
                callback_data="admin_menu"
            )
        ])
    return keyboard


def get_route_types_keyboard(user_routes: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{'✅' if user_routes.get('photo') else '☐'} Маршрут с живописными местами",
                    callback_data="toggle_photo",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{'✅' if user_routes.get('food') else '☐'} Маршрут с питанием",
                    callback_data="toggle_food",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить выбор",
                    callback_data="confirm_routes"
                )
            ],
            [
                InlineKeyboardButton(
                    text="↩️ Вернуться в главное меню",
                    callback_data="back_to_main"
                )
            ],
        ]
    )
    return keyboard


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="↩️ Вернуться в главное меню",
                    callback_data="back_to_main"
                )
            ]
        ]
    )


def get_photo_locations_keyboard(selected: list, options: list) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{'✅' if option in selected else '☐'} {option}",
                callback_data=f"toggle_photo_location:{option}",
            )
        ]
        for option in options
    ]
    all_selected = len(selected) == len(options)
    buttons.append([
        InlineKeyboardButton(
            text=f"{'✅' if all_selected else '☐'} {'Снять все' if all_selected else 'Выбрать все'}",
            callback_data="toggle_photo_location:all"
        )
    ])
    buttons.append([
        InlineKeyboardButton(text="✅ Подтвердить выбор", callback_data="confirm_photo_locations")
    ])
    buttons.append([
        InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_first_time_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, первый раз", callback_data="first_time:yes")
            ],
            [
                InlineKeyboardButton(text="❌ Нет, уже был(а)", callback_data="first_time:no")
            ],
            [
                InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back_to_main")
            ],
        ]
    )


def get_cuisine_keyboard(selected: list, options: list) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{'✅' if option in selected else '☐'} {option}",
                callback_data=f"toggle_cuisine:{option}",
            )
        ]
        for option in options
    ]
    all_selected = len(selected) == len(options)
    buttons.append([
        InlineKeyboardButton(
            text=f"{'✅' if all_selected else '☐'} {'Снять все' if all_selected else 'Выбрать все'}",
            callback_data="toggle_cuisine:all"
        )
    ])
    buttons.append([
        InlineKeyboardButton(text="✅ Подтвердить выбор", callback_data="confirm_cuisine")
    ])
    buttons.append([
        InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Меню админа: логи, пользователи, назначить админа, очистить логи.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📜 Просмотреть логи", callback_data="view_logs")],
            [InlineKeyboardButton(text="👥 Просмотреть пользователей", callback_data="view_users")],
            [InlineKeyboardButton(text="➕ Назначить админа", callback_data="make_admin")],
            [InlineKeyboardButton(text="🗑️ Очистить логи", callback_data="clear_logs")],
            [InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back_to_main")],
        ]
    )
