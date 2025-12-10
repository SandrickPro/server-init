# SSH Gate v2 - Comprehensive Documentation Index

## 🚀 Quick Start

**Хотите быстро развернуть?**

```bash
sudo bash install_ssh_gate_v2.sh
```

Затем следуйте интерактивным подсказкам. ~10-15 минут и система готова!

---

## 📚 Документация

### Для новичков

1. **[QUICK_START_V2.sh](QUICK_START_V2.sh)** ← **НАЧНИТЕ ОТСЮДА**
   - Интерактивное руководство на экране
   - Пошаговые инструкции
   - Объяснение каждого шага установки
   - Примеры команд

   ```bash
   bash QUICK_START_V2.sh
   ```

### Для разработчиков и администраторов

2. **[V2_ENHANCEMENTS.md](V2_ENHANCEMENTS.md)** - Новые функции v2
   - Per-user SSH snippets
   - Автоматическое удаление deleted users
   - Protocol-based firewall selection
   - Deduped IPTables rules
   - Deployment archive
   - Final summary report

3. **[ADMIN_GUIDE_V2.md](ADMIN_GUIDE_V2.md)** - Полное руководство администратора
   - Архитектура системы
   - Управление пользователями (добавление, удаление, ротация)
   - Управление SSH snippets
   - Управление firewall
   - Управление ключами
   - Мониторинг и логирование
   - Troubleshooting

4. **[EXAMPLES_V2.md](EXAMPLES_V2.md)** - Практические примеры
   - Web Server
   - Mail Server
   - Multi-purpose Server
   - Managed Hosting
   - FAQ

### Для миграции с v1

5. **[V1_VS_V2.md](V1_VS_V2.md)** - Сравнение версий
   - Что изменилось
   - Чего нет в v1
   - Migration path
   - Когда использовать какую версию

---

## 📋 Архитектура

### Основные компоненты

```
/srv/sys/
├── ssh/
│   ├── sshd_config.d/          Per-user SSH config snippets
│   ├── key-export/             SSH keys (export для скачивания)
│   ├── win_config/             Windows SSH config template
│   └── ssh_session/            Session logs с SID tracking
├── iptables/
│   └── v4/, v6/               Firewall rules (deduped)
├── audit/
│   └── rules.d/               Auditd rules
├── systemd/
│   └── system/                Systemd unit files
└── deploy/
    └── ssh-gate-deploy-*.tar.gz  Ready-to-download archive

/srv/home/
├── <user>/
│   ├── local/rbin/            Role-based restricted commands
│   └── .ssh/authorized_keys   SSH public keys
└── gate/
    ├── local/bin/             Gate helper scripts
    └── local/rbin/2<user>     Switch commands
```

### Ключевые функции

| Функция | Локация | Описание |
|---------|---------|-----------|
| Per-user SSH | `/srv/sys/ssh/sshd_config.d/10-user_*.conf` | Отдельный config для каждого пользователя |
| Role-based access | `/srv/home/<user>/local/rbin/` | Symlinks на разрешённые команды |
| Firewall | `/srv/sys/iptables/v4/merged.v4` | Deduped правила IPTables |
| Session logs | `/srv/sys/ssh/ssh_session/<date>/` | SID-based session tracking |
| Keys export | `/srv/sys/ssh/key-export/<user>/` | Для скачивания |
| Deploy archive | `/srv/sys/deploy/` | Готовый архив с ключами и конфигами |

---

## 🎯 Типичные задачи

### Установка системы
```bash
sudo bash install_ssh_gate_v2.sh
# Выполнить интерактивный wizard
```
→ See: [QUICK_START_V2.sh](QUICK_START_V2.sh)

