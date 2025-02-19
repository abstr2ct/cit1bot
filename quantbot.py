import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Sticker
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = '7681732840:AAH21CATzaJNXfIDOyxyWXJy5APw_IAAocA'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class UserStates(StatesGroup):
    waiting_for_registration = State()
    waiting_for_name = State()
    waiting_for_password = State()
    waiting_for_phone = State()
    checking_password = State()

users_db = {}


@dp.message(Command('start'))
async def start(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Чтобы начать регистрацию, напишите 'регистрация' или 'отказ'. Если вы хотите пропустить, напишите 'отказ'."
    )
    await state.set_state(UserStates.waiting_for_registration)


@dp.message(UserStates.waiting_for_registration)
async def handle_registration(message: Message, state: FSMContext):
    if message.text.lower() == "отказ":
        await message.answer("Регистрация отменена.")
        await state.clear()
        return
    elif message.text.lower() == "регистрация":
        await message.answer("Отлично! Теперь введите ваше имя.")
        await state.set_state(UserStates.waiting_for_name)
    else:
        await message.answer("Пожалуйста, напишите 'регистрация' или 'отказ'.")
        return


@dp.message(UserStates.waiting_for_name)
async def handle_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Имя сохранено. Теперь введите ваш пароль.")
    await state.set_state(UserStates.waiting_for_password)


@dp.message(UserStates.waiting_for_password)
async def handle_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer(
        "Пароль сохранен. Теперь отправьте свой номер телефона.")
    await state.set_state(UserStates.waiting_for_phone)


@dp.message(UserStates.waiting_for_phone)
async def handle_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    user_data = await state.get_data()
    users_db[message.from_user.id] = {
        'name': user_data['name'],
        'password': user_data['password'],
        'phone': user_data['phone']
    }
    await message.answer(
        "Вы успешно зарегистрированы! Теперь можете использовать команду /pull для получения доступа."
    )
    await state.clear()


@dp.message(Command('pull'))
async def pull(message: Message, state: FSMContext):
    await message.answer("Введите ваше имя пользователя:")
    await state.set_state(UserStates.checking_password)


@dp.message(UserStates.checking_password)
async def check_password(message: Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.answer("Введите ваш пароль:")
    await state.set_state(UserStates.waiting_for_password)


@dp.message(UserStates.waiting_for_password)
async def validate_password(message: Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    username = user_data.get('username')
    if username in users_db and users_db[username]['password'] == password:
        await message.answer("Пароль верный! Вот ваш стикер:")
        await bot.send_sticker(
            message.chat.id,
            "CAACAgIAAxkBAAEB3J9fkdgVjFiXDJYH_xEej1hH4QshqgACmQsAAlMebQ3y57W7oxu9cAI"
        )
    else:
        await message.answer(
            "Неверное имя пользователя или пароль. Попробуйте снова.")
        await state.clear()


if __name__ == '__main__':
    dp.run_polling(bot)
