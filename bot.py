import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
# =========================
# НАСТРОЙКИ
# =========================
TOKEN = os.getenv("BOT_TOKEN")
PROXY = os.getenv("BOT_PROXY")
if not TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN")
if PROXY:
    session = AiohttpSession(proxy=PROXY)
else:
    session = AiohttpSession()
bot = Bot(
    token=TOKEN,
    session=session
)
dp = Dispatcher()
# =========================
# ГЛАВНОЕ МЕНЮ
# =========================
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
# =========================
# МЕНЮ ИНФОРМАЦИИ
# =========================
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
# =========================
# КНОПКА НАЗАД
# =========================
def back_button():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="◀️ Назад",
        callback_data="info"
    )
    return kb.as_markup()
# =========================
# /START
# =========================
@dp.message(CommandStart())
async def start(message: Message):
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
# =========================
# ИНФОРМАЦИЯ
# =========================
@dp.callback_query(F.data == "info")
async def information(callback: CallbackQuery):
    await callback.message.edit_text(
        "VIX Help — Проекты\n\n"
        "Выберите интересующий Вас раздел:",
        reply_markup=info_menu()
    )
    await callback.answer()
# =========================
# НАЗАД
# =========================
@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
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
# =========================
# БИЗНЕС
# =========================
@dp.callback_query(F.data == "business")
async def business(callback: CallbackQuery):
    await callback.message.edit_text(
        "💼 Бизнес\n\n"
        "Здесь будет информация о бизнес-направлении VIX.",
        reply_markup=back_button()
    )
    await callback.answer()
# =========================
# SECURITY
# =========================
@dp.callback_query(F.data == "security")
async def security(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛡 VIX Security System\n\n"
        "Здесь будет подробная информация о VIX Security System.",
        reply_markup=back_button()
    )
    await callback.answer()
# =========================
# GAME CLUB
# =========================
@dp.callback_query(F.data == "gameclub")
async def gameclub(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎮 VIX Game Club\n\n"
        "Здесь будет подробная информация о VIX Game Club.",
        reply_markup=back_button()
    )
    await callback.answer()
# =========================
# CARHUB
# =========================
@dp.callback_query(F.data == "carhub")
async def carhub(callback: CallbackQuery):
    await callback.message.edit_text(
        "🚗 VIX CarHub\n\n"
        "Здесь будет подробная информация о VIX CarHub.",
        reply_markup=back_button()
    )
    await callback.answer()
# =========================
# О НАС
# =========================
@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.message.edit_text(
        "👤 О нас\n\n"
        "Здесь будет информация о VIX и нашей команде.",
        reply_markup=back_button()
    )
    await callback.answer()
# =========================
# ОБРАТНАЯ СВЯЗЬ
# =========================
@dp.callback_query(F.data == "feedback")
async def feedback(callback: CallbackQuery):
    await callback.message.edit_text(
        "💬 Обратная связь\n\n"
        "Здесь будут указаны контакты для связи с командой VIX.",
        reply_markup=back_button()
    )
    await callback.answer()
# =========================
# ЗАПУСК
# =========================
async def main():
    print("VIX Help запускается...")
    if PROXY:
        print("Прокси включён.")
    else:
        print("Прокси не используется.")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
