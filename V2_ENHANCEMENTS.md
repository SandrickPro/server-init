# SSH Gate v2 - Расширения и улучшения

## Новые функциональности

### 1. **Динамические SSH-снипеты для каждого пользователя**

Каждый созданный пользователь получает свой собственный SSH config снипет:

```bash
# Автоматически создаётся:
/srv/sys/ssh/sshd_config.d/10-user_<username>.conf
/srv/sys/ssh/sshd_config.d/10-user_<username>.conf.inactive
```

#### Функция:
```bash
write_user_ssh_snippet "$user" "$shell"
```

**Преимущества:**
- Можно включать/отключать доступ конкретного пользователя без переконфигурации всей системы
- Каждый пользователь имеет независимый ForceCommand
- Легко отследить, какие пользователи активны

#### Пример для gate:
```
Match User gate
  ForceCommand /srv/home/gate/local/bin/gate_login_wrapper
  X11Forwarding no
  AllowAgentForwarding no
```

---

### 2. **Удаление deleted-пользователей из gate rbin**

При переустановке скрипта или удалении пользователя система автоматически очищает leftover symlinks:

```bash
cleanup_deleted_users "$GATE_USER"
```

#### Как это работает:
1. Скрипт сканирует `/srv/home/gate/local/rbin/2*`
2. Проверяет, существует ли пользователь с `id <username>`
3. Если пользователя нет → удаляет symlink `2<deleted_user>`

#### Логирование:
```
[!] Cleaned up deleted user switch for olduser
```

---

### 3. **Интерактивный выбор протоколов с группировкой портов**

Система предлагает на выбор протоколы с автоматической подтверждением (2 секунды):

```bash
select_protocols()
```

#### Доступные протоколы:
| Протокол | Порты |
|----------|-------|
| web | 80, 443 |
| mail | 25, 110, 143, 465, 587, 993, 995 |
| dns | 53 |
| ftp | 20, 21, 989, 990 |
| db | 3306, 5432, 27017, 6379 |
| vpn | 1194, 51820 |
| ntp | 123 |
| snmp | 161, 162 |
| ldap | 389, 636 |
| nfs | 111, 2049 |
| monitoring | 8080, 8443, 9090 |

#### Интерактивный процесс:
```
[i] Select network protocols to enable (with 2-second auto-confirm):

Available protocols:
   1) web             Ports: 80 443
   2) mail            Ports: 25 110 143 465 587 993 995
   ...

Enable web? [Y/n] (auto: yes in 2s): 
```

**Если не ответить за 2 секунды → автоматическое подтверждение по умолчанию**

#### Отслеживание:
```bash
CREATED_PROTOCOLS+="web"
CREATED_PORTS+=(80 443)
```

---

### 4. **Неповторяющиеся IPTables правила**

Функция `write_merged_iptables_file()` собирает все активные правила и удаляет дубликаты:

```bash
write_merged_iptables_file()
```

#### Как это работает:

1. **Сканирование файлов:**
   - Читает все `*.v4` и `*.v6` файлы из `/srv/sys/iptables/`
   - Пропускает `*.inactive` файлы
   - Пропускает уже merged файлы

2. **Дедупликация:**
   ```bash
   if ! grep -q "$port_line" "$temp_v4" 2>/dev/null; then
     echo "$port_line"
   fi
   ```

3. **Результат:**
   - `/srv/sys/iptables/v4/merged.v4` - объединённые IPv4 правила без дубликатов
   - `/srv/sys/iptables/v6/merged.v6` - объединённые IPv6 правила без дубликатов

#### Пример merged.v4:
```
*filter
:INPUT DROP [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
-A INPUT -p tcp --dport 22 -j ACCEPT
-A INPUT -p tcp --dport 80 -j ACCEPT
-A INPUT -p tcp --dport 443 -j ACCEPT
-A INPUT -p tcp --dport 53 -j ACCEPT
COMMIT
```

---

### 5. **Финальный Summary с полной информацией**

Функция `print_final_summary()` выводит полный отчёт о развертывании:

```
╔════════════════════════════════════════════════════════════════╗
║                    DEPLOYMENT SUMMARY                          ║
╚════════════════════════════════════════════════════════════════╝

SERVER INFORMATION:
  Hostname:                  server.example.com
  IP Address:                192.168.1.100
  SSH Port:                  22

PROTOCOLS CONFIGURED:
  ✓ web
  ✓ mail
  ✓ dns

FIREWALL PORTS:
  Opened: 22, 80, 443, 25, 110, 143, 465, 587, 993, 995, 53

USERS CREATED:
  main            role=admin                ssh=yes   sudo=yes  rbash=no
  gate            role=guest                ssh=no    sudo=no   rbash=yes
  mail_admin      role=mail-admin           ssh=yes   sudo=no   rbash=yes

SSH KEYS:
  main            Keys: 1
  mail_admin      Keys: 1

WINDOWS SSH CONFIG:
  Location: /srv/sys/ssh/win_config/config
  Size: 1024 bytes

INFRASTRUCTURE PATHS:
  Base:                      /srv/sys
  Home:                      /srv/home
  SSH Keys:                  /srv/sys/ssh/key-export
  SSH Config:                /srv/sys/ssh/sshd_config.d
  Session Logs:              /srv/sys/ssh/ssh_session
  Firewall:                  /srv/sys/iptables

╔════════════════════════════════════════════════════════════════╗
║                  DOWNLOAD ARCHIVE                              ║
╚════════════════════════════════════════════════════════════════╝

Download deployment archive with SSH keys and configs:

  scp -P 22 gate@192.168.1.100:/srv/sys/deploy/ssh-gate-deploy-20250108_143022.tar.gz ./

  Archive: ssh-gate-deploy-20250108_143022.tar.gz (2.3M)

After download, extract and follow SCP_INSTRUCTIONS.txt

╔════════════════════════════════════════════════════════════════╗
║                  NEXT STEPS                                    ║
╚════════════════════════════════════════════════════════════════╝

  1. Download the deployment archive
  2. Extract keys to ~/.ssh/ with chmod 600
  3. Configure your SSH client with provided config
  4. Connect via gate user to access restricted accounts
  5. Monitor logs at: /srv/sys/ssh/ssh_session
```

---

### 6. **Архив для скачивания**

Функция `create_deployment_archive()` создаёт готовый к распространению архив:

```bash
create_deployment_archive()
```

#### Структура архива:
```
ssh-gate-deploy-20250108_143022.tar.gz
├── keys/
│   ├── main/
│   │   ├── main@server-08_JAN-192-168-1-100
│   │   └── main@server-08_JAN-192-168-1-100.pub
│   └── mail_admin/
│       ├── mail_admin@server-08_JAN-192-168-1-100
│       └── mail_admin@server-08_JAN-192-168-1-100.pub
├── configs/
│   ├── ssh_config (Windows SSH config template)
│   ├── 00-PermitRootLogin.conf
│   ├── 01-PasswordAuthentication.conf
│   ├── 02-PubkeyAuthentication.conf
│   └── ...
└── docs/
    ├── DEPLOYMENT_INFO.txt (summary with all info)
    └── SCP_INSTRUCTIONS.txt (как скачать и использовать)
```

#### Локация:
```
/srv/sys/deploy/ssh-gate-deploy-<timestamp>.tar.gz
```

#### SCP команда для скачивания:
```bash
scp -P 22 gate@server:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./
tar -xzf ssh-gate-deploy-*.tar.gz
```

#### Файл SCP_INSTRUCTIONS.txt содержит:
- Инструкции для Linux/Mac
- Инструкции для Windows (WSL/Git Bash)
- Как установить ключи в ~/.ssh/
- Как использовать ssh_config

---

### 7. **Per-User Tracking (deployed_users.txt)**

Все созданные пользователи логируются в файл:

```
/srv/sys/deploy/deployed_users.txt
```

**Формат:**
```
user|role|ssh|sudo|rbash
main|admin|y|y|n
gate|guest|n|n|y
mail_admin|mail-admin|y|n|y
```

Используется для:
- Финального summary в консоли
- Включения в архив для документации
- Отслеживания состояния при переустановке

---

### 8. **Улучшенная функция create_or_update_user()**

```bash
create_or_update_user "$user" "$role" "$ssh" "$sudo" "$rbash" "$type"
```

**Параметры:**
- `$1` - username
- `$2` - role (из ALL_ROLES)
- `$3` - SSH access (y/n)
- `$4` - sudo access (y/n)
- `$5` - rbash shell (y/n)
- `$6` - user type (main/gate/user)

