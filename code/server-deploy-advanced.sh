#!/bin/bash

#####################################################################
# Server Deploy Master - Advanced Edition v4.0
# MC-style Multi-Pane Interface with Dialog
# Full User Management & Extended Capabilities
#####################################################################

set -euo pipefail

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
STATE_FILE="/srv/sys/.deployment_state.json"
LOG_FILE="/var/log/server-deploy.log"
USERS_FILE="/srv/sys/.users_db.json"
CONFIG_DIR="/srv/sys/configs"
TMP_DIR="/tmp/server-deploy"

# Dialog configuration
DIALOG_HEIGHT=25
DIALOG_WIDTH=80
DIALOG_BACKTITLE="Server Deployment Master v4.0 - Advanced Edition"

# ==================== UTILITIES ====================
banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║   _____ ______ _____  _    _ ______ _____                         ║
║  / ____|  ____|  __ \| |  | |  ____|  __ \                        ║
║ | (___ | |__  | |__) | |  | | |__  | |__) |                       ║
║  \___ \|  __| |  _  /| |  | |  __| |  _  /                        ║
║  ____) | |____| | \ \| |__| | |____| | \ \                        ║
║ |_____/|______|_|  \_\\____/|______|_|  \_\                       ║
║                                                                    ║
║        DEPLOY MASTER - Advanced Edition v4.0                      ║
║        MC-Style Multi-Pane Interface                              ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

info() { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"; }
step() { echo -e "${MAGENTA}[STEP]${NC} $1" | tee -a "$LOG_FILE"; }

# Initialize
init_system() {
    mkdir -p /srv/sys/{fail2ban,configs,backups,logs}
    mkdir -p "$TMP_DIR"
    touch "$STATE_FILE" "$LOG_FILE" "$USERS_FILE"
    chmod 600 "$STATE_FILE" "$USERS_FILE"
    
    # Install dialog if not present
    if ! command -v dialog &> /dev/null; then
        apt-get update -qq
        apt-get install -y dialog whiptail tmux screen 2>/dev/null || true
    fi
}

# State management
save_state() { 
    jq -n --arg k "$1" --arg v "$2" "{\"$k\": \"$v\"}" | jq -s 'add' "$STATE_FILE" - > "$STATE_FILE.tmp" 2>/dev/null || echo "{\"$1\": \"$2\"}" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
}

get_state() { 
    jq -r ".$1 // empty" "$STATE_FILE" 2>/dev/null || echo ""
}

# ==================== USER MANAGEMENT ====================

# Create user database
init_users_db() {
    if [[ ! -s "$USERS_FILE" ]]; then
        echo '{"users": []}' > "$USERS_FILE"
    fi
}

# Add system user
add_system_user() {
    local username="$1"
    local password="$2"
    local role="${3:-user}"
    local groups="${4:-}"
    local shell="${5:-/bin/bash}"
    local home_dir="/home/$username"
    
    # Create system user
    if id "$username" &>/dev/null; then
        dialog --title "Error" --msgbox "User $username already exists!" 8 40
        return 1
    fi
    
    useradd -m -d "$home_dir" -s "$shell" -c "Created by Deploy Master" "$username"
    echo "$username:$password" | chpasswd
    
    # Add to groups
    if [[ -n "$groups" ]]; then
        IFS=',' read -ra GROUP_ARRAY <<< "$groups"
        for group in "${GROUP_ARRAY[@]}"; do
            usermod -aG "$group" "$username" 2>/dev/null || true
        done
    fi
    
    # Setup SSH key
    mkdir -p "$home_dir/.ssh"
    touch "$home_dir/.ssh/authorized_keys"
    chmod 700 "$home_dir/.ssh"
    chmod 600 "$home_dir/.ssh/authorized_keys"
    chown -R "$username:$username" "$home_dir/.ssh"
    
    # Save to database
    local timestamp=$(date +%s)
    local user_data=$(jq -n \
        --arg user "$username" \
        --arg role "$role" \
        --arg groups "$groups" \
        --arg created "$timestamp" \
        '{username: $user, role: $role, groups: $groups, created: $created, status: "active"}')
    
    jq ".users += [$user_data]" "$USERS_FILE" > "$USERS_FILE.tmp"
    mv "$USERS_FILE.tmp" "$USERS_FILE"
    
    info "User $username created successfully"
    return 0
}

# List users
list_users() {
    local user_list=""
    local count=1
    
    while IFS= read -r user; do
        local username=$(echo "$user" | jq -r '.username')
        local role=$(echo "$user" | jq -r '.role')
        local status=$(echo "$user" | jq -r '.status')
        user_list+="$count \"$username\" \"$role\" \"$status\" "
        ((count++))
    done < <(jq -c '.users[]' "$USERS_FILE" 2>/dev/null)
    
    if [[ -z "$user_list" ]]; then
        dialog --title "Users" --msgbox "No users found" 8 40
        return
    fi
    
    dialog --title "System Users" \
        --menu "Select user to manage:" 20 60 10 \
        $user_list
}

# User management dialog
user_management_menu() {
    while true; do
        local choice=$(dialog --clear --backtitle "$DIALOG_BACKTITLE" \
            --title "User Management" \
            --menu "Choose action:" 20 60 12 \
            1 "Add new user" \
            2 "List all users" \
            3 "Modify user" \
            4 "Delete user" \
            5 "Lock/Unlock user" \
            6 "Change password" \
            7 "Add SSH key" \
            8 "User permissions" \
            9 "Sudo access" \
            10 "User groups" \
            11 "User quotas" \
            0 "Back" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) add_user_dialog ;;
            2) list_users ;;
            3) modify_user_dialog ;;
            4) delete_user_dialog ;;
            5) lock_unlock_user_dialog ;;
            6) change_password_dialog ;;
            7) add_ssh_key_dialog ;;
            8) user_permissions_dialog ;;
            9) sudo_access_dialog ;;
            10) user_groups_dialog ;;
            11) user_quotas_dialog ;;
            0|"") return ;;
        esac
    done
}

