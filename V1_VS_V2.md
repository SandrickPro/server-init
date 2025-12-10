# SSH Gate v1 vs v2 - Сравнение версий

## Краткое резюме изменений

| Функция | v1 | v2 |
|---------|----|----|
| **Базовая функциональность** | ✓ | ✓ |
| **Role-based RBAC** | ✓ | ✓ |
| **IPTables firewall** | ✓ | ✓ Enhanced |
| **Auditd logging** | ✓ | ✓ |
| **Session recording** | ✓ | ✓ |
| **Per-user SSH snippets** | ✗ | **✓ NEW** |
| **Auto-cleanup deleted users** | ✗ | **✓ NEW** |
| **Protocol-based port selection** | ✗ | **✓ NEW** |
| **Deduped IPTables rules** | ✗ | **✓ NEW** |
| **Deployment archive** | ✗ | **✓ NEW** |
| **Final summary report** | ✗ | **✓ NEW** |
| **Windows SSH config auto-gen** | ✓ | ✓ |
| **Auto SSH key generation** | ✓ | ✓ |
| **Systemd units** | ✓ | ✓ |
| **MOTD banner** | ✓ | ✓ |
| **Maintenance timers** | ✓ | ✓ |

---

## Детальное сравнение по функциям

### 1. Per-User SSH Snippets

#### v1:
```bash
# Один общий snippet для всех пользователей
/srv/sys/ssh/sshd_config.d/06-ForceCommand-gate.conf

Match User gate
  ForceCommand /srv/home/gate/local/bin/gate_login_wrapper
```

**Проблемы:**
- Нельзя включить/отключить доступ одного пользователя без переконфигурации всей системы
- Все пользователи с одинаковыми ForceCommand
- Сложно управлять разными уровнями ограничения для разных пользователей

#### v2:
```bash
# Отдельный snippet для каждого пользователя
/srv/sys/ssh/sshd_config.d/10-user_main.conf
/srv/sys/ssh/sshd_config.d/10-user_gate.conf
/srv/sys/ssh/sshd_config.d/10-user_mail_admin.conf

Match User main
  ForceCommand /srv/home/main/local/bin/gate_login_wrapper
  X11Forwarding no
  AllowAgentForwarding no

Match User mail_admin
  ForceCommand /srv/home/mail_admin/local/bin/gate_login_wrapper
  X11Forwarding no
  AllowAgentForwarding no
```

**Преимущества:**
✓ Включать/отключать доступ одного пользователя независимо  
✓ Разные ForceCommand и опции для разных пользователей  
✓ Легко найти конфиг конкретного пользователя  
✓ Простое управление и аудит  

---

### 2. Удаление Deleted Users

#### v1:
```bash
# Нет автоматического удаления
# Если удалить пользователя, остаётся "мусор" в системе

# Leftovers after user deletion:
/srv/home/gate/local/rbin/2olduser    # <- остаётся!
/srv/sys/ssh/sshd_config.d/10-user_olduser.conf  # <- остаётся!
/srv/sys/ssh/key-export/olduser/      # <- остаётся!
```

**Проблемы:**
- Ручное удаление забывают делать
- Накапливается "мусор"
- Риск случайного доступа через leftover команды
- Усложняется аудит

#### v2:
```bash
# Автоматическая очистка при переустановке
cleanup_deleted_users "$GATE_USER"

# Что происходит:
# 1. Сканирует /srv/home/gate/local/rbin/2*
# 2. Проверяет существует ли пользователь: id <user>
# 3. Если НЕТ → удаляет /srv/home/gate/local/rbin/2<deleted_user>
# 4. Логирует: [!] Cleaned up deleted user switch for olduser
```

**Преимущества:**
✓ Автоматическая очистка при переустановке скрипта  
✓ Нет остатков от удалённых пользователей  
✓ Безопаснее (нет leftover доступа)  
✓ Чище система  

---

### 3. Интерактивный выбор протоколов

#### v1:
```bash
# Ручной выбор каждого сервиса по одному
read -rp "Open port for ssh (port 22)? [y/N]: " ans
read -rp "Open port for http (port 80)? [y/N]: " ans
read -rp "Open port for https (port 443)? [y/N]: " ans
read -rp "Open port for smtp (port 25)? [y/N]: " ans
read -rp "Open port for mysql (port 3306)? [y/N]: " ans
# ... 15 сервисов один за другим

# ~60 вопросов!
```

**Проблемы:**
- Очень долгий процесс интерактивного ввода
- Легко запутаться какие порты зачем
- Не сгруппированы логически