### Добавление пользователя
```bash
sudo bash install_ssh_gate_v2.sh
# Ответить на: Add additional user? [y/N]: y
```
→ See: [ADMIN_GUIDE_V2.md#добавление-пользователя](ADMIN_GUIDE_V2.md)

### Удаление пользователя
```bash
sudo userdel -r username
sudo rm -rf /srv/home/username
sudo rm /srv/sys/ssh/sshd_config.d/10-user_username.*
sudo rm /srv/home/gate/local/rbin/2username
sudo systemctl reload ssh
```
→ See: [ADMIN_GUIDE_V2.md#удаление-пользователя](ADMIN_GUIDE_V2.md)

### Включение/отключение пользователя
```bash
# Отключить
sudo mv /srv/sys/ssh/sshd_config.d/10-user_username.conf \
       /srv/sys/ssh/sshd_config.d/10-user_username.conf.OFF
sudo systemctl reload ssh

# Включить
sudo mv /srv/sys/ssh/sshd_config.d/10-user_username.conf.OFF \
       /srv/sys/ssh/sshd_config.d/10-user_username.conf
sudo systemctl reload ssh
```
→ See: [ADMIN_GUIDE_V2.md#включениеотключение-пользователя](ADMIN_GUIDE_V2.md)

### Скачивание ключей
```bash
# На локальной машине
scp -P 22 gate@server:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./
tar -xzf ssh-gate-deploy-*.tar.gz
cd ssh-gate-deploy-*/

# Установка ключей
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cp keys/username@* ~/.ssh/
chmod 600 ~/.ssh/username@*
cat configs/ssh_config >> ~/.ssh/config
```
→ See: [ADMIN_GUIDE_V2.md#скачивание-ключей](ADMIN_GUIDE_V2.md)

### Добавление портов в firewall
```bash
# При установке выбрать протокол с портами
sudo bash install_ssh_gate_v2.sh

# Или вручную
sudo iptables -A INPUT -p tcp --dport 9000 -j ACCEPT
sudo /usr/local/sbin/restore_srv_iptables.sh save
```
→ See: [ADMIN_GUIDE_V2.md#добавление-нового-порта](ADMIN_GUIDE_V2.md)

### Просмотр логов сессий
```bash
tail -f /srv/sys/ssh/ssh_session/$(date +%d-%b\'%y | tr a-z A-Z)/*.log
grep "USER=username" /srv/sys/ssh/ssh_session/*/*.log
grep "192.168.1.50" /srv/sys/ssh/ssh_session/*/*.log
```
→ See: [ADMIN_GUIDE_V2.md#просмотр-логов-сессий](ADMIN_GUIDE_V2.md)

### Блокирование IP
```bash
sudo ipset add ssh_ban 192.168.1.50 timeout 3600
sudo ipset list ssh_ban
```
→ See: [ADMIN_GUIDE_V2.md#ip-based-whitelistban](ADMIN_GUIDE_V2.md)

---

## 🔧 Выбор по сценарию

### Я администратор одного сервера
→ [QUICK_START_V2.sh](QUICK_START_V2.sh) + [ADMIN_GUIDE_V2.md](ADMIN_GUIDE_V2.md)

### У меня несколько серверов разного типа
→ [EXAMPLES_V2.md](EXAMPLES_V2.md) (Web, Mail, Database examples)

### Я мигрирую с v1 на v2
→ [V1_VS_V2.md](V1_VS_V2.md) (Migration path)

### Я разрабатываю/модифицирую скрипт
→ [V2_ENHANCEMENTS.md](V2_ENHANCEMENTS.md) + исходный код в `install_ssh_gate_v2.sh`

### Я ищу troubleshooting помощь
→ [ADMIN_GUIDE_V2.md#troubleshooting](ADMIN_GUIDE_V2.md)

---

## 📁 Файлы проекта

### Основные скрипты

| Файл | Размер | Описание |
|------|--------|----------|
| `install_ssh_gate_v2.sh` | ~25 KB | **Основной скрипт установки v2** |
| `install_ssh_env.sh` | ~30 KB | SSH gate v1 (legacy) |
| `install_nginx_certbot.sh` | ~6 KB | Nginx + Certbot SSL (опционально) |

### Документация

| Файл | Размер | Для кого |
|------|--------|----------|
| `QUICK_START_V2.sh` | ~11 KB | Новичков (интерактивный гайд) |
| `V2_ENHANCEMENTS.md` | ~20 KB | Разработчиков (новые функции) |
| `ADMIN_GUIDE_V2.md` | ~30 KB | Администраторов (управление) |
| `EXAMPLES_V2.md` | ~20 KB | Всех (практические примеры) |
| `V1_VS_V2.md` | ~15 KB | Мигрирующих с v1 (сравнение) |
| `README.md` (этот файл) | ~5 KB | Навигация по документации |

### Вспомогательные файлы

| Файл | Описание |
|------|----------|
| `index.html` | Login page для nginx |
| `unauthorized.html` | Error page для nginx |
| `nginx_site.conf.template` | Nginx конфиг шаблон |

---

## ⚙️ Системные требования

- **OS**: Ubuntu 20.04 LTS, 22.04 LTS, или 24.04 LTS (CentOS/AlmaLinux также работают)
- **Архитектура**: x86_64 (amd64)
- **Размер диска**: 500MB минимум для `/srv/sys/`
- **RAM**: 512MB минимум
- **Сеть**: Публичный IP (опционально, если не требуется внешний доступ)

## 📦 Зависимости

Скрипт автоматически установит:
- OpenSSH (sshd)
- IPTables / IP6Tables
- IPSet
- Auditd
- Systemd (уже установлен)

## 🔐 Безопасность

Система по умолчанию:
- ✓ **Ключ-ориентирована**: Only SSH keys, no passwords
- ✓ **Restricted shell**: rbash для ограниченных пользователей
- ✓ **Session tracking**: Все сессии логируются с SID
- ✓ **Role-based**: Разные команды для разных пользователей
- ✓ **Auditd**: All changes logged to auditd
- ✓ **IPTables**: Stateful firewall с whitelisting
- ✓ **Auto-ban**: IP bans after 3 failed auth attempts

## 🚀 Быстрый старт в 4 шага

### 1. Скачайте скрипт на сервер
```bash
# На сервере
cd ~
curl -O https://your-repo/install_ssh_gate_v2.sh
# или скопируйте файл вручную
```

### 2. Запустите интерактивный wizard
```bash
sudo bash install_ssh_gate_v2.sh
```

### 3. Ответьте на вопросы
- Выберите протоколы (2 сек автоподтверждение)
- Введите SSH port
- Создайте gate и main пользователей
- Добавьте дополнительных пользователей если нужно

### 4. Скачайте архив с ключами
```bash
# На локальной машине
scp -P <ssh_port> gate@<server>:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./
tar -xzf ssh-gate-deploy-*.tar.gz
```

**Готово!** Система работает и готова к использованию.

---

## 📞 Поддержка

### Если что-то не работает

1. **Проверьте синтаксис SSHD**:
   ```bash
   sudo sshd -t
   ```

2. **Посмотрите логи SSH**:
   ```bash
   sudo journalctl -u ssh -n 50
   tail -50 /var/log/auth.log
   ```

3. **Проверьте firewall**:
   ```bash
   sudo iptables -L INPUT -n | head -20
   ```

4. **Читайте [ADMIN_GUIDE_V2.md#troubleshooting](ADMIN_GUIDE_V2.md#troubleshooting)**

---

## 📖 Дополнительное чтение

- [Linux rbash restricted shell](https://www.gnu.org/software/bash/manual/html_node/The-Restricted-Shell.html)
- [OpenSSH documentation](https://man.openbsd.org/sshd_config)
- [IPTables guide](https://linux.die.net/man/8/iptables)
- [auditd framework](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/security_guide/chap-system_auditing)

---

## 📝 Версионирование

- **v2.0** (Current) - Per-user snippets, auto-cleanup, protocol selection, deduped iptables, deployment archive
- **v1.0** - Basic SSH gate environment

---

## 📄 Лицензия

Скрипты предоставляются AS-IS. Используйте на свой риск. Тестируйте в non-production перед развертыванием.

---

## 🎓 Обучающие материалы

1. **Для новичков в SSH**:
   - Читайте [QUICK_START_V2.sh](QUICK_START_V2.sh) - имеет примеры всех команд

2. **Для администраторов Linux**:
   - [ADMIN_GUIDE_V2.md](ADMIN_GUIDE_V2.md) - полный справочник всех операций

3. **Для планирования развертывания**:
   - [EXAMPLES_V2.md](EXAMPLES_V2.md) - сценарии Web, Mail, Database, Hosting

4. **Для разработчиков и DevOps**:
   - [V2_ENHANCEMENTS.md](V2_ENHANCEMENTS.md) - архитектура новых функций

---

## ✅ Checklist для развертывания

- [ ] Скачан скрипт `install_ssh_gate_v2.sh`
- [ ] Server имеет минимум 500MB свободного места
- [ ] Выбран SSH port (рекомендуется 2022 или выше для безопасности)
- [ ] Определены пользователи и их роли
- [ ] Выбраны необходимые протоколы/порты
- [ ] Скрипт успешно выполнен (`Apply SSHD configuration? Y`)
- [ ] Архив создан в `/srv/sys/deploy/`
- [ ] Архив скачан на локальную машину
- [ ] SSH ключи установлены в `~/.ssh/` с правами 600
- [ ] SSH конфиг добавлен в `~/.ssh/config`
- [ ] Проверена SSH коннекция через gate
- [ ] Логирование работает (проверены `/srv/sys/ssh/ssh_session/` логи)

---

## 🔄 Continuous Improvement

Для регулярного maintenance:

```bash
# Еженедельно
sudo sshd -t              # Validate configuration
sudo iptables -L INPUT    # Check firewall rules

# Ежемесячно
tar -czf /backup/ssh_gate_$(date +%Y-%m-%d).tar.gz /srv/sys/
find /srv/sys/ssh/ssh_session -mtime +90 -delete   # Old logs cleanup

# При изменениях
sudo bash install_ssh_gate_v2.sh                    # Reinitialize with new settings
```

---

**Готовы начать?** 

```bash
sudo bash install_ssh_gate_v2.sh
```

или посмотрите интерактивный гайд:

```bash
bash QUICK_START_V2.sh
```