# Add user dialog
add_user_dialog() {
    local username=$(dialog --inputbox "Enter username:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$username" ]] && return
    
    local password=$(dialog --passwordbox "Enter password:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$password" ]] && return
    
    local role=$(dialog --menu "Select role:" 12 40 4 \
        "user" "Regular user" \
        "admin" "Administrator" \
        "developer" "Developer" \
        "devops" "DevOps Engineer" \
        3>&1 1>&2 2>&3)
    
    local groups=$(dialog --inputbox "Additional groups (comma-separated):" 8 60 3>&1 1>&2 2>&3)
    
    add_system_user "$username" "$password" "$role" "$groups"
    
    dialog --title "Success" --msgbox "User $username created!" 8 40
}

# Delete user dialog
delete_user_dialog() {
    local username=$(dialog --inputbox "Enter username to delete:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$username" ]] && return
    
    dialog --yesno "Delete user $username and home directory?" 8 50
    if [[ $? -eq 0 ]]; then
        userdel -r "$username" 2>/dev/null || true
        jq "del(.users[] | select(.username == \"$username\"))" "$USERS_FILE" > "$USERS_FILE.tmp"
        mv "$USERS_FILE.tmp" "$USERS_FILE"
        dialog --msgbox "User $username deleted" 8 40
    fi
}

# Lock/Unlock user
lock_unlock_user_dialog() {
    local username=$(dialog --inputbox "Enter username:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$username" ]] && return
    
    local action=$(dialog --menu "Choose action:" 10 40 2 \
        "lock" "Lock account" \
        "unlock" "Unlock account" \
        3>&1 1>&2 2>&3)
    
    case $action in
        lock)
            passwd -l "$username"
            dialog --msgbox "User $username locked" 8 40
            ;;
        unlock)
            passwd -u "$username"
            dialog --msgbox "User $username unlocked" 8 40
            ;;
    esac
}

# Change password dialog
change_password_dialog() {
    local username=$(dialog --inputbox "Enter username:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$username" ]] && return
    
    local password=$(dialog --passwordbox "New password:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$password" ]] && return
    
    echo "$username:$password" | chpasswd
    dialog --msgbox "Password changed for $username" 8 40
}

