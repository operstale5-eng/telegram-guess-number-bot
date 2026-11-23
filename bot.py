import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

secret_number = 0
attempts = 0  # НОВОЕ: Счётчик попыток игрока

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global secret_number, attempts  # НОВОЕ: Разрешаем менять обе переменные
    secret_number = random.randint(1, 100)
    attempts = 0  # НОВОЕ: Сбрасываем попытки в ноль при новой игре
    
    await message.answer(
        "🎲 Новая игра началась!\n"
        "Я загадал случайное число от 1 до 100.\n"
        "Попробуй угадать его за минимальное число попыток! Пиши число:"
    )

@dp.message()
async def game_handler(message: types.Message):
    global attempts, secret_number  # Теперь можно менять обе переменные!

    
    if secret_number == 0:
        await message.answer("Сначала нажми /start, чтобы я загадал число! 🎲")
        return

    if message.text.isdigit():
        guess = int(message.text)
        attempts += 1  # НОВОЕ: Прибавляем +1 к попыткам за каждый ход!
        
        if guess == secret_number:
            await message.answer(
                f"🎉 ПОБЕДА! Ты угадал число {secret_number}!\n"
                f"🏆 Потрачено попыток: {attempts}\n\n"
                "Нажми /start, чтобы сыграть ещё раз."
            )
            secret_number = 0  # НОВОЕ: Обнуляем игру, чтобы после победы нельзя было спамить числами
        elif guess > secret_number:
            await message.answer(f"📉 Моё число МЕНЬШЕ. (Попытка №{attempts})")
        else:
            await message.answer(f"📈 Моё число БОЛЬШЕ. (Попытка №{attempts})")
    else:
        await message.answer("Пиши только числа от 1 до 100! 🔢")

async def main():
    print("Финальная версия игры запущена...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
