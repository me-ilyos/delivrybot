import asyncio
import logging
import csv
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Message
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config_reader import config
from emoji import replace_emoji


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())

dp = Dispatcher()

WELCOME_MESSAGE = f"<b>Hello! Welcome to 'Three Broomsticks' delivery service.</b>" \
             "\n\n<b>Assalomu alaykum! 'Three Broomsticks' yetkazib berish xismatiga hush kelibsiz</b>" \
             "\n\n<b>Zdravstvuyte! Dobro Pojalovat v slujbu dostavki 'Three Broomsticks'</b>"


class OrderFood(StatesGroup):
    language = State()
    city = State()
    menu = State()


@dp.message(Command(commands=['start']))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(OrderFood.language)

    kb = [
        [types.KeyboardButton(text="🇷🇺 Russkiy"), types.KeyboardButton(text="🇬🇧 English"),
         types.KeyboardButton(text="🇺🇿 O'zbek")]
    ]

    await message.answer(WELCOME_MESSAGE, reply_markup=types.ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True
    ), parse_mode="HTML")


@dp.message(OrderFood.language)
async def process_language(message: Message, state: FSMContext, bot_data: dict):
    await state.update_data(lang=replace_emoji(message.text, '').strip())

    await state.set_state(OrderFood.city)

    offices: list[str] = []

    with open('db/offices.csv') as file:
        for row in csv.DictReader(file):
            offices.append(row['city'])

    bot_data['cities'] = offices

    builder = ReplyKeyboardBuilder()

    for i in range(len(offices)):
        builder.add(types.KeyboardButton(text=offices[i].title()))

    builder.adjust(3)

    await message.answer(text="Choose the city you live",
                         reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(OrderFood.city, F.text)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    # user_data = await state.get_data()
    await state.set_state(OrderFood.menu)
    
    kb = [
        [types.KeyboardButton(text="🍟 Order")],
        [types.KeyboardButton(text="🛒 My orders")],
        [types.KeyboardButton(text="⚙ Settings"), 
         types.KeyboardButton(text="💥 Discount")],
        [types.KeyboardButton(text="👩‍🍳 Join our team"), 
         types.KeyboardButton(text="☎ Feedback")]
    ]

    await message.answer(text="Our Menu",
                reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True))

# @dp.message(OrderFood.menu)
# async def menu():
#     pass 

async def main():
    await dp.start_polling(bot, bot_data={})

if __name__ == '__main__':
    asyncio.run(main())