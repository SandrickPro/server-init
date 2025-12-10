# SSH Gate v2 - Полное руководство администратора

## Оглавление

1. [Архитектура](#архитектура)
2. [Управление пользователями](#управление-пользователями)
3. [Управление снипетами SSH](#управление-снипетами-ssh)
4. [Управление брандмауэром](#управление-брандмауэром)
5. [Управление ключами](#управление-ключами)
6. [Мониторинг и логирование](#мониторинг-и-логирование)
7. [Troubleshooting](#troubleshooting)

---

## Архитектура

### Директорийная структура

```
/srv/sys/
├── ssh/
│   ├── def_ssh_conf/
│   │   └── default_sshd_config_from_share  (базовая конфигурация)
│   ├── sshd_config.d/
│   │   ├── 00-PermitRootLogin.conf         (root запрещен)
│   │   ├── 01-PasswordAuthentication.conf  (пароли отключены)
│   │   ├── 02-PubkeyAuthentication.conf    (ключи включены)
│   │   ├── 06-Ciphers.conf                 (криптография)
│   │   ├── 10-user_main.conf               (конфиг для main)
│   │   ├── 10-user_gate.conf               (конфиг для gate)
│   │   ├── 10-user_mail_admin.conf         (конфиг для mail_admin)
│   │   └── ZZ-SSH-Port.conf                (порт SSH)
│   ├── key-export/
│   │   ├── main/
│   │   │   ├── main@server-08_JAN-IP
│   │   │   └── main@server-08_JAN-IP.pub
│   │   ├── mail_admin/
│   │   │   ├── mail_admin@server-08_JAN-IP
│   │   │   └── mail_admin@server-08_JAN-IP.pub
│   │   └── [другие пользователи...]
│   ├── win_config/
│   │   └── config                          (SSH config для Windows)
│   ├── ssh_session/
│   │   ├── 08-JAN'25/
│   │   │   ├── 192-168-1-100_main_08-JAN'25_14.22_main@08-JAN'25=14:22-14:45.log
│   │   │   └── [логи сессий по дате]
│   │   └── [другие даты...]
│   └── ssh_fail2ban/
│       ├── hits/          (счётчик неудачных попыток)
│       ├── level/         (уровень блокировки IP)
│       └── bans.log       (логи блокировок)
│
├── iptables/
│   ├── v4/
│   │   ├── merged.v4      (объединённые правила IPv4)
│   │   └── rules.v4       (сохранённые правила)
│   └── v6/
│       ├── merged.v6      (объединённые правила IPv6)
│       └── rules.v6       (сохранённые правила)
│
├── audit/
│   └── rules.d/
│       └── 99-ssh-audit.rules  (правила auditd)
│
├── systemd/
│   └── system/
│       ├── iptables-restore.service
│       ├── session-maintenance.service
│       ├── session-maintenance.timer
│       └── [другие unit-файлы]
│
├── sudoers.d/
│   ├── main                (sudoers для main)
│   └── [другие пользователи с sudo]
│
├── etc/
│   └── profile.d/
│       └── gate-banner.sh  (MOTD баннер)
│
└── deploy/
    ├── ssh-gate-deploy-20250108_143022.tar.gz  (архив для скачивания)
    ├── deployed_users.txt   (отслеживание пользователей)
    └── [другие архивы...]

/srv/home/
├── main/
│   ├── local/
│   │   ├── bin/
│   │   │   └── [пользовательские скрипты]
│   │   └── rbin/          (restricted bin - symlinks на разрешённые команды)
│   └── .ssh/
│       └── authorized_keys
│
├── gate/
│   ├── local/
│   │   ├── bin/
│   │   │   ├── enter_as_user.sh         (переключение пользователя)
│   │   │   ├── gate_finalize_session    (финализация сессии)
│   │   │   └── gate_login_wrapper       (ForceCommand для SSH)
│   │   └── rbin/                        (команды переключения 2<user>)
│   │       ├── 2main                    (switch to main)
│   │       ├── 2mail_admin              (switch to mail_admin)
│   │       └── [другие переключатели...]
│   └── .ssh/
│       └── authorized_keys
│
└── mail_admin/
    ├── local/
    │   ├── bin/
    │   └── rbin/          (разрешённые команды для mail-admin роли)
    └── .ssh/
        └── authorized_keys
```

---

## Управление пользователями

### 1. Добавление нового пользователя

**Способ 1: При первоначальной установке**
```bash
sudo bash install_ssh_gate_v2.sh

# На запрос:
# Add additional user? [y/N]: y
# Username: newuser
# Role number [0-13]: 8   (например, monitoring)
# SSH access via gate? [y/N]: y
# Grant sudo? [y/N]: n
# Use rbash? [y/N]: y
# Generate SSH key now? [y/N]: y
```

**Способ 2: Вручную после установки**
```bash
# Создать пользователя
sudo useradd -m -d /srv/home/newuser -s /bin/bash newuser

# Создать директории
sudo mkdir -p /srv/home/newuser/{.ssh,local/{bin,rbin}}
sudo chown -R newuser:newuser /srv/home/newuser

# Установить role-based rbin
# (скопировать функцию install_role_rbin из скрипта и выполнить)

# Создать SSH snippet
sudo tee /srv/sys/ssh/sshd_config.d/10-user_newuser.conf > /dev/null <<'EOF'
Match User newuser
  ForceCommand /srv/home/newuser/local/bin/gate_login_wrapper
  X11Forwarding no
  AllowAgentForwarding no
EOF

# Добавить в gate rbin команду переключения
sudo tee /srv/home/gate/local/rbin/2newuser > /dev/null <<EOF
#!/usr/bin/env bash
exec /srv/home/gate/local/bin/enter_as_user.sh newuser
EOF
sudo chmod 755 /srv/home/gate/local/rbin/2newuser

# Генерировать SSH ключ
sudo ssh-keygen -t ed25519 -C "newuser@$(hostname -f)" \
  -f /srv/sys/ssh/key-export/newuser/newuser@server \
  -N "" -q

# Добавить public key в authorized_keys
sudo cat /srv/sys/ssh/key-export/newuser/newuser@server.pub >> \
  /srv/home/newuser/.ssh/authorized_keys

# Проверить конфиг
sudo sshd -t
sudo systemctl reload ssh
```

### 2. Удаление пользователя

**Полное удаление:**
```bash
# Переименовать пользователя (безопаснее чем удаление)
sudo usermod -l olduser_ARCHIVED olduser

# Или полное удаление:
sudo userdel -r olduser

# Удалить из /srv/home/
sudo rm -rf /srv/home/olduser

# Удалить SSH snippet
sudo rm /srv/sys/ssh/sshd_config.d/10-user_olduser.{conf,conf.inactive}

# Удалить из gate rbin (автоматически при переустановке, или вручную)
sudo rm /srv/home/gate/local/rbin/2olduser

# Удалить ключи
sudo rm -rf /srv/sys/ssh/key-export/olduser

# Проверить и перезагрузить SSH
sudo sshd -t
sudo systemctl reload ssh
```

### 3. Изменение роли пользователя

```bash
# 1. Удалить старые symlink из rbin
sudo rm -f /srv/home/username/local/rbin/*

# 2. Установить новые symlink для новой роли
# (используя install_role_rbin функцию из скрипта)
# Или скопировать разрешённые команды:

sudo ln -sf /bin/ls /srv/home/username/local/rbin/ls
sudo ln -sf /usr/bin/curl /srv/home/username/local/rbin/curl
# ... и т.д.

# 3. Перезагрузить SSH
sudo systemctl reload ssh
```

### 4. Выдача/отзыв sudo доступа

**Выдать sudo:**
```bash
sudo tee /srv/sys/sudoers.d/username > /dev/null <<EOF
username ALL=(ALL) NOPASSWD:ALL
EOF
sudo ln -sf /srv/sys/sudoers.d/username /etc/sudoers.d/username
sudo chmod 440 /srv/sys/sudoers.d/username
sudo visudo -c  # проверить синтаксис
```

**Отозвать sudo:**
```bash
sudo rm -f /srv/sys/sudoers.d/username /etc/sudoers.d/username
sudo visudo -c  # проверить синтаксис
```

---

## Управление снипетами SSH

### 1. Структура снипетов

Каждый снипет состоит из двух файлов:

```bash
# АКТИВНЫЙ - применяется к sshd
/srv/sys/ssh/sshd_config.d/10-user_username.conf

# НЕАКТИВНЫЙ - заменяет активный при отключении
/srv/sys/ssh/sshd_config.d/10-user_username.conf.inactive
```

### 2. Включение/отключение пользователя

```bash
# ОТКЛЮЧИТЬ пользователя (переименовать активный)
sudo mv /srv/sys/ssh/sshd_config.d/10-user_username.conf \
       /srv/sys/ssh/sshd_config.d/10-user_username.conf.OFF

# Или заменить на неактивный
sudo cp /srv/sys/ssh/sshd_config.d/10-user_username.conf.inactive \
       /srv/sys/ssh/sshd_config.d/10-user_username.conf

# ВКЛЮЧИТЬ пользователя (восстановить из backup)
sudo cp /srv/sys/ssh/sshd_config.d/10-user_username.conf.OFF \
       /srv/sys/ssh/sshd_config.d/10-user_username.conf

# Проверить синтаксис
sudo sshd -t

# Перезагрузить SSH
sudo systemctl reload ssh
```

### 3. Просмотр активных снипетов

```bash
# Только активные (применяющиеся)
ls -la /srv/sys/ssh/sshd_config.d/*.conf

# Только неактивные
ls -la /srv/sys/ssh/sshd_config.d/*.conf.inactive

# Все
ls -la /srv/sys/ssh/sshd_config.d/

# Содержимое конкретного снипета
cat /srv/sys/ssh/sshd_config.d/10-user_main.conf

# Проверить полную конфигурацию sshd
sudo sshd -T | head -30
```

### 4. Редактирование снипета

```bash
# Отредактировать активный снипет
sudo nano /srv/sys/ssh/sshd_config.d/10-user_username.conf

# Добавить больше опций в ForceCommand
# Пример: отключить agent forwarding и X11
sudo cat >> /srv/sys/ssh/sshd_config.d/10-user_username.conf <<'EOF'

# Дополнительные ограничения
PermitUserEnvironment no
AllowTcpForwarding no
X11Forwarding no
EOF

# Проверить синтаксис
sudo sshd -t

# Перезагрузить
sudo systemctl reload ssh
```

---

## Управление брандмауэром

### 1. Просмотр текущих правил

```bash
# Посмотреть объединённые правила IPv4
cat /srv/sys/iptables/v4/merged.v4

# Посмотреть текущие активные правила iptables
sudo iptables -L INPUT -n | head -30

# Посмотреть IPv6 правила
sudo ip6tables -L INPUT -n | head -30

# Посмотреть все правила с counters
sudo iptables -L -n -v
```

### 2. Добавление нового порта

```bash
# СПОСОБ 1: Переустановить скрипт и добавить протокол
sudo bash install_ssh_gate_v2.sh
# На запросе Enable <protocol>? выбрать нужный

# СПОСОБ 2: Вручную добавить порт
# Добавить правило iptables
sudo iptables -A INPUT -p tcp --dport 9000 -j ACCEPT

# Сохранить в файл
sudo /usr/local/sbin/restore_srv_iptables.sh save

# Перестроить merged файл (скопировать и запустить)
# (используйте write_merged_iptables_file из скрипта)

# Проверить
sudo iptables -L INPUT -n | grep 9000
```

### 3. Удаление портов

```bash
# СПОСОБ 1: Переустановить и отказать от протокола
sudo bash install_ssh_gate_v2.sh
# Ответить NO на неиспользуемый протокол

# СПОСОБ 2: Вручную
# Найти строку в merged.v4
grep "dport 9000" /srv/sys/iptables/v4/merged.v4

# Удалить правило iptables
sudo iptables -D INPUT -p tcp --dport 9000 -j ACCEPT

# Сохранить
sudo /usr/local/sbin/restore_srv_iptables.sh save
```

### 4. Дедупликация правил

Скрипт автоматически удаляет дубликаты при вызове `write_merged_iptables_file()`.

Если нужно сделать вручную:

```bash
# Просмотреть дубликаты
grep "dport" /srv/sys/iptables/v4/merged.v4 | sort | uniq -d

# Очистить всё и перестроить
sudo bash install_ssh_gate_v2.sh

# Выбрать только нужные протоколы
# Система автоматически создаст неповторяющиеся правила
```

### 5. IP-based whitelist/ban

```bash
# Добавить IP в whitelist
sudo ipset add ssh_white 192.168.1.50 timeout 2592000

# Добавить IP в ban list
sudo ipset add ssh_ban 10.0.0.100 timeout 86400

# Посмотреть whitelist
sudo ipset list ssh_white

# Посмотреть bans
sudo ipset list ssh_ban

# Удалить IP из ban list
sudo ipset del ssh_ban 10.0.0.100

# Просмотреть лог блокировок
tail -20 /srv/sys/ssh/ssh_fail2ban/bans.log
```

---

## Управление ключами

### 1. Генерация ключей

```bash
# При установке - автоматически при выборе "Generate SSH key now"

# Вручную для существующего пользователя
sudo ssh-keygen -t ed25519 \
  -C "username@$(hostname -f)" \
  -f /srv/sys/ssh/key-export/username/username@server \
  -N "" -q

# Добавить public key в authorized_keys пользователя
sudo cat /srv/sys/ssh/key-export/username/username@server.pub >> \
  /srv/home/username/.ssh/authorized_keys
```

### 2. Скачивание ключей

```bash
# На локальной машине:
scp -P 22 gate@server:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./

# Или скачать отдельный ключ:
scp -P 22 gate@server:/srv/sys/ssh/key-export/username/username@server ~/.ssh/

# Установить права
chmod 600 ~/.ssh/username@server
```

### 3. Управление Windows SSH config

```bash
# Автоматически обновляется при добавлении/удалении ключей
cat /srv/sys/ssh/win_config/config

# Пример содержимого:
# Host main
#     HostName 192.168.1.100
#     Port 22
#     User main
#     ProxyJump gate@192.168.1.100
#     IdentityFile C:\Users\<you>\.ssh\main@server

# Использовать в SSH client:
# Скопировать содержимое в ~/.ssh/config на Windows машине
# Или импортировать в PuTTY/Termius
```

### 4. Ротация ключей

```bash
# Создать новый ключ
sudo ssh-keygen -t ed25519 \
  -C "username@$(hostname -f)" \
  -f /srv/sys/ssh/key-export/username/username@server-new \
  -N "" -q

# Добавить новый public key
sudo cat /srv/sys/ssh/key-export/username/username@server-new.pub >> \
  /srv/home/username/.ssh/authorized_keys

# Проверить что работает с новым ключом
ssh -i ~/.ssh/username@server-new gate@server

# Удалить старый public key (после проверки нового)
sudo sed -i '/username@server/d' /srv/home/username/.ssh/authorized_keys

# Или вручную удалить старую строку из authorized_keys:
sudo nano /srv/home/username/.ssh/authorized_keys
```

---

## Мониторинг и логирование

### 1. Просмотр логов сессий

```bash
# Все логи по дате
ls -la /srv/sys/ssh/ssh_session/

# Логи за сегодня
ls -la /srv/sys/ssh/ssh_session/$(date +%d-%b\'%y | tr a-z A-Z)/

# Последние 10 логов
ls -lt /srv/sys/ssh/ssh_session/*/*.log | head -10

# Содержимое конкретной сессии
cat /srv/sys/ssh/ssh_session/08-JAN\'25/192-168-1-100_main_08-JAN\'25_14.22_main@08-JAN\'25=14:22-14:45.log

# Все сессии конкретного пользователя
grep "USER=main" /srv/sys/ssh/ssh_session/*/*.log

# Поиск по IP
grep "192.168.1.50" /srv/sys/ssh/ssh_session/*/*.log | head -20

# Последние активности (real-time)
tail -f /srv/sys/ssh/ssh_session/$(date +%d-%b\'%y | tr a-z A-Z)/*.log
```

### 2. SID (Session ID) формат

```
IP-IP-IP-IP_USERNAME_DD-MON'YY_HH.MM

Пример: 192-168-1-50_main_08-JAN'25_14.22

Можно разобрать по компонентам:
- 192-168-1-50 = IP адрес клиента (точки заменены на дефисы)
- main = имя пользователя
- 08-JAN'25 = дата (08 января 2025)
- 14.22 = время начала сессии (14:22)
```

### 3. Auditd логирование

```bash
# Проверить что auditd включен
sudo systemctl status auditd

# Просмотреть правила
sudo auditctl -l

# Просмотреть логи auditd
sudo tail -100 /var/log/audit/audit.log | grep ssh

# Фильтр по типу события
sudo aureport -k -ts recent | head -30

# Посмотреть кто что делал
sudo aureport --tty

# Полный отчет за период
sudo aureport -ts today
```

### 4. Мониторинг firewall

```bash
# Проверить что iptables применены
sudo iptables -L INPUT -n | head -20

# Посмотреть counter's для каждого правила
sudo iptables -L INPUT -n -v

# Сброс счётчиков
sudo iptables -Z

# Проверить статус systemd unit
sudo systemctl status iptables-restore.service

# Просмотреть IP bans
tail -50 /srv/sys/ssh/ssh_fail2ban/bans.log

# Текущие забанены IP
sudo ipset list ssh_ban

# Whitelisted IPs
sudo ipset list ssh_white
```

### 5. Systemd timers

```bash
# Список всех таймеров
sudo systemctl list-timers

# Статус конкретного таймера
sudo systemctl status session-maintenance.timer

# Просмотреть последнее время запуска
sudo systemctl status session-maintenance.service

# Вручную запустить maintenance
sudo /usr/local/sbin/maintain_sessions.sh

# Лог запусков
sudo journalctl -u session-maintenance.timer -n 30

# Лог последнего запуска
sudo journalctl -u session-maintenance.service -n 30
```

---

## Troubleshooting

### Проблема: SSH connection refused

```bash
# Проверить что SSH слушает на нужном порту
sudo ss -tlnp | grep sshd

# Проверить что порт в iptables разрешен
sudo iptables -L INPUT -n | grep <port>

# Проверить SSH configuration
sudo sshd -t

# Перезагрузить SSH
sudo systemctl restart ssh

# Проверить логи SSH
sudo tail -30 /var/log/auth.log | grep ssh
```

### Проблема: Permission denied при SSH

```bash
# Проверить что ключ установлен правильно
ls -la ~/.ssh/<key>
chmod 600 ~/.ssh/<key>

# Проверить что public key в authorized_keys
cat /srv/home/username/.ssh/authorized_keys | grep "$(cat ~/.ssh/<key>.pub)"

# Проверить что пользователь существует
id username

# Проверить что SSH snippet создан
cat /srv/sys/ssh/sshd_config.d/10-user_username.conf

# Проверить sshd конфиг
sudo sshd -T | grep -i match
```

### Проблема: rbash команда не найдена

```bash
# Проверить что symlink создан
ls -la /srv/home/username/local/rbin/

# Проверить что команда существует на сервере
which ls
which curl

# Пересоздать symlink
sudo ln -sf /bin/ls /srv/home/username/local/rbin/ls

# Проверить права
ls -la /srv/home/username/local/rbin/ls
```

### Проблема: SSHD не перезагружается

```bash
# Проверить синтаксис конфига
sudo sshd -t

# Если ошибка - прочитать её внимательно
# Обычно ошибка в один из файлов в sshd_config.d/

# Временно отключить проблемный снипет
sudo mv /srv/sys/ssh/sshd_config.d/10-user_problem.conf \
       /srv/sys/ssh/sshd_config.d/10-user_problem.conf.OFF

# Проверить снова
sudo sshd -t

# Перезагрузить
sudo systemctl reload ssh

# Потом отредактировать и включить обратно
sudo nano /srv/sys/ssh/sshd_config.d/10-user_problem.conf.OFF
sudo mv /srv/sys/ssh/sshd_config.d/10-user_problem.conf.OFF \
       /srv/sys/ssh/sshd_config.d/10-user_problem.conf
sudo sshd -t
sudo systemctl reload ssh
```

### Проблема: Firewall заблокировал IP

```bash
# Посмотреть текущие bans
sudo ipset list ssh_ban

# Удалить IP из ban list
sudo ipset del ssh_ban 192.168.1.50

# Или добавить в whitelist
sudo ipset add ssh_white 192.168.1.50 timeout 2592000

# Просмотреть лог блокировок
tail -50 /srv/sys/ssh/ssh_fail2ban/bans.log

# Если частые блокировки - увеличить допуск в скрипте
# (отредактировать BAN_DURATIONS и переустановить)
```

### Проблема: Не генерируется архив

```bash
# Проверить что директория существует
ls -la /srv/sys/deploy/

# Проверить права
sudo ls -la /srv/sys/deploy/

# Создать правильно
sudo mkdir -p /srv/sys/deploy
sudo chmod 755 /srv/sys/deploy

# Переустановить скрипт
sudo bash install_ssh_gate_v2.sh

# Проверить архив
ls -lh /srv/sys/deploy/ssh-gate-deploy-*.tar.gz
```

---

## Дополнительные команды для управления

```bash
# Просмотреть все пользователи в /srv/home
ls -d /srv/home/*/

# Просмотреть все SSH snippets
ls -1 /srv/sys/ssh/sshd_config.d/10-user_*.conf

# Просмотреть архивы для скачивания
ls -lh /srv/sys/deploy/

# Статистика по сессиям
find /srv/sys/ssh/ssh_session -name '*.log' | wc -l

# Размер логов
du -sh /srv/sys/ssh/ssh_session/

# Архивирование старых логов
find /srv/sys/ssh/ssh_session -type f -name '*.log' -mtime +30 -exec gzip {} \;

# Проверить размер /srv/sys
du -sh /srv/sys/

# Найти крупные файлы
find /srv/sys -type f -size +10M

# Очистить temp файлы
find /srv/sys/tmp -type f -mtime +7 -delete
```

---

## Best Practices

1. **Регулярно делайте бэкапы:**
   ```bash
   tar -czf /backup/ssh_gate_$(date +%Y-%m-%d).tar.gz /srv/sys/
   ```

2. **Ротируйте ключи ежемесячно**

3. **Удаляйте старые логи:**
   ```bash
   find /srv/sys/ssh/ssh_session -type f -mtime +90 -delete
   ```

4. **Мониторьте IP bans:**
   ```bash
   watch -n 10 'sudo ipset list ssh_ban | head -20'
   ```

5. **Проверяйте SSH конфиг еженедельно:**
   ```bash
   sudo sshd -t && echo "OK" || echo "ERROR"
   ```

6. **Логируйте все изменения:**
   ```bash
   echo "$(date): Удалён пользователь olduser" >> /var/log/ssh_gate_changes.log
   ```
