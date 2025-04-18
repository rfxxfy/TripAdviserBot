from collections import deque
from aiogram import types
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from database.db import is_user_admin, get_all_users, set_user_admin
from states.travel_states import TravelForm
from keyboards.inline_keyboards import get_admin_menu_keyboard, get_back_to_main_keyboard

async def show_admin_menu(callback_query: types.CallbackQuery):
    """
    Показывает меню админа (вторая страница клавиатуры).
    """
    if not is_user_admin(callback_query.from_user.id):
        await callback_query.answer("Недостаточно прав.", show_alert=True)
        return

    await callback_query.message.edit_reply_markup(
        reply_markup=get_admin_menu_keyboard()
    )
    await callback_query.answer()

async def view_logs(callback_query: types.CallbackQuery):
    if not is_user_admin(callback_query.from_user.id):
        await callback_query.answer("Недостаточно прав.", show_alert=True)
        return

    try:
        with open("bot.log", "r", encoding="utf-8") as f:
            last_lines = deque(f, maxlen=20)
    except FileNotFoundError:
        await callback_query.message.answer("Файл логов не найден.", reply_markup=get_back_to_main_keyboard())
        await callback_query.answer()
        return
    except Exception as e:
        await callback_query.message.answer(f"Ошибка при чтении логов: {e}", reply_markup=get_back_to_main_keyboard())
        await callback_query.answer()
        return

    text = "".join(last_lines).strip() or "Логи пусты."
    await callback_query.message.answer(
        f"<pre>{text}</pre>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_to_main_keyboard()
    )
    await callback_query.answer()

async def clear_logs(callback_query: types.CallbackQuery):
    if not is_user_admin(callback_query.from_user.id):
        await callback_query.answer("Недостаточно прав.", show_alert=True)
        return

    try:
        open("bot.log", "w", encoding="utf-8").close()
        await callback_query.message.answer(
            "🗑️ Логи успешно очищены.",
            reply_markup=get_back_to_main_keyboard()
        )
    except Exception as e:
        await callback_query.message.answer(
            f"Ошибка при очистке логов: {e}",
            reply_markup=get_back_to_main_keyboard()
        )
    finally:
        await callback_query.answer()

async def view_users(callback_query: types.CallbackQuery):
    if not is_user_admin(callback_query.from_user.id):
        await callback_query.answer("Недостаточно прав.", show_alert=True)
        return

    users = get_all_users(limit=100)
    if not users:
        await callback_query.message.answer(
            "Пользователи не найдены.",
            reply_markup=get_back_to_main_keyboard()
        )
        await callback_query.answer()
        return

    lines = []
    for u in users:
        uid = u["user_id"]
        username = f"@{u['username']}" if u['username'] else "—"
        name = f"{u['first_name'] or ''} {u['last_name'] or ''}".strip() or "—"
        admin_flag = "✅" if u['is_admin'] else "❌"
        lines.append(f"ID: <b>{uid}</b>, {username}, {name}, Admin: {admin_flag}")

    text = "\n".join(lines)
    chunks = [text[i:i+3800] for i in range(0, len(text), 3800)]
    for idx, chunk in enumerate(chunks):
        if idx == len(chunks) - 1:
            await callback_query.message.answer(
                chunk,
                parse_mode=ParseMode.HTML,
                reply_markup=get_back_to_main_keyboard()
            )
        else:
            await callback_query.message.answer(
                chunk,
                parse_mode=ParseMode.HTML
            )
    await callback_query.answer()

async def make_admin(callback_query: types.CallbackQuery, state: FSMContext):
    if not is_user_admin(callback_query.from_user.id):
        await callback_query.answer("Недостаточно прав.", show_alert=True)
        return

    await callback_query.message.answer(
        "Введите ID пользователя, которого хотите назначить администратором.",
        reply_markup=get_back_to_main_keyboard()
    )
    await TravelForm.waiting_for_admin_id.set()
    await callback_query.answer()

async def process_set_admin(message: types.Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        await message.answer("Недостаточно прав.")
        await state.finish()
        return

    try:
        target_user_id = int(message.text)
        set_user_admin(target_user_id, True)
        await message.answer(
            f"Пользователь с ID <b>{target_user_id}</b> успешно назначен администратором.",
            parse_mode=ParseMode.HTML,
            reply_markup=get_back_to_main_keyboard()
        )
    except ValueError:
        await message.answer(
            "Ошибка! Введите корректный числовой ID.",
            reply_markup=get_back_to_main_keyboard()
        )
    finally:
        await state.finish()