import os
import asyncio
import json

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


# =========================================================
# НАСТРОЙКИ
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")
PROXY = os.getenv("BOT_PROXY")

# Первый администратор задаётся здесь через переменную окружения.
# Например:
# set ADMIN_IDS=123456789
#
# Если администраторов несколько:
# set ADMIN_IDS=123456789,987654321

ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")

if not TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN")

if not ADMIN_IDS_RAW:
    raise RuntimeError("Не задан ADMIN_IDS")

ADMIN_IDS = set()

for admin_id in ADMIN_IDS_RAW.split(","):
    admin_id = admin_id.strip()

    if admin_id.isdigit():
        ADMIN_IDS.add(int(admin_id))


if not ADMIN_IDS:
    raise RuntimeError("ADMIN_IDS содержит некорректный Telegram ID")


# =========================================================
# ФАЙЛЫ ДАННЫХ
# =========================================================

USERS_FILE = "users.json"
ADMINS_FILE = "admins.json"


def load_json(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)
    except Exception:
        pass

    return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


# Загружаем пользователей
users = load_json(USERS_FILE, [])

# Загружаем дополнительных админов
saved_admins = load_json(ADMINS_FILE, [])

for admin_id in saved_admins:
    try:
        ADMIN_IDS.add(int(admin_id))
    except:
        pass


def save_admins():
    save_json(
        ADMINS_FILE,
        list(ADMIN_IDS)
    )


def save_users():
    save_json(
        USERS_FILE,
        users
    )


def register_user(user_id):
    if user_id not in users:
        users.append(user_id)
        save_users()


# =========================================================
# BOT
# =========================================================

if PROXY:
    session = AiohttpSession(proxy=PROXY)
else:
    session = AiohttpSession()


bot = Bot(
    token=TOKEN,
    session=session
)

dp = Dispatcher(
    storage=MemoryStorage()
)


# =========================================================
# СОСТОЯНИЯ
# =========================================================

class FeedbackState(StatesGroup):
    waiting_message = State()


class BroadcastState(StatesGroup):
    waiting_message = State()


class ReplyState(StatesGroup):
    waiting_message = State()


class AddAdminState(StatesGroup):
    waiting_id = State()


# =========================================================
# ПРОВЕРКА АДМИНА
# =========================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS


# =========================================================
# ГЛАВНОЕ МЕНЮ
# =========================================================

def main_menu():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📋 Информация",
        callback_data="info"
    )

    kb.button(
        text="💬 Обратная связь",
        callback_data="feedback"
    )

    kb.adjust(1)

    return kb.as_markup()


# =========================================================
# МЕНЮ ИНФОРМАЦИИ
# =========================================================

def info_menu():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="💼 Бизнес",
        callback_data="business"
    )

    kb.button(
        text="🛡 VIX Security System",
        callback_data="security"
    )

    kb.button(
        text="🎮 VIX Game Club",
        callback_data="gameclub"
    )

    kb.button(
        text="🚗 VIX CarHub",
        callback_data="carhub"
    )

    kb.button(
        text="👤 О нас",
        callback_data="about"
    )

    kb.button(
        text="◀️ Назад",
        callback_data="back"
    )

    kb.adjust(1)

    return kb.as_markup()


# =========================================================
# КНОПКА НАЗАД
# =========================================================

def back_button():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="◀️ Назад",
        callback_data="info"
    )

    return kb.as_markup()


# =========================================================
# АДМИН-ПАНЕЛЬ
# =========================================================

def admin_menu():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📢 Рассылка",
        callback_data="admin_broadcast"
    )

    kb.button(
        text="👥 Пользователи",
        callback_data="admin_users"
    )

    kb.button(
        text="👑 Администраторы",
        callback_data="admin_admins"
    )

    kb.button(
        text="➕ Добавить администратора",
        callback_data="admin_add"
    )

    kb.adjust(1)

    return kb.as_markup()


# =========================================================
# /START
# =========================================================

@dp.message(CommandStart())
async def start(message: Message):

    register_user(message.from_user.id)

    text = (
        "VIX Help\n\n"
        "Здравствуйте! Если Вам нужна подробная информация "
        "о наших проектах, нажмите на кнопку «Информация».\n\n"
        "Если нужна обратная связь, нажмите на кнопку "
        "«Обратная связь»."
    )

    await message.answer(
        text,
        reply_markup=main_menu()
    )


# =========================================================
# /ADMIN
# =========================================================

@dp.message(Command("admin"))
async def admin_command(message: Message):

    register_user(message.from_user.id)

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ У вас нет доступа к админ-панели."
        )
        return

    await message.answer(
        "👑 VIX Help — Админ-панель\n\n"
        "Выберите действие:",
        reply_markup=admin_menu()
    )


# =========================================================
# ИНФОРМАЦИЯ
# =========================================================

