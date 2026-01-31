# Инструкция по настройке Telegram бота

## Что нужно для работы бота

### 1. Файлы бота (уже есть):
- ✅ `bot.py` - основной файл бота
- ✅ `database.py` - модуль для работы с БД
- ✅ `config.py` - конфигурация (токен и URL)
- ✅ `requirements.txt` - зависимости Python

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

Или вручную:
```bash
pip install aiogram==3.13.1
pip install aiosqlite==0.20.0
```

### 3. Настройка config.py

Откройте `config.py` и укажите:
- **BOT_TOKEN** - токен вашего бота (получите у @BotFather)
- **WEBAPP_URL** - URL вашего хостинга с веб-приложением

Пример:
```python
BOT_TOKEN = "ваш-токен-от-BotFather"
WEBAPP_URL = "https://ваш-домен.com"
```

### 4. Запуск бота

```bash
python bot.py
```

Или для постоянной работы используйте:
- **systemd** (Linux)
- **screen/tmux**
- **pm2** (Node.js процесс-менеджер)
- **Docker**

## Команды бота

### `/start`
Приветственное сообщение с кнопкой для открытия Web App

### Кнопки:
- **🎮 Открыть приложение** - открывает веб-приложение
- **📊 Топ игроков** - показывает топ 10 игроков
- **❓ Помощь** - справка по использованию

## База данных

Бот использует SQLite базу данных `pdd_duel.db`, которая создается автоматически при первом запуске.

### Таблицы:
- **users** - информация о пользователях
- **games** - история игр (для будущего функционала дуэлей)

## Развертывание на сервере

### Вариант 1: Python + systemd (Linux)

1. Создайте файл `/etc/systemd/system/pdd-bot.service`:

```ini
[Unit]
Description=PDD Duel Telegram Bot
After=network.target

[Service]
Type=simple
User=ваш-пользователь
WorkingDirectory=/path/to/pdd-duel-webapp
ExecStart=/usr/bin/python3 /path/to/pdd-duel-webapp/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Запустите:
```bash
sudo systemctl enable pdd-bot
sudo systemctl start pdd-bot
```

### Вариант 2: Docker

Создайте `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py database.py config.py ./

CMD ["python", "bot.py"]
```

### Вариант 3: Хостинг (PythonAnywhere, Heroku, Railway и т.д.)

1. Загрузите файлы бота
2. Установите зависимости
3. Настройте переменные окружения (BOT_TOKEN, WEBAPP_URL)
4. Запустите бота

## Важно!

⚠️ **Никогда не публикуйте токен бота в открытом доступе!**

- Используйте переменные окружения
- Добавьте `config.py` в `.gitignore`
- Не коммитьте токен в Git

## Проверка работы

1. Запустите бота
2. Откройте Telegram
3. Найдите вашего бота
4. Отправьте `/start`
5. Должно появиться приветствие с кнопкой

## Подключение Web App к боту

1. Откройте @BotFather
2. Выберите вашего бота
3. Отправьте `/newapp`
4. Выберите бота
5. Укажите название: "ПДД ДУЭЛИ"
6. Укажите описание: "Подготовка к экзамену ГИБДД"
7. Добавьте фото (опционально)
8. Укажите URL: `https://nikirir.github.io/pdd-duel-webapp/index.html`
9. Готово!

Теперь в боте будет кнопка "Menu" которая открывает Web App.

