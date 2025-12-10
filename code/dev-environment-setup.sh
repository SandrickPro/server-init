#!/bin/bash
################################################################################
# Dev Environment Setup Module
# Автор: Sandrick Tech
# Дата: 2024-12-09
# Описание: Настройка среды разработки C/C++ и Python с примерами проектов
################################################################################

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

DEV_DIR="/srv/dev"
EXAMPLES_DIR="$DEV_DIR/examples"
PROJECTS_DIR="$DEV_DIR/projects"
LOG_FILE="/srv/sys/logs/dev-setup.log"

info() { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
step() { echo -e "${CYAN}[STEP]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"; }

################################################################################
# C/C++ ENVIRONMENT
################################################################################

install_c_environment() {
    step "Установка среды разработки C/C++..."
    
    apt-get update -qq
    apt-get install -y build-essential gcc g++ make cmake gdb valgrind git \
        autoconf automake libtool pkg-config
    
    mkdir -p "$EXAMPLES_DIR/c"/{basic,intermediate,advanced}
    
    # 1. Basic: Hello World
    cat > "$EXAMPLES_DIR/c/basic/hello.c" <<'EOF'
/**
 * Пример 1: Hello World
 * Компиляция: gcc -o hello hello.c
 * Запуск: ./hello
 */
#include <stdio.h>

int main() {
    printf("Hello, World! Это простейшая программа на C.\n");
    printf("Компилятор: GCC %d.%d\n", __GNUC__, __GNUC_MINOR__);
    return 0;
}
EOF

    # 2. Intermediate: Calculator
    cat > "$EXAMPLES_DIR/c/intermediate/calc.c" <<'EOF'
/**
 * Пример 2: Калькулятор с функциями
 * Демонстрирует: функции, условия, циклы
 * Компиляция: gcc -o calc calc.c -lm
 */
#include <stdio.h>
#include <math.h>

int add(int a, int b) { return a + b; }
int subtract(int a, int b) { return a - b; }
int multiply(int a, int b) { return a * b; }
double divide(int a, int b) {
    if (b == 0) {
        printf("Ошибка: деление на ноль!\n");
        return 0;
    }
    return (double)a / b;
}

int main() {
    int x = 20, y = 4;
    
    printf("=== Калькулятор ===\n");
    printf("%d + %d = %d\n", x, y, add(x, y));
    printf("%d - %d = %d\n", x, y, subtract(x, y));
    printf("%d * %d = %d\n", x, y, multiply(x, y));
    printf("%d / %d = %.2f\n", x, y, divide(x, y));
    printf("sqrt(%d) = %.2f\n", x, sqrt(x));
    
    return 0;
}
EOF

    # 3. Advanced: TCP Server
    cat > "$EXAMPLES_DIR/c/advanced/tcp_server.c" <<'EOF'
/**
 * Пример 3: Простой TCP сервер
 * Демонстрирует: сокеты, многопоточность (accept loop)
 * Компиляция: gcc -o server tcp_server.c
 * Запуск: ./server
 * Тест: curl http://localhost:8080
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};
    const char *response = 
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        "Connection: close\r\n"
        "\r\n"
        "<h1>Hello from C TCP Server!</h1>"
        "<p>This is a simple HTTP server written in C.</p>";

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                   &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("🚀 Server listening on http://0.0.0.0:%d\n", PORT);
    printf("Press Ctrl+C to stop\n\n");

    while(1) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address,
                                 (socklen_t*)&addrlen)) < 0) {
            perror("accept");
            continue;
        }

        read(new_socket, buffer, BUFFER_SIZE);
        printf("📨 Request received\n");
        
        send(new_socket, response, strlen(response), 0);
        printf("✅ Response sent\n\n");
        
        close(new_socket);
    }

    return 0;
}
EOF

    # Makefile для всех примеров
    cat > "$EXAMPLES_DIR/c/Makefile" <<'EOF'
# Makefile для C примеров
CC=gcc
CFLAGS=-Wall -Wextra -O2

all: basic intermediate advanced

basic:
	$(CC) $(CFLAGS) -o basic/hello basic/hello.c

intermediate:
	$(CC) $(CFLAGS) -o intermediate/calc intermediate/calc.c -lm

advanced:
	$(CC) $(CFLAGS) -o advanced/tcp_server advanced/tcp_server.c

clean:
	rm -f basic/hello intermediate/calc advanced/tcp_server

.PHONY: all basic intermediate advanced clean
EOF

    # README
    cat > "$EXAMPLES_DIR/c/README.md" <<'EOF'
# C/C++ Examples

## Быстрый старт

```bash
cd /srv/dev/examples/c
make all
```

## Примеры

### 1. Basic (hello.c)
```bash
cd basic
gcc -o hello hello.c
./hello
```

### 2. Intermediate (calc.c)
```bash
cd intermediate
gcc -o calc calc.c -lm
./calc
```

### 3. Advanced (tcp_server.c)
```bash
cd advanced
gcc -o tcp_server tcp_server.c
./tcp_server
# В другом терминале: curl http://localhost:8080
```

## Полезные команды

- `gcc -v` — версия компилятора
- `gdb ./program` — отладчик
- `valgrind ./program` — проверка утечек памяти
- `man function_name` — справка по функциям

EOF

    success "✅ C/C++ среда установлена: $EXAMPLES_DIR/c/"
}

################################################################################
# PYTHON ENVIRONMENT (РАСШИРЕННАЯ!)
################################################################################

install_python_environment() {
    step "Установка Python среды разработки..."
    
    apt-get install -y python3 python3-pip python3-venv python3-dev \
        python3-setuptools python3-wheel
    
    pip3 install --upgrade pip setuptools wheel
    
    # Web frameworks (7 пакетов)
    step "Установка Web frameworks..."
    pip3 install flask django fastapi uvicorn requests aiohttp httpx
    
    # Data science (10 пакетов)
    step "Установка Data Science библиотек..."
    pip3 install numpy pandas matplotlib seaborn scipy scikit-learn jupyter notebook ipython statsmodels
    
    # Testing & Quality (8 пакетов)
    step "Установка Testing & QA..."
    pip3 install pytest pytest-cov black flake8 mypy pylint autopep8 isort
    
    # Utilities (10 пакетов)
    step "Установка утилит..."
    pip3 install python-dotenv click rich pyyaml pydantic colorama tqdm typer loguru python-decouple
    
    # Scraping & Parsing (5 пакетов)
    pip3 install beautifulsoup4 lxml selenium scrapy requests-html
    
    # Database (5 пакетов)
    pip3 install sqlalchemy pymysql psycopg2-binary redis pymongo
    
    # Image & Media (3 пакета)
    pip3 install pillow opencv-python-headless imageio
    
    # Async & Concurrency
    pip3 install asyncio aiofiles celery
    
    info "📦 Установлено 55+ Python библиотек"
    
    mkdir -p "$EXAMPLES_DIR/python"/{basic,web,data,scraping,cli}
    mkdir -p "$PROJECTS_DIR/python"
    
    create_python_examples
    create_python_projects
    
    success "✅ Python среда установлена: $EXAMPLES_DIR/python/"
}

create_python_examples() {
    # 1. Basic: Quick Start
    cat > "$EXAMPLES_DIR/python/basic/quick_start.py" <<'EOF'
#!/usr/bin/env python3
"""
Пример 1: Быстрый старт Python
Демонстрирует: базовый синтаксис, функции, list comprehensions
Запуск: python3 quick_start.py
"""
import os
import sys
from datetime import datetime

def greet(name):
    """Приветствие пользователя"""
    return f"Привет, {name}! 👋"

def main():
    print("=" * 50)
    print("🐍 Python Quick Start")
    print("=" * 50)
    
    print(f"\n📊 Python version: {sys.version}")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    name = input("\n👤 Введите ваше имя: ").strip() or "Developer"
    print(greet(name))
    
    # List comprehension
    numbers = list(range(1, 11))
    squares = [x**2 for x in numbers]
    print(f"\n🔢 Квадраты чисел {numbers[:5]}...: {squares[:5]}...")
    
    # Dictionary
    person = {"name": name, "role": "Developer", "language": "Python"}
    print(f"\n📝 Ваш профиль: {person}")

if __name__ == "__main__":
    main()
EOF
    chmod +x "$EXAMPLES_DIR/python/basic/quick_start.py"

    # 2. Web: Flask API
    cat > "$EXAMPLES_DIR/python/web/flask_api.py" <<'EOF'
#!/usr/bin/env python3
"""
Пример 2: REST API на Flask
Демонстрирует: веб-разработку, JSON API, роутинг
Запуск: python3 flask_api.py
Тест: curl http://localhost:5000/api/users
"""
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Простая "база данных"
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]

@app.route('/')
def home():
    return jsonify({
        "message": "🚀 Flask API Server",
        "version": "1.0",
        "time": datetime.now().isoformat()
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({"users": users, "count": len(users)})

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = {
        "id": len(users) + 1,
        "name": data.get("name"),
        "email": data.get("email")
    }
    users.append(new_user)
    return jsonify(new_user), 201

if __name__ == '__main__':
    print("🌐 Starting Flask API on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF
    chmod +x "$EXAMPLES_DIR/python/web/flask_api.py"

    # 3. Data Science
    cat > "$EXAMPLES_DIR/python/data/analysis.py" <<'EOF'
#!/usr/bin/env python3
"""
Пример 3: Анализ данных с Pandas
Демонстрирует: работу с данными, статистику, визуализацию
Запуск: python3 analysis.py
"""
import pandas as pd
import numpy as np

def analyze_data():
    # Создаём тестовые данные
    np.random.seed(42)
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 40, 28],
        'Salary': [50000, 60000, 75000, 90000, 55000],
        'Department': ['IT', 'Sales', 'IT', 'Management', 'Sales']
    }
    
    df = pd.DataFrame(data)
    
    print("=" * 60)
    print("📊 DATA ANALYSIS WITH PANDAS")
    print("=" * 60)
    
    print("\n📋 DataFrame:")
    print(df)
    
    print("\n📈 Statistics:")
    print(df.describe())
    
    print("\n💰 Средняя зарплата по отделам:")
    print(df.groupby('Department')['Salary'].mean())
    
    print("\n👥 Количество сотрудников по отделам:")
    print(df['Department'].value_counts())
    
    print(f"\n💵 Общий фонд зарплат: ${df['Salary'].sum():,}")
    print(f"📊 Средняя зарплата: ${df['Salary'].mean():,.2f}")

if __name__ == "__main__":
    analyze_data()
EOF
    chmod +x "$EXAMPLES_DIR/python/data/analysis.py"

    # 4. Web Scraping
    cat > "$EXAMPLES_DIR/python/scraping/scraper.py" <<'EOF'
#!/usr/bin/env python3
"""
Пример 4: Web Scraping с BeautifulSoup
Демонстрирует: парсинг HTML, работу с requests
Запуск: python3 scraper.py
"""
import requests
from bs4 import BeautifulSoup

def scrape_example():
    url = "http://example.com"
    
    print(f"🌐 Загрузка {url}...")
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.find('title')
        h1 = soup.find('h1')
        paragraphs = soup.find_all('p')
        
        print("\n✅ Успешно загружено!")
        print(f"📄 Title: {title.text if title else 'N/A'}")
        print(f"📌 H1: {h1.text if h1 else 'N/A'}")
        print(f"📝 Paragraphs: {len(paragraphs)}")
        
        if paragraphs:
            print("\nПервый параграф:")
            print(paragraphs[0].text[:200] + "...")
    else:
        print(f"❌ Ошибка: {response.status_code}")

if __name__ == "__main__":
    scrape_example()
EOF
    chmod +x "$EXAMPLES_DIR/python/scraping/scraper.py"

    # 5. CLI Tool with Rich
    cat > "$EXAMPLES_DIR/python/cli/rich_cli.py" <<'EOF'
#!/usr/bin/env python3
"""
Пример 5: Красивый CLI с библиотекой Rich
Демонстрирует: цветной вывод, прогресс-бары, таблицы
Запуск: python3 rich_cli.py
"""
from rich.console import Console
from rich.table import Table
from rich.progress import track
from time import sleep

console = Console()

def main():
    console.print("[bold magenta]🎨 Rich CLI Example[/bold magenta]")
    console.print("[cyan]Beautiful terminal output with Python![/cyan]\n")
    
    # Таблица
    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="green")
    
    table.add_row("1", "Alice", "alice@example.com")
    table.add_row("2", "Bob", "bob@example.com")
    table.add_row("3", "Charlie", "charlie@example.com")
    
    console.print(table)
    console.print()
    
    # Прогресс-бар
    console.print("[yellow]Processing data...[/yellow]")
    for _ in track(range(20), description="Loading..."):
        sleep(0.1)
    
    console.print("\n[bold green]✅ Done![/bold green]")

if __name__ == "__main__":
    main()
EOF
    chmod +x "$EXAMPLES_DIR/python/cli/rich_cli.py"

    # 6. Telegram Bot - Продвинутый бот с 25+ командами
    info "Создание примера Telegram бота..."
    cp "$(dirname "$0")/telegram_bot_advanced.py" "$EXAMPLES_DIR/python/web/telegram_bot.py" 2>/dev/null || \
    curl -sSL https://raw.githubusercontent.com/sandrick-tech/server-deploy/main/telegram_bot_advanced.py -o "$EXAMPLES_DIR/python/web/telegram_bot.py" 2>/dev/null || \
    cat > "$EXAMPLES_DIR/python/web/telegram_bot.py" <<'BOTEOF'
#!/usr/bin/env python3
"""
Telegram Bot - Продвинутый бот с 25+ командами
Установка: pip install python-telegram-bot psutil requests
Запуск: export TELEGRAM_BOT_TOKEN=your_token && python3 telegram_bot.py
"""
# См. полную версию в telegram_bot_advanced.py
# Здесь минимальная версия для быстрого старта

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('👋 Привет! Я бот. Используй /help')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '/start - Начало\n'
        '/help - Помощь\n'
        '/stats - Статистика\n'
        '/system - Система\n'
    )

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print('❌ Установите TELEGRAM_BOT_TOKEN')
        return
    
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    
    print('🚀 Бот запущен!')
    app.run_polling()

if __name__ == '__main__':
    main()
BOTEOF
    chmod +x "$EXAMPLES_DIR/python/web/telegram_bot.py"

    # README для примеров
    cat > "$EXAMPLES_DIR/python/README.md" <<'EOF'
# Python Examples - Быстрый старт

## Установленные библиотеки (55+)

### Web
- Flask, Django, FastAPI, Uvicorn, Requests, AIOHTTP, HTTPX

### Data Science
- NumPy, Pandas, Matplotlib, Seaborn, SciPy, Scikit-Learn, Jupyter

### Testing & QA
- Pytest, Black, Flake8, MyPy, Pylint, Autopep8, Isort

### Utilities
- Python-dotenv, Click, Rich, PyYAML, Pydantic, Colorama, Tqdm, Typer, Loguru

### Scraping
- BeautifulSoup4, Selenium, Scrapy, Lxml

### Database
- SQLAlchemy, PyMySQL, Psycopg2, Redis, PyMongo

### Telegram
- python-telegram-bot, psutil (для системного мониторинга)

## Запуск примеров

```bash
# Пример 1: Базовый синтаксис
python3 basic/quick_start.py

# Пример 2: Flask API
python3 web/flask_api.py
# Тест: curl http://localhost:5000/api/users

# Пример 3: Анализ данных
python3 data/analysis.py

# Пример 4: Web Scraping
python3 scraping/scraper.py

# Пример 5: CLI с Rich
python3 cli/rich_cli.py

# Пример 6: Telegram Bot (требуется токен)
export TELEGRAM_BOT_TOKEN="your_token_from_@BotFather"
export ADMIN_IDS="123456789,987654321"
python3 web/telegram_bot.py

# Полная версия бота с 25+ командами:
# См. telegram_bot_advanced.py в корне проекта
```

## Telegram Bot - Возможности

**25+ команд:**
- /start - Главное меню с кнопками
- /stats - Статистика бота (пользователи, команды)
- /system - Мониторинг сервера (CPU, RAM, Disk)
- /files - Управление файлами (upload/download)
- /remind - Создание напоминаний
- /poll - Создание опросов
- /weather - Прогноз погоды
- /calc - Калькулятор
- И многое другое...

**Админ команды:**
- /cpu, /memory, /disk - Детальная статистика
- /processes - Топ процессов
- /network - Сетевая статистика

**Установка зависимостей бота:**
```bash
pip install -r telegram_bot_requirements.txt
# или
pip install python-telegram-bot psutil requests
```

## Проекты-шаблоны

Готовые шаблоны проектов находятся в `/srv/dev/projects/python/`:

1. **todo-api** - REST API на FastAPI с SQLAlchemy
2. **data-dashboard** - Dashboard с Pandas + Matplotlib

```bash
cd /srv/dev/projects/python/todo-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

EOF
}

create_python_projects() {
    # PROJECT 1: TODO API (FastAPI)
    mkdir -p "$PROJECTS_DIR/python/todo-api"
    cat > "$PROJECTS_DIR/python/todo-api/main.py" <<'EOF'
"""
Проект 1: TODO API на FastAPI
Полноценное REST API с базой данных
Запуск: uvicorn main:app --reload
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="TODO API", version="1.0")

# Модель данных
class TodoItem(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[datetime] = None

# "База данных"
todos = []
todo_id_counter = 1

@app.get("/")
def root():
    return {"message": "TODO API", "docs": "/docs"}

@app.get("/todos", response_model=List[TodoItem])
def get_todos():
    return todos

@app.post("/todos", response_model=TodoItem, status_code=201)
def create_todo(todo: TodoItem):
    global todo_id_counter
    todo.id = todo_id_counter
    todo.created_at = datetime.now()
    todo_id_counter += 1
    todos.append(todo)
    return todo

@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo(todo_id: int):
    todo = next((t for t in todos if t.id == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    global todos
    todos = [t for t in todos if t.id != todo_id]
    return {"message": "Deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

    cat > "$PROJECTS_DIR/python/todo-api/requirements.txt" <<'EOF'
fastapi
uvicorn[standard]
pydantic
EOF

    cat > "$PROJECTS_DIR/python/todo-api/README.md" <<'EOF'
# TODO API Project

REST API на FastAPI с автодокументацией.

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn main:app --reload
```

Откройте http://localhost:8000/docs для Swagger UI.

## API Endpoints

- `GET /todos` - список задач
- `POST /todos` - создать задачу
- `GET /todos/{id}` - получить задачу
- `DELETE /todos/{id}` - удалить задачу

EOF

    # PROJECT 2: Data Dashboard
    mkdir -p "$PROJECTS_DIR/python/data-dashboard"
    cat > "$PROJECTS_DIR/python/data-dashboard/dashboard.py" <<'EOF'
"""
Проект 2: Data Dashboard
Анализ данных с визуализацией
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_dashboard():
    # Генерируем данные
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=30)
    data = pd.DataFrame({
        'Date': dates,
        'Sales': np.random.randint(100, 500, 30),
        'Visitors': np.random.randint(1000, 5000, 30)
    })
    
    print("📊 Sales Dashboard")
    print("=" * 50)
    print(data.head())
    print(f"\nTotal Sales: ${data['Sales'].sum():,}")
    print(f"Average Sales: ${data['Sales'].mean():.2f}")
    
    # Визуализация
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(data['Date'], data['Sales'], marker='o')
    ax1.set_title('Daily Sales')
    ax1.set_ylabel('Sales ($)')
    ax1.grid(True)
    
    ax2.plot(data['Date'], data['Visitors'], marker='s', color='orange')
    ax2.set_title('Daily Visitors')
    ax2.set_ylabel('Visitors')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('dashboard.png', dpi=150)
    print("\n✅ Dashboard saved as dashboard.png")

if __name__ == "__main__":
    create_dashboard()
EOF

    cat > "$PROJECTS_DIR/python/data-dashboard/requirements.txt" <<'EOF'
pandas
matplotlib
numpy
EOF

    # README для всех проектов
    cat > "$PROJECTS_DIR/python/README.md" <<'EOF'
# Python Project Templates

Готовые шаблоны проектов для быстрого старта.

## Список проектов

### 1. todo-api (FastAPI)
REST API с автодокументацией Swagger.

```bash
cd todo-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. data-dashboard (Pandas + Matplotlib)
Анализ данных с графиками.

```bash
cd data-dashboard
pip install -r requirements.txt
python dashboard.py
```

## Создание нового проекта

```bash
# Создайте venv
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install <packages>

# Создайте requirements.txt
pip freeze > requirements.txt
```

EOF
}

################################################################################
# MENU
################################################################################

dev_menu() {
    mkdir -p "$(dirname $LOG_FILE)"
    
    while true; do
        local choice=$(dialog --clear \
            --backtitle "Dev Environment Setup" \
            --title "Среда разработки" \
            --menu "Выберите действие:" \
            18 70 8 \
            1 "🐍 Python (55+ библиотек + проекты)" \
            2 "🔧 C/C++ (GCC + примеры)" \
            3 "🚀 Всё сразу (Python + C)" \
            4 "📖 Показать README (Python)" \
            5 "📖 Показать README (C)" \
            6 "📂 Открыть директорию примеров" \
            0 "◀ Назад" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) 
                install_python_environment
                dialog --msgbox "✅ Python установлен!\n\nПримеры: $EXAMPLES_DIR/python/\nПроекты: $PROJECTS_DIR/python/\n\nСм. README для деталей" 12 60
                ;;
            2) 
                install_c_environment
                dialog --msgbox "✅ C/C++ установлен!\n\nПримеры: $EXAMPLES_DIR/c/\n\nКомпиляция: make all" 10 60
                ;;
            3) 
                install_python_environment
                install_c_environment
                dialog --msgbox "✅ Всё установлено!" 8 40
                ;;
            4)
                if [[ -f "$EXAMPLES_DIR/python/README.md" ]]; then
                    dialog --textbox "$EXAMPLES_DIR/python/README.md" 30 80
                else
                    dialog --msgbox "Сначала установите Python окружение" 6 40
                fi
                ;;
            5)
                if [[ -f "$EXAMPLES_DIR/c/README.md" ]]; then
                    dialog --textbox "$EXAMPLES_DIR/c/README.md" 30 80
                else
                    dialog --msgbox "Сначала установите C окружение" 6 40
                fi
                ;;
            6)
                dialog --msgbox "Директории:\n\nПримеры:\n$EXAMPLES_DIR\n\nПроекты:\n$PROJECTS_DIR" 12 60
                ;;
            0|"") return ;;
        esac
    done
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo "Требуются права root"
        exit 1
    fi
    dev_menu
fi