@dp.callback_query(F.data == "info")
async def information(callback: CallbackQuery):

    register_user(callback.from_user.id)

    await callback.message.edit_text(
        "VIX Help — Проекты\n\n"
        "Выберите интересующий Вас раздел:",
        reply_markup=info_menu()
    )

    await callback.answer()


# =========================================================
# НАЗАД
# =========================================================

@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):

    register_user(callback.from_user.id)

    text = (
        "VIX Help\n\n"
        "Здравствуйте! Если Вам нужна подробная информация "
        "о наших проектах, нажмите на кнопку «Информация».\n\n"
        "Если нужна обратная связь, нажмите на кнопку "
        "«Обратная связь»."
    )

    await callback.message.edit_text(
        text,
        reply_markup=main_menu()
    )

    await callback.answer()


# =========================================================
# БИЗНЕС
# =========================================================

@dp.callback_query(F.data == "business")
async def business(callback: CallbackQuery):

    await callback.message.edit_text(
        "💼 Бизнес\n\n"
        "Здесь будет информация о бизнес-направлении VIX.",
        reply_markup=back_button()
    )

    await callback.answer()


# =========================================================
# SECURITY
# =========================================================

@dp.callback_query(F.data == "security")
async def security(callback: CallbackQuery):

    await callback.message.edit_text(
        "🛡 VIX Security System\n\n"
        "Здесь будет подробная информация о VIX Security System.",
        reply_markup=back_button()
    )

    await callback.answer()


# =========================================================
# GAME CLUB
# =========================================================

@dp.callback_query(F.data == "gameclub")
async def gameclub(callback: CallbackQuery):

    await callback.message.edit_text(
        "🎮 VIX Game Club\n\n"
        "Здесь будет подробная информация о VIX Game Club.",
        reply_markup=back_button()
    )

    await callback.answer()


# =========================================================
# CARHUB
# =========================================================

@dp.callback_query(F.data == "carhub")
async def carhub(callback: CallbackQuery):

    await callback.message.edit_text(
        "🚗 VIX CarHub\n\n"
        "Здесь будет подробная информация о VIX CarHub.",
        reply_markup=back_button()
    )

    await callback.answer()


# =========================================================
# О НАС
# =========================================================

@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):

    await callback.message.edit_text(
        "👤 О нас\n\n"
        "Здесь будет информация о VIX и нашей команде.",
        reply_markup=back_button()
    )

    await callback.answer()


# =========================================================
# ОБРАТНАЯ СВЯЗЬ — НАЧАЛО
# =========================================================

@dp.callback_query(F.data == "feedback")
async def feedback(callback: CallbackQuery, state: FSMContext):

    register_user(callback.from_user.id)

    await state.set_state(
        FeedbackState.waiting_message
    )

    await callback.message.edit_text(
        "💬 Обратная связь\n\n"
        "Напишите сообщение, которое хотите отправить "
        "команде VIX.\n\n"
        "Для отмены отправьте /cancel"
    )

    await callback.answer()


# =========================================================
# ОБРАТНАЯ СВЯЗЬ — ПОЛУЧЕНИЕ СООБЩЕНИЯ
# =========================================================

@dp.message(FeedbackState.waiting_message)
async def feedback_message(
    message: Message,
    state: FSMContext
):

    if message.text == "/cancel":

        await state.clear()

        await message.answer(
            "❌ Обратная связь отменена.",
            reply_markup=main_menu()
        )

        return

    user_id = message.from_user.id

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "нет username"
    )

    admin_text = (
        "📩 НОВАЯ ОБРАТНАЯ СВЯЗЬ\n\n"
        f"👤 Пользователь: {message.from_user.full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 Telegram ID: `{user_id}`\n\n"
        "💬 Сообщение:\n"
        f"{message.text or '[не текстовое сообщение]'}"
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="↩️ Ответить",
        callback_data=f"reply:{user_id}"
    )

    kb.adjust(1)

    for admin_id in ADMIN_IDS:

        try:
            await bot.send_message(
                admin_id,
                admin_text,
                reply_markup=kb.as_markup(),
                parse_mode="Markdown"
            )

        except Exception as error:

            print(
                f"Не удалось отправить уведомление админу "
                f"{admin_id}: {error}"
            )

    await state.clear()

    await message.answer(
        "✅ Сообщение отправлено команде VIX.\n\n"
        "Спасибо за обратную связь!",
        reply_markup=main_menu()
    )


# =========================================================
# ОТВЕТ ПОЛЬЗОВАТЕЛЮ
# =========================================================

@dp.callback_query(F.data.startswith("reply:"))
async def reply_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )

        return

    try:
        user_id = int(
            callback.data.split(":")[1]
        )
    except:
        await callback.answer(
            "Ошибка ID пользователя.",
            show_alert=True
        )
        return

    await state.update_data(
        reply_user_id=user_id
    )

    await state.set_state(
        ReplyState.waiting_message
    )

    await callback.message.answer(
        f"↩️ Ответ пользователю `{user_id}`\n\n"
        "Напишите сообщение для пользователя.\n\n"
        "Для отмены: /cancel",
        parse_mode="Markdown"
    )

    await callback.answer()


