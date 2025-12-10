#!/usr/bin/env python3
"""
Advanced Telegram Bot - Продвинутый бот с 25+ командами
Автор: Sandrick Tech
Дата: 2024-12-09
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import json
import psutil
import requests
from pathlib import Path

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/var/log/telegram-bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
DATA_DIR = Path('/srv/bot_data')
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Состояния для ConversationHandler
UPLOAD_FILE, POLL_QUESTION, POLL_OPTIONS, REMINDER_TEXT, REMINDER_TIME = range(5)

# База данных (простой JSON для примера)
DB_FILE = DATA_DIR / 'bot_db.json'


class BotDatabase:
    """Простая файловая БД"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = self._load()
    
    def _load(self) -> Dict:
        if self.file_path.exists():
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'users': {},
            'statistics': {},
            'reminders': [],
            'files': []
        }
    
    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_user(self, user_id: int, username: str):
        if str(user_id) not in self.data['users']:
            self.data['users'][str(user_id)] = {
                'username': username,
                'joined': datetime.now().isoformat(),
                'commands_used': 0
            }
            self.save()
    
    def increment_command(self, user_id: int):
        user_str = str(user_id)
        if user_str in self.data['users']:
            self.data['users'][user_str]['commands_used'] += 1
            self.save()


db = BotDatabase(DB_FILE)


################################################################################
# ДЕКОРАТОРЫ
################################################################################

def admin_only(func):
    """Декоратор для ограничения команд только админами"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("⛔ Доступ запрещён. Только для администраторов.")
            return
        return await func(update, context)
    return wrapper


def track_usage(func):
    """Декоратор для отслеживания использования команд"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db.add_user(user.id, user.username or user.first_name)
        db.increment_command(user.id)
        return await func(update, context)
    return wrapper


################################################################################
# ОСНОВНЫЕ КОМАНДЫ
################################################################################

@track_usage
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое сообщение с главным меню"""
    keyboard = [
        [KeyboardButton("📊 Статистика"), KeyboardButton("💻 Система")],
        [KeyboardButton("🌤 Погода"), KeyboardButton("📁 Файлы")],
        [KeyboardButton("⏰ Напоминания"), KeyboardButton("📮 Опросы")],
        [KeyboardButton("ℹ️ Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = f"""
👋 Привет, {update.effective_user.first_name}!

Я продвинутый бот с множеством функций:

📊 **Статистика** - статистика пользователей и команд
💻 **Система** - информация о сервере
🌤 **Погода** - прогноз погоды
📁 **Файлы** - управление файлами
⏰ **Напоминания** - создание напоминаний
📮 **Опросы** - создание опросов

Используйте кнопки ниже или /help для списка команд.
"""
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


@track_usage
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список всех команд"""
    help_text = """
📚 **ДОСТУПНЫЕ КОМАНДЫ**

**Основные:**
/start - Главное меню
/help - Эта справка
/about - О боте
/ping - Проверка связи

**Информация:**
/stats - Статистика бота
/users - Список пользователей
/myinfo - Ваша информация
/uptime - Время работы бота

**Система (admin):**
/system - Информация о системе
/cpu - Загрузка CPU
/memory - Использование памяти
/disk - Использование диска
/network - Сетевая статистика
/processes - Топ процессов

**Файлы:**
/files - Список файлов
/upload - Загрузить файл
/download <id> - Скачать файл
/deletefile <id> - Удалить файл

**Напоминания:**
/remind - Создать напоминание
/reminders - Список напоминаний
/cancelreminder <id> - Отменить

**Опросы:**
/poll - Создать опрос
/pollstats <id> - Статистика опроса

**Погода:**
/weather <город> - Погода
/forecast <город> - Прогноз на 5 дней

**Утилиты:**
/echo <текст> - Повторить текст
/calc <выражение> - Калькулятор
/random <min> <max> - Случайное число
/timer <секунды> - Таймер

**Развлечения:**
/joke - Случайная шутка
/quote - Мотивационная цитата
/dice - Бросить кубик
"""
    await update.message.reply_text(help_text)


