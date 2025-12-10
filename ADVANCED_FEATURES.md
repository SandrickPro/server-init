# Server Deploy Master v4.0 - Advanced Edition

## 🚀 Новые возможности

### 1. **MC-Style Multi-Pane Interface**

Многооконный интерфейс в стиле Midnight Commander с использованием `tmux`:

```bash
sudo ./server-deploy-advanced.sh
# Выберите: MC-Style Interface → Launch tmux workspace
```

**Компоновка экрана:**
```
┌─────────────────────────────────────────┐
│  TOP: Config Editor (ranger/mc)         │
│  Navigate /etc, edit configs            │
├─────────────────────┬───────────────────┤
│ BOTTOM-LEFT: Logs   │ BOTTOM-RIGHT:     │
│ tail -f logs        │ System Monitor    │
│ Real-time output    │ htop/glances      │
└─────────────────────┴───────────────────┘
```

**Навигация в tmux:**
- `Ctrl+B` затем `↑↓←→` - переключение между панелями
- `Ctrl+B` затем `[` - режим прокрутки
- `Ctrl+B` затем `d` - отсоединиться (detach)
- `tmux attach -t deploy_master` - подключиться обратно

### 2. **Расширенное управление пользователями**

#### Основные функции:
- ✅ Создание пользователей с ролями (user/admin/developer/devops)
- ✅ Управление группами (docker, www-data, sudo)
- ✅ SSH ключи (добавление/удаление)
- ✅ Sudo доступ (full/nopasswd/limited/revoke)
- ✅ Блокировка/разблокировка аккаунтов
- ✅ Дисковые квоты (soft/hard limits)
- ✅ ACL permissions для директорий
- ✅ База данных пользователей (JSON)

#### Примеры использования:

**Создание пользователя-разработчика:**
```
User Management → Add new user
Username: john
Role: developer
Groups: docker,www-data
```

**Настройка sudo без пароля:**
```
User Management → Sudo access → nopasswd
```

**Ограничение места на диске:**
```
User Management → User quotas
Soft: 1000MB, Hard: 1500MB
```

### 3. **Configuration Editor с предпросмотром**

**Поддерживаемые форматы:**
- Nginx (`.conf`)
- Apache (`.conf`)
- MySQL/PostgreSQL (`.cnf`, `.conf`)
- SSH (`sshd_config`)
- YAML (`.yml`, `.yaml`)
- JSON (`.json`)

**Возможности:**
- Просмотр файлов
- Редактирование (nano/vim)
- Создание бэкапов
- Восстановление из бэкапа
- Валидация синтаксиса
- Автоматическая проверка конфигурации

### 4. **Расширенные категории**

#### 📦 System Setup
- Обновление системы и ядра
- Настройка timezone/locale
- Конфигурация swap
- Установка базовых пакетов
- Fail2ban с динамическими blacklist
- Автоматические обновления

#### 🔐 Security Hardening
- SSH hardening (disable root, key-only auth)
- Firewall rules (iptables with persistent save)
- SELinux/AppArmor
- Audit logs
- Port scanning
- Vulnerability scanning
- SSL/TLS проверка
- Password policies
- 2FA setup

#### ⚡ Performance Tuning
- System tuning (vm.swappiness, file limits)
- Web server optimization
- Database optimization (InnoDB, query cache)
- Kernel parameters
- Disk I/O tuning
- Network optimization (TCP, buffer sizes)
- Cache configuration

#### 💾 Backup & Restore
- Config backups (/etc, /srv/sys)
- Database backups (MySQL, PostgreSQL, MongoDB)
- User backups (accounts + home dirs)
- Full system backup
- Scheduled backups (cron)
- Restore from backup

#### 📊 Monitoring & Logs
- System resources (CPU, RAM, Disk)
- Active connections
- Service status
- Log viewer (real-time tail)
- htop/glances integration

#### 🐳 Docker Management
- Container management
- Image management
- Docker Compose
- Networks & volumes
- Registry management

#### 🗄️ Database Management
- Multi-DB support (MySQL/PostgreSQL/MariaDB/MongoDB)
- User management
- Backup/restore
- Query optimization
- Replication setup

### 5. **MC-Style Layouts**

**Доступные компоновки:**

1. **Horizontal** (2 панели рядом)
   ```
   ┌─────────┬─────────┐
   │  Left   │  Right  │
   │         │         │
   └─────────┴─────────┘
   ```

2. **Vertical** (2 панели сверху/снизу)
   ```
   ┌─────────────────┐
   │      Top        │
   ├─────────────────┤
   │     Bottom      │
   └─────────────────┘
   ```

3. **Quad** (4 панели 2×2)
   ```
   ┌─────────┬─────────┐
   │  TL     │  TR     │
   ├─────────┼─────────┤
   │  BL     │  BR     │
   └─────────┴─────────┘
   ```

4. **Triple Horizontal** (3 панели)
   ```
   ┌─────┬─────┬─────┐
   │  L  │  M  │  R  │
   └─────┴─────┴─────┘
   ```

5. **Triple Vertical** (3 панели)
   ```
   ┌─────────────────┐
   │      Top        │
   ├─────────────────┤
   │     Middle      │
   ├─────────────────┤
   │     Bottom      │
   └─────────────────┘
   ```

### 6. **Интеграция с Ranger/MC**

**Установка файловых менеджеров:**
```bash
# Ranger (современный, с превью)
MC-Style Interface → Install ranger file manager

# Midnight Commander (классический)
MC-Style Interface → Install midnight commander
```

