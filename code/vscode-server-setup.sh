#!/bin/bash
################################################################################
# VSCode Server Setup - Полная интеграция среды разработки
# Автор: Sandrick Tech
# Дата: 2024-12-09
# Описание: Установка code-server с интеграцией Git, Python, Docker, Node.js
################################################################################

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

VSCODE_DIR="/opt/code-server"
VSCODE_DATA="/srv/vscode"
VSCODE_PORT=8443
VSCODE_CONFIG="$VSCODE_DATA/config.yaml"
PROJECTS_DIR="/srv/dev/projects"
LOG_FILE="/srv/sys/logs/vscode-setup.log"

info() { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
step() { echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"; }

################################################################################
# УСТАНОВКА CODE-SERVER
################################################################################

install_code_server() {
    step "Установка code-server (VSCode в браузере)..."
    
    # Создаём директории
    mkdir -p "$VSCODE_DATA" "$PROJECTS_DIR" "$(dirname $LOG_FILE)"
    
    # Устанавливаем code-server через официальный скрипт
    if ! command -v code-server &>/dev/null; then
        info "Загрузка и установка code-server..."
        curl -fsSL https://code-server.dev/install.sh | sh
    else
        info "code-server уже установлен"
    fi
    
    # Генерируем пароль если не существует
    if [[ ! -f "$VSCODE_DATA/.password" ]]; then
        VSCODE_PASS=$(openssl rand -base64 20)
        echo "$VSCODE_PASS" > "$VSCODE_DATA/.password"
        chmod 600 "$VSCODE_DATA/.password"
        info "Сгенерирован пароль: $VSCODE_PASS"
    else
        VSCODE_PASS=$(cat "$VSCODE_DATA/.password")
    fi
    
    # Конфигурация
    cat > "$VSCODE_CONFIG" <<EOF
bind-addr: 0.0.0.0:$VSCODE_PORT
auth: password
password: $VSCODE_PASS
cert: false
user-data-dir: $VSCODE_DATA/data
extensions-dir: $VSCODE_DATA/extensions
EOF
    
    info "✅ code-server установлен"
}

################################################################################
# УСТАНОВКА РАСШИРЕНИЙ
################################################################################

install_vscode_extensions() {
    step "Установка расширений VSCode..."
    
    local extensions=(
        # Python
        "ms-python.python"
        "ms-python.vscode-pylance"
        "ms-python.black-formatter"
        "ms-python.flake8"
        "ms-python.isort"
        
        # Git
        "eamodio.gitlens"
        "mhutchie.git-graph"
        "donjayamanne.githistory"
        
        # Docker
        "ms-azuretools.vscode-docker"
        "ms-vscode-remote.remote-containers"
        
        # JavaScript/Node
        "dbaeumer.vscode-eslint"
        "esbenp.prettier-vscode"
        "ms-vscode.vscode-typescript-next"
        
        # Web Development
        "formulahendry.auto-close-tag"
        "formulahendry.auto-rename-tag"
        "zignd.html-css-class-completion"
        
        # Database
        "mtxr.sqltools"
        "cweijan.vscode-mysql-client2"
        "cweijan.vscode-postgresql-client2"
        
        # Utilities
        "christian-kohler.path-intellisense"
        "wayou.vscode-todo-highlight"
        "gruntfuggly.todo-tree"
        "oderwat.indent-rainbow"
        "pkief.material-icon-theme"
        "zhuangtongfa.material-theme"
        
        # Markdown
        "yzhang.markdown-all-in-one"
        "davidanson.vscode-markdownlint"
        
        # REST API
        "humao.rest-client"
        
        # YAML/JSON
        "redhat.vscode-yaml"
        "tamasfe.even-better-toml"
    )
    
    info "Установка ${#extensions[@]} расширений..."
    
    for ext in "${extensions[@]}"; do
        if code-server --extensions-dir "$VSCODE_DATA/extensions" --list-extensions | grep -q "$ext"; then
            info "  ✓ $ext уже установлен"
        else
            info "  ⬇ Установка $ext..."
            code-server --extensions-dir "$VSCODE_DATA/extensions" --install-extension "$ext" 2>/dev/null || warn "Не удалось установить $ext"
        fi
    done
    
    success "Расширения установлены"
}

################################################################################
# GIT ИНТЕГРАЦИЯ
################################################################################

setup_git_integration() {
    step "Настройка Git интеграции..."
    
    # Устанавливаем Git если не установлен
    if ! command -v git &>/dev/null; then
        apt-get install -y git git-lfs
    fi
    
    # Git LFS для больших файлов
    git lfs install
    
    # Глобальная конфигурация
    cat > /root/.gitconfig <<EOF
[user]
    name = Server Admin
    email = admin@$(hostname)
[core]
    editor = code-server --wait
    autocrlf = input
[init]
    defaultBranch = main
[pull]
    rebase = false
[push]
    default = current
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    lg = log --oneline --graph --decorate --all
    last = log -1 HEAD
    unstage = reset HEAD --
[color]
    ui = auto
EOF
    
    # Pre-commit hooks шаблон
    mkdir -p "$PROJECTS_DIR/.git-templates/hooks"
    
    cat > "$PROJECTS_DIR/.git-templates/hooks/pre-commit" <<'EOF'
#!/bin/bash
# Pre-commit hook: проверка Python кода

if git diff --cached --name-only | grep -q '\.py$'; then
    echo "🔍 Checking Python files..."
    
    # Black formatter
    if command -v black &>/dev/null; then
        git diff --cached --name-only | grep '\.py$' | xargs black --check || {
            echo "❌ Black formatting required. Run: black ."
            exit 1
        }
    fi
    
    # Flake8 linter
    if command -v flake8 &>/dev/null; then
        git diff --cached --name-only | grep '\.py$' | xargs flake8 || {
            echo "❌ Flake8 errors found"
            exit 1
        }
    fi
    
    echo "✅ Python checks passed"
fi

exit 0
EOF
    chmod +x "$PROJECTS_DIR/.git-templates/hooks/pre-commit"
    
    git config --global init.templatedir "$PROJECTS_DIR/.git-templates"
    
    # Создаём .gitignore шаблоны
    cat > "$PROJECTS_DIR/.gitignore_python" <<EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/
.eggs/
.pytest_cache/
.coverage
.mypy_cache/
.ruff_cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
*.log
EOF
    
    success "Git интеграция настроена"
}

################################################################################
# DOCKER INTEGRATION
################################################################################

setup_docker_integration() {
    step "Настройка Docker интеграции..."
    
    # Проверяем Docker
    if ! command -v docker &>/dev/null; then
        warn "Docker не установлен, пропускаем интеграцию"
        return
    fi
    
    # Dev Container шаблоны
    mkdir -p "$PROJECTS_DIR/.devcontainer"
    
    # Python Dev Container
    cat > "$PROJECTS_DIR/.devcontainer/python.devcontainer.json" <<EOF
{
    "name": "Python Dev",
    "image": "mcr.microsoft.com/devcontainers/python:3.11",
    "features": {
        "ghcr.io/devcontainers/features/git:1": {},
        "ghcr.io/devcontainers/features/docker-in-docker:2": {}
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "eamodio.gitlens"
            ]
        }
    },
    "postCreateCommand": "pip install -r requirements.txt",
    "forwardPorts": [8000],
    "remoteUser": "vscode"
}
EOF
    
    # Node.js Dev Container
    cat > "$PROJECTS_DIR/.devcontainer/node.devcontainer.json" <<EOF
{
    "name": "Node.js Dev",
    "image": "mcr.microsoft.com/devcontainers/javascript-node:18",
    "features": {
        "ghcr.io/devcontainers/features/git:1": {}
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "dbaeumer.vscode-eslint",
                "esbenp.prettier-vscode"
            ]
        }
    },
    "postCreateCommand": "npm install",
    "forwardPorts": [3000]
}
EOF
    
    # Docker Compose для разработки
    cat > "$PROJECTS_DIR/docker-compose.dev.yml" <<EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: dev_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  mongodb:
    image: mongo:6
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: dev_password
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  postgres_data:
  redis_data:
  mongo_data:
