import aiohttp
import requests
import json
from datetime import datetime

from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types

router = Router()


@router.message(Command('category_search_random'))
async def start_search(message: Message, command: CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы")
        return
    await state.set_data({'quantity': int(command.args)})
    response = requests.get('https://www.themealdb.com/api/json/v1/1/list.php?c=list')
    response_text = json.loads(response.text)['meals']
    meals_list = []
    for item in response_text:
        meals_list.append(item.get('strCategory'))
    builder = ReplyKeyboardBuilder()
    for meals_item in meals_list:
        builder.add(types.KeyboardButton(text=meals_item))
    await message.answer(f'Выберите категорию блюд:',
                             reply_markup=builder.as_markup(resize_keyboard=True),)