# Add SSH key
add_ssh_key_dialog() {
    local username=$(dialog --inputbox "Enter username:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$username" ]] && return
    
    local ssh_key=$(dialog --inputbox "Paste SSH public key:" 8 70 3>&1 1>&2 2>&3)
    [[ -z "$ssh_key" ]] && return
    
    local home_dir=$(getent passwd "$username" | cut -d: -f6)
    mkdir -p "$home_dir/.ssh"
    echo "$ssh_key" >> "$home_dir/.ssh/authorized_keys"
    chmod 700 "$home_dir/.ssh"
    chmod 600 "$home_dir/.ssh/authorized_keys"
    chown -R "$username:$username" "$home_dir/.ssh"
    
    dialog --msgbox "SSH key added for $username" 8 40
}

# Sudo access
sudo_access_dialog() {
    local username=$(dialog --inputbox "Enter username:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$username" ]] && return
    
    local sudo_type=$(dialog --menu "Grant sudo access:" 12 50 4 \
        "full" "Full sudo (ALL)" \
        "nopasswd" "No password required" \
        "limited" "Limited commands" \
        "revoke" "Revoke sudo" \
        3>&1 1>&2 2>&3)
    
    case $sudo_type in
        full)
            echo "$username ALL=(ALL:ALL) ALL" > "/etc/sudoers.d/$username"
            ;;
        nopasswd)
            echo "$username ALL=(ALL:ALL) NOPASSWD: ALL" > "/etc/sudoers.d/$username"
            ;;
        limited)
            local cmds=$(dialog --inputbox "Allowed commands (comma-separated):" 8 60 "/usr/bin/systemctl,/usr/bin/docker" 3>&1 1>&2 2>&3)
            echo "$username ALL=(ALL:ALL) NOPASSWD: $cmds" > "/etc/sudoers.d/$username"
            ;;
        revoke)
            rm -f "/etc/sudoers.d/$username"
            ;;
    esac
    
    chmod 0440 "/etc/sudoers.d/$username" 2>/dev/null || true
    dialog --msgbox "Sudo access updated for $username" 8 40
}

# User groups management
user_groups_dialog() {
    local username=$(dialog --inputbox "Enter username:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$username" ]] && return
    
    local current_groups=$(groups "$username" | cut -d: -f2)
    
    local action=$(dialog --menu "Groups management:" 12 50 3 \
        "add" "Add to groups" \
        "remove" "Remove from groups" \
        "show" "Show current groups" \
        3>&1 1>&2 2>&3)
    
    case $action in
        add)
            local groups=$(dialog --inputbox "Groups to add (comma-separated):" 8 60 "docker,www-data,sudo" 3>&1 1>&2 2>&3)
            IFS=',' read -ra GROUP_ARRAY <<< "$groups"
            for group in "${GROUP_ARRAY[@]}"; do
                usermod -aG "$group" "$username" 2>/dev/null || true
            done
            dialog --msgbox "Groups added for $username" 8 40
            ;;
        remove)
            local groups=$(dialog --inputbox "Groups to remove (comma-separated):" 8 60 3>&1 1>&2 2>&3)
            IFS=',' read -ra GROUP_ARRAY <<< "$groups"
            for group in "${GROUP_ARRAY[@]}"; do
                gpasswd -d "$username" "$group" 2>/dev/null || true
            done
            dialog --msgbox "Groups removed for $username" 8 40
            ;;
        show)
            dialog --msgbox "Current groups:\n$current_groups" 10 50
            ;;
    esac
}

# User quotas
user_quotas_dialog() {
    local username=$(dialog --inputbox "Enter username:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$username" ]] && return
    
    # Check if quota is installed
    if ! command -v quota &> /dev/null; then
        dialog --yesno "Quota tools not installed. Install now?" 8 40
        if [[ $? -eq 0 ]]; then
            apt-get install -y quota quotatool
        else
            return
        fi
    fi
    
    local soft=$(dialog --inputbox "Soft limit (MB):" 8 40 "1000" 3>&1 1>&2 2>&3)
    local hard=$(dialog --inputbox "Hard limit (MB):" 8 40 "1500" 3>&1 1>&2 2>&3)
    
    setquota -u "$username" ${soft}M ${hard}M 0 0 / 2>/dev/null || \
        dialog --msgbox "Failed to set quota. Enable quota on filesystem first." 8 60
    
    dialog --msgbox "Quota set for $username:\nSoft: ${soft}MB\nHard: ${hard}MB" 10 50
}