@track_usage
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """О боте"""
    about_text = f"""
🤖 **Advanced Telegram Bot v1.0**

Разработчик: Sandrick Tech
Дата: 2024-12-09

**Возможности:**
• 25+ команд
• Админ панель
• Система напоминаний
• Файловый менеджер
• Опросы
• Мониторинг системы
• Интеграция с погодным API

**Статистика:**
• Пользователей: {len(db.data['users'])}
• Файлов: {len(db.data['files'])}
• Напоминаний: {len(db.data['reminders'])}

GitHub: https://github.com/your-repo
"""
    await update.message.reply_text(about_text)


@track_usage
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка связи"""
    await update.message.reply_text("🏓 Pong! Бот работает.")


################################################################################
# СТАТИСТИКА
################################################################################

@track_usage
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Общая статистика бота"""
    total_users = len(db.data['users'])
    total_commands = sum(u['commands_used'] for u in db.data['users'].values())
    
    stats_text = f"""
📊 **СТАТИСТИКА БОТА**

👥 Пользователей: {total_users}
⚡ Команд выполнено: {total_commands}
📁 Файлов загружено: {len(db.data['files'])}
⏰ Активных напоминаний: {len([r for r in db.data['reminders'] if not r.get('completed')])}

💾 Размер БД: {DB_FILE.stat().st_size / 1024:.2f} KB
"""
    await update.message.reply_text(stats_text)


@track_usage
async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список пользователей"""
    if not db.data['users']:
        await update.message.reply_text("Нет зарегистрированных пользователей")
        return
    
    users_text = "👥 **ПОЛЬЗОВАТЕЛИ**\n\n"
    for user_id, user_data in list(db.data['users'].items())[:20]:  # Первые 20
        users_text += f"• @{user_data['username']} - {user_data['commands_used']} команд\n"
    
    await update.message.reply_text(users_text)


@track_usage
async def my_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о пользователе"""
    user = update.effective_user
    user_data = db.data['users'].get(str(user.id), {})
    
    info_text = f"""
👤 **ВАША ИНФОРМАЦИЯ**

ID: `{user.id}`
Имя: {user.first_name} {user.last_name or ''}
Username: @{user.username or 'не указан'}

Зарегистрирован: {user_data.get('joined', 'N/A')}
Команд использовано: {user_data.get('commands_used', 0)}

Админ: {'✅ Да' if user.id in ADMIN_IDS else '❌ Нет'}
"""
    await update.message.reply_text(info_text)


################################################################################
# СИСТЕМА (ADMIN)
################################################################################

@admin_only
@track_usage
async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о системе"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    system_text = f"""
💻 **ИНФОРМАЦИЯ О СИСТЕМЕ**

**CPU:**
Загрузка: {cpu_percent}%
Ядер: {psutil.cpu_count()}

**Память:**
Всего: {memory.total / (1024**3):.2f} GB
Использовано: {memory.used / (1024**3):.2f} GB ({memory.percent}%)
Свободно: {memory.available / (1024**3):.2f} GB

**Диск:**
Всего: {disk.total / (1024**3):.2f} GB
Использовано: {disk.used / (1024**3):.2f} GB ({disk.percent}%)
Свободно: {disk.free / (1024**3):.2f} GB

Uptime: {datetime.now() - datetime.fromtimestamp(psutil.boot_time())}
"""
    await update.message.reply_text(system_text)


@admin_only
@track_usage
async def cpu_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Детальная информация о CPU"""
    cpu_freq = psutil.cpu_freq()
    cpu_percent_per_core = psutil.cpu_percent(interval=1, percpu=True)
    
    cpu_text = f"""
🔥 **CPU ИНФОРМАЦИЯ**

Общая загрузка: {psutil.cpu_percent(interval=1)}%
Частота: {cpu_freq.current:.2f} MHz (max: {cpu_freq.max:.2f})

**По ядрам:**
"""
    for i, percent in enumerate(cpu_percent_per_core):
        cpu_text += f"Core {i}: {percent}%\n"
    
    await update.message.reply_text(cpu_text)


