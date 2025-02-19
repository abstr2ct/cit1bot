import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7926041524:AAGu3uSEdLwIiQz6BqsZ7ufR6E6TMe3iZfs' 
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class RegistrationStates(StatesGroup):
    asking_registration = State()
    getting_username = State()
    getting_password = State()
    getting_number = State()
    getting_name = State()

class PullStates(StatesGroup):
    waiting_credentials = State()

registered_users = {} 
non_registered_users = {}  

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="Yes")],
        [types.KeyboardButton(text="No")]
    ], resize_keyboard=True, selective=True)
    await message.answer("Do you want to register?", reply_markup=markup)
    await state.set_state(RegistrationStates.asking_registration)

@dp.message(RegistrationStates.asking_registration)
async def process_registration_choice(message: types.Message, state: FSMContext):
    if message.text.lower() == "yes":
        await message.answer("Please enter your username:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.getting_username)
    elif message.text.lower() == "no":
        await message.answer("Please enter your name:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.getting_name)
    else:
        await message.answer("Please choose Yes or No.")

@dp.message(RegistrationStates.getting_username)
async def process_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Please enter your password:")
    await state.set_state(RegistrationStates.getting_password)

@dp.message(RegistrationStates.getting_password)
async def process_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer("Please enter your number:")
    await state.set_state(RegistrationStates.getting_number)

@dp.message(RegistrationStates.getting_number)
async def process_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get("username")
    password = data.get("password")
    registered_users[username] = password
    await message.answer("Registration complete! Username and password saved.")
    await state.clear()

@dp.message(RegistrationStates.getting_name)
async def process_name(message: types.Message, state: FSMContext):
    non_registered_users[message.from_user.id] = message.text
    await message.answer(f"Name '{message.text}' saved.")
    await state.clear()

@dp.message(Command("pull"))
async def cmd_pull(message: types.Message, state: FSMContext):
    await message.answer("Please send your username and password separated by a space:")
    await state.set_state(PullStates.waiting_credentials)

@dp.message(PullStates.waiting_credentials)
async def process_credentials(message: types.Message, state: FSMContext):
    credentials = message.text.split()
    if len(credentials) != 2:
        await message.answer("Invalid format. Please send: username password")
        return
    
    username, password = credentials
    if registered_users.get(username) == password:
        await message.answer_sticker("CAACAgIAAxkBAAEL3hRmFgABY9M3rC3uBwABH5Wj3mWQJQAC8iUAAjLZ0UvIOVxQd_ly9TQE")
    else:
        await message.answer("Invalid username or password.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
