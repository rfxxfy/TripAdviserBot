import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_routes = {}

async def welcome(message: types.Message):
    welcome_text = """Добро пожаловать в наш бот!

Я могу помочь вам с планированием вашего путешествия.
Выберите интересующее вас действие:"""

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Построить маршрут")],
            [KeyboardButton(text="Найти ближайшие обменники валюты с выгодным курсом")],
            [KeyboardButton(text="Информация про бота")]
        ],
        resize_keyboard=True
    )
    
    await message.reply(welcome_text, reply_markup=keyboard)

async def route_builder(message: types.Message):
    user_id = message.from_user.id
    
    user_routes[user_id] = {
        "photo": False,
        "budget": False,
        "sights": False
    }
    
    routes_text = "Выберите типы маршрутов (можно выбрать несколько):"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="☐ Маршрут с живописными местами",
            callback_data="toggle_photo"
        )],
        [InlineKeyboardButton(
            text="☐ Бюджетный маршрут",
            callback_data="toggle_budget"
        )],
        [InlineKeyboardButton(
            text="☐ Маршрут с достопримечательностями",
            callback_data="toggle_sights"
        )],
        [InlineKeyboardButton(
            text="✅ Подтвердить выбор",
            callback_data="confirm_routes"
        )],
        [InlineKeyboardButton(
            text="↩️ Вернуться в главное меню",
            callback_data="back_to_main"
        )]
    ])
    
    await message.reply(routes_text, reply_markup=ReplyKeyboardRemove())
    await message.answer("Выберите варианты:", reply_markup=keyboard)

async def toggle_route_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    route_type = callback.data.replace("toggle_", "")
    
    user_routes[user_id][route_type] = not user_routes[user_id][route_type]
    
    routes = user_routes[user_id]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{'☑' if routes['photo'] else '☐'} Маршрут с живописными местами",
            callback_data="toggle_photo"
        )],
        [InlineKeyboardButton(
            text=f"{'☑' if routes['budget'] else '☐'} Бюджетный маршрут",
            callback_data="toggle_budget"
        )],
        [InlineKeyboardButton(
            text=f"{'☑' if routes['sights'] else '☐'} Маршрут с достопримечательностями",
            callback_data="toggle_sights"
        )],
        [InlineKeyboardButton(
            text="✅ Подтвердить выбор",
            callback_data="confirm_routes"
        )],
        [InlineKeyboardButton(
            text="↩️ Вернуться в главное меню",
            callback_data="back_to_main"
        )]
    ])
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()

async def confirm_routes_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    routes = user_routes[user_id]
    
    selected_routes = []
    if routes["photo"]:
        selected_routes.append("Маршрут с живописными местами")
    if routes["budget"]:
        selected_routes.append("Бюджетный маршрут")
    if routes["sights"]:
        selected_routes.append("Маршрут с достопримечательностями")
    
    if not selected_routes:
        await callback.message.answer("Вы не выбрали ни одного маршрута. Пожалуйста, выберите хотя бы один маршрут.")
        await callback.answer()
        return
    
    response_text = "Вы выбрали следующие маршруты:\n"
    for route in selected_routes:
        response_text += f"- {route}\n"
    
    response_text += "\nПожалуйста, укажите пункт отправления для построения маршрутов."
    
    await callback.message.answer(response_text)
    await callback.answer()

async def back_to_main_callback(callback: types.CallbackQuery):
    await welcome(callback.message)
    await callback.answer()

async def currency_exchange(message: types.Message):
    await message.reply("Функция поиска обменников валюты в разработке.", reply_markup=ReplyKeyboardRemove())
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back_to_main")]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)

async def bot_info(message: types.Message):
    await message.reply("Этот бот поможет вам спланировать путешествие, построить маршруты и найти выгодные обменники валюты.", reply_markup=ReplyKeyboardRemove())
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Вернуться в главное меню", callback_data="back_to_main")]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)

dp.message.register(welcome, Command("start"))
dp.message.register(route_builder, F.text == "Построить маршрут")
dp.message.register(currency_exchange, F.text == "Найти ближайшие обменники валюты с выгодным курсом")
dp.message.register(bot_info, F.text == "Информация про бота")

dp.callback_query.register(toggle_route_callback, F.data.startswith("toggle_"))
dp.callback_query.register(confirm_routes_callback, F.data == "confirm_routes")
dp.callback_query.register(back_to_main_callback, F.data == "back_to_main")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())