**Функция автоматически:**
1. Создаёт пользователя (если не существует)
2. Настраивает домашнюю директорию в /srv/home/$user
3. Устанавливает role-based rbin
4. Выбирает shell (bash или rbash)
5. Настраивает sudo если нужно
6. Создаёт SSH snippet если есть доступ
7. Логирует в deployed_users.txt

---

## Управление режимом verbosity

Добавьте перед запуском скрипта для debug-информации:

```bash
DEBUG=1 sudo bash install_ssh_gate_v2.sh
```

Выводит дополнительные debug-сообщения:
```
[D] Snippet pair: 00-PermitRootLogin
[D] Added port 80 to tracking
[D] Created gate switch 2main
```

---

## Примеры использования

### Пример 1: Стандартная установка с web + mail
```bash
sudo bash install_ssh_gate_v2.sh

# На запрос портов ответить:
# Enable web? [Y/n] (auto: yes in 2s): <ждём 2 сек или нажимаем Y>
# Enable mail? [y/N] (auto: no in 2s): y

# На запрос пользователей ответить:
# Enter gate username [gate]: gate
# Enter main admin username [main]: main
```

### Пример 2: Добавить пользователя при повторном запуске
```bash
sudo bash install_ssh_gate_v2.sh

# Система проверит existing gate и main
# Предложит: Add additional user? [y/N]: y
# Username: mail_admin
# Role number: 10 (mail-admin)
# SSH access: y
# Generate SSH key: y
```

### Пример 3: Удаление пользователя и очистка
```bash
# На сервере удалить пользователя:
userdel -r olduser

# Переустановить скрипт:
sudo bash install_ssh_gate_v2.sh

# Система автоматически:
# - Очистит /srv/home/gate/local/rbin/2olduser
# - Удалит /srv/sys/ssh/sshd_config.d/10-user_olduser.*
# Выведет: [!] Cleaned up deleted user switch for olduser
```

---

## Миграция с v1 на v2

Если уже установлена v1:

1. **Сохранить текущие ключи:**
   ```bash
   tar -czf ssh_keys_backup.tar.gz /srv/sys/ssh/key-export/
   ```

2. **Запустить v2 скрипт:**
   ```bash
   sudo bash install_ssh_gate_v2.sh
   ```

3. **Система автоматически:**
   - Обновит существующие пользователей
   - Сохранит существующие ключи
   - Добавит новые dynamic snippets
   - Пересоберёт iptables без дубликатов

4. **Проверить результат:**
   ```bash
   ls -la /srv/sys/ssh/sshd_config.d/10-user_*.conf
   sshd -t
   ```

---

## Troubleshooting

### Проблема: Дублирующиеся iptables правила
**Решение:** Функция `write_merged_iptables_file()` автоматически дедуплицирует. Если проблема сохраняется:
```bash
# Очистить старые файлы
rm /srv/sys/iptables/v4/*.v4
rm /srv/sys/iptables/v6/*.v6

# Переустановить
sudo bash install_ssh_gate_v2.sh
```

### Проблема: SSH snippet не применяется к пользователю
**Решение:** Убедитесь что snippet создан:
```bash
ls /srv/sys/ssh/sshd_config.d/10-user_<username>.conf
sshd -t
systemctl reload sshd
```

### Проблема: Не найти gate-switch команду после удаления пользователя
**Решение:** Запустить cleanup вручную:
```bash
# В скрипте это происходит автоматически
# Или вручную:
rm /srv/home/gate/local/rbin/2<deleted_user>
```

### Проблема: Архив пустой или не создался
**Решение:** Проверить права доступа:
```bash
ls -la /srv/sys/deploy/
chmod 755 /srv/sys/deploy/
sudo bash install_ssh_gate_v2.sh
```

---

## Заключение

SSH Gate v2 предоставляет:
✅ Динамическую конфигурацию на пользователя  
✅ Автоматическую очистку старых пользователей  
✅ Удобный выбор протоколов с автоподтверждением  
✅ Чистые iptables без дубликатов  
✅ Полный архив для развертывания  
✅ Детальный summary с инструкциями  

Все это делает развертывание безопаснее, удобнее и более масштабируемым.