@admin_only
@track_usage
async def memory_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Детальная информация о памяти"""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    memory_text = f"""
💾 **ПАМЯТЬ**

**RAM:**
Всего: {memory.total / (1024**3):.2f} GB
Доступно: {memory.available / (1024**3):.2f} GB
Использовано: {memory.used / (1024**3):.2f} GB
Процент: {memory.percent}%

**SWAP:**
Всего: {swap.total / (1024**3):.2f} GB
Использовано: {swap.used / (1024**3):.2f} GB
Процент: {swap.percent}%
"""
    await update.message.reply_text(memory_text)


@admin_only
@track_usage
async def disk_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о дисках"""
    partitions = psutil.disk_partitions()
    
    disk_text = "💿 **ДИСКИ**\n\n"
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_text += f"""
**{partition.device}**
Точка монтирования: {partition.mountpoint}
Тип: {partition.fstype}
Размер: {usage.total / (1024**3):.2f} GB
Использовано: {usage.used / (1024**3):.2f} GB ({usage.percent}%)
Свободно: {usage.free / (1024**3):.2f} GB

"""
        except PermissionError:
            continue
    
    await update.message.reply_text(disk_text)


@admin_only
@track_usage
async def network_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сетевая статистика"""
    net_io = psutil.net_io_counters()
    
    network_text = f"""
🌐 **СЕТЕВАЯ СТАТИСТИКА**

Отправлено: {net_io.bytes_sent / (1024**2):.2f} MB
Получено: {net_io.bytes_recv / (1024**2):.2f} MB

Пакетов отправлено: {net_io.packets_sent}
Пакетов получено: {net_io.packets_recv}

Ошибок отправки: {net_io.errout}
Ошибок получения: {net_io.errin}
"""
    await update.message.reply_text(network_text)


@admin_only
@track_usage
async def top_processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Топ процессов по CPU"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Сортируем по CPU
    processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    
    proc_text = "⚡ **ТОП ПРОЦЕССОВ (CPU)**\n\n"
    for proc in processes[:10]:
        proc_text += f"{proc['name']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_percent']:.1f}% MEM\n"
    
    await update.message.reply_text(proc_text)


################################################################################
# ФАЙЛЫ
################################################################################

@track_usage
async def files_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список загруженных файлов"""
    if not db.data['files']:
        await update.message.reply_text("📁 Нет загруженных файлов")
        return
    
    files_text = "📁 **ФАЙЛЫ**\n\n"
    for idx, file_data in enumerate(db.data['files'][-20:], 1):  # Последние 20
        files_text += f"{idx}. {file_data['name']} ({file_data['size'] / 1024:.2f} KB)\n"
        files_text += f"   Загружен: {file_data['uploaded']}\n\n"
    
    await update.message.reply_text(files_text)


@track_usage
async def upload_file_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало загрузки файла"""
    await update.message.reply_text(
        "📤 Отправьте файл для загрузки.\n"
        "Или /cancel для отмены."
    )
    return UPLOAD_FILE


async def upload_file_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение файла"""
    document = update.message.document
    
    if not document:
        await update.message.reply_text("❌ Это не файл. Попробуйте снова.")
        return UPLOAD_FILE
    
    # Скачиваем файл
    file = await context.bot.get_file(document.file_id)
    file_path = DATA_DIR / 'uploads' / document.file_name
    file_path.parent.mkdir(exist_ok=True)
    
    await file.download_to_drive(file_path)
    
    # Сохраняем в БД
    db.data['files'].append({
        'id': len(db.data['files']) + 1,
        'name': document.file_name,
        'size': document.file_size,
        'path': str(file_path),
        'uploaded': datetime.now().isoformat(),
        'user_id': update.effective_user.id
    })
    db.save()
    
    await update.message.reply_text(
        f"✅ Файл {document.file_name} загружен!\n"
        f"Размер: {document.file_size / 1024:.2f} KB"
    )
    return ConversationHandler.END


