# SSH Gate Environment Installer

## Описание

Полнофункциональный инсталлер для создания защищённого SSH jump host (gate) сервера с поддержкой:

- **Ролевого управления доступом** (13 предустановленных ролей)
- **Автоматической генерации SSH ключей** ed25519 для всех пользователей
- **IPTables/IPSet защиты** с прогрессивными временами блокировки (от 30 сек до 24 часов)
- **auditd логирования** всех критических действий
- **Регистрации сессий** с детерминированными SID
- **Модульной конфигурации sshd** с активными/неактивными снипетами
- **Systemd таймерами** для автоматической очистки логов

## Требования

### ОС
- Ubuntu 20.04+ / Debian 10+
- CentOS 8+ / AlmaLinux 8+
- Любой современный Linux с systemd, openssh-server, auditd

### Права доступа
- Скрипт должен запускаться от root

### Пакеты
Автоматически проверяются и используются при наличии:
- openssh-server
- openssh-client
- auditd
- iptables / ip6tables
- ipset
- systemd

## Установка

### 1. Скачайте скрипт

```bash
curl -o install_ssh_gate.sh https://your-repo/install_ssh_gate.sh
chmod +x install_ssh_gate.sh
```

### 2. Запустите на тестовой ВМ (ОБЯЗАТЕЛЬНО!)

```bash
sudo bash install_ssh_gate.sh
```

### 3. Следуйте интерактивным подсказкам

При запуске скрипт запросит:

```
Enter SSH port (default 22): 22
Enter gate username [gate]: gate
Enter main admin username [main]: main
```

Затем предложит создать дополнительных пользователей с выбором:
- Ролей (admin, advanced, user, guest, net-ops, db-admin и т.д.)
- SSH доступа через gate
- Привилегий sudo
- Использования rbash (restricted shell)

### 4. Загрузите сгенерированные ключи

SSH ключи экспортируются в:
```
/srv/sys/ssh/key-export/
```

Загрузите их на клиентские машины и **удалите с сервера** после завершения.

## Архитектура

### Структура директорий

```
/srv/sys/                          # Корень инфраструктуры
├── ssh/
│   ├── def_ssh_conf/             # Болван конфига sshd
│   ├── sshd_config.d/            # Модульные снипеты конфига
│   ├── key-export/               # Экспортированные SSH ключи
│   ├── ssh_session/              # Логи сессий (организованы по датам)
│   └── ssh_fail2ban/             # Счётчики и логи попыток входа
├── iptables/
│   ├── v4/                       # IPv4 правила firewall
│   └── v6/                       # IPv6 правила firewall
├── audit/
│   └── rules.d/                  # Правила auditd
├── sudoers.d/                    # Шаблоны sudo файлов
├── systemd/system/               # Systemd unit файлы
└── backup_passwd/                # Резервные копии /etc/passwd, /etc/shadow
```

### Пользователи и роли

#### Главные пользователи
- **gate** — restricted shell (rbash), может переключаться на других пользователей
- **main** — полный admin доступ, может работать с sudo без пароля

#### 13 предустановленных ролей
1. **admin** — полный доступ к системным утилитам
2. **advanced** — продвинутый пользователь (top, journalctl, curl, wget)
3. **user** — базовый пользователь (ls, grep, tail)
4. **guest** — гостевой доступ (только ls, cat, pwd, whoami)
5. **sandbox-isolated** — полная изоляция
6. **fake-admin** — подделка админа (stub команды)
7. **backup-ops** — операции с резервными копиями
8. **net-ops** — сетевые утилиты (ip, ss, ping, dig)
9. **monitoring** — мониторинг (iostat, vmstat, journalctl)
10. **readonly-audit** — только чтение audit логов
11. **mail-admin** — администрирование почты
12. **web-admin** — администрирование веб-сервиса
13. **db-admin** — администрирование БД

### SSH ключи