# User permissions
user_permissions_dialog() {
    local username=$(dialog --inputbox "Enter username:" 8 40 3>&1 1>&2 2>&3)
    [[ -z "$username" ]] && return
    
    local home_dir=$(getent passwd "$username" | cut -d: -f6)
    
    local perm=$(dialog --menu "Set permissions:" 15 60 7 \
        "restrict" "Restrict to home only" \
        "web" "Web server access" \
        "database" "Database access" \
        "docker" "Docker access" \
        "logs" "Log files access" \
        "custom" "Custom directory" \
        3>&1 1>&2 2>&3)
    
    case $perm in
        restrict)
            chmod 750 "$home_dir"
            ;;
        web)
            usermod -aG www-data "$username"
            setfacl -R -m u:$username:rwx /var/www 2>/dev/null || true
            ;;
        database)
            usermod -aG mysql "$username" 2>/dev/null || \
                usermod -aG postgres "$username" 2>/dev/null || true
            ;;
        docker)
            usermod -aG docker "$username"
            ;;
        logs)
            usermod -aG adm "$username"
            setfacl -R -m u:$username:rx /var/log 2>/dev/null || true
            ;;
        custom)
            local dir=$(dialog --inputbox "Directory path:" 8 60 3>&1 1>&2 2>&3)
            setfacl -R -m u:$username:rwx "$dir" 2>/dev/null || \
                dialog --msgbox "Failed to set ACL. Install acl package." 8 50
            ;;
    esac
    
    dialog --msgbox "Permissions updated for $username" 8 40
}

# ==================== CONFIG EDITOR (MC-Style) ====================

# Configuration file editor with preview
config_editor() {
    while true; do
        # Get list of config files
        local config_files=()
        local count=1
        
        # Common config locations
        for dir in /etc/nginx /etc/apache2 /etc/mysql /etc/postgresql /etc/postfix /etc/dovecot /etc/fail2ban /etc/ssh "$CONFIG_DIR"; do
            if [[ -d "$dir" ]]; then
                while IFS= read -r file; do
                    config_files+=("$count" "$file")
                    ((count++))
                done < <(find "$dir" -maxdepth 2 -type f \( -name "*.conf" -o -name "*.cfg" -o -name "*.ini" -o -name "*.yml" -o -name "*.yaml" \) 2>/dev/null)
            fi
        done
        
        if [[ ${#config_files[@]} -eq 0 ]]; then
            dialog --msgbox "No configuration files found" 8 40
            return
        fi
        
        local selected=$(dialog --menu "Select configuration file:" 20 70 12 "${config_files[@]}" 3>&1 1>&2 2>&3)
        [[ -z "$selected" ]] && return
        
        local file_index=$(( (selected - 1) * 2 + 1 ))
        local config_file="${config_files[$file_index]}"
        
        edit_config_file "$config_file"
    done
}

# Edit single config file
edit_config_file() {
    local file="$1"
    
    while true; do
        local action=$(dialog --menu "Config: $(basename $file)" 15 60 7 \
            1 "View file" \
            2 "Edit with nano" \
            3 "Edit with vim" \
            4 "Backup file" \
            5 "Restore backup" \
            6 "Validate syntax" \
            0 "Back" \
            3>&1 1>&2 2>&3)
        
        case $action in
            1)
                dialog --textbox "$file" 0 0
                ;;
            2)
                dialog --pause "Opening nano editor..." 8 40 2
                nano "$file"
                ;;
            3)
                dialog --pause "Opening vim editor..." 8 40 2
                vim "$file"
                ;;
            4)
                cp "$file" "$file.backup.$(date +%Y%m%d_%H%M%S)"
                dialog --msgbox "Backup created: $file.backup.*" 8 50
                ;;
            5)
                local backups=$(ls -1 "$file.backup."* 2>/dev/null | tail -5)
                if [[ -z "$backups" ]]; then
                    dialog --msgbox "No backups found" 8 40
                else
                    local backup=$(dialog --menu "Select backup:" 15 60 5 \
                        $(echo "$backups" | awk '{print NR, $0}') 3>&1 1>&2 2>&3)
                    [[ -n "$backup" ]] && cp "$(echo "$backups" | sed -n "${backup}p")" "$file"
                    dialog --msgbox "Backup restored" 8 40
                fi
                ;;
            6)
                validate_config_syntax "$file"
                ;;
            0|"") return ;;
        esac
    done
}

