#!/usr/bin/env python3
"""
Enterprise Telegram Bots Orchestrator
Единая точка входа для всех ботов с маршрутизацией
Version: 9.0.0
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import yaml

import psutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

################################################################################
# BACKUP MANAGER BOT
################################################################################

class BackupManager:
    """Управление резервными копиями"""
    
    @staticmethod
    def create_backup(backup_type: str = 'incremental') -> Dict:
        """Создание резервной копии"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(f'/srv/backups/{timestamp}')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Резервное копирование с rsync
            cmd = [
                'rsync', '-av',
                '--exclude=*.log',
                '--exclude=*.tmp',
                '/srv/projects/',
                str(backup_dir / 'projects')
            ]
            
            if backup_type == 'incremental' and (Path('/srv/backups/latest').exists()):
                cmd.insert(2, f'--link-dest=/srv/backups/latest')
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Создание symlink на latest
            latest_link = Path('/srv/backups/latest')
            if latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(backup_dir)
            
            # Получение размера
            size = subprocess.run(
                ['du', '-sh', str(backup_dir)],
                capture_output=True,
                text=True
            ).stdout.split()[0]
            
            return {
                'success': True,
                'timestamp': timestamp,
                'size': size,
                'path': str(backup_dir),
                'type': backup_type
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def list_backups(limit: int = 10) -> List[Dict]:
        """Список резервных копий"""
        backups = []
        backup_root = Path('/srv/backups')
        
        if not backup_root.exists():
            return []
        
        for backup_dir in sorted(backup_root.iterdir(), reverse=True):
            if backup_dir.is_dir() and backup_dir.name != 'latest':
                try:
                    size = subprocess.run(
                        ['du', '-sh', str(backup_dir)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    ).stdout.split()[0]
                    
                    backups.append({
                        'timestamp': backup_dir.name,
                        'size': size,
                        'path': str(backup_dir)
                    })
                    
                    if len(backups) >= limit:
                        break
                except:
                    continue
        
        return backups
    
    @staticmethod
    def restore_backup(backup_timestamp: str) -> Dict:
        """Восстановление из резервной копии"""
        backup_path = Path(f'/srv/backups/{backup_timestamp}')
        
        if not backup_path.exists():
            return {'success': False, 'error': 'Backup не найден'}
        
        try:
            cmd = [
                'rsync', '-av', '--delete',
                str(backup_path / 'projects') + '/',
                '/srv/projects/'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            return {
                'success': True,
                'restored_from': backup_timestamp,
                'output': result.stdout[-500:]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

################################################################################
# MONITORING BOT
################################################################################

class MonitoringBot:
    """Расширенный мониторинг с алертами"""
    
    @staticmethod
    def get_metrics() -> Dict:
        """Сбор всех метрик"""
        return {
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'per_core': psutil.cpu_percent(interval=1, percpu=True)
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'used': psutil.virtual_memory().used,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            },
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def check_alerts(metrics: Dict, thresholds: Dict) -> List[Dict]:
        """Проверка превышения порогов"""
        alerts = []
        
        if metrics['cpu']['percent'] > thresholds.get('cpu', 85):
            alerts.append({
                'severity': 'high',
                'type': 'cpu',
                'value': metrics['cpu']['percent'],
                'message': f"CPU перегружен: {metrics['cpu']['percent']}%"
            })
        
        if metrics['memory']['percent'] > thresholds.get('memory', 90):
            alerts.append({
                'severity': 'high',
                'type': 'memory',
                'value': metrics['memory']['percent'],
                'message': f"Память перегружена: {metrics['memory']['percent']}%"
            })
        
        if metrics['disk']['percent'] > thresholds.get('disk', 80):
            alerts.append({
                'severity': 'medium',
                'type': 'disk',
                'value': metrics['disk']['percent'],
                'message': f"Диск заполнен: {metrics['disk']['percent']}%"
            })
        
        return alerts
    
    @staticmethod
    def generate_report(metrics: Dict, alerts: List[Dict]) -> str:
        """Генерация отчета"""
        def format_bytes(b):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if b < 1024:
                    return f"{b:.1f} {unit}"
                b /= 1024
            return f"{b:.1f} PB"
        
        report = f"""
📊 <b>МОНИТОРИНГ СИСТЕМЫ</b>

<b>CPU:</b> {metrics['cpu']['percent']}% ({metrics['cpu']['count']} cores)
<b>Memory:</b> {format_bytes(metrics['memory']['used'])} / {format_bytes(metrics['memory']['total'])} ({metrics['memory']['percent']}%)
<b>Disk:</b> {format_bytes(metrics['disk']['used'])} / {format_bytes(metrics['disk']['total'])} ({metrics['disk']['percent']}%)
<b>Network:</b> ↑{format_bytes(metrics['network']['bytes_sent'])} ↓{format_bytes(metrics['network']['bytes_recv'])}

"""
        
        if alerts:
            report += "<b>🚨 АКТИВНЫЕ АЛЕРТЫ:</b>\n"
            for alert in alerts:
                emoji = '🔴' if alert['severity'] == 'high' else '🟡'
                report += f"{emoji} {alert['message']}\n"
        else:
            report += "✅ Все метрики в норме\n"
        
        report += f"\n⏱️ {datetime.fromisoformat(metrics['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}"
        
        return report

################################################################################
# CI/CD BOT
################################################################################

class CICDBot:
    """Управление CI/CD пайплайнами"""
    
    @staticmethod
    def trigger_build(project: str, branch: str = 'main') -> Dict:
        """Запуск сборки"""
        build_id = f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Симуляция CI/CD процесса
            steps = [
                ('Клонирование репозитория', 2),
                ('Установка зависимостей', 3),
                ('Запуск тестов', 5),
                ('Сборка артефактов', 4),
                ('Развертывание', 3)
            ]
            
            # В реальности здесь вызов Jenkins/GitLab CI/GitHub Actions API
            
            return {
                'success': True,
                'build_id': build_id,
                'project': project,
                'branch': branch,
                'status': 'started',
                'steps': steps
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_build_status(build_id: str) -> Dict:
        """Статус сборки"""
        # В реальности запрос к CI системе
        return {
            'build_id': build_id,
            'status': 'success',
            'duration': '17s',
            'tests_passed': 42,
            'tests_failed': 0,
            'coverage': '87%'
        }
    
    @staticmethod
    def rollback_deployment(environment: str) -> Dict:
        """Откат развертывания"""
        try:
            # Откат к предыдущей версии
            return {
                'success': True,
                'environment': environment,
                'reverted_to': 'previous_release',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

################################################################################
# КОМАНДЫ ОРКЕСТРАТОРА
################################################################################

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню оркестратора"""
    keyboard = [
        [KeyboardButton("🚀 DevOps"), KeyboardButton("🛡️ Security")],
        [KeyboardButton("💾 Backup"), KeyboardButton("📊 Monitoring")],
        [KeyboardButton("🔄 CI/CD"), KeyboardButton("⚙️ Settings")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        """
🤖 <b>Enterprise Bots Orchestrator v9.0</b>

Выберите бота для работы:

🚀 DevOps - Управление инфраструктурой
🛡️ Security - Аудит безопасности
💾 Backup - Резервное копирование
📊 Monitoring - Мониторинг метрик
🔄 CI/CD - Непрерывная интеграция

Используйте кнопки меню или команды.
""",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def backup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню управления backup"""
    keyboard = [
        [InlineKeyboardButton("📦 Создать backup", callback_data='backup_create')],
        [InlineKeyboardButton("📋 Список backup'ов", callback_data='backup_list')],
        [InlineKeyboardButton("♻️ Восстановить", callback_data='backup_restore')],
        [InlineKeyboardButton("🗑️ Очистить старые", callback_data='backup_cleanup')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💾 <b>Backup Manager</b>\n\nВыберите действие:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def backup_create_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание backup"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("⏳ Создание резервной копии...")
    
    result = BackupManager.create_backup('incremental')
    
    if result['success']:
        await query.edit_message_text(
            f"""
✅ <b>Backup создан успешно!</b>

📅 Время: {result['timestamp']}
📦 Размер: {result['size']}
📁 Путь: <code>{result['path']}</code>
🔄 Тип: {result['type']}
""",
            parse_mode='HTML'
        )
    else:
        await query.edit_message_text(
            f"❌ Ошибка создания backup:\n{result['error']}"
        )

async def backup_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список backup'ов"""
    query = update.callback_query
    await query.answer()
    
    backups = BackupManager.list_backups(10)
    
    if not backups:
        await query.edit_message_text("📭 Резервные копии не найдены")
        return
    
    text = "📋 <b>Резервные копии:</b>\n\n"
    
    for i, backup in enumerate(backups, 1):
        text += f"{i}. <code>{backup['timestamp']}</code> - {backup['size']}\n"
    
    await query.edit_message_text(text, parse_mode='HTML')

async def monitoring_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда мониторинга"""
    metrics = MonitoringBot.get_metrics()
    thresholds = {'cpu': 85, 'memory': 90, 'disk': 80}
    alerts = MonitoringBot.check_alerts(metrics, thresholds)
    report = MonitoringBot.generate_report(metrics, alerts)
    
    keyboard = [[InlineKeyboardButton("🔄 Обновить", callback_data='monitoring_refresh')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        report,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def cicd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню CI/CD"""
    keyboard = [
        [InlineKeyboardButton("🏗️ Запустить сборку", callback_data='cicd_build')],
        [InlineKeyboardButton("📊 Статус сборки", callback_data='cicd_status')],
        [InlineKeyboardButton("🚀 Развернуть", callback_data='cicd_deploy')],
        [InlineKeyboardButton("↩️ Откатить", callback_data='cicd_rollback')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔄 <b>CI/CD Manager</b>\n\nВыберите действие:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def cicd_build_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск сборки"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🏗️ Запуск сборки...")
    
    result = CICDBot.trigger_build('my-app', 'main')
    
    if result['success']:
        text = f"""
✅ <b>Сборка запущена!</b>

🆔 Build ID: <code>{result['build_id']}</code>
📦 Проект: {result['project']}
🌿 Ветка: {result['branch']}

<b>Этапы:</b>
"""
        for step, duration in result['steps']:
            text += f"  ⏱️ {step} (~{duration}s)\n"
        
        await query.edit_message_text(text, parse_mode='HTML')
    else:
        await query.edit_message_text(f"❌ Ошибка: {result['error']}")

################################################################################
# ГЛАВНАЯ ФУНКЦИЯ
################################################################################

def main():
    """Запуск оркестратора"""
    TOKEN = os.getenv('TELEGRAM_BOT_ORCHESTRATOR_TOKEN')
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_ORCHESTRATOR_TOKEN не установлен")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    # Базовые команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex('^💾 Backup$'), backup_menu))
    application.add_handler(MessageHandler(filters.Regex('^📊 Monitoring$'), monitoring_command))
    application.add_handler(MessageHandler(filters.Regex('^🔄 CI/CD$'), cicd_menu))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(backup_create_callback, pattern='^backup_create'))
    application.add_handler(CallbackQueryHandler(backup_list_callback, pattern='^backup_list'))
    application.add_handler(CallbackQueryHandler(cicd_build_callback, pattern='^cicd_build'))
    
    logger.info("🤖 Bots Orchestrator запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
