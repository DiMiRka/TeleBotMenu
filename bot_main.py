import asyncio

import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section)

from token_data import TOKEN

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = [
        [
            types.KeyboardButton(text="Начать"),
            types.KeyboardButton(text="Что делает бот?"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer('Привет! Начнём?', reply_markup=keyboard)


@dp.message(F.text.lower() == 'что делает бот?')
async def description(message: types.Message):
    await message.answer("Этот бот предоставляет рецепты на основании выбранной категории блюд")

@dp.message(F.text.lower() == "начать")
async def start_bot(message: types.message):
    await message.answer('Введите команду /category_search_random и количество желаемых рецептов')

async def main() -> None:
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