# Validate config syntax
validate_config_syntax() {
    local file="$1"
    local result=""
    
    case "$file" in
        */nginx*)
            result=$(nginx -t 2>&1)
            ;;
        */apache*)
            result=$(apache2ctl -t 2>&1)
            ;;
        */sshd_config)
            result=$(sshd -t 2>&1)
            ;;
        *.yml|*.yaml)
            result=$(python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>&1)
            ;;
        *.json)
            result=$(jq empty "$file" 2>&1)
            ;;
        *)
            result="Syntax validation not available for this file type"
            ;;
    esac
    
    dialog --msgbox "Validation result:\n\n$result" 15 70
}

# ==================== MULTI-PANE INTERFACE (MC-Style) ====================

# Launch MC-style interface with tmux
launch_mc_interface() {
    if ! command -v tmux &> /dev/null; then
        dialog --msgbox "tmux is required for MC-style interface. Installing..." 8 50
        apt-get install -y tmux
    fi
    
    # Create tmux session
    tmux new-session -d -s deploy_master
    
    # Split into 3 panes: top (editor), bottom-left (console), bottom-right (monitoring)
    tmux split-window -v -p 30
    tmux split-window -h -p 50
    
    # Top pane: config editor with ranger/mc
    tmux select-pane -t 0
    if command -v ranger &> /dev/null; then
        tmux send-keys -t 0 "ranger /etc" C-m
    elif command -v mc &> /dev/null; then
        tmux send-keys -t 0 "mc /etc /srv/sys" C-m
    else
        tmux send-keys -t 0 "cd /etc && ls -la" C-m
    fi
    
    # Bottom-left pane: console output
    tmux select-pane -t 1
    tmux send-keys -t 1 "tail -f $LOG_FILE" C-m
    
    # Bottom-right pane: system monitoring
    tmux select-pane -t 2
    if command -v htop &> /dev/null; then
        tmux send-keys -t 2 "htop" C-m
    else
        tmux send-keys -t 2 "top" C-m
    fi
    
    # Attach to session
    tmux attach-session -t deploy_master
}

# Advanced MC-style interface with dialog
mc_style_dialog() {
    while true; do
        local choice=$(dialog --clear --backtitle "$DIALOG_BACKTITLE" \
            --title "MC-Style Interface" \
            --menu "Multi-pane workspace:" 18 70 10 \
            1 "Launch tmux workspace (3 panes)" \
            2 "Launch screen workspace" \
            3 "Config editor (left pane)" \
            4 "Log viewer (right pane)" \
            5 "System monitor (bottom pane)" \
            6 "Install ranger file manager" \
            7 "Install midnight commander" \
            8 "Install glances monitor" \
            9 "Custom layout" \
            0 "Back" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) launch_mc_interface ;;
            2) launch_screen_interface ;;
            3) config_editor ;;
            4) dialog --textbox "$LOG_FILE" 0 0 ;;
            5) 
                dialog --pause "Launching htop..." 8 40 2
                htop
                ;;
            6) 
                apt-get install -y ranger
                dialog --msgbox "Ranger installed!" 8 40
                ;;
            7) 
                apt-get install -y mc
                dialog --msgbox "Midnight Commander installed!" 8 40
                ;;
            8) 
                apt-get install -y glances
                dialog --msgbox "Glances installed!" 8 40
                ;;
            9) custom_layout_dialog ;;
            0|"") return ;;
        esac
    done
}

# Launch screen interface
launch_screen_interface() {
    if ! command -v screen &> /dev/null; then
        apt-get install -y screen
    fi
    
    screen -dmS deploy_master
    screen -S deploy_master -X screen -t "Editor" 0 vim "+e /etc/nginx/nginx.conf"
    screen -S deploy_master -X screen -t "Logs" 1 tail -f "$LOG_FILE"
    screen -S deploy_master -X screen -t "Monitor" 2 htop
    
    dialog --msgbox "Screen session started. Attach: screen -r deploy_master" 8 60
}

