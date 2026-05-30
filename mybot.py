from asyncio import run


from pymysql import IntegrityError
from aiogram import Bot, Dispatcher, F
from aiogram.filters.command import CommandStart
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from environs import Env

from weather import get_weather_date
from db import db


env = Env()
env.read_env()

TOKEN = env.str("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def say_hello(message: Message):
    fullname = message.from_user.full_name

    await message.answer(text=f"Assalomu aleykum {fullname}")
    try:
        db.register_user(
            telegram_id=str(message.from_user.id),
            fullname=message.from_user.full_name,
        )
        await message.answer(text="Muvaffaqiyatli royhatga olindingiz")
    except IntegrityError:
        user_id = db.get_user(telegram_id=message.from_user.id).get("id")
        cities = db.get_user_cities(user_id=user_id)  
        
        markup = ReplyKeyboardBuilder()
        for city in cities:
            markup.button(text=city.get('city_name'))
        markup.adjust(2)

        markup.row(
            KeyboardButton(text="🚮 Shaharlar ro'yxatini tozalash"),
        )
        await message.answer(text="Qaytganinggizdan xursandmiz", reply_markup=markup.as_markup(resize_keyboard=True))


@dp.message(F.text == "/delete_acount")
async def delete_acount(message: Message):
    telegram_id = str(message.from_user.id)
    user = db.get_user(telegram_id)

    if user:
        db.delete_user(telegram_id)
        await message.answer(text="✅ Acountingiz malumotlari bazadan ochirildi")
    else:
        await message.answer(text="❌ Siz bazada mavjud emassiz")


@dp.message(F.text == "/show_info")
async def info(message: Message):
    telegram_id = str(message.from_user.id)
    user = db.get_user(telegram_id)

    if user:
        await message.answer(text=f"""
...Siz haqingizdagi malumotlar:...

Foydalanuvchi ID:  {user['id']}
Foydalanuvchi nomi:  {user['fullname']}
Telegram_id si:  {user['telegram_id']}               
""")
    else:
        await message.answer(text="Bazadan siz haqingizdagi malumotlar topilmadi.")


@dp.message()
async def send_weather_date(message: Message):
    
    if message.text == "🚮 Shaharlar ro'yxatini tozalash":
        user_id = db.get_user(telegram_id=str(message.from_user.id)).get("id")
        db.clear_user_cities(user_id=user_id)
        
        await message.answer(
            text="Shaharlar ro'yxati tozalandi",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    
    weather_date, is_success = get_weather_date(city_name=message.text)
    
    markup = InlineKeyboardBuilder()
    markup.button(text="Shaxarni saqlab qo'yish", callback_data=f"{message.text}")

    user_id = db.get_user(telegram_id=str(message.from_user.id)).get('id') 
    user_cities = db.get_user_cities(user_id=user_id)
    
    found = False
    for city in user_cities:
        if message.text == city.get('city_name'):
            found = True
            break
    
    if is_success and not found:
        await message.answer(text=weather_date, reply_markup=markup.as_markup(),)
    else:
        await message.answer(text=weather_date)


@dp.callback_query()
async def save_city(call: CallbackQuery):
    city_name = call.data
    user_id = db.get_user(telegram_id=str(call.from_user.id)).get('id')  

    try:
        db.add_city(user_id=user_id, city_name=city_name)

        markup = InlineKeyboardBuilder()
        markup.button(text="✅ Shaxar saqlandi", callback_data=f"{city_name}")
        await call.message.edit_reply_markup(
            reply_markup=markup.as_markup(),
        )
    except Exception:
        await call.answer(text="Shaxar allaqachon qoshilgan", show_alert=True)
        return

    cities = db.get_user_cities(user_id=user_id)

    markup = ReplyKeyboardBuilder()
    for city in cities:
        markup.button(text=city.get('city_name'))
    markup.adjust(2)
    
    markup.row(
        KeyboardButton(text="🚮 Shaharlar ro'yxatini tozalash"),
    )


    await call.message.answer(
        text="Shahar muvaffaqiyatli qo'shildi ✅",
        reply_markup=markup.as_markup(resize_keyboard=True),
    )
    await call.answer(text=f"✅ '{city_name}' shahri saqlandi!", show_alert=True)  # ✅ db.save_city o'chirildi


async def main():
    db.create_users_table()
    db.create_cities_table()  
    await dp.start_polling(bot)


run(main())