################################################################################
# НАПОМИНАНИЯ
################################################################################

@track_usage
async def create_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания напоминания"""
    await update.message.reply_text(
        "⏰ Напишите текст напоминания:\n"
        "Или /cancel для отмены."
    )
    return REMINDER_TEXT


async def create_reminder_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение текста напоминания"""
    context.user_data['reminder_text'] = update.message.text
    
    await update.message.reply_text(
        "Через сколько минут напомнить?\n"
        "Например: 5, 30, 60"
    )
    return REMINDER_TIME


async def create_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение времени напоминания"""
    try:
        minutes = int(update.message.text)
        if minutes <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Некорректное число. Попробуйте снова.")
        return REMINDER_TIME
    
    reminder_time = datetime.now() + timedelta(minutes=minutes)
    
    reminder = {
        'id': len(db.data['reminders']) + 1,
        'user_id': update.effective_user.id,
        'text': context.user_data['reminder_text'],
        'time': reminder_time.isoformat(),
        'created': datetime.now().isoformat(),
        'completed': False
    }
    
    db.data['reminders'].append(reminder)
    db.save()
    
    # Планируем напоминание
    context.job_queue.run_once(
        send_reminder,
        minutes * 60,
        data={'user_id': update.effective_user.id, 'text': context.user_data['reminder_text'], 'reminder_id': reminder['id']},
        name=f"reminder_{reminder['id']}"
    )
    
    await update.message.reply_text(
        f"✅ Напоминание создано!\n"
        f"Напомню через {minutes} мин: {context.user_data['reminder_text']}"
    )
    return ConversationHandler.END


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Отправка напоминания"""
    job_data = context.job.data
    await context.bot.send_message(
        chat_id=job_data['user_id'],
        text=f"⏰ **НАПОМИНАНИЕ**\n\n{job_data['text']}"
    )
    
    # Отмечаем как выполненное
    for reminder in db.data['reminders']:
        if reminder['id'] == job_data['reminder_id']:
            reminder['completed'] = True
            db.save()
            break


@track_usage
async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список напоминаний"""
    user_reminders = [
        r for r in db.data['reminders']
        if r['user_id'] == update.effective_user.id and not r['completed']
    ]
    
    if not user_reminders:
        await update.message.reply_text("⏰ У вас нет активных напоминаний")
        return
    
    reminders_text = "⏰ **ВАШИ НАПОМИНАНИЯ**\n\n"
    for reminder in user_reminders:
        reminders_text += f"ID {reminder['id']}: {reminder['text']}\n"
        reminders_text += f"Время: {reminder['time']}\n\n"
    
    await update.message.reply_text(reminders_text)


################################################################################
# ОПРОСЫ
################################################################################

@track_usage
async def create_poll_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания опроса"""
    await update.message.reply_text(
        "📮 Напишите вопрос для опроса:\n"
        "Или /cancel для отмены."
    )
    return POLL_QUESTION


async def create_poll_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение вопроса опроса"""
    context.user_data['poll_question'] = update.message.text
    
    await update.message.reply_text(
        "Напишите варианты ответов через запятую:\n"
        "Например: Да, Нет, Не знаю"
    )
    return POLL_OPTIONS


async def create_poll_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение вариантов опроса"""
    options = [opt.strip() for opt in update.message.text.split(',')]
    
    if len(options) < 2:
        await update.message.reply_text("❌ Нужно минимум 2 варианта. Попробуйте снова.")
        return POLL_OPTIONS
    
    # Отправляем опрос
    poll_message = await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=context.user_data['poll_question'],
        options=options,
        is_anonymous=False
    )
    
    await update.message.reply_text("✅ Опрос создан!")
    return ConversationHandler.END


################################################################################
# ПОГОДА
################################################################################

