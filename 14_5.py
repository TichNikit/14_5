from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *


token = ""
bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())


my_product = get_all_products()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()

@dp.message_handler(commands='start')
async def start(message):
    k = [[KeyboardButton(text='Информация'), KeyboardButton(text='Рассчитать')],
         [KeyboardButton(text='Купить'), KeyboardButton(text='Регистрация')]]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=k)
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text):
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()
    else:
        await state.update_data(username=message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    inf_user = await state.get_data()
    add_user(inf_user['username'], inf_user['email'],  inf_user['age'], balance=1000)
    await state.finish()
    await message.answer('Регистрация прошла успешно')


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    with (open('1.jpg', 'rb') as f_1, open('2.jpg', 'rb') as f_2, open('3.jpg', 'rb') as f_3,
          open('4.png', 'rb') as f_4):
        vitamins = [
            [InlineKeyboardButton(text="Витамин А", callback_data='A'),
             InlineKeyboardButton(text="Витамин B", callback_data='B'),
             InlineKeyboardButton(text="Витамин C", callback_data='C'),
             InlineKeyboardButton(text="Витамин D", callback_data='D')]
        ]
        vitamins = InlineKeyboardMarkup(inline_keyboard=vitamins)
        await message.answer_photo(f_1, f'Название: {my_product[0][1]} | '
                                        f'Описание: {my_product[0][2]} | '
                                        f'Цена: {my_product[0][3]}')
        await message.answer_photo(f_2, f'Название: {my_product[1][1]} | '
                                        f'Описание: {my_product[1][2]} | '
                                        f'Цена: {my_product[1][3]}')
        await message.answer_photo(f_3, f'Название: {my_product[2][1]} | '
                                        f'Описание: {my_product[2][2]} | '
                                        f'Цена: {my_product[2][3]}')
        await message.answer_photo(f_4, f'Название: {my_product[3][1]} | '
                                        f'Описание: {my_product[3][2]} | '
                                        f'Цена: {my_product[3][3]}')
        await message.answer('Выберете продукт для покупки', reply_markup=vitamins)


@dp.callback_query_handler(text=['A', 'B', 'C', 'D'])
async def product_buying(callback_query):
    k = [[KeyboardButton(text='Информация'), KeyboardButton(text='Рассчитать')],
         [KeyboardButton(text='Купить'), KeyboardButton(text='Регистрация')]]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=k)
    await callback_query.message.answer('Вы успешно приобрели продукт!', reply_markup=kb)
    await callback_query.answer()


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('Информация о боте')


@dp.message_handler(text='Рассчитать')
async def set_age(message):
    make_choice = [
        [InlineKeyboardButton(text="Рассчитать норму калорий", callback_data='norm'),
         InlineKeyboardButton(text="Формула расчета", callback_data='form')]
    ]
    keyboard_make_choice = InlineKeyboardMarkup(inline_keyboard=make_choice)
    await message.answer('Выберите опцию:', reply_markup=keyboard_make_choice)


@dp.callback_query_handler(text='form')
async def formm(callback_query):
    tex = [
        [types.InlineKeyboardButton(text="Формула", url='https://www.calc.ru/Formula-Mifflinasan-Zheora.html')],
    ]
    keyboard_tex = types.InlineKeyboardMarkup(inline_keyboard=tex)
    await callback_query.message.answer(
        f'Формула расчета нормы калорий:\n',
        reply_markup=keyboard_tex)
    await callback_query.answer()


@dp.callback_query_handler(text='norm')
async def nor(callback_query):
    await callback_query.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await callback_query.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    await message.answer(
        f"Ваша норма калорий {10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5}")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
