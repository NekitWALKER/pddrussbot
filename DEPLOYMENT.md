# Инструкция по развертыванию на хостинге

## Структура файлов для загрузки

### Обязательные файлы и папки:

```
/
├── index.html          # Главный файл приложения
├── style.css           # Стили приложения
├── script.js           # JavaScript приложения
├── .htaccess          # Конфигурация Apache (опционально)
├── robots.txt         # Для поисковых систем (опционально)
│
├── questions/          # Папка с вопросами
│   ├── index.json     # Манифест билетов
│   └── A_B/
│       ├── tickets/   # 40 билетов (Билет 1.json - Билет 40.json)
│       └── topics/    # 26 тем (файлы .json)
│
├── markup/             # Папка с разметкой
│   └── markup.json    # Данные о разметке
│
├── penalties/          # Папка со штрафами
│   └── penalties.json # Данные о штрафах
│
└── images/             # Папка с изображениями
    ├── A_B/           # 542 изображения вопросов (.jpg)
    ├── markup/         # 45 SVG изображений разметки
    └── signs/         # 278 SVG изображений знаков
```

## Проверка перед развертыванием

### ✅ Обязательно должно быть:

1. **index.html** - главный файл
2. **style.css** - стили
3. **script.js** - JavaScript
4. **questions/index.json** - манифест билетов
5. **questions/A_B/tickets/** - 40 файлов билетов
6. **questions/A_B/topics/** - 26 файлов тем
7. **markup/markup.json** - данные разметки
8. **penalties/penalties.json** - данные штрафов
9. **images/** - все изображения

### ⚠️ Не обязательны для фронтенда (можно не загружать):

- `package.json` - для Node.js (не нужен для веб-приложения)
- `auto-edit.js` - служебный файл (не нужен)
- `.cursor-config.json` - конфигурация редактора (не нужен)

### 🤖 Файлы Telegram бота (нужны для работы бота, но не для веб-приложения):

Эти файлы нужны, если вы хотите запустить Telegram бота отдельно:
- `bot.py` - основной файл бота
- `database.py` - модуль для работы с БД
- `config.py` - конфигурация (токен и URL)
- `requirements.txt` - зависимости Python

**Важно:** Для работы веб-приложения файлы бота НЕ обязательны. Бот нужен только для команды `/start` и интеграции с Telegram. Веб-приложение может работать самостоятельно через прямой URL.

## Настройки хостинга

### Требования:

1. **Веб-сервер**: Apache или Nginx
2. **Поддержка**: JavaScript, JSON, изображения (JPG, SVG)
3. **Кодировка**: UTF-8
4. **HTTPS**: Рекомендуется для Telegram Web App

### Apache (.htaccess)

Если хостинг использует Apache, файл `.htaccess` уже настроен:
- Кеширование статических файлов
- Gzip сжатие
- CORS заголовки для JSON
- Защита конфигурационных файлов

### Nginx

Если хостинг использует Nginx, добавьте в конфигурацию:

```nginx
location / {
    try_files $uri $uri/ /index.html;
    charset utf-8;
}

location ~* \.(jpg|jpeg|png|svg|gif|ico)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ~* \.(css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ~* \.(json)$ {
    expires 1h;
    add_header Access-Control-Allow-Origin "*";
    add_header Access-Control-Allow-Methods "GET, OPTIONS";
}
```

## Проверка после развертывания

1. Откройте `https://ваш-домен.com/index.html` в браузере
2. Проверьте загрузку:
   - Откройте DevTools (F12)
   - Вкладка Network
   - Проверьте, что все файлы загружаются без ошибок

3. Проверьте пути к файлам:
   - `questions/index.json` должен быть доступен
   - `markup/markup.json` должен быть доступен
   - `penalties/penalties.json` должен быть доступен
   - Изображения должны загружаться

## Возможные проблемы

### Проблема: 404 ошибка при загрузке JSON файлов

**Решение**: Проверьте пути в `script.js`:
- `MANIFEST_URL = "questions/index.json"`
- `MARKUP_URL = "markup/markup.json"`
- `PENALTIES_URL = "penalties/penalties.json"`

### Проблема: Изображения не загружаются

**Решение**: Проверьте, что папка `images/` загружена полностью и пути к изображениям корректны.

### Проблема: Кодировка неправильная (кириллица)

**Решение**: Убедитесь, что:
- Все файлы сохранены в UTF-8
- В `.htaccess` есть `AddDefaultCharset UTF-8`
- Сервер настроен на UTF-8

## Размер проекта

- **HTML/CSS/JS**: ~300 KB
- **JSON файлы**: ~5-10 MB
- **Изображения**: ~50-100 MB (в зависимости от качества)

**Общий размер**: ~60-110 MB

## Подключение к Telegram Bot

### Вариант 1: Через Web App Menu Button (рекомендуется)

1. Создайте бота через @BotFather
2. Получите токен бота
3. Настройте Web App URL в боте:
   - Отправьте `/newapp` боту @BotFather
   - Выберите вашего бота
   - Укажите название: "ПДД ДУЭЛИ"
   - Укажите URL: `https://nikirir.github.io/pdd-duel-webapp/index.html`
   - Готово! Теперь в боте будет кнопка "Menu" которая открывает Web App

### Вариант 2: Запуск бота с командой /start

Если вы хотите, чтобы бот отвечал на команду `/start`, нужно:

1. Загрузить файлы бота на сервер с Python:
   - `bot.py`
   - `database.py`
   - `config.py`
   - `requirements.txt`

2. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настроить `config.py`:
   - Указать `BOT_TOKEN` (от @BotFather)
   - Указать `WEBAPP_URL` (ваш хостинг)

4. Запустить бота:
   ```bash
   python bot.py
   ```

Подробная инструкция в файле `BOT_SETUP.md`

## Готово! 🚀

После загрузки всех файлов приложение должно работать на хостинге.

**Примечание:** Веб-приложение работает независимо от бота. Бот нужен только для удобства запуска через Telegram.