EOF
    
    success "Docker интеграция настроена"
}

################################################################################
# WORKSPACE SETTINGS
################################################################################

create_workspace_settings() {
    step "Создание workspace настроек..."
    
    mkdir -p "$VSCODE_DATA/User"
    
    # Settings.json
    cat > "$VSCODE_DATA/User/settings.json" <<EOF
{
    "workbench.colorTheme": "Material Theme Ocean High Contrast",
    "workbench.iconTheme": "material-icon-theme",
    "editor.fontSize": 14,
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "editor.formatOnSave": true,
    "editor.rulers": [80, 120],
    "editor.minimap.enabled": true,
    "editor.suggestSelection": "first",
    "editor.bracketPairColorization.enabled": true,
    "editor.guides.bracketPairs": true,
    
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000,
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.pylintEnabled": false,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.testing.pytestEnabled": true,
    
    "git.enableSmartCommit": true,
    "git.confirmSync": false,
    "git.autofetch": true,
    "gitlens.currentLine.enabled": true,
    
    "terminal.integrated.fontSize": 13,
    "terminal.integrated.shell.linux": "/bin/bash",
    
    "todo-tree.general.tags": ["TODO", "FIXME", "BUG", "HACK", "NOTE"],
    
    "rest-client.environmentVariables": {
        "local": {
            "host": "localhost",
            "port": "8000"
        }
    }
}
EOF
    
    # Keybindings
    cat > "$VSCODE_DATA/User/keybindings.json" <<EOF
[
    {
        "key": "ctrl+shift+t",
        "command": "workbench.action.terminal.new"
    },
    {
        "key": "ctrl+shift+f",
        "command": "workbench.action.findInFiles"
    }
]
EOF
    
    success "Workspace настроен"
}