**Ranger features:**
- Предпросмотр файлов
- Syntax highlighting
- Навигация vim-style
- Bulk rename
- Закладки (bookmarks)

**MC features:**
- Двухпанельный интерфейс
- FTP/SFTP клиент
- Встроенный редактор
- Diff tool

### 7. **Dialog UI Components**

**Input boxes:**
```bash
dialog --inputbox "Enter value:" 8 40
```

**Password boxes:**
```bash
dialog --passwordbox "Enter password:" 8 40
```

**Menu selections:**
```bash
dialog --menu "Choose:" 15 60 5 \
  1 "Option 1" \
  2 "Option 2"
```

**Checklists:**
```bash
dialog --checklist "Select services:" 15 60 5 \
  1 "Nginx" off \
  2 "MySQL" on
```

**Yes/No dialogs:**
```bash
dialog --yesno "Continue?" 8 40
```

**Progress bars:**
```bash
dialog --gauge "Installing..." 8 40 50
```

### 8. **Рекомендуемый workflow**

**Первый запуск:**
```bash
# 1. Запустить скрипт
sudo ./server-deploy-advanced.sh

# 2. System Setup
- Update system
- Configure timezone
- Setup swap

# 3. Security Hardening
- SSH hardening
- Firewall rules
- Install Fail2ban

# 4. User Management
- Create admin users
- Setup SSH keys
- Configure sudo

# 5. Launch MC Interface
- Top: Config editor
- Bottom-left: Logs
- Bottom-right: Monitor
```

**Ежедневное использование:**
```bash
# Быстрый доступ к MC интерфейсу
sudo ./server-deploy-advanced.sh
→ MC-Style Interface
→ Launch tmux workspace

# Или напрямую
tmux attach -t deploy_master
```

### 9. **Горячие клавиши**

**tmux:**
- `Ctrl+B %` - вертикальный сплит
- `Ctrl+B "` - горизонтальный сплит
- `Ctrl+B o` - следующая панель
- `Ctrl+B x` - закрыть панель
- `Ctrl+B z` - zoom панели
- `Ctrl+B [` - режим копирования

**ranger:**
- `j/k` - вверх/вниз
- `h/l` - назад/вперед
- `gg/G` - начало/конец
- `Space` - выбрать файл
- `yy` - копировать
- `dd` - вырезать
- `pp` - вставить
- `zh` - показать скрытые файлы

**mc:**
- `Tab` - переключить панель
- `F3` - просмотр
- `F4` - редактирование
- `F5` - копировать
- `F6` - переместить
- `F8` - удалить
- `F10` - выход

### 10. **Расширения системы**

**Для добавления нового модуля:**

1. Создайте функцию в скрипте:
```bash
my_custom_module() {
    step "My Custom Module"
    # ваш код
}
```

2. Добавьте в меню:
```bash
local choice=$(dialog --menu "..." \
    ...
    15 "My Module" \
    ...
)
```

3. Добавьте case:
```bash
case $choice in
    ...
    15) my_custom_module ;;
    ...
esac
```

### 11. **Интеграция с существующими инструментами**

**Glances (системный монитор):**
```bash
apt-get install -y glances
glances -w  # Web UI на порту 61208
```

**Netdata (real-time monitoring):**
```bash
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
# http://server-ip:19999
```

**Portainer (Docker UI):**
```bash
docker volume create portainer_data
docker run -d -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce
```

### 12. **Troubleshooting**

**Dialog не установлен:**
```bash
apt-get install -y dialog whiptail
```

**tmux не работает:**
```bash
apt-get install -y tmux
tmux -V  # проверить версию
```

**Проблемы с permissions:**
```bash
chmod +x server-deploy-advanced.sh
sudo ./server-deploy-advanced.sh
```

**Логи не отображаются:**
```bash
tail -f /var/log/server-deploy.log
```

**JSON база данных повреждена:**
```bash
echo '{"users": []}' > /srv/sys/.users_db.json
```

### 13. **Best Practices**

1. **Всегда делайте бэкап** перед изменениями
2. **Тестируйте на staging** окружении
3. **Используйте SSH ключи** вместо паролей
4. **Регулярно обновляйте** систему
5. **Мониторьте логи** в реальном времени
6. **Настройте автобэкапы** (ежедневно)
7. **Документируйте изменения** в config editor

### 14. **API для расширений**

**Создание плагина:**
```bash
# /srv/sys/plugins/my_plugin.sh

plugin_init() {
    info "My plugin loaded"
}

plugin_menu() {
    dialog --menu "My Plugin" 10 50 3 \
        1 "Action 1" \
        2 "Action 2"
}

# Подключение
source /srv/sys/plugins/my_plugin.sh
```

## 📊 Статистика возможностей

- **14 категорий** меню
- **80+ функций** управления
- **5 layout** вариантов
- **4 файловых менеджера** (встроенный + ranger + mc + возможность добавить)
- **Неограниченное** количество tmux панелей
- **JSON база данных** для users/state
- **Multi-pane** интерфейс
- **Real-time** логи и мониторинг

## 🎯 Roadmap v5.0

- [ ] Web UI (Flask/Django)
- [ ] REST API
- [ ] Ansible playbooks integration
- [ ] Kubernetes deployment
- [ ] Terraform integration
- [ ] CI/CD pipelines
- [ ] Automated testing
- [ ] Metrics & alerting
- [ ] Multi-server management
- [ ] Cloud provider integration (AWS/Azure/GCP)

---

**Поддержка:** admin@example.com  
**Документация:** https://github.com/your-repo/server-deploy-master  
**License:** MIT
