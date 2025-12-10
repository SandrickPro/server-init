# SSH Gate v2 - Практические примеры использования

## Содержание

1. [Сценарий 1: Web Server](#сценарий-1-web-server)
2. [Сценарий 2: Mail Server](#сценарий-2-mail-server)
3. [Сценарий 3: Multi-purpose Server](#сценарий-3-multi-purpose-server)
4. [Сценарий 4: Managed Hosting с несколькими клиентами](#сценарий-4-managed-hosting)
5. [Часто задаваемые вопросы](#часто-задаваемые-вопросы)

---

## Сценарий 1: Web Server

Nginx/Apache web сервер с Let's Encrypt и несколькими администраторами.

### Начальная установка

```bash
$ sudo bash install_ssh_gate_v2.sh

[i] Creating directories under /srv...
[i] Core SSH snippets written

[i] Select network protocols to enable (with 2-second auto-confirm):

Available protocols:
   1) web             Ports: 80 443
   2) mail            Ports: 25 110 143 465 587 993 995
   3) dns             Ports: 53
   4) ftp             Ports: 20 21 989 990
   5) db              Ports: 3306 5432 27017 6379
   ...

Enable web? [Y/n] (auto: yes in 2s): [wait 2 sec]  # YES - default
Enable mail? [y/N] (auto: no in 2s): n             # NO
Enable dns? [Y/n] (auto: yes in 2s): [wait 2 sec]  # YES - default (for Let's Encrypt)
Enable monitoring? [y/N] (auto: no in 2s): y       # YES - for monitoring

[i] Enter SSH port [22]: 2222
[i] Enter gate username [gate]: gate
[i] Enter main admin username [main]: admin

# Users creation
[i] User admin created (role=admin, ssh=yes, sudo=yes)
[i] User gate created (role=guest, ssh=no, sudo=no)

# Additional users
Add additional user? [y/N]: y

Username: web_admin
Role number [0-13]: 11         # web-admin role
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

[i] Created user web_admin (role=web-admin)
[i] Generated SSH key for web_admin

# Более подробный вывод...
Add additional user? [y/N]: y

Username: letsencrypt
Role number [0-13]: 2          # user role
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: n

[i] Created user letsencrypt (role=user)

Add additional user? [y/N]: n

# Apply configuration
Apply SSHD configuration? [Y/n]: Y

[i] Applying SSHD configuration...
[i] SSHD configuration valid
[i] SSHD reloaded

# Final summary
╔════════════════════════════════════════════════════════════════╗
║                    DEPLOYMENT SUMMARY                          ║
╚════════════════════════════════════════════════════════════════╝

SERVER INFORMATION:
  Hostname:                  webserver.example.com
  IP Address:                203.0.113.100
  SSH Port:                  2222

PROTOCOLS CONFIGURED:
  ✓ web
  ✓ dns
  ✓ monitoring

FIREWALL PORTS:
  Opened: 2222, 80, 443, 53, 8080, 8443, 9090

USERS CREATED:
  admin           role=admin                ssh=yes   sudo=yes  rbash=no
  gate            role=guest                ssh=no    sudo=no   rbash=yes
  web_admin       role=web-admin            ssh=yes   sudo=no   rbash=yes
  letsencrypt     role=user                 ssh=yes   sudo=no   rbash=yes

SSH KEYS:
  admin           Keys: 1
  web_admin       Keys: 1

DOWNLOAD ARCHIVE:

  scp -P 2222 gate@203.0.113.100:/srv/sys/deploy/ssh-gate-deploy-20250108_143022.tar.gz ./
```

### Локальное использование

```bash
# На локальной машине администратора
$ scp -P 2222 gate@203.0.113.100:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./
$ tar -xzf ssh-gate-deploy-*.tar.gz
$ cd ssh-gate-deploy-*

# Setup SSH keys
$ mkdir -p ~/.ssh && chmod 700 ~/.ssh
$ cp keys/admin@server-* ~/.ssh/
$ chmod 600 ~/.ssh/admin@server-*

# Add to SSH config
$ cat configs/ssh_config >> ~/.ssh/config

# Содержимое .ssh/config:
Host admin
    HostName 203.0.113.100
    Port 2222
    User admin
    ProxyJump gate@203.0.113.100
    IdentityFile ~/.ssh/admin@server-08_JAN-203-0-113-100

Host web_admin
    HostName 203.0.113.100
    Port 2222
    User web_admin
    ProxyJump gate@203.0.113.100
    IdentityFile ~/.ssh/web_admin@server-08_JAN-203-0-113-100

Host letsencrypt
    HostName 203.0.113.100
    Port 2222
    User letsencrypt
    ProxyJump gate@203.0.113.100
    IdentityFile ~/.ssh/letsencrypt@server-08_JAN-203-0-113-100
```

### Подключение и управление

```bash
# Подключиться как admin
$ ssh admin

# Внутри gate shell, типируем 2admin для переключения
gate> 2admin
# Теперь в shell admin пользователя с полным sudo доступом

admin@webserver:~$ sudo systemctl restart nginx
admin@webserver:~$ sudo tail -f /var/log/nginx/access.log

# Подключиться как web_admin (для управления веб-приложением)
$ ssh web_admin

# Внутри gate shell
gate> 2web_admin
# Ограниченный доступ: ls, ps, curl, journalctl, tail, df

# Только просмотр логов сессии
admin@webserver:~$ tail -f /srv/sys/ssh/ssh_session/08-JAN\'25/*.log
```

### Мониторинг

```bash
# На сервере - просмотр всех подключений
tail -f /srv/sys/ssh/ssh_session/$(date +%d-%b\'%y | tr a-z A-Z)/*.log

# Просмотр подключений конкретного пользователя
grep "USER=web_admin" /srv/sys/ssh/ssh_session/*/*.log

# Просмотр подключений с конкретного IP
grep "192.168.1.50" /srv/sys/ssh/ssh_session/*/*.log
```

---

## Сценарий 2: Mail Server

Mail server (Postfix, Dovecot) с несколькими операторами.

### Установка

```bash
$ sudo bash install_ssh_gate_v2.sh

# Protocol selection
Enable web? [Y/n]: n          # NO - не веб
Enable mail? [y/N]: y         # YES - mail protocols!
Enable dns? [Y/n]: y          # YES - DNS для почты
Enable monitoring? [y/N]: y   # YES

# Users
Enter SSH port [22]: 2222
Enter gate username [gate]: gate
Enter main admin username [main]: mailadmin

Add additional user? [y/N]: y

Username: mailop1             # Mail operator 1
Role number [0-13]: 10        # mail-admin
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

Add additional user? [y/N]: y

Username: mailop2             # Mail operator 2
Role number [0-13]: 10        # mail-admin
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

Add additional user? [y/N]: y

Username: monitoring_agent
Role number [0-13]: 8         # monitoring
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

Add additional user? [y/N]: n

# Final setup
Apply SSHD configuration? [Y/n]: Y
```

### Результат

```
USERS CREATED:
  mailadmin       role=admin                ssh=yes   sudo=yes  rbash=no
  gate            role=guest                ssh=no    sudo=no   rbash=yes
  mailop1         role=mail-admin           ssh=yes   sudo=no   rbash=yes
  mailop2         role=mail-admin           ssh=yes   sudo=no   rbash=yes
  monitoring_agent role=monitoring          ssh=yes   sudo=no   rbash=yes

FIREWALL PORTS:
  Opened: 2222, 25, 110, 143, 465, 587, 993, 995, 53, 8080, 8443, 9090

SSH KEYS:
  mailadmin       Keys: 1
  mailop1         Keys: 1
  mailop2         Keys: 1
  monitoring_agent Keys: 1
```

### Использование

```bash
# Mail operator подключается
$ ssh mailop1

# Переключается на mailop1 в gate
gate> 2mailop1
mailop1@mailserver:~$ 

# Доступные команды (mail-admin role):
mailop1@mailserver:~$ curl -s http://localhost:8080/health
mailop1@mailserver:~$ journalctl -n 50 -u postfix
mailop1@mailserver:~$ tail -f /var/log/mail.log
mailop1@mailserver:~$ ps aux | grep dovecot

# Monitoring agent подключается отдельно
$ ssh monitoring_agent

gate> 2monitoring_agent
monitoring_agent@mailserver:~$

# Доступные команды (monitoring role):
# top, ss, ps, df, curl, journalctl
monitoring_agent@mailserver:~$ top -b -n 1 | head -20
monitoring_agent@mailserver:~$ ss -tlnp
monitoring_agent@mailserver:~$ df -h

# Главный админ может всё
$ ssh mailadmin

gate> 2mailadmin
mailadmin@mailserver:~$ sudo systemctl restart postfix
mailadmin@mailserver:~$ sudo systemctl status dovecot
mailadmin@mailserver:~$ sudo tail -100 /var/log/auth.log
```

---

## Сценарий 3: Multi-purpose Server

Сервер с web, mail, database, VPN и несколькими командами.

### Установка

```bash
$ sudo bash install_ssh_gate_v2.sh

# Protocol selection - выбрать все нужные
Enable web? [Y/n]: Y          # YES
Enable mail? [y/N]: y         # YES
Enable dns? [Y/n]: Y          # YES
Enable ftp? [y/N]: n          # NO
Enable db? [y/N]: y           # YES (PostgreSQL, MySQL)
Enable vpn? [y/N]: y          # YES (OpenVPN, WireGuard)
Enable ntp? [y/N]: Y          # YES (для синхронизации)
Enable monitoring? [y/N]: y   # YES
Enable ldap? [y/N]: n         # NO
Enable nfs? [y/N]: n          # NO

[i] Selected 8 protocols

# Enter SSH port
Enter SSH port [22]: 2222

# Create users for different roles
Enter gate username [gate]: gate
Enter main admin username [main]: sysadmin

Add additional user? [y/N]: y

Username: web_team
Role number [0-13]: 11        # web-admin
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

Add additional user? [y/N]: y

Username: mail_team
Role number [0-13]: 10        # mail-admin
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

Add additional user? [y/N]: y

Username: db_admin
Role number [0-13]: 12        # db-admin
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

Add additional user? [y/N]: y

Username: net_ops
Role number [0-13]: 7         # net-ops
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

Add additional user? [y/N]: y

Username: backup_op
Role number [0-13]: 6         # backup-ops
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

Add additional user? [y/N]: y

Username: audit_reader
Role number [0-13]: 9         # readonly-audit
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: n

Add additional user? [y/N]: n

Apply SSHD configuration? [Y/n]: Y
```

### Финальная конфигурация

```
SERVER INFORMATION:
  SSH Port:                  2222

PROTOCOLS CONFIGURED:
  ✓ web                  (80, 443)
  ✓ mail                 (25, 110, 143, 465, 587, 993, 995)
  ✓ dns                  (53)
  ✓ db                   (3306, 5432)
  ✓ vpn                  (1194, 51820)
  ✓ ntp                  (123)
  ✓ monitoring           (8080, 8443, 9090)

FIREWALL PORTS OPENED: 2222, 80, 443, 25, 110, 143, 465, 587, 993, 995, 
                       53, 3306, 5432, 1194, 51820, 123, 8080, 8443, 9090

USERS CREATED:
  sysadmin        role=admin                ssh=yes   sudo=yes  rbash=no
  gate            role=guest                ssh=no    sudo=no   rbash=yes
  web_team        role=web-admin            ssh=yes   sudo=no   rbash=yes
  mail_team       role=mail-admin           ssh=yes   sudo=no   rbash=yes
  db_admin        role=db-admin             ssh=yes   sudo=no   rbash=yes
  net_ops         role=net-ops              ssh=yes   sudo=no   rbash=yes
  backup_op       role=backup-ops           ssh=yes   sudo=no   rbash=yes
  audit_reader    role=readonly-audit       ssh=yes   sudo=no   rbash=yes
```

### Пример использования

```bash
# Сотрудник web team
$ ssh web_team
gate> 2web_team
web_team@server:~$ curl -s https://localhost/health

# Сотрудник mail team
$ ssh mail_team
gate> 2mail_team
mail_team@server:~$ tail -f /var/log/mail.log

# DBA
$ ssh db_admin
gate> 2db_admin
db_admin@server:~$ ss -tlnp | grep postgres
db_admin@server:~$ df -h /var/lib/postgresql

# Network ops
$ ssh net_ops
gate> 2net_ops
net_ops@server:~$ ss -tlnp    # все слушающие порты
net_ops@server:~$ ip addr     # IP адреса
net_ops@server:~$ ping -c 1 8.8.8.8

# Backup operator
$ ssh backup_op
gate> 2backup_op
backup_op@server:~$ rsync -av backup_location:/data ./

# Audit reader (read-only)
$ ssh audit_reader
gate> 2audit_reader
audit_reader@server:~$ journalctl -x
audit_reader@server:~$ aureport -ts today

# Main sysadmin (полный доступ)
$ ssh sysadmin
gate> 2sysadmin
sysadmin@server:~$ sudo systemctl restart postgresql
sysadmin@server:~$ sudo tail -100 /var/log/auth.log
```

---

## Сценарий 4: Managed Hosting

Hosting провайдер с несколькими клиентами (customer1, customer2, customer3).

### Установка

```bash
$ sudo bash install_ssh_gate_v2.sh

# Выбрать все протоколы
Enable web? [Y/n]: Y
Enable mail? [y/N]: y
Enable dns? [Y/n]: Y
...

Enter SSH port [22]: 2022
Enter gate username [gate]: gate
Enter main admin username [main]: hosting_admin

# Create users for each customer
Add additional user? [y/N]: y

Username: customer1_admin
Role number [0-13]: 11        # web-admin (для их веб-приложений)
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

Add additional user? [y/N]: y

Username: customer1_backup
Role number [0-13]: 6         # backup-ops
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

# ... repeat for customer2, customer3 ...

Add additional user? [y/N]: y

Username: customer2_admin
Role number [0-13]: 11        # web-admin
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y

# ... и т.д.
```

### Распределение ключей

```bash
# Создаётся один архив со всеми ключами
/srv/sys/deploy/ssh-gate-deploy-20250108_143022.tar.gz

# Извлечь ключи для конкретного клиента
tar -xzf ssh-gate-deploy-*.tar.gz

# Дать customer1 только их ключи:
tar -czf customer1_keys.tar.gz keys/customer1_* configs/

# Отправить customer1
scp customer1_keys.tar.gz customer1@their-secure-email:/

# Они распаковывают и используют:
tar -xzf customer1_keys.tar.gz
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cp keys/customer1_* ~/.ssh/
chmod 600 ~/.ssh/customer1_*
cat configs/ssh_config >> ~/.ssh/config
```

### Администрирование

```bash
# Hosting admin может контролировать всех
$ ssh hosting_admin

gate> 2hosting_admin
hosting_admin@server:~$ 

# Просмотреть логи подключений customer1
hosting_admin@server:~$ grep "customer1" /srv/sys/ssh/ssh_session/*/*.log

# Просмотреть SID сессии
hosting_admin@server:~$ grep "USER=customer1_admin" /srv/sys/ssh/ssh_session/*/*.log | head -5

# Отключить доступ customer2 временно
hosting_admin@server:~$ sudo mv /srv/sys/ssh/sshd_config.d/10-user_customer2_admin.conf \
                                  /srv/sys/ssh/sshd_config.d/10-user_customer2_admin.conf.OFF
hosting_admin@server:~$ sudo sshd -t
hosting_admin@server:~$ sudo systemctl reload ssh

# Включить обратно
hosting_admin@server:~$ sudo mv /srv/sys/ssh/sshd_config.d/10-user_customer2_admin.conf.OFF \
                                  /srv/sys/ssh/sshd_config.d/10-user_customer2_admin.conf
hosting_admin@server:~$ sudo sshd -t
hosting_admin@server:~$ sudo systemctl reload ssh
```

---

## Часто задаваемые вопросы

### Q: Где мне найти мой приватный ключ?

A: В архиве при скачивании:
```bash
ssh-gate-deploy-20250108_*/keys/<username>/<username>@server
```

Или на сервере:
```bash
/srv/sys/ssh/key-export/<username>/<username>@server
```

### Q: Как поменять SSH port с 22 на 2222?

A: При установке выбрать `2222`, или вручную:
```bash
sudo nano /srv/sys/ssh/sshd_config.d/ZZ-SSH-Port.conf
# Изменить "Port 22" на "Port 2222"
sudo sshd -t
sudo systemctl reload ssh
```

### Q: Как добавить новый порт в firewall?

A: 
```bash
# Способ 1: Переустановить скрипт и выбрать протокол
sudo bash install_ssh_gate_v2.sh

# Способ 2: Вручную
sudo iptables -A INPUT -p tcp --dport 9000 -j ACCEPT
sudo /usr/local/sbin/restore_srv_iptables.sh save
```

### Q: Как заблокировать IP вручную?

A:
```bash
sudo ipset add ssh_ban 192.168.1.50 timeout 3600
```

### Q: Где я найду логи сессий?

A: На сервере в `/srv/sys/ssh/ssh_session/<date>/`:
```bash
tail -f /srv/sys/ssh/ssh_session/$(date +%d-%b\'%y | tr a-z A-Z)/*.log
```

### Q: Как изменить доступные команды для пользователя?

A: Отредактировать role или вручную создать symlinks в `/srv/home/<user>/local/rbin/`

### Q: Можно ли удалить пользователя?

A:
```bash
# На сервере
sudo userdel -r <username>
sudo rm -rf /srv/home/<username>
sudo rm /srv/sys/ssh/sshd_config.d/10-user_<username>.*
sudo rm /srv/home/gate/local/rbin/2<username>

# Перезагрузить SSH
sudo sshd -t
sudo systemctl reload ssh
```

### Q: Архив занимает слишком много места. Как уменьшить?

A: В архиве copy public keys (.pub). Можно удалить их:
```bash
tar -xzf ssh-gate-deploy-*.tar.gz
rm ssh-gate-deploy-*/keys/*/*.pub
tar -czf ssh-gate-deploy-minimal.tar.gz ssh-gate-deploy-*/
```

### Q: Могу ли я использовать один ключ для нескольких пользователей?

A: Не рекомендуется. Каждый пользователь должен иметь свой ключ для аудита.

### Q: Как восстановить доступ если потеря приватного ключа?

A: На сервере:
```bash
sudo ssh-keygen -t ed25519 -C "user@host" \
  -f /srv/sys/ssh/key-export/<user>/newkey -N "" -q
sudo cat /srv/sys/ssh/key-export/<user>/newkey.pub >> \
  /srv/home/<user>/.ssh/authorized_keys

# Скачать новый ключ
scp -P 22 gate@server:/srv/sys/key-export/<user>/newkey ~/.ssh/
```

---

## Заключение

SSH Gate v2 гибкий и масштабируемый для разных сценариев:

- **Web Server**: web_admin для управления веб-приложениями
- **Mail Server**: mail-admin операторы для управления почтой
- **Multi-purpose**: Разные роли для разных команд
- **Managed Hosting**: Изолированные ключи для разных клиентов

Все варианты включают:
✓ Безопасный rbash доступ через gate jump host
✓ Role-based команды
✓ Session recording и аудит
✓ Firewall с протоколами
✓ Готовые архивы для распределения
