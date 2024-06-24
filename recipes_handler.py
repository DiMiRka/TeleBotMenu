import aiohttp
from random import choices
from googletrans import Translator
import re

from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types

router = Router()
translator = Translator()


class OrderWeather(StatesGroup):
    waiting_for_category = State()
    waiting_for_meals = State()


@router.message(Command('category_search_random'))
async def start_search(message: Message, command: CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы")
        return
    try:
        int(command.args)
    except ValueError:
        await message.answer(
            "Ошибка: введите численное значение")
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(url='https://www.themealdb.com/api/json/v1/1/list.php?c=list') as response:
            result = await response.json()
            categories = result['meals']
            meals_list = []
            for item in categories:
                meals_list.append(item['strCategory'])
        await state.set_data({'quantity': int(command.args)})
        builder = ReplyKeyboardBuilder()
        for meals_item in meals_list:
            builder.add(types.KeyboardButton(text=meals_item))
    await message.answer(f'Выберите категорию блюд:', reply_markup=builder.as_markup(resize_keyboard=True), )
    await state.set_state(OrderWeather.waiting_for_category.state)


@router.message(OrderWeather.waiting_for_category)
async def search_meals(message: types.Message, state: FSMContext):
    qu = await state.get_data()
    qu = qu['quantity']
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f'https://www.themealdb.com/api/json/v1/1/filter.php?c={message.text}') as response:
            response = await response.json()
            result = response['meals']
            dishes = choices(result, k=qu)
            choice_list = []
            id_list = []
            for item in dishes:
                id_list.append(item['idMeal'])
                choice_list.append(translator.translate(item['strMeal'], dest='ru').text)
            await state.set_data({'meal_id': id_list})
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text='Покажи рецепты'))
        await message.answer('Мы подобрали для Вас следующие варианты: ' + ', '.join(choice_list),
                             reply_markup=builder.as_markup(resize_keyboard=True), )
        await state.set_state(OrderWeather.waiting_for_meals.state)


@router.message(OrderWeather.waiting_for_meals)
async def show(message: types.Message, state: FSMContext):
    meals_id = await state.get_data()
    meals_id = meals_id['meal_id']
    meals = []
    async with aiohttp.ClientSession() as session:
        for item in meals_id:
            async with session.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={item}') as resp:
                result = await resp.json()
                meals.append(result['meals'][0])
    for meal in meals:
        async def ans():
            name = translator.translate(meal['strMeal'], dest='ru').text
            recipe = re.sub('^\s+|\n|\r|\s+$', '', translator.translate(meal['strInstructions'], dest='ru').text)
            ingredients = []
            for key, value in meal.items():
                if 'Ingredient' in key:
                    if value != '':
                        ingredients.append(translator.translate(value, dest='ru').text)
            ingredients = ', '.join(ingredients)
            return f'{name}\n\nРецепт:\n{recipe}\n\nИнгредиенты: {ingredients}'
        await message.answer(await ans())