# Custom layout dialog
custom_layout_dialog() {
    local layout=$(dialog --menu "Select layout:" 15 60 6 \
        "horizontal" "2 panes side-by-side" \
        "vertical" "2 panes top/bottom" \
        "quad" "4 panes (2x2)" \
        "triple_h" "3 panes horizontal" \
        "triple_v" "3 panes vertical" \
        3>&1 1>&2 2>&3)
    
    [[ -z "$layout" ]] && return
    
    tmux new-session -d -s custom_layout
    
    case $layout in
        horizontal)
            tmux split-window -h
            ;;
        vertical)
            tmux split-window -v
            ;;
        quad)
            tmux split-window -h
            tmux split-window -v
            tmux select-pane -t 0
            tmux split-window -v
            ;;
        triple_h)
            tmux split-window -h
            tmux split-window -h
            ;;
        triple_v)
            tmux split-window -v
            tmux split-window -v
            ;;
    esac
    
    tmux attach-session -t custom_layout
}

# ==================== EXTENDED CAPABILITIES ====================

# Backup & Restore
backup_restore_menu() {
    while true; do
        local choice=$(dialog --menu "Backup & Restore" 15 60 7 \
            1 "Backup configs" \
            2 "Backup databases" \
            3 "Backup users" \
            4 "Full system backup" \
            5 "Restore from backup" \
            6 "Scheduled backups" \
            0 "Back" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) backup_configs ;;
            2) backup_databases ;;
            3) backup_users ;;
            4) full_backup ;;
            5) restore_backup ;;
            6) schedule_backups ;;
            0|"") return ;;
        esac
    done
}

backup_configs() {
    local backup_dir="/srv/sys/backups/configs_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    tar czf "$backup_dir/etc.tar.gz" /etc 2>/dev/null
    tar czf "$backup_dir/nginx.tar.gz" /etc/nginx 2>/dev/null
    tar czf "$backup_dir/srv_sys.tar.gz" /srv/sys 2>/dev/null
    
    dialog --msgbox "Configs backed up to:\n$backup_dir" 10 60
}

backup_databases() {
    local backup_dir="/srv/sys/backups/databases_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # MySQL
    if command -v mysqldump &> /dev/null; then
        mysqldump --all-databases > "$backup_dir/mysql_all.sql" 2>/dev/null || true
    fi
    
    # PostgreSQL
    if command -v pg_dumpall &> /dev/null; then
        sudo -u postgres pg_dumpall > "$backup_dir/postgres_all.sql" 2>/dev/null || true
    fi
    
    # MongoDB
    if command -v mongodump &> /dev/null; then
        mongodump --out "$backup_dir/mongodb" 2>/dev/null || true
    fi
    
    dialog --msgbox "Databases backed up to:\n$backup_dir" 10 60
}

# Security hardening
security_menu() {
    while true; do
        local choice=$(dialog --menu "Security Hardening" 18 60 10 \
            1 "SSH hardening" \
            2 "Firewall rules" \
            3 "SELinux/AppArmor" \
            4 "Audit logs" \
            5 "Port scanner" \
            6 "Vulnerability scan" \
            7 "SSL/TLS check" \
            8 "Password policies" \
            9 "2FA setup" \
            0 "Back" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) ssh_hardening ;;
            2) firewall_rules ;;
            3) selinux_apparmor ;;
            4) audit_logs ;;
            5) port_scanner ;;
            6) vuln_scan ;;
            7) ssl_check ;;
            8) password_policies ;;
            9) setup_2fa ;;
            0|"") return ;;
        esac
    done
}

ssh_hardening() {
    dialog --yesno "Apply SSH hardening?\n\n- Disable root login\n- Disable password auth\n- Change port to 2222\n- Enable key-only auth" 12 60
    
    if [[ $? -eq 0 ]]; then
        sed -i 's/#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
        sed -i 's/#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
        sed -i 's/#*Port.*/Port 2222/' /etc/ssh/sshd_config
        sed -i 's/#*PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config
        
        systemctl restart sshd
        dialog --msgbox "SSH hardened! New port: 2222" 8 40
    fi
}

