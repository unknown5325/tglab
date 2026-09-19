from aiogram import Bot, Dispatcher, types, F
import asyncio
import os
from dotenv import load_dotenv
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.filters import Command
import requests
from aiogram.fsm.state import State, StatesGroup
from transl import translate_word
import datetime
import pandas as pd
from functools import wraps

def logg():
    file_check = os.path.isfile("logs.csv")
    if file_check:
        current_id = len(pd.read_csv("logs.csv"))
    else:
        current_id = 0

    df = pd.DataFrame({"User_ID" : [], "@TG_nick": [], "Motion": [], "API": [], "DateTime": [], "API_answer": []})
    df.to_csv("logs.csv", index_label="User_ID",  mode="a", sep=",", header=not os.path.isfile("logs.csv"))

    def logger(func):
        @wraps(func)
        async def wrapper(*args):
            message = args[0]
            target = await func(*args)
            if len(target) == 2:
                link = target[0]
                ans = target[1]
            elif len(target) < 2:
                link = target
                ans = 'None'

            if func.__name__ == 'noth':
                with open("logs.csv", mode="a", encoding="utf-8") as filed:
                    filed.write(f"{message.from_user.id}, {message.from_user.username}, {'Keyboard typing'}, {link}, {datetime.datetime.now()}, {ans}\n")
            else:
                with open("logs.csv", mode="a", encoding="utf-8") as filed:
                    filed.write(f"{message.from_user.id}, {message.from_user.username}, {func.__name__}, {link}, {datetime.datetime.now()}, {ans}\n")
            return None
        return wrapper

    load_dotenv()
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    dp = Dispatcher()

    class Loading_states(StatesGroup):
        name = State()


    @dp.message(Command('start'))
    @logger
    async def start(message):
        keyboard = [
        [types.KeyboardButton(text='Случайное фото кота')],
        [types.KeyboardButton(text='Чем заняться?')],
        [types.KeyboardButton(text='Альтернативное имя героя')]
        ]
        builder = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await message.answer('Привет!', reply_markup=builder)
        return 'None', 'None'

    
    @dp.message(F.text == 'Назад')
    @logger
    async def back(message, state):
        await start(message)
        await state.clear()
        return

    
    @dp.message(F.text == 'Случайное фото кота')
    @logger
    async def cat(message):
        link = 'https://api.thecatapi.com/v1/images/search'
        try:
            responce = requests.get(link)
            json_cat = responce.json()
            ans = json_cat[0]['url']
            await message.answer(ans)
        except Exception:
            await message.answer('API не доступен')
        return link, ans
    
    @dp.message(F.text == 'Чем заняться?')
    @logger
    async def dev(message):
        link = 'https://bored-api.appbrewery.com/random'
        try:
            responce = requests.get(link)
            json_cat = responce.json()
            photo = json_cat['activity']
            ans = translate_word(photo)
            await message.answer(ans)
        except Exception:
            await message.answer('API не доступен')
        return link, ans
    
    @dp.message(F.text == 'Альтернативное имя героя')
    async def alt_name(message, state):
        new_keyboard = [
                [types.KeyboardButton(text='Назад')]
            ]
        new_builder = ReplyKeyboardMarkup(keyboard=new_keyboard, resize_keyboard=True)
        await message.answer("Введите имя", reply_markup=new_builder)
        await state.set_state(Loading_states.name)

    
    @dp.message(Loading_states.name)
    @logger
    async def alt_names(message):
        alt = message.text
        link = 'https://hp-api.onrender.com/api/characters'
        try:
            responce = requests.get(link)
            js = responce.json()
            for i in range(len(js) - 1):
                if js[i]['name'] == alt:
                    ans = ', '.join(js[i]['alternate_names'])
                    await message.answer(ans)
        except Exception:
            await message.answer('Такого персонажа нет или превышено время ождиания')
        return link, ans
    
    @dp.message()
    @logger
    async def noth(message):
        await message.answer(f'Вы написали "{message.text}", я не знаю такой команды')
        return 'None', 'None'

    async def main():
        bot = Bot(token=BOT_TOKEN)
        await dp.start_polling(bot)

    if __name__ == '__main__':
        asyncio.run(main())

logg()