#### v2:
```bash
# Протоколы с группировкой портов и автоподтверждением (2 сек)
select_protocols()

# Доступные протоколы с портами:
[i] Select network protocols to enable (with 2-second auto-confirm):

Available protocols:
   1) web             Ports: 80 443
   2) mail            Ports: 25 110 143 465 587 993 995
   3) dns             Ports: 53
   4) ftp             Ports: 20 21 989 990
   5) db              Ports: 3306 5432 27017 6379
   6) vpn             Ports: 1194 51820
   ...

Enable web? [Y/n] (auto: yes in 2s):    # <- default YES, wait 2 sec or press Y
Enable mail? [y/N] (auto: no in 2s):    # <- default NO, wait 2 sec or press N

# Один вопрос на протокол + логическая группировка портов!
```

**Преимущества:**
✓ Быстрее (2 сек автоподтверждение вместо ручного ввода)  
✓ Логически сгруппированы порты  
✓ Понятнее что включается  
✓ 11 вопросов вместо 60+  
✓ Разумные defaults (web/dns YES по умолчанию)  

---

### 4. Дедупликация IPTables

#### v1:
```bash
# Создаются отдельные файлы для каждого сервиса
/srv/sys/iptables/v4/ssh.v4
/srv/sys/iptables/v4/http.v4
/srv/sys/iptables/v4/https.v4
/srv/sys/iptables/v4/mysql.v4
...

# При применении просто конкатенируются все вместе
# Возможны ДУБЛИКАТЫ!

*filter
:INPUT DROP [0:0]
...
-A INPUT -p tcp --dport 80 -j ACCEPT      # дубль 1
-A INPUT -p tcp --dport 80 -j ACCEPT      # дубль 2 (ОШИБКА!)
-A INPUT -p tcp --dport 443 -j ACCEPT
...
```

**Проблемы:**
- Дубликаты в iptables (неправильно, но работает)
- Непонятные правила при просмотре
- Сложнее отлаживать

#### v2:
```bash
# Функция write_merged_iptables_file() собирает и дедуплицирует

# Алгоритм:
# 1. Сканирует все *.v4 файлы (исключая *.inactive)
# 2. Для каждого порта проверяет: уже ли этот порт есть?
# 3. Если НЕТ → добавляет правило в merged.v4
# 4. Если ДА → пропускает (дублирующийся!)

# Результат:
*filter
:INPUT DROP [0:0]
...
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
-A INPUT -p tcp --dport 22 -j ACCEPT      # ОДИН раз!
-A INPUT -p tcp --dport 80 -j ACCEPT      # ОДИН раз!
-A INPUT -p tcp --dport 443 -j ACCEPT     # ОДИН раз!
...
COMMIT
```

**Преимущества:**
✓ NO DUPLICATES (проверка при добавлении)  
✓ Чистые iptables  
✓ Понятные правила  
✓ Правильный синтаксис  
✓ Автоматически при переустановке  

---

### 5. Архив для скачивания

#### v1:
```bash
# Нет встроенного архива
# Нужно скачивать всё вручную

# Скачивать:
scp -P 22 gate@server:/srv/sys/ssh/key-export/username/username@* ~/.ssh/
scp -P 22 gate@server:/srv/sys/ssh/win_config/config ~/.ssh/
scp -P 22 gate@server:/srv/sys/ssh/sshd_config.d/*.conf ~/configs/
# ... много отдельных команд
```

**Проблемы:**
- Много отдельных scp команд
- Легко забыть что-то скачать
- Неудобно распределять ключи
- Пользователь не знает что скачать

#### v2:
```bash
# Встроенный архив со ВСЕМ необходимым
create_deployment_archive()

# Структура архива:
ssh-gate-deploy-20250108_143022.tar.gz
├── keys/
│   ├── main/main@server-08_JAN-IP
│   ├── main/main@server-08_JAN-IP.pub
│   ├── mail_admin/mail_admin@server-08_JAN-IP
│   └── mail_admin/mail_admin@server-08_JAN-IP.pub
├── configs/
│   ├── ssh_config              (Windows SSH config)
│   ├── 00-PermitRootLogin.conf
│   ├── 01-PasswordAuthentication.conf
│   └── ...
└── docs/
    ├── DEPLOYMENT_INFO.txt     (все инструкции)
    ├── SCP_INSTRUCTIONS.txt    (как скачать)
    └── README.txt

# Одна команда для скачивания:
scp -P 22 gate@server:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./

# Один tar для распакования:
tar -xzf ssh-gate-deploy-*.tar.gz

# Всё в одном месте!
```

**Преимущества:**
✓ Всё в одном архиве  
✓ Одна scp команда для скачивания  
✓ Включены все инструкции  
✓ Готово к распределению  
✓ Версионирование по timestamp  

---

### 6. Финальный Summary

