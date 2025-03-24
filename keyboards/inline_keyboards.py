from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PHOTO_OPTIONS = ["Природные", "Городские пейзажи", "Памятники", "Музеи"]
CUISINE_OPTIONS = ["Итальянская", "Русская", "Азиатская", "Фастфуд", "Вегетарианская", "Десерты"]


def get_main_menu_keyboard():
    """
    Создает главное меню бота с основными действиями.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Построить маршрут", callback_data="build_route"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Найти ближайшие обменники валюты",
                    callback_data="currency_exchange",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Информация про бота", callback_data="bot_info"
                )
            ],
        ]
    )
    keyboard.inline_keyboard.append([get_feedback_button()])
    return keyboard


def get_route_types_keyboard(user_routes: dict):
    """
    Создает inline-клавиатуру для мультивыбора типа маршрута.

    :param user_routes: Словарь с текущим состоянием выбора маршрутов (выбрано/не выбрано).
    """
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
    """
    Создает кнопку возврата в главное меню.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="↩️ Вернуться в главное меню", callback_data="back_to_main")]])
    return keyboard


def get_photo_locations_keyboard(selected: list, options: list):
    """
    Формирует клавиатуру для мультивыбора фото-локаций.

    :param selected: Список уже выбранных пользователем фото-локаций.
    :param options: Список доступных вариантов фото-локаций.
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{chr(0x2705) if option in selected else '☐'} {option}",
                callback_data=f"toggle_photo_location:{option}",
            )
        ]
        for option in options
    ]
    buttons.append([
        InlineKeyboardButton(
            text="\U0001F197 Подтвердить выбор", 
            callback_data="confirm_photo_locations"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(
            text="↩️ Вернуться в главное меню", 
            callback_data="back_to_main"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cuisine_keyboard(selected: list, options: list):
    """
    Формирует клавиатуру для мультивыбора кухонь.
    
    :param selected: Список уже выбранных пользователем кухонь.
    :param options: Список доступных вариантов кухонь.
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{chr(0x2705) if option in selected else '☐'} {option}",
                callback_data=f"toggle_cuisine:{option}",
            )
        ]
        for option in options
    ]
    buttons.append([
        InlineKeyboardButton(
            text="\U0001F197 Подтвердить выбор", 
            callback_data="confirm_cuisine"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(
            text="↩️ Вернуться в главное меню", 
            callback_data="back_to_main"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_feedback_button() -> InlineKeyboardButton:
    """
    Создает кнопку для фидбека.
    """
    return InlineKeyboardButton(
        text="Обратная связь",
        callback_data="feedback")
