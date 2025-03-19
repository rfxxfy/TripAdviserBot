import asyncio
from aiogram import F
from aiogram.filters import Command, StateFilter
from loader import dp, bot
from handlers import start, routes, currency, info, parameters, feedback
from states.travel_states import TravelForm

# Регистрация команды /start:
dp.message.register(start.welcome, Command("start"))

# Регистрация хендлеров:
dp.callback_query.register(routes.route_builder, F.data == "build_route")

dp.callback_query.register(currency.currency_exchange, F.data == "currency_exchange")

dp.callback_query.register(info.bot_info, F.data == "bot_info")

dp.callback_query.register(routes.confirm_routes_callback, F.data == "confirm_routes")

dp.callback_query.register(routes.back_to_main_callback, F.data == "back_to_main")

dp.callback_query.register(feedback.feedback_handler, F.data == "feedback")

# Регистрация хендлеров для уточнения параметров (FSM):
dp.message.register(
    parameters.process_location,
    StateFilter(TravelForm.waiting_for_location),
    F.content_type.in_(["text", "location"]),
)

dp.message.register(
    parameters.process_budget, StateFilter(TravelForm.waiting_for_budget)
)

dp.message.register(
    parameters.process_days, StateFilter(TravelForm.waiting_for_days)
)

dp.callback_query.register(
    parameters.toggle_photo_locations,
    F.data.startswith("toggle_photo_location"),
    StateFilter(TravelForm.waiting_for_photo_locations),
)

dp.callback_query.register(
    parameters.confirm_photo_locations,
    F.data == "confirm_photo_locations",
    StateFilter(TravelForm.waiting_for_photo_locations),
)

dp.callback_query.register(
    routes.toggle_route_callback,
    (F.data.startswith("toggle_") & ~F.data.startswith("toggle_photo_location")),
)

dp.message.register(
    parameters.finish_parameters_collection,
    StateFilter(TravelForm.waiting_for_photo_locations),
)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())