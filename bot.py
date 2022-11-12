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
from pyrogram.errors.exceptions.bad_request_400 import PhotoCropSizeSmall

from main import parser, sender_with_photo, new_first_name, new_photo, new_last_name, add_user_to_chat
import os
import sys


class GetChanal(StatesGroup):
    get_chanal = State()


class Sender(StatesGroup):
    get_users = State()
    get_text = State()


class NewFirstName(StatesGroup):
    get_name = State()


class NewLastName(StatesGroup):
    get_name = State()


class NewPhoto(StatesGroup):
    get_photo = State()


class PhotoToSend(StatesGroup):
    get_photo = State()


class AddToChat(StatesGroup):
    get_chat = State()
    get_users = State()


storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

main_board = ReplyKeyboardMarkup(resize_keyboard=True)
parse_kb = KeyboardButton("📄 Парсинг")
sender_kb = KeyboardButton("✉ Рассылка")
photo_to_send_kb = KeyboardButton("📷 Загрузить фото для рассылки")
new_first_name_kb = KeyboardButton("Установить новое имя")
new_last_name_kb = KeyboardButton("Установть новое второе имя")
new_photo_kb = KeyboardButton("Установть новую фотографию")
add_user_to_chat_kb = KeyboardButton("Добавить пользователей в чат")
main_board.add(parse_kb, sender_kb).row(new_first_name_kb, new_last_name_kb, new_photo_kb).row(photo_to_send_kb).row(
    add_user_to_chat_kb)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Приветствую в профессиональном инструменте для работы с аудиторией телеграм!",
                        reply_markup=main_board)


@dp.message_handler(commands=['fixer'])
async def process_start_command(message: types.Message):
    os.system("python3 fixer.py")
    sys.exit()
    


@dp.message_handler()
async def echo_message(msg: types.Message):
    if msg.text == "📄 Парсинг":
        await bot.send_message(msg.from_user.id, "Отправьте ссылку на чат (без https://t.me/)")
        await GetChanal.get_chanal.set()
    elif msg.text == "✉ Рассылка":
        await bot.send_message(msg.from_user.id, "Отправьте файл с никами для рассылки")
        await Sender.get_users.set()
    elif msg.text == "Установить новое имя":
        await bot.send_message(msg.from_user.id, "Введите новое имя")
        await NewFirstName.get_name.set()
    elif msg.text == "Установть новое второе имя":
        await bot.send_message(msg.from_user.id, "Введите второе имя")
        await NewLastName.get_name.set()
    elif msg.text == "Установть новую фотографию":
        await bot.send_message(msg.from_user.id, "Отправьте новое фото")
        await NewPhoto.get_photo.set()
    elif msg.text == "📷 Загрузить фото для рассылки":
        await bot.send_message(msg.from_user.id, "Отправьте фото которое будет рассылаться вместе с текстом")
        await PhotoToSend.get_photo.set()
    elif msg.text == "Добавить пользователей в чат":
        await bot.send_message(msg.from_user.id, "Отправьте ссылку на чат (без https://t.me/)")
        await AddToChat.get_chat.set()


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
    await sender_with_photo(text)
    await bot.send_message(message.from_user.id, "Расслыка окончена")


@dp.message_handler(state=NewFirstName.get_name)
async def get_new_first_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.finish()
    await new_first_name(name)
    await bot.send_message(message.from_user.id, "Новое имя установлено")


@dp.message_handler(state=NewLastName.get_name)
async def get_new_first_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.finish()
    await new_last_name(name)
    await bot.send_message(message.from_user.id, "Новое второе имя установлено")


@dp.message_handler(state=NewPhoto.get_photo, content_types=['photo'])
async def get_new_photo(message: types.Message, state: FSMContext):
    await message.photo[-1].download('./user_photo.jpg')
    await state.finish()
    try:
        await new_photo()
        await bot.send_message(message.from_user.id, "Новое фото установлено")
    except PhotoCropSizeSmall:
        await bot.send_message(message.from_user.id, "Фотография слишком маленькая")


@dp.message_handler(state=PhotoToSend.get_photo, content_types=['photo'])
async def get_photo_to_send(message: types.Message, state: FSMContext):
    await message.photo[-1].download('./photo_to_send.jpg')
    await state.finish()
    await bot.send_message(message.from_user.id, "Фото добавлено и будет рассылаться вместе с текстом")


@dp.message_handler(state=AddToChat.get_chat)
async def get_chat_name(message: types.Message, state: FSMContext):
    await state.update_data(chanal_name=message.text)
    await bot.send_message(message.from_user.id, "Отпрьвте файл с никами")
    await AddToChat.get_users.set()


@dp.message_handler(state=AddToChat.get_users, content_types=['document'])
async def get_users_to_chat(message: types.Message, state: FSMContext):
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open("users_to_chat.txt", 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())
    await bot.send_message(message.from_user.id,
                           "Отлично!\nНики пользователей получены")
    data = await state.get_data()
    await state.finish()
    with open("users_to_chat.txt", "r") as f:
        users = f.readlines()
    for user in users:
        try:
            await add_user_to_chat(data["chanal_name"], user)
        except Exception as e:
            await bot.send_message(message.from_user.id,
                                   f"При добавлении произошли проблемы, пожалуйста перепровеьте этот ник")
            await bot.send_message(message.from_user.id, f"Exeption: {e}")

    await bot.send_message(message.from_user.id, "Работа окончена")


if __name__ == '__main__':
    executor.start_polling(dp)