@dp.message(ReplyState.waiting_message)
async def reply_send(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    if message.text == "/cancel":

        await state.clear()

        await message.answer(
            "❌ Ответ отменён."
        )

        return

    data = await state.get_data()

    user_id = data.get("reply_user_id")

    if not user_id:

        await state.clear()

        await message.answer(
            "❌ Пользователь не найден."
        )

        return

    try:

        await bot.send_message(
            user_id,
            "💬 Сообщение от команды VIX:\n\n"
            f"{message.text}"
        )

        await message.answer(
            "✅ Ответ отправлен."
        )

    except Exception as error:

        await message.answer(
            "❌ Не удалось отправить сообщение.\n\n"
            f"{error}"
        )

    await state.clear()


# =========================================================
# АДМИН — РАССЫЛКА
# =========================================================

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )

        return

    await state.set_state(
        BroadcastState.waiting_message
    )

    await callback.message.answer(
        "📢 РАССЫЛКА\n\n"
        "Напишите сообщение, которое получат все "
        f"пользователи бота.\n\n"
        f"👥 Получателей: {len(users)}\n\n"
        "Для отмены: /cancel"
    )

    await callback.answer()


@dp.message(BroadcastState.waiting_message)
async def broadcast_send(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    if message.text == "/cancel":

        await state.clear()

        await message.answer(
            "❌ Рассылка отменена."
        )

        return

    await message.answer(
        "📢 Рассылка началась..."
    )

    success = 0
    failed = 0

    for user_id in users:

        try:

            await bot.send_message(
                user_id,
                message.text
            )

            success += 1

            await asyncio.sleep(0.05)

        except Exception as error:

            failed += 1

            print(
                f"Ошибка отправки {user_id}: {error}"
            )

    await state.clear()

    await message.answer(
        "📊 Результат рассылки\n\n"
        f"✅ Отправлено: {success}\n"
        f"❌ Ошибок: {failed}\n"
        f"👥 Всего: {len(users)}"
    )


# =========================================================
# АДМИН — ПОЛЬЗОВАТЕЛИ
# =========================================================

@dp.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )

        return

    await callback.message.answer(
        "👥 Пользователи\n\n"
        f"Всего пользователей: {len(users)}"
    )

    await callback.answer()


# =========================================================
# АДМИН — СПИСОК АДМИНОВ
# =========================================================

@dp.callback_query(F.data == "admin_admins")
async def admin_admins(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )

        return

    text = "👑 Администраторы:\n\n"

    for admin_id in ADMIN_IDS:
        text += f"🆔 `{admin_id}`\n"

    await callback.message.answer(
        text,
        parse_mode="Markdown"
    )

    await callback.answer()


# =========================================================
# АДМИН — ДОБАВИТЬ АДМИНА
# =========================================================

@dp.callback_query(F.data == "admin_add")
async def admin_add(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):

        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )

        return

    await state.set_state(
        AddAdminState.waiting_id
    )

    await callback.message.answer(
        "➕ Добавление администратора\n\n"
        "Отправьте Telegram ID нового администратора.\n\n"
        "Например:\n"
        "123456789\n\n"
        "Для отмены: /cancel"
    )

    await callback.answer()


@dp.message(AddAdminState.waiting_id)
async def admin_add_process(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    if message.text == "/cancel":

        await state.clear()

        await message.answer(
            "❌ Добавление отменено."
        )

        return

    if not message.text.isdigit():

        await message.answer(
            "❌ Некорректный Telegram ID.\n\n"
            "Отправьте только цифры."
        )

        return

    new_admin_id = int(message.text)

    ADMIN_IDS.add(new_admin_id)

    save_admins()

    await state.clear()

    await message.answer(
        "✅ Администратор добавлен.\n\n"
        f"🆔 ID: `{new_admin_id}`",
        parse_mode="Markdown"
    )

    try:

        await bot.send_message(
            new_admin_id,
            "👑 Вам предоставлен доступ "
            "к админ-панели VIX Help.\n\n"
            "Используйте команду /admin."
        )

    except Exception as error:

        print(
            f"Не удалось уведомить нового админа: {error}"
        )


# =========================================================
# ОТМЕНА
# =========================================================

@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state:

        await state.clear()

        await message.answer(
            "❌ Действие отменено.",
            reply_markup=main_menu()
        )

    else:

        await message.answer(
            "Сейчас нет активного действия."
        )


# =========================================================
# ЗАПУСК
# =========================================================

async def main():

    print("VIX Help запускается...")

    if PROXY:
        print("Прокси включён.")
    else:
        print("Прокси не используется.")

    print(
        "Администраторы:",
        ", ".join(
            str(admin_id)
            for admin_id in ADMIN_IDS
        )
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
