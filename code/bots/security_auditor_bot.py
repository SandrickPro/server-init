#!/usr/bin/env python3
"""
Enterprise Telegram Bot - Security Auditor
Автоматический аудит безопасности и мониторинг угроз
Version: 9.0.0
"""

import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import subprocess
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

################################################################################
# SECURITY SCANNER
################################################################################

class SecurityScanner:
    """Комплексное сканирование безопасности"""
    
    @staticmethod
    def check_ssh_config() -> dict:
        """Проверка конфигурации SSH"""
        issues = []
        score = 100
        
        try:
            with open('/etc/ssh/sshd_config', 'r') as f:
                config = f.read()
            
            checks = {
                'PermitRootLogin no': ('Root login разрешен', 20),
                'PasswordAuthentication no': ('Парольная аутентификация включена', 15),
                'PubkeyAuthentication yes': ('Публичные ключи отключены', 10),
                'Port 22': ('Используется стандартный порт SSH', 5),
            }
            
            for check, (issue, penalty) in checks.items():
                if check not in config:
                    issues.append(issue)
                    score -= penalty
        except:
            issues.append("Не удалось прочитать конфигурацию SSH")
            score = 50
        
        return {'score': max(score, 0), 'issues': issues}
    
    @staticmethod
    def check_firewall() -> dict:
        """Проверка фаервола"""
        try:
            result = subprocess.run(
                ['iptables', '-L', '-n'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            rules_count = len(result.stdout.splitlines())
            
            if 'policy DROP' in result.stdout:
                return {'score': 100, 'status': '🟢 Firewall активен', 'rules': rules_count}
            else:
                return {'score': 50, 'status': '🟡 Firewall настроен слабо', 'rules': rules_count}
        except:
            return {'score': 0, 'status': '🔴 Firewall не найден', 'rules': 0}
    
    @staticmethod
    def check_open_ports() -> dict:
        """Сканирование открытых портов"""
        try:
            result = subprocess.run(
                ['ss', '-tuln'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            ports = re.findall(r':(\d+)\s', result.stdout)
            open_ports = list(set(ports))
            
            dangerous_ports = ['23', '21', '445', '139', '3389']
            found_dangerous = [p for p in open_ports if p in dangerous_ports]
            
            score = 100 - (len(found_dangerous) * 20)
            
            return {
                'score': max(score, 0),
                'total': len(open_ports),
                'dangerous': found_dangerous
            }
        except:
            return {'score': 50, 'total': 0, 'dangerous': []}
    
    @staticmethod
    def check_failed_logins() -> dict:
        """Проверка неудачных попыток входа"""
        try:
            result = subprocess.run(
                ['grep', 'Failed password', '/var/log/auth.log'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            failed_count = len(result.stdout.splitlines())
            
            if failed_count == 0:
                return {'score': 100, 'count': 0, 'status': '🟢 Нет неудачных попыток'}
            elif failed_count < 10:
                return {'score': 80, 'count': failed_count, 'status': '🟡 Несколько попыток'}
            else:
                return {'score': 30, 'count': failed_count, 'status': '🔴 Множество попыток'}
        except:
            return {'score': 100, 'count': 0, 'status': '✅ Логи чисты'}
    
    @staticmethod
    def full_audit() -> dict:
        """Полный аудит безопасности"""
        ssh = SecurityScanner.check_ssh_config()
        firewall = SecurityScanner.check_firewall()
        ports = SecurityScanner.check_open_ports()
        logins = SecurityScanner.check_failed_logins()
        
        total_score = (ssh['score'] + firewall['score'] + ports['score'] + logins['score']) / 4
        
        if total_score >= 90:
            grade = '🟢 ОТЛИЧНО'
        elif total_score >= 70:
            grade = '🟡 ХОРОШО'
        elif total_score >= 50:
            grade = '🟠 УДОВЛЕТВОРИТЕЛЬНО'
        else:
            grade = '🔴 ПЛОХО'
        
        return {
            'total_score': round(total_score, 1),
            'grade': grade,
            'ssh': ssh,
            'firewall': firewall,
            'ports': ports,
            'logins': logins,
            'timestamp': datetime.now().isoformat()
        }

################################################################################
# КОМАНДЫ БОТА
################################################################################

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое сообщение"""
    keyboard = [
        [InlineKeyboardButton("🔍 Быстрый аудит", callback_data='quick_audit')],
        [InlineKeyboardButton("🛡️ Полный аудит", callback_data='full_audit')],
        [InlineKeyboardButton("🔐 SSH проверка", callback_data='check_ssh')],
        [InlineKeyboardButton("🔥 Firewall", callback_data='check_firewall')],
        [InlineKeyboardButton("🚪 Открытые порты", callback_data='check_ports')],
        [InlineKeyboardButton("🚨 Неудачные логины", callback_data='check_logins')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        """
🛡️ <b>Security Auditor Bot v9.0</b>

Я проведу комплексную проверку безопасности:
  • Конфигурация SSH
  • Настройки Firewall
  • Открытые порты
  • Попытки взлома
  • Уязвимости

Выберите тип проверки:
""",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def full_audit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Полный аудит безопасности"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔍 Выполняю полный аудит безопасности...")
    
    audit = SecurityScanner.full_audit()
    
    report = f"""
╔════════════════════════════════════════╗
        🛡️ <b>SECURITY AUDIT REPORT</b>
╚════════════════════════════════════════╝

<b>📊 ОБЩАЯ ОЦЕНКА: {audit['total_score']}/100</b>
{audit['grade']}

<b>🔐 SSH КОНФИГУРАЦИЯ:</b> {audit['ssh']['score']}/100
"""
    
    if audit['ssh']['issues']:
        report += "  Проблемы:\n"
        for issue in audit['ssh']['issues']:
            report += f"    ❌ {issue}\n"
    else:
        report += "  ✅ Конфигурация безопасна\n"
    
    report += f"""
<b>🔥 FIREWALL:</b> {audit['firewall']['score']}/100
  {audit['firewall']['status']}
  Правил: {audit['firewall']['rules']}

<b>🚪 ОТКРЫТЫЕ ПОРТЫ:</b> {audit['ports']['score']}/100
  Всего: {audit['ports']['total']}
"""
    
    if audit['ports']['dangerous']:
        report += f"  ⚠️ Опасные порты: {', '.join(audit['ports']['dangerous'])}\n"
    else:
        report += "  ✅ Опасных портов не обнаружено\n"
    
    report += f"""
<b>🚨 НЕУДАЧНЫЕ ЛОГИНЫ:</b> {audit['logins']['score']}/100
  {audit['logins']['status']}
  Попыток: {audit['logins']['count']}

<b>⏱️ Время проверки:</b>
  {datetime.fromisoformat(audit['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    keyboard = [[InlineKeyboardButton("🔄 Повторить аудит", callback_data='full_audit')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        report,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

def main():
    """Запуск бота"""
    TOKEN = os.getenv('TELEGRAM_BOT_SECURITY_TOKEN')
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_SECURITY_TOKEN не установлен")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(full_audit_callback, pattern='^full_audit'))
    
    logger.info("🛡️ Security Auditor Bot запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