#### v1:
```bash
# Просто список вывода, без форматирования

INSTALL COMPLETE
- Gate: gate
- Main: main
- SSH port: 22
- Snippets in: /srv/sys/ssh/sshd_config.d
- Win config: /srv/sys/ssh/win_config/config
- IPTABLES files: /srv/sys/iptables/v4, /srv/sys/iptables/v6
- Sessions: /srv/sys/ssh/ssh_session
- Keys: /srv/sys/ssh/key-export

Notes:
- SID format: <IP-with-dashes>_<GATEUSER>_<DD-MON'YY>_<HH.MM>
- To adjust snippets, edit files...
```

**Проблемы:**
- Неполная информация
- Нет форматирования
- Нет инструкций по скачиванию архива
- Нет списка пользователей
- Нет инструкций для локального setup

#### v2:
```bash
# Полный форматированный summary с ASCII art

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
  ...all paths...

DOWNLOAD ARCHIVE:

  scp -P 22 gate@192.168.1.100:/srv/sys/deploy/ssh-gate-deploy-20250108_143022.tar.gz ./

  Archive: ssh-gate-deploy-20250108_143022.tar.gz (2.3M)

NEXT STEPS:
  1. Download the deployment archive
  2. Extract keys to ~/.ssh/ with chmod 600
  3. Configure your SSH client with provided config
  4. ...
```

**Преимущества:**
✓ Красивое форматирование  
✓ Все ключевые информация на одном экране  
✓ Список всех созданных пользователей  
✓ Инструкции по скачиванию архива  
✓ Next steps для новичков  

---

## Migration Path (Миграция с v1 на v2)

### Shоаг 1: Бэкап существующей системы
```bash
# На сервере
sudo tar -czf /backup/ssh_gate_v1_$(date +%Y-%m-%d).tar.gz /srv/sys/

# На локальной машине
scp -P 22 gate@server:/backup/ssh_gate_v1_*.tar.gz ./
```

### Шаг 2: Запустить v2 скрипт
```bash
sudo bash install_ssh_gate_v2.sh

# Выбрать те же протоколы и пользователей как раньше
# Скрипт автоматически:
# - Обновит существующих пользователей
# - Создаст per-user snippets для каждого
# - Пересоберёт deduped iptables
# - Создаст архив для скачивания
```

### Шаг 3: Проверить
```bash
# На сервере
sudo sshd -t
sudo systemctl reload ssh

# Все существующие ключи и доступы продолжат работать
# Добавятся новые функции v2
```

### Шаг 4: Обновить архив
```bash
# Скачать новый архив v2
scp -P 22 gate@server:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./

# В архиве будут ВСЕ ключи и конфиги в нужном формате
```

---

## Feature Comparison Table (Детальная таблица)

| Feature | v1 | v2 | Notes |
|---------|----|----|-------|
| SSH key generation | ✓ | ✓ | ed25519 |
| Role-based RBAC | ✓ | ✓ | 13 roles |
| rbash restricted shell | ✓ | ✓ | |
| Gate jump host | ✓ | ✓ | |
| IPTables firewall | ✓ | ✓ | v2: deduped |
| IPSet ban/whitelist | ✓ | ✓ | |
| Auditd logging | ✓ | ✓ | |
| Session recording | ✓ | ✓ | with SID |
| MOTD banner | ✓ | ✓ | |
| Systemd units | ✓ | ✓ | |
| Windows SSH config | ✓ | ✓ | Auto-gen |
| **Per-user SSH snippets** | ✗ | **✓** | **NEW** |
| **Auto-cleanup users** | ✗ | **✓** | **NEW** |
| **Protocol selection** | ✗ | **✓** | **NEW** |
| **Deduped iptables** | ✗ | **✓** | **NEW** |
| **Deployment archive** | ✗ | **✓** | **NEW** |
| **Summary report** | ✗ | **✓** | **NEW** |
| **Admin guide** | ✗ | **✓** | **NEW** |
| **Quick start guide** | ✗ | **✓** | **NEW** |

---

## Когда использовать v1 vs v2?

### Используйте v1, если:
- Нужна минимальная функциональность (базовый SSH gate)
- Мало пользователей (1-3)
- Не нужно часто добавлять/удалять пользователей
- Хотите простой и понятный скрипт

### Используйте v2, если:
- **Нужно часто управлять пользователями** ← РЕКОМЕНДУЕТСЯ
- **Много сервисов на одной машине** (web, mail, db, vpn, etc.)
- Требуется аудит и точное логирование
- Нужен готовый архив для распределения ключей
- Требуется чистая и управляемая система
- Нужны инструкции для операторов

---

## Рекомендация

**Используйте v2** для всех новых развертываний. Он имеет:
✓ Больше функций  
✓ Лучше управление пользователями  
✓ Чище система (нет дубликатов)  
✓ Готовые инструкции для операторов  
✓ Архив для быстрого распределения ключей  

Для миграции с v1 → v2 просто запустите v2 скрипт на существующей системе.
