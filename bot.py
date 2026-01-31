import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from database import Database

logging.basicConfig(level=logging.INFO)

# Импортируем токен из config.py (если он там есть) или используем переменную окружения
import os
try:
    from config import BOT_TOKEN, WEBAPP_URL
except ImportError:
    # Если config.py не найден, используем переменные окружения
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8390787038:AAHChRwHsSbDKHcXEqS8oJXhi0_ASUSq4P8")
    # URL веб-приложения на GitHub Pages
    WEBAPP_URL = os.getenv("WEBAPP_URL", "https://nikirir.github.io/pdd-duel-webapp")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()

def get_main_keyboard():
    # Убираем слэш в конце если есть, и добавляем /index.html
    webapp_url = f"{WEBAPP_URL.rstrip('/')}/index.html"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎮 Открыть приложение", 
            web_app=WebAppInfo(url=webapp_url)
        )],
        [InlineKeyboardButton(text="📊 Топ игроков", callback_data="top_players")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])
    return keyboard

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    logging.info(f"📝 Регистрация пользователя: ID={user_id}, username={username}, first_name={first_name}")
    
    # Получаем фото пользователя если есть
    photo_url = None
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.photos:
            file = await bot.get_file(photos.photos[0][0].file_id)
            photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
            logging.info(f"✅ Фото пользователя получено: {photo_url}")
        else:
            logging.info(f"ℹ️ У пользователя {user_id} нет фото профиля")
    except Exception as e:
        logging.warning(f"⚠️ Не удалось получить фото пользователя {user_id}: {e}")
    
    # Сохраняем/обновляем пользователя в локальной БД
    logging.info(f"💾 Сохранение пользователя в локальной БД: ID={user_id}, username={username}, first_name={first_name}, photo_url={photo_url}")
    user = db.get_or_create_user(
        user_id, 
        username, 
        first_name,
        photo_url
    )
    logging.info(f"✅ Пользователь {user_id} сохранен в локальной БД")
    
    # Также регистрируем пользователя в API сервере (Vercel)
    # Делаем это асинхронно в фоне, не блокируя отправку сообщения
    async def register_in_api():
        try:
            import aiohttp
            api_url = os.getenv("API_BASE_URL", "https://pdd-duel-webapp.vercel.app")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_url}/api/users/register",
                    json={
                        'user_id': user_id,
                        'username': username,
                        'first_name': first_name,
                        'photo_url': photo_url
                    },
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        logging.info(f"✅ Пользователь {user_id} зарегистрирован в API сервере")
                    else:
                        error_text = await response.text()
                        logging.warning(f"⚠️ Не удалось зарегистрировать пользователя {user_id} в API: {response.status} - {error_text}")
        except asyncio.TimeoutError:
            logging.warning(f"⚠️ Таймаут при регистрации пользователя {user_id} в API")
        except Exception as e:
            logging.warning(f"⚠️ Ошибка регистрации пользователя в API: {e}")
    
    # Запускаем регистрацию в фоне, не ждем её завершения
    asyncio.create_task(register_in_api())
    
    welcome_text = f"""🚗 Привет, {message.from_user.first_name or 'друг'}!

Добро пожаловать в **ПДД ДУЭЛИ**! 🎮

Подготовка к экзамену ГИБДД стала еще интереснее!

🎯 **Возможности:**
• 📚 Решение билетов ГИБДД
• 🎓 Тренировка по темам ПДД
• 🏆 Топ игроков по рейтингу
• 📊 Статистика и прогресс
• ⚡ Мгновенная проверка ответов

Нажми кнопку ниже, чтобы начать! 👇"""
    
    # Отправляем приветственное сообщение с обработкой ошибок и таймаутом
    # Пробуем несколько раз с разными стратегиями
    message_sent = False
    
    # Попытка 1: С клавиатурой и таймаутом 8 секунд
    if not message_sent:
        try:
            await asyncio.wait_for(
                message.answer(welcome_text, reply_markup=get_main_keyboard()),
                timeout=8.0
            )
            logging.info(f"✅ Приветственное сообщение отправлено пользователю {user_id}")
            message_sent = True
        except asyncio.TimeoutError:
            logging.warning(f"⚠️ Таймаут при отправке сообщения с клавиатурой пользователю {user_id}")
        except Exception as e:
            logging.warning(f"⚠️ Ошибка при отправке сообщения с клавиатурой пользователю {user_id}: {e}")
    
    # Попытка 2: Без клавиатуры с таймаутом 5 секунд
    if not message_sent:
        try:
            await asyncio.wait_for(
                message.answer(welcome_text),
                timeout=5.0
            )
            logging.info(f"✅ Приветственное сообщение отправлено без клавиатуры пользователю {user_id}")
            message_sent = True
        except asyncio.TimeoutError:
            logging.warning(f"⚠️ Таймаут при отправке сообщения без клавиатуры пользователю {user_id}")
        except Exception as e:
            logging.warning(f"⚠️ Ошибка при отправке сообщения без клавиатуры пользователю {user_id}: {e}")
    
    # Попытка 3: Простое сообщение без таймаута (последняя попытка)
    if not message_sent:
        try:
            await message.answer("Привет! 👋\n\nДобро пожаловать в ПДД Дуэли! 🚗\n\nИспользуй /start для начала.")
            logging.info(f"✅ Простое приветственное сообщение отправлено пользователю {user_id}")
            message_sent = True
        except Exception as e:
            logging.error(f"❌ Критическая ошибка при отправке сообщения пользователю {user_id}: {e}")
    
    if not message_sent:
        logging.error(f"❌ Не удалось отправить сообщение пользователю {user_id} после всех попыток")

@dp.callback_query(F.data == "top_players")
async def show_top_players(callback: types.CallbackQuery):
    # Получаем всех пользователей (без лимита)
    top_users = db.get_top_users(limit=None)
    
    if not top_users:
        await callback.answer("Пока нет игроков")
        return
    
    text = "🏆 Топ игроков по винрейту:\n\n"
    # Показываем максимум 50 игроков в Telegram
    for i, user in enumerate(top_users[:50], 1):
        # user может быть с photo_url или без (в зависимости от версии БД)
        if len(user) >= 8:
            user_id, username, first_name, photo_url, wins, losses, total_games, win_rate = user
        else:
            user_id, username, first_name, wins, losses, total_games, win_rate = user
        name = first_name or username or f"Игрок {user_id}"
        games_text = f"({wins}/{total_games})" if total_games > 0 else "(0/0)"
        text += f"{i}. {name} - {win_rate}% {games_text}\n"
    
    if len(top_users) > 50:
        text += f"\n... и еще {len(top_users) - 50} игроков"
    
    await callback.message.answer(text)

@dp.callback_query(F.data == "help")
async def show_help(callback: types.CallbackQuery):
    help_text = """
❓ Как играть:

1. Нажми "Открыть приложение"
2. Выбери режим игры:
   - 🤺 Дуэль: Соревнование с другим игроком
   - 📚 Тренировка: Практика без соперника
3. Отвечай на вопросы быстро и правильно
4. Поднимайся в рейтинге!

📊 Статистика:
• Винрейт = (Победы / Все игры) * 100%
• Минимум 5 игр для попадания в топ
    """
    await callback.message.answer(help_text)

async def main():
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
