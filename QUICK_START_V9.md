# 🚀 Quick Start Guide - Enterprise Deploy v9.0

Быстрое развертывание за **3 минуты**.

---

## ⚡ Установка в 3 команды

```bash
# 1. Клонирование
git clone https://github.com/your-repo/enterprise-deploy.git
cd enterprise-deploy

# 2. Запуск мастер-скрипта
sudo ./code/enterprise-deploy-master.sh

# 3. Выбрать: 1) Быстрая установка → Готово! 🎉
```

---

## 🎯 Что установится (профиль Professional):

- ✅ VSCode Server (порт 8443)
- ✅ Docker Manager
- ✅ Prometheus (порт 9090) + Grafana (порт 3000)
- ✅ 5 Telegram ботов
- ✅ Автоматический backup (3:00 AM daily)
- ✅ Security hardening
- ✅ Structured logging
- ✅ Health checks

---

## 🖥️ Использование CLI

```bash
# Мониторинг
enterprise-cli monitor dashboard

# Backup
enterprise-cli backup create
enterprise-cli backup list

# Сервисы
enterprise-cli services list
enterprise-cli services restart nginx

# Deploy
enterprise-cli deploy start
```

---

## 🤖 Настройка Telegram ботов

### 1. Создайте ботов через @BotFather:

```
/newbot
Имя: DevOps Manager
Username: my_devops_bot
→ Скопируйте токен: 123456:ABCdef...
```

### 2. Получите свой Telegram ID:

Откройте @userinfobot → Скопируйте Id

### 3. Настройте токены:

```bash
sudo ./code/enterprise-deploy-master.sh
# Меню → 5 (Управление ботами) → 6 (Настроить токены)
```

### 4. Запустите ботов:

```bash
# DevOps Manager
python3 /opt/enterprise-deploy/code/bots/devops_manager_bot.py &

# Security Auditor  
python3 /opt/enterprise-deploy/code/bots/security_auditor_bot.py &

# Orchestrator
python3 /opt/enterprise-deploy/code/bots/bots_orchestrator.py &
```

---

## 📊 Первый запуск

### 1. Проверьте статус:
```bash
enterprise-cli monitor dashboard
```

### 2. Просмотрите сервисы:
```bash
enterprise-cli services list
```

### 3. Создайте первый backup:
```bash
enterprise-cli backup create
```

### 4. Откройте VSCode Server:
```
https://YOUR_IP:8443
Пароль в: /opt/code-server/config.yaml
```

---

## 🔧 Порты

| Сервис | Порт | URL |
|--------|------|-----|
| VSCode Server | 8443 | https://IP:8443 |
| Prometheus | 9090 | http://IP:9090 |
| Grafana | 3000 | http://IP:3000 |
| Nginx | 80, 443 | http://IP |

---

## 📚 Полная документация

- `ENTERPRISE_REPORT_V9.md` - Полный отчет (150 страниц)
- `README_V8.md` - Документация v8
- `code/config/enterprise-config.yaml` - Конфигурация

---

## 🆘 Помощь

```bash
enterprise-cli help
./code/enterprise-deploy-master.sh
```

**Support:** https://github.com/your-repo/enterprise-deploy/issues

---

✅ **Готово! Система развёрнута.**