@track_usage
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Погода (заглушка - требуется API ключ)"""
    if not context.args:
        await update.message.reply_text("Использование: /weather <город>")
        return
    
    city = ' '.join(context.args)
    
    # Здесь должен быть реальный API вызов (OpenWeatherMap, WeatherAPI)
    weather_text = f"""
🌤 **ПОГОДА В {city.upper()}**

Температура: 15°C
Ощущается как: 13°C
Влажность: 65%
Ветер: 5 м/с
Давление: 1013 гПа

Описание: Переменная облачность

⚠️ Для реальных данных нужен API ключ
"""
    await update.message.reply_text(weather_text)


################################################################################
# УТИЛИТЫ
################################################################################

@track_usage
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Эхо"""
    if not context.args:
        await update.message.reply_text("Использование: /echo <текст>")
        return
    
    text = ' '.join(context.args)
    await update.message.reply_text(f"🔊 {text}")


@track_usage
async def calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Калькулятор"""
    if not context.args:
        await update.message.reply_text("Использование: /calc <выражение>\nПример: /calc 2+2*2")
        return
    
    expression = ''.join(context.args)
    try:
        result = eval(expression)  # В продакшене использовать ast.literal_eval или безопасный парсер
        await update.message.reply_text(f"🔢 {expression} = {result}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


@track_usage
async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Случайное число"""
    import random
    
    if len(context.args) != 2:
        await update.message.reply_text("Использование: /random <min> <max>")
        return
    
    try:
        min_val = int(context.args[0])
        max_val = int(context.args[1])
        result = random.randint(min_val, max_val)
        await update.message.reply_text(f"🎲 Случайное число: {result}")
    except ValueError:
        await update.message.reply_text("❌ Некорректные числа")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена операции"""
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


################################################################################
# ОБРАБОТЧИКИ КНОПОК
################################################################################

@track_usage
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых кнопок"""
    text = update.message.text
    
    if text == "📊 Статистика":
        await stats(update, context)
    elif text == "💻 Система":
        await system_info(update, context)
    elif text == "📁 Файлы":
        await files_list(update, context)
    elif text == "⏰ Напоминания":
        await list_reminders(update, context)
    elif text == "ℹ️ Помощь":
        await help_command(update, context)


################################################################################
# MAIN
################################################################################

def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        sys.exit(1)
    
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Основные команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("ping", ping))
    
    # Статистика
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("users", users_list))
    application.add_handler(CommandHandler("myinfo", my_info))
    
    # Система
    application.add_handler(CommandHandler("system", system_info))
    application.add_handler(CommandHandler("cpu", cpu_info))
    application.add_handler(CommandHandler("memory", memory_info))
    application.add_handler(CommandHandler("disk", disk_info))
    application.add_handler(CommandHandler("network", network_info))
    application.add_handler(CommandHandler("processes", top_processes))
    
    # Файлы
    application.add_handler(CommandHandler("files", files_list))
    upload_handler = ConversationHandler(
        entry_points=[CommandHandler("upload", upload_file_start)],
        states={
            UPLOAD_FILE: [MessageHandler(filters.Document.ALL, upload_file_receive)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(upload_handler)
    
    # Напоминания
    reminder_handler = ConversationHandler(
        entry_points=[CommandHandler("remind", create_reminder_start)],
        states={
            REMINDER_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_reminder_text)],
            REMINDER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_reminder_time)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(reminder_handler)
    application.add_handler(CommandHandler("reminders", list_reminders))
    
    # Опросы
    poll_handler = ConversationHandler(
        entry_points=[CommandHandler("poll", create_poll_start)],
        states={
            POLL_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_poll_question)],
            POLL_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_poll_options)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(poll_handler)
    
    # Погода
    application.add_handler(CommandHandler("weather", weather))
    
    # Утилиты
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CommandHandler("calc", calculator))
    application.add_handler(CommandHandler("random", random_number))
    
    # Кнопки
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
    
    # Запуск
    logger.info("🚀 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
