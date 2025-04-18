from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PHOTO_OPTIONS = ["Природные", "Городские пейзажи", "Памятники", "Музеи"]
CUISINE_OPTIONS = ["Итальянская", "Русская", "Азиатская", "Фастфуд", "Вегетарианская", "Десерты"]


def get_main_menu_keyboard(is_admin: bool = False):
    """
    Главное меню. Если is_admin=True — добавляет кнопку перехода в админ‑меню.
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺️ Построить маршрут",     callback_data="build_route")],
        [InlineKeyboardButton(text="💲 Обмен валюты",           callback_data="currency_exchange")],
        [InlineKeyboardButton(text="ℹ️ Информация про бота",    callback_data="bot_info")],
        [InlineKeyboardButton(text="💬 Обратная связь",         callback_data="feedback")],
    ])
    if is_admin:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="⚙️ Команды админа", callback_data="admin_menu")
        ])
    return kb

def get_admin_menu_keyboard():
    """
    Меню админа — список админских команд + кнопка «Назад».
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Просмотр логов", callback_data="view_logs")],
        [InlineKeyboardButton(text="👥 Пользователи",     callback_data="view_users")],
        [InlineKeyboardButton(text="🛡️ Сделать админом",  callback_data="make_admin")],
        [InlineKeyboardButton(text="🗑️ Очистить логи",    callback_data="clear_logs")],
        [InlineKeyboardButton(text="↩️ Назад",            callback_data="back_to_main")],
    ])


def get_route_types_keyboard(user_routes: dict):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{chr(0x2705) if user_routes.get('photo') else '☐'} Маршрут с живописными местами",
                    callback_data="toggle_photo",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{chr(0x2705) if user_routes.get('food') else '☐'} Маршрут с питанием",
                    callback_data="toggle_food",
                )
            ],
            [
                InlineKeyboardButton(
                    text="\U0001F197 Подтвердить выбор", callback_data="confirm_routes"
                )
            ],
            [
                InlineKeyboardButton(
                    text="↩️ Вернуться в главное меню", callback_data="back_to_main"
                )
            ],
        ]
    )
    return keyboard


def get_back_to_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="↩️ Вернуться в главное меню", callback_data="back_to_main"
            )]
        ]
    )


def get_photo_locations_keyboard(selected: list, options: list):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{chr(0x2705) if option in selected else '☐'} {option}",
                callback_data=f"toggle_photo_location:{option}",
            )
        ]
        for option in options
    ]

    all_selected = len(selected) == len(options)
    buttons.append([
        InlineKeyboardButton(
            text=f"{chr(0x2705) if all_selected else '☐'} {'Снять все отметки' if all_selected else 'Выбрать все'}",
            callback_data="toggle_photo_location:all"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="\U0001F197 Подтвердить выбор", callback_data="confirm_photo_locations"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="↩️ Вернуться в главное меню", callback_data="back_to_main"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_first_time_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, первый раз", callback_data="first_time:yes")],
            [InlineKeyboardButton(text="❌ Нет, уже был(а) здесь", callback_data="first_time:no")],
            [InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back_to_main")],
        ]
    )


def get_cuisine_keyboard(selected: list, options: list):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{chr(0x2705) if option in selected else '☐'} {option}",
                callback_data=f"toggle_cuisine:{option}",
            )
        ]
        for option in options
    ]

    all_selected = len(selected) == len(options)
    buttons.append([
        InlineKeyboardButton(
            text=f"{chr(0x2705) if all_selected else '☐'} {'Снять все отметки' if all_selected else 'Выбрать все'}",
            callback_data="toggle_cuisine:all"
        )
    ])
    buttons.append([
        InlineKeyboardButton(text="\U0001F197 Подтвердить выбор", callback_data="confirm_cuisine")
    ])
    buttons.append([
        InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_feedback_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="💬 Обратная связь",
        callback_data="feedback"
    )
