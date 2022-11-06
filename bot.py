from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from main import parser, sender
import asyncio


class GetChanal(StatesGroup):
    get_chanal = State()


class Sender(StatesGroup):
    get_users = State()
    get_text = State()


storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

main_board = ReplyKeyboardMarkup(resize_keyboard=True)
parse_kb = KeyboardButton("📄 Парсинг")
sender_kb = KeyboardButton("✉ Рассылка")
main_board.add(parse_kb, sender_kb)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Приветствую в профессиональном инструменте для работы с аудиторией телеграм!",
                        reply_markup=main_board)


@dp.message_handler()
async def echo_message(msg: types.Message):
    if msg.text == "📄 Парсинг":
        await bot.send_message(msg.from_user.id, "Отправьте ссылку на чат (без https://t.me/)")
        await GetChanal.get_chanal.set()
    elif msg.text == "✉ Рассылка":
        await bot.send_message(msg.from_user.id, "Отправьте файл с никами для рассылки")
        await Sender.get_users.set()


@dp.message_handler(state=GetChanal.get_chanal)
async def get_chanal_handler(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Парсинг начался, это займет какое то время")
    chanal = message.text
    try:
        await parser(chanal)
        await bot.send_document(message.from_user.id, open(f"{chanal}_members.txt", 'rb'))
    except Exception as e:
        await bot.send_message(message.from_user.id, "Ошибка при вводе чата")
    await state.finish()


@dp.message_handler(state=Sender.get_users, content_types=['document'])
async def get_users_to_send(message: types.Message, state: FSMContext):
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open("users_to_spam.txt", 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())
    await bot.send_message(message.from_user.id,
                           "Отлично!\nНики пользователей получены\n\nОтправьте текст который будет рассылаться")
    await state.finish()
    await Sender.get_text.set()


@dp.message_handler(state=Sender.get_text)
async def get_users_to_send(message: types.Message, state: FSMContext):
    text = message.text
    await state.finish()
    await bot.send_message(message.from_user.id, "Рассылка началась")
    await sender(text)
    await bot.send_message(message.from_user.id, "Расслыка окончена")


if __name__ == '__main__':
    executor.start_polling(dp)