################################################################################
# SYSTEMD SERVICE
################################################################################

create_systemd_service() {
    step "Создание systemd service..."
    
    cat > /etc/systemd/system/code-server.service <<EOF
[Unit]
Description=code-server (VSCode Server)
After=network.target

[Service]
Type=exec
ExecStart=/usr/bin/code-server --config $VSCODE_CONFIG
Restart=always
User=root
Environment=PASSWORD=$VSCODE_PASS
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable code-server
    systemctl restart code-server
    
    # Открываем порт в iptables
    iptables -C INPUT -p tcp --dport $VSCODE_PORT -j ACCEPT 2>/dev/null || \
        iptables -I INPUT -p tcp --dport $VSCODE_PORT -j ACCEPT
    iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    
    success "Systemd service создан и запущен"
}

################################################################################
# PROJECT TEMPLATES
################################################################################

create_project_templates() {
    step "Создание шаблонов проектов..."
    
    # Python FastAPI template
    mkdir -p "$PROJECTS_DIR/templates/fastapi-template"
    cd "$PROJECTS_DIR/templates/fastapi-template"
    
    cat > requirements.txt <<EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
sqlalchemy==2.0.23
alembic==1.13.0
EOF
    
    cat > main.py <<'EOF'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="My API", version="1.0.0")

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float

items_db = []

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}

@app.get("/items", response_model=List[Item])
async def get_items():
    return items_db

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    item.id = len(items_db) + 1
    items_db.append(item)
    return item

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
    
    cat > .env.example <<EOF
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
DEBUG=True
EOF
    
    cat > README.md <<EOF
# FastAPI Template

## Setup
\`\`\`bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

## Run
\`\`\`bash
uvicorn main:app --reload
\`\`\`

## API Docs
http://localhost:8000/docs
EOF
    
    success "Шаблоны проектов созданы"
}

################################################################################
# МЕНЮ
################################################################################

vscode_menu() {
    mkdir -p "$(dirname $LOG_FILE)"
    
    while true; do
        local status="❌ Остановлен"
        if systemctl is-active --quiet code-server 2>/dev/null; then
            status="✅ Запущен"
        fi
        
        local ip=$(hostname -I | awk '{print $1}')
        
        local choice=$(dialog --clear \
            --backtitle "VSCode Server Setup" \
            --title "VSCode Server [$status] | Port: $VSCODE_PORT" \
            --menu "Выберите действие:" \
            20 75 12 \
            1 "📥 Установить code-server" \
            2 "🔌 Установить расширения VSCode" \
            3 "🔧 Настроить Git интеграцию" \
            4 "🐳 Настроить Docker интеграцию" \
            5 "⚙️  Создать workspace настройки" \
            6 "🚀 Создать systemd service" \
            7 "📁 Создать шаблоны проектов" \
            8 "🔄 Перезапустить сервис" \
            9 "📊 Показать статус" \
            10 "🌐 Открыть URL" \
            11 "🔑 Показать пароль" \
            0 "◀ Назад" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) install_code_server ;;
            2) install_vscode_extensions ;;
            3) setup_git_integration ;;
            4) setup_docker_integration ;;
            5) create_workspace_settings ;;
            6) create_systemd_service ;;
            7) create_project_templates ;;
            8) 
                systemctl restart code-server
                dialog --msgbox "✅ Сервис перезапущен" 6 30
                ;;
            9)
                local status_text=$(cat <<STATUS
╔═══════════════════════════════════════════╗
║       VSCode Server Status                ║
╚═══════════════════════════════════════════╝

Service: $(systemctl is-active code-server 2>/dev/null || echo "inactive")
Port: $VSCODE_PORT
Data: $VSCODE_DATA
Projects: $PROJECTS_DIR

Extensions: $(code-server --list-extensions 2>/dev/null | wc -l)

URL: https://$ip:$VSCODE_PORT

Recent logs:
$(tail -n 10 "$LOG_FILE" 2>/dev/null || echo "No logs")
STATUS
)
                dialog --title "Status" --msgbox "$status_text" 25 70
                ;;
            10)
                dialog --msgbox "Откройте в браузере:\n\nhttps://$ip:$VSCODE_PORT\n\nПароль см. в пункте 'Показать пароль'" 10 50
                ;;
            11)
                if [[ -f "$VSCODE_DATA/.password" ]]; then
                    local pass=$(cat "$VSCODE_DATA/.password")
                    dialog --msgbox "Пароль VSCode:\n\n$pass\n\nURL: https://$ip:$VSCODE_PORT" 10 50
                else
                    dialog --msgbox "Пароль не найден. Установите code-server сначала." 7 50
                fi
                ;;
            0|"") return ;;
        esac
    done
}

# Запуск
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}Требуются права root${NC}"
        exit 1
    fi
    vscode_menu
fi
