#!/usr/bin/env python3
"""
Enterprise Telegram Bot - DevOps Manager
Полнофункциональный бот для управления инфраструктурой
Version: 9.0.0
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

import psutil
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/var/log/enterprise-deploy/devops-bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

################################################################################
# КОНФИГУРАЦИЯ
################################################################################

class Config:
    """Централизованная конфигурация бота"""
    
    TOKEN = os.getenv('TELEGRAM_BOT_DEVOPS_TOKEN')
    ADMIN_IDS = [int(x) for x in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',') if x]
    
    BASE_PATH = Path('/opt/enterprise-deploy')
    DATA_PATH = Path('/srv/enterprise-data/devops-bot')
    LOGS_PATH = Path('/var/log/enterprise-deploy')
    
    # Создание директорий
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    LOGS_PATH.mkdir(parents=True, exist_ok=True)
    
    DB_FILE = DATA_PATH / 'devops-bot.json'
    
    # Пороги мониторинга
    THRESHOLDS = {
        'cpu': 85,
        'memory': 90,
        'disk': 80,
        'response_time': 1000
    }

################################################################################
# БАЗА ДАННЫХ
################################################################################

class Database:
    """Продвинутая БД с кешированием и транзакциями"""
    
    def __init__(self, db_file: Path):
        self.db_file = db_file
        self.data = self._load()
        self._cache = {}
        self._cache_ttl = 60  # seconds
        
    def _load(self) -> Dict:
        """Загрузка данных с проверкой целостности"""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"✅ БД загружена: {self.db_file}")
                return data
            except json.JSONDecodeError:
                logger.error(f"❌ Ошибка чтения БД, создание новой")
                return self._init_db()
        else:
            return self._init_db()
    
    def _init_db(self) -> Dict:
        """Инициализация новой БД"""
        return {
            'users': {},
            'deployments': [],
            'services': {},
            'metrics': [],
            'alerts': [],
            'tasks': [],
            'backups': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'version': '9.0.0'
            }
        }
    
    def save(self):
        """Атомарное сохранение с резервной копией"""
        backup_file = self.db_file.with_suffix('.bak')
        
        # Создаем резервную копию
        if self.db_file.exists():
            self.db_file.rename(backup_file)
        
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            
            # Удаляем резервную копию при успехе
            if backup_file.exists():
                backup_file.unlink()
                
            logger.debug("✅ БД сохранена")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения БД: {e}")
            # Восстанавливаем из резервной копии
            if backup_file.exists():
                backup_file.rename(self.db_file)
    
    def get_user(self, user_id: int) -> Dict:
        """Получение пользователя с кешированием"""
        cache_key = f"user_{user_id}"
        
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if (datetime.now() - cached_time).seconds < self._cache_ttl:
                return cached_data
        
        user = self.data['users'].get(str(user_id), {})
        self._cache[cache_key] = (datetime.now(), user)
        return user
    
    def update_user(self, user_id: int, update_data: Dict):
        """Обновление данных пользователя"""
        user_key = str(user_id)
        
        if user_key not in self.data['users']:
            self.data['users'][user_key] = {
                'id': user_id,
                'first_seen': datetime.now().isoformat(),
                'command_count': 0,
                'last_active': datetime.now().isoformat()
            }
        
        self.data['users'][user_key].update(update_data)
        self.data['users'][user_key]['last_active'] = datetime.now().isoformat()
        
        # Инвалидация кеша
        cache_key = f"user_{user_id}"
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        self.save()
    
    def add_deployment(self, deployment: Dict):
        """Добавление записи о развертывании"""
        deployment['id'] = len(self.data['deployments']) + 1
        deployment['timestamp'] = datetime.now().isoformat()
        self.data['deployments'].append(deployment)
        self.save()
    
    def get_recent_deployments(self, limit: int = 10) -> List[Dict]:
        """Получение последних развертываний"""
        return sorted(
            self.data['deployments'],
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
    
    def add_metric(self, metric: Dict):
        """Добавление метрики с автоочисткой старых"""
        metric['timestamp'] = datetime.now().isoformat()
        self.data['metrics'].append(metric)
        
        # Храним только последние 1000 метрик
        if len(self.data['metrics']) > 1000:
            self.data['metrics'] = self.data['metrics'][-1000:]
        
        self.save()

################################################################################
# ДЕКОРАТОРЫ
################################################################################

def admin_only(func):
    """Проверка прав администратора"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if user_id not in Config.ADMIN_IDS:
            await update.message.reply_text(
                "❌ Доступ запрещен. Требуются права администратора."
            )
            logger.warning(f"Попытка несанкционированного доступа: {user_id}")
            return
        
        return await func(update, context)
    return wrapper