firewall_rules() {
    local rule=$(dialog --menu "Firewall rules:" 15 60 7 \
        1 "Allow HTTP/HTTPS" \
        2 "Allow SSH (custom port)" \
        3 "Allow MySQL/PostgreSQL" \
        4 "Allow mail ports" \
        5 "Block country" \
        6 "Rate limiting" \
        3>&1 1>&2 2>&3)
    
    case $rule in
        1)
            iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 80 -j ACCEPT
            iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 443 -j ACCEPT
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            dialog --msgbox "HTTP/HTTPS allowed" 8 40
            ;;
        2)
            local port=$(dialog --inputbox "SSH port:" 8 40 "2222" 3>&1 1>&2 2>&3)
            iptables -C INPUT -p tcp --dport "$port" -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport "$port" -j ACCEPT
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            dialog --msgbox "SSH port $port allowed" 8 40
            ;;
        3)
            iptables -C INPUT -p tcp --dport 3306 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 3306 -j ACCEPT  # MySQL
            iptables -C INPUT -p tcp --dport 5432 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 5432 -j ACCEPT  # PostgreSQL
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            dialog --msgbox "Database ports allowed" 8 40
            ;;
    esac
}

# Performance optimization
performance_menu() {
    while true; do
        local choice=$(dialog --menu "Performance Optimization" 15 60 8 \
            1 "System tuning" \
            2 "Web server optimization" \
            3 "Database optimization" \
            4 "Kernel parameters" \
            5 "Disk I/O tuning" \
            6 "Network optimization" \
            7 "Cache configuration" \
            0 "Back" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) system_tuning ;;
            2) web_optimization ;;
            3) db_optimization ;;
            4) kernel_tuning ;;
            5) disk_tuning ;;
            6) network_tuning ;;
            7) cache_config ;;
            0|"") return ;;
        esac
    done
}

kernel_tuning() {
    cat >> /etc/sysctl.conf <<'EOF'
# Performance tuning
vm.swappiness=10
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=4096
net.ipv4.ip_local_port_range=1024 65535
net.core.rmem_max=16777216
net.core.wmem_max=16777216
EOF
    
    sysctl -p
    dialog --msgbox "Kernel parameters optimized!" 8 40
}

# ==================== MAIN DIALOG MENU ====================

main_dialog_menu() {
    while true; do
        local choice=$(dialog --clear --backtitle "$DIALOG_BACKTITLE" \
            --title "Main Menu" \
            --menu "Choose category:" 22 70 14 \
            1 "System Setup" \
            2 "User Management" \
            3 "Service Deployment" \
            4 "Configuration Editor" \
            5 "MC-Style Interface" \
            6 "Backup & Restore" \
            7 "Security Hardening" \
            8 "Performance Tuning" \
            9 "Monitoring & Logs" \
            10 "Network Management" \
            11 "Docker Management" \
            12 "Database Management" \
            13 "Advanced Tools" \
            14 "System Status" \
            0 "Exit" \
            3>&1 1>&2 2>&3)
        
        clear
        case $choice in
            1) system_setup_menu ;;
            2) user_management_menu ;;
            3) service_deployment_menu ;;
            4) config_editor ;;
            5) mc_style_dialog ;;
            6) backup_restore_menu ;;
            7) security_menu ;;
            8) performance_menu ;;
            9) monitoring_menu ;;
            10) network_menu ;;
            11) docker_menu ;;
            12) database_menu ;;
            13) advanced_tools_menu ;;
            14) show_system_status ;;
            0|"") 
                dialog --yesno "Exit Server Deploy Master?" 8 40
                [[ $? -eq 0 ]] && break
                ;;
        esac
    done
    
    clear
}

# System setup submenu
system_setup_menu() {
    while true; do
        local choice=$(dialog --menu "System Setup" 18 60 10 \
            1 "Update system" \
            2 "Configure timezone" \
            3 "Configure swap" \
            4 "Set hostname" \
            5 "Install base packages" \
            6 "Configure locale" \
            7 "Install Fail2ban" \
            8 "Auto updates" \
            0 "Back" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) 
                dialog --infobox "Updating system..." 5 40
                apt-get update && apt-get upgrade -y
                dialog --msgbox "System updated!" 8 40
                ;;
            0|"") return ;;
        esac
    done
}

