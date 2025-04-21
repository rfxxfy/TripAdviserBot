import asyncio
from helpers.logger import setup_logging
setup_logging(logfile="data/bot.log")

from aiogram import F, types
from aiogram.filters import Command, StateFilter
from loader import dp, bot
from handlers import start, routes, currency, info, parameters, feedback, fallback, admin
from commands import set_bot_commands
from middlewares.db_middleware import DatabaseMiddleware
from states.travel_states import TravelForm

dp.message.register(start.welcome, Command("start"))

dp.callback_query.register(routes.route_builder, F.data == "build_route")
dp.callback_query.register(currency.currency_exchange, F.data == "currency_exchange")
dp.callback_query.register(info.bot_info, F.data == "bot_info")
dp.callback_query.register(routes.confirm_routes_callback, F.data == "confirm_routes")
dp.callback_query.register(start.back_to_main_callback, F.data == "back_to_main")
dp.callback_query.register(feedback.feedback_handler, F.data == "feedback")
dp.callback_query.register(
    routes.toggle_route_callback,
    (
        F.data.startswith("toggle_")
        & ~F.data.startswith("toggle_photo_location")
        & ~F.data.startswith("toggle_cuisine")
    )
)

# админские
dp.callback_query.register(admin.show_admin_menu, F.data == "admin_menu")
dp.callback_query.register(admin.view_logs,      F.data == "view_logs")
dp.callback_query.register(admin.clear_logs,     F.data == "clear_logs")
dp.callback_query.register(admin.view_users,     F.data == "view_users")
dp.callback_query.register(admin.make_admin,     F.data == "make_admin")

dp.message.register(
    admin.process_set_admin,
    StateFilter(TravelForm.waiting_for_admin_id),
    F.content_type.in_(["text"])
)
dp.message.register(
    parameters.process_location,
    StateFilter(TravelForm.waiting_for_location),
    F.content_type.in_(["text", "location"])
)
dp.message.register(
    parameters.process_budget,
    StateFilter(TravelForm.waiting_for_budget)
)
dp.message.register(
    parameters.process_days,
    StateFilter(TravelForm.waiting_for_days)
)
dp.message.register(
    feedback.process_feedback,
    StateFilter(TravelForm.waiting_for_feedback)
)
dp.callback_query.register(
    parameters.toggle_photo_locations,
    F.data.startswith("toggle_photo_location"),
    StateFilter(TravelForm.waiting_for_photo_locations)
)
dp.callback_query.register(
    parameters.confirm_photo_locations,
    F.data == "confirm_photo_locations",
    StateFilter(TravelForm.waiting_for_photo_locations)
)
dp.callback_query.register(
    parameters.toggle_cuisine,
    F.data.startswith("toggle_cuisine"),
    StateFilter(TravelForm.waiting_for_cuisine)
)
dp.callback_query.register(
    parameters.confirm_cuisine,
    F.data == "confirm_cuisine",
    StateFilter(TravelForm.waiting_for_cuisine)
)
dp.callback_query.register(
    parameters.process_first_time,
    F.data.startswith("first_time:"),
    StateFilter(TravelForm.waiting_for_first_time)
)
dp.message.register(
    currency.process_currency_location,
    StateFilter(TravelForm.waiting_for_currency_location),
    F.content_type.in_(["text", "location"])
)
dp.message.register(
    parameters.finish_parameters_collection,
    StateFilter(TravelForm.waiting_for_photo_locations, TravelForm.waiting_for_cuisine)
)

dp.message.register(fallback.fallback_message_handler)

async def main():
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    await set_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