def track_usage(func):
    """Отслеживание использования команд"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        command = func.__name__
        
        db = context.bot_data['db']
        user = db.get_user(user_id)
        
        db.update_user(user_id, {
            'command_count': user.get('command_count', 0) + 1,
            'last_command': command
        })
        
        logger.info(f"Command: {command} by user {user_id}")
        
        return await func(update, context)
    return wrapper

def with_progress(message: str):
    """Показывать прогресс выполнения"""
    def decorator(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            progress_msg = await update.message.reply_text(f"⏳ {message}...")
            
            try:
                result = await func(update, context)
                await progress_msg.delete()
                return result
            except Exception as e:
                await progress_msg.edit_text(f"❌ Ошибка: {str(e)}")
                raise
        
        return wrapper
    return decorator

################################################################################
# СИСТЕМА МОНИТОРИНГА
################################################################################

class SystemMonitor:
    """Расширенный мониторинг системы"""
    
    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """Детальная информация о CPU"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        
        return {
            'total': cpu_percent,
            'cores': cpu_count,
            'frequency': {
                'current': cpu_freq.current if cpu_freq else 0,
                'min': cpu_freq.min if cpu_freq else 0,
                'max': cpu_freq.max if cpu_freq else 0
            },
            'per_core': cpu_per_core,
            'status': '🔴 Critical' if cpu_percent > Config.THRESHOLDS['cpu'] 
                     else '🟢 Normal'
        }
    
    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """Детальная информация о памяти"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'percent': swap.percent
            },
            'status': '🔴 Critical' if mem.percent > Config.THRESHOLDS['memory']
                     else '🟢 Normal'
        }
    
    @staticmethod
    def get_disk_info() -> Dict[str, Any]:
        """Информация о дисках"""
        partitions = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                    'status': '🔴 Critical' if usage.percent > Config.THRESHOLDS['disk']
                             else '🟢 Normal'
                })
            except PermissionError:
                continue
        
        return {'partitions': partitions}
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """Информация о сети"""
        net_io = psutil.net_io_counters()
        connections = len(psutil.net_connections())
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errors_in': net_io.errin,
            'errors_out': net_io.errout,
            'connections': connections
        }
    
    @staticmethod
    def get_processes() -> List[Dict[str, Any]]:
        """Топ процессов по использованию ресурсов"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'],
                    'memory': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Сортировка по CPU
        processes.sort(key=lambda x: x['cpu'], reverse=True)
        return processes[:10]
    
    @staticmethod
    def get_service_status(service_name: str) -> Dict[str, Any]:
        """Статус systemd сервиса"""
        try:
            result = subprocess.run(
                ['systemctl', 'status', service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            is_active = 'active (running)' in result.stdout
            
            return {
                'service': service_name,
                'active': is_active,
                'status': '🟢 Running' if is_active else '🔴 Stopped',
                'output': result.stdout[:500]  # Первые 500 символов
            }
        except subprocess.TimeoutExpired:
            return {'service': service_name, 'status': '⏱️ Timeout'}
        except Exception as e:
            return {'service': service_name, 'status': f'❌ Error: {e}'}

################################################################################
# КОМАНДЫ БОТА - БАЗОВЫЕ
################################################################################

@track_usage
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое сообщение с главным меню"""
    keyboard = [
        [KeyboardButton("📊 Dashboard"), KeyboardButton("🚀 Deploy")],
        [KeyboardButton("💻 Системa"), KeyboardButton("📈 Метрики")],
        [KeyboardButton("🔧 Сервисы"), KeyboardButton("📁 Логи")],
        [KeyboardButton("⚙️ Настройки"), KeyboardButton("❓ Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = f"""
👋 Добро пожаловать в <b>DevOps Manager Bot v9.0</b>

🤖 Я помогу управлять вашей инфраструктурой:
  • Мониторинг системы в реальном времени
  • Развертывание приложений
  • Управление сервисами
  • Просмотр логов
  • Алерты и уведомления

Используйте кнопки меню или команды:
/help - Список всех команд
/dashboard - Обзор системы
/deploy - Развертывание
/services - Управление сервисами
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

@track_usage
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка по командам"""
    help_text = """
📚 <b>Доступные команды DevOps Manager Bot</b>

<b>📊 МОНИТОРИНГ:</b>
/dashboard - Обзор системы
/cpu - Информация о CPU
/memory - Информация о памяти
/disk - Информация о дисках
/network - Сетевая статистика
/processes - Топ процессов

<b>🚀 РАЗВЕРТЫВАНИЕ:</b>
/deploy - Развернуть приложение
/rollback - Откатить развертывание
/deployments - История развертываний
/status - Статус текущего развертывания

<b>🔧 СЕРВИСЫ:</b>
/services - Список сервисов
/start_service - Запустить сервис
/stop_service - Остановить сервис
/restart_service - Перезапустить сервис

<b>📁 ЛОГИ:</b>
/logs - Просмотр логов
/tail - Следить за логом
/errors - Только ошибки

<b>🔔 АЛЕРТЫ:</b>
/alerts - Активные алерты
/subscribe - Подписаться на алерты
/unsubscribe - Отписаться

<b>⚙️ АДМИНИСТРИРОВАНИЕ:</b>
/backup - Создать резервную копию
/restore - Восстановить из копии
/update - Обновить систему
/reboot - Перезагрузить сервер
"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')

################################################################################
# КОМАНДЫ БОТА - DASHBOARD
################################################################################

@track_usage
@with_progress("Загрузка dashboard")
async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Комплексный dashboard системы"""
    cpu = SystemMonitor.get_cpu_info()
    memory = SystemMonitor.get_memory_info()
    disk = SystemMonitor.get_disk_info()
    network = SystemMonitor.get_network_info()
    
    def format_bytes(bytes_val):
        """Форматирование байтов в человекочитаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"
    
    dashboard_text = f"""
╔═══════════════════════════════════════╗
        🖥️  <b>SYSTEM DASHBOARD</b>
╚═══════════════════════════════════════╝

<b>💻 CPU:</b> {cpu['status']}
  Загрузка: {cpu['total']}%
  Ядер: {cpu['cores']}
  Частота: {cpu['frequency']['current']:.0f} MHz

<b>🧠 MEMORY:</b> {memory['status']}
  Использовано: {format_bytes(memory['used'])} / {format_bytes(memory['total'])}
  Процент: {memory['percent']}%
  Swap: {memory['swap']['percent']}%

<b>💾 DISK:</b>
"""
    
    for partition in disk['partitions'][:3]:  # Первые 3 раздела
        dashboard_text += f"  {partition['mountpoint']}: {partition['percent']}% {partition['status']}\n"
    
    dashboard_text += f"""
<b>🌐 NETWORK:</b>
  Отправлено: {format_bytes(network['bytes_sent'])}
  Получено: {format_bytes(network['bytes_recv'])}
  Соединений: {network['connections']}

<b>⏱️ UPTIME:</b>
  {datetime.now() - datetime.fromtimestamp(psutil.boot_time())}
"""
    
    # Inline кнопки для детального просмотра
    keyboard = [
        [
            InlineKeyboardButton("📊 CPU", callback_data='detail_cpu'),
            InlineKeyboardButton("🧠 Memory", callback_data='detail_memory'),
            InlineKeyboardButton("💾 Disk", callback_data='detail_disk')
        ],
        [
            InlineKeyboardButton("🔄 Обновить", callback_data='refresh_dashboard')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        dashboard_text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

################################################################################
# КОМАНДЫ БОТА - DEPLOYMENT
################################################################################

# States для ConversationHandler
DEPLOY_SELECT_APP, DEPLOY_SELECT_ENV, DEPLOY_CONFIRM = range(3)

@admin_only
@track_usage
async def deploy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса развертывания"""
    keyboard = [
        [InlineKeyboardButton("🐍 Python App", callback_data='deploy_python')],
        [InlineKeyboardButton("🟢 Node.js App", callback_data='deploy_nodejs')],
        [InlineKeyboardButton("🐳 Docker Container", callback_data='deploy_docker')],
        [InlineKeyboardButton("❌ Отмена", callback_data='deploy_cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚀 <b>Развертывание приложения</b>\n\nВыберите тип приложения:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return DEPLOY_SELECT_APP

@admin_only
async def deploy_select_env(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор окружения для развертывания"""
    query = update.callback_query
    await query.answer()
    
    app_type = query.data.replace('deploy_', '')
    context.user_data['deploy_app_type'] = app_type
    
    keyboard = [
        [InlineKeyboardButton("🧪 Development", callback_data='env_dev')],
        [InlineKeyboardButton("🧪 Staging", callback_data='env_staging')],
        [InlineKeyboardButton("🚀 Production", callback_data='env_prod')],
        [InlineKeyboardButton("◀️ Назад", callback_data='deploy_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"Выбрано: <b>{app_type}</b>\n\nВыберите окружение:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return DEPLOY_SELECT_ENV

@admin_only
async def deploy_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение развертывания"""
    query = update.callback_query
    await query.answer()
    
    env = query.data.replace('env_', '')
    context.user_data['deploy_env'] = env
    
    app_type = context.user_data.get('deploy_app_type', 'unknown')
    
    keyboard = [
        [InlineKeyboardButton("✅ Развернуть", callback_data='deploy_execute')],
        [InlineKeyboardButton("❌ Отмена", callback_data='deploy_cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"""
🚀 <b>Подтверждение развертывания</b>

Приложение: <code>{app_type}</code>
Окружение: <code>{env}</code>

Продолжить?
""",
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return DEPLOY_CONFIRM

@admin_only
async def deploy_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выполнение развертывания"""
    query = update.callback_query
    await query.answer()
    
    app_type = context.user_data.get('deploy_app_type', 'unknown')
    env = context.user_data.get('deploy_env', 'unknown')
    
    await query.edit_message_text("⏳ Развертывание...")
    
    # Симуляция развертывания (в реальности здесь вызов Ansible/Kubernetes/etc)
    await asyncio.sleep(2)
    
    # Сохранение в БД
    db = context.bot_data['db']
    db.add_deployment({
        'user_id': update.effective_user.id,
        'app_type': app_type,
        'environment': env,
        'status': 'success'
    })
    
    await query.edit_message_text(
        f"""
✅ <b>Развертывание завершено!</b>

Приложение: <code>{app_type}</code>
Окружение: <code>{env}</code>
Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Статус: 🟢 Running
""",
        parse_mode='HTML'
    )
    
    return ConversationHandler.END

################################################################################
# ГЛАВНАЯ ФУНКЦИЯ
################################################################################

def main():
    """Запуск бота"""
    if not Config.TOKEN:
        logger.error("❌ TELEGRAM_BOT_DEVOPS_TOKEN не установлен")
        sys.exit(1)
    
    # Создание приложения
    application = Application.builder().token(Config.TOKEN).build()
    
    # Инициализация БД
    db = Database(Config.DB_FILE)
    application.bot_data['db'] = db
    
    # Базовые команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("dashboard", dashboard))
    
    # ConversationHandler для развертывания
    deploy_conv = ConversationHandler(
        entry_points=[CommandHandler('deploy', deploy_start)],
        states={
            DEPLOY_SELECT_APP: [CallbackQueryHandler(deploy_select_env, pattern='^deploy_')],
            DEPLOY_SELECT_ENV: [CallbackQueryHandler(deploy_confirm, pattern='^env_')],
            DEPLOY_CONFIRM: [CallbackQueryHandler(deploy_execute, pattern='^deploy_execute')]
        },
        fallbacks=[CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern='^deploy_cancel')]
    )
    application.add_handler(deploy_conv)
    
    logger.info("🚀 DevOps Manager Bot запущен")
    
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
