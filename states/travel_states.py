from aiogram.fsm.state import StatesGroup, State

class TravelForm(StatesGroup):
    """
    Класс для описания состояний при работе с пользователем.
    """
    waiting_for_location = State()
    waiting_for_budget = State()
    waiting_for_days = State()
    waiting_for_photo_locations = State()
    waiting_for_route_selection = State()
    waiting_for_cuisine = State()
    waiting_for_feedback = State()
    waiting_for_first_time = State()
    waiting_for_currency_location = State()
    waiting_for_admin_id = State()