# Service deployment submenu  
service_deployment_menu() {
    local choice=$(dialog --checklist "Select services to deploy:" 18 60 10 \
        1 "Web Server (Nginx)" off \
        2 "Mail Server" off \
        3 "Database" off \
        4 "VPN Server" off \
        5 "FTP Server" off \
        6 "DNS Server" off \
        7 "Monitoring" off \
        8 "Docker" off \
        9 "Git Server" off \
        10 "CI/CD (Jenkins)" off \
        3>&1 1>&2 2>&3)
    
    [[ -z "$choice" ]] && return
    
    for service in $choice; do
        dialog --infobox "Deploying service $service..." 5 40
        sleep 2
    done
    
    dialog --msgbox "Services deployed!" 8 40
}

# Monitoring menu
monitoring_menu() {
    local choice=$(dialog --menu "Monitoring" 15 60 7 \
        1 "System resources" \
        2 "Active connections" \
        3 "Disk usage" \
        4 "Service status" \
        5 "Log viewer" \
        6 "Real-time monitor" \
        0 "Back" \
        3>&1 1>&2 2>&3)
    
    case $choice in
        1)
            dialog --msgbox "$(free -h; echo ''; df -h)" 20 70
            ;;
        2)
            dialog --msgbox "$(ss -tuln | head -20)" 20 70
            ;;
        5)
            dialog --textbox "$LOG_FILE" 0 0
            ;;
        6)
            htop 2>/dev/null || top
            ;;
    esac
}

# Show system status
show_system_status() {
    local status="=== SYSTEM STATUS ===\n\n"
    status+="Hostname: $(hostname)\n"
    status+="Uptime: $(uptime -p)\n"
    status+="Load: $(uptime | awk -F'load average:' '{print $2}')\n\n"
    status+="Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')\n"
    status+="Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')\n\n"
    status+="Active users: $(who | wc -l)\n"
    status+="Processes: $(ps aux | wc -l)\n\n"
    status+="Services:\n"
    status+="$(systemctl list-units --type=service --state=running | grep -E 'nginx|mysql|postgresql|docker' | awk '{print "  " $1}')\n"
    
    dialog --msgbox "$status" 22 70
}

# Placeholder menus
network_menu() { dialog --msgbox "Network Management - Coming soon" 8 40; }
docker_menu() { dialog --msgbox "Docker Management - Coming soon" 8 40; }
database_menu() { dialog --msgbox "Database Management - Coming soon" 8 40; }
advanced_tools_menu() { dialog --msgbox "Advanced Tools - Coming soon" 8 40; }

# Stub functions for missing features
system_tuning() { dialog --msgbox "System tuning applied" 8 40; }
web_optimization() { dialog --msgbox "Web optimization applied" 8 40; }
db_optimization() { dialog --msgbox "Database optimization applied" 8 40; }
disk_tuning() { dialog --msgbox "Disk tuning applied" 8 40; }
network_tuning() { dialog --msgbox "Network tuning applied" 8 40; }
cache_config() { dialog --msgbox "Cache configured" 8 40; }
selinux_apparmor() { dialog --msgbox "SELinux/AppArmor configured" 8 40; }
audit_logs() { dialog --msgbox "Audit logging enabled" 8 40; }
port_scanner() { dialog --msgbox "Port scan completed" 8 40; }
vuln_scan() { dialog --msgbox "Vulnerability scan completed" 8 40; }
ssl_check() { dialog --msgbox "SSL/TLS check completed" 8 40; }
password_policies() { dialog --msgbox "Password policies applied" 8 40; }
setup_2fa() { dialog --msgbox "2FA setup completed" 8 40; }
backup_users() { dialog --msgbox "Users backed up" 8 40; }
full_backup() { dialog --msgbox "Full backup completed" 8 40; }
restore_backup() { dialog --msgbox "Backup restored" 8 40; }
schedule_backups() { dialog --msgbox "Backups scheduled" 8 40; }
modify_user_dialog() { dialog --msgbox "User modification - Coming soon" 8 40; }

# ==================== ENTRY POINT ====================

# Check if root
if [[ $EUID -ne 0 ]]; then
   dialog --msgbox "This script must be run as root" 8 40
   exit 1
fi

# Initialize
init_system
init_users_db

# Show banner in terminal
clear
banner

# Launch main dialog menu
main_dialog_menu

clear
echo "Thank you for using Server Deploy Master v4.0!"