Для каждого пользователя автоматически:
1. Генерируется ed25519 ключевая пара
2. Публичный ключ добавляется в `~/.ssh/authorized_keys`
3. Приватный ключ экспортируется в `/srv/sys/ssh/key-export/$user/`

Формат имени ключа: `$user@server-DD_MMM_YY-$ip`

### Регистрация сессий

Каждая сессия через gate рекордится с:
- **SID** (Session ID) формата: `IP_user_DD-MMM_YY_HH.MM`
- **Временные метки** входа и выхода
- **Истории команд** (если rbash используется)

Логи хранятся в: `/srv/sys/ssh/ssh_session/$DATE/`

### IPTables/IPSet защита

- **Базовые правила**: DROP по умолчанию, разрешен только SSH
- **IPSet ban**: автоматический бан IP после 3 неудачных попыток
- **Прогрессивное увеличение**: время блокировки растет с каждым повторением (30с → 24ч)

### auditd логирование

Отслеживаются:
- Выполнение бинарников (execve)
- Использование sudo/su
- Изменения SSH конфига
- Изменения passwd/shadow/sudoers
- Изменения sshd конфига

Логи в systemd journal, доступны через `journalctl -u auditd`

## Использование

### Подключение через gate

```bash
ssh -i $KEY gate@server
# Внутри системы:
2main      # Переключиться на main пользователя
2user1     # Переключиться на user1
```

### Windows SSH конфиг

Автоматически генерируется в:
```
/srv/sys/ssh/key-export/ssh_config_windows.txt
```

Используйте с помощью:
```bash
ssh -F ssh_config_windows.txt gate@server
```

### Просмотр логов сессий

```bash
# Все логи за сегодня
ls /srv/sys/ssh/ssh_session/$(date +'%d-%b'%y | tr a-z A-Z)/

# Следить за новыми логами
tail -f /srv/sys/ssh/ssh_session/*/SID_*.log

# Просмотр через journalctl
journalctl -u auditd -f
```

### Просмотр IP банов

```bash
ipset list ssh_ban
ipset list ssh_white
```

### Добавление нового пользователя вручную

```bash
# Создание пользователя
useradd -m -d /srv/home/newuser -s /bin/bash newuser

# Установка роли
bash -c '. /srv/sys/ssh/sshd_config.d/roles.sh; install_role_rbin newuser admin'

# Генерация SSH ключа
bash -c '. /srv/sys/ssh/key-export/gen_key.sh; generate_and_install_key newuser $SERVER_IP'
```

## Безопасность

### Рекомендации

1. **Тестируйте в VM перед production** — это комплексная система
2. **Регулярно скачивайте и удаляйте приватные ключи** с сервера
3. **Мониторьте audit логи** на предмет anomalies
4. **Настраивайте SELinux/AppArmor** для дополнительной изоляции
5. **Используйте rbash** для restricted пользователей
6. **Регулярно обновляйте OpenSSH** и патчи безопасности

### Аудит

```bash
# Проверка audit логов
sudo ausearch -m EXECVE | tail -20

# Проверка изменений конфига
sudo ausearch -m CONFIG_CHANGE

# Полный аудит за день
sudo ausearch -ts today
```

## Troubleshooting

### SSH не стартует после применения конфига

```bash
# Проверка конфига
sshd -t

# Откат к последней хорошей версии
cp /srv/sys/ssh/last_good_sshd_config /etc/ssh/sshd_config
systemctl restart sshd
```

### Ключи не генерируются

```bash
# Проверка директории
ls -la /srv/sys/ssh/key-export/

# Ручная генерация
ssh-keygen -t ed25519 -C "user@host" -f /tmp/test -N ""
```

### IPSet не работает

```bash
# Проверка установки
apt install ipset  # или: yum install ipset

# Запуск сервиса
systemctl start ipset
systemctl enable ipset

# Пересоздание sets
ipset create ssh_ban hash:ip timeout 86400
ipset create ssh_white hash:ip timeout 0
```

## Лицензия

MIT

## Поддержка

Для вопросов и issues обратитесь к администратору системы.
