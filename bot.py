import asyncio
import random
import sqlite3  # 1. Подключаем встроенную базу данных SQLite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "YOUR_TOKEN_HERE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. Создаём базу данных и таблицу рекордов при запуске программы
conn = sqlite3.connect("game.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        user_id INTEGER PRIMARY KEY,
        best_score INTEGER
    )
""")
conn.commit()

# Словарь для хранения активных игр каждого игрока (чтобы друзья не мешали друг другу)
games = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    # Создаём личную игру для конкретного пользователя
    games[user_id] = {
        "secret": random.randint(1, 100),
        "attempts": 0
    }
    
    # Проверяем в базе данных, есть ли у игрока старый рекорд
    cursor.execute("SELECT best_score FROM records WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    record_text = f"Твой лучший рекорд: {row[0]} попыток. 🏆" if row else "У тебя пока нет рекордов. Сыграем!"
    
    await message.answer(
        f"🎲 Новая игра началась!\n{record_text}\n\n"
        "Я загадал число от 1 до 100. Попробуй угадать:"
    )

@dp.message()
async def game_handler(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in games:
        await message.answer("Сначала нажми /start, чтобы начать новую игру! 🎲")
        return

    if message.text.isdigit():
        guess = int(message.text)
        games[user_id]["attempts"] += 1
        
        secret = games[user_id]["secret"]
        attempts = games[user_id]["attempts"]
        
        if guess == secret:
            # Достаём прошлый рекорд из базы
            cursor.execute("SELECT best_score FROM records WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            # Если рекорда не было ИЛИ текущие попытки меньше старого рекорда — обновляем базу!
            if row is None or attempts < row[0]:
                cursor.execute("INSERT OR REPLACE INTO records (user_id, best_score) VALUES (?, ?)", (user_id, attempts))
                conn.commit()
                record_msg = "🔥 НОВЫЙ ЛИЧНЫЙ РЕКОРД! Я записал его в базу данных!"
            else:
                record_msg = f"Твой прошлый рекорд ({row[0]} попыток) пока не побит."

            await message.answer(
                f"🎉 ПОБЕДА! Загаданное число: {secret}\n"
                f"Попыток затрачено: {attempts}\n"
                f"{record_msg}\n\n"
                "Нажми /start для новой игры."
            )
            # Удаляем завершённую игру из памяти
            del games[user_id]
            
        elif guess > secret:
            await message.answer(f"📉 Моё число МЕНЬШЕ. (Попытка №{attempts})")
        else:
            await message.answer(f"📈 Моё число БОЛЬШЕ. (Попытка №{attempts})")
    else:
        await message.answer("Пиши только числа от 1 до 100! 🔢")

async def main():
    print("Бот с базой данных SQLite запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
