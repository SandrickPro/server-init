#!/usr/bin/env bash
# install_ssh_gate_v2.sh - Enhanced SSH gate environment installer
# With per-user SSH snippets, protocol-based firewall config, and deployment archive
# Usage: sudo bash install_ssh_gate_v2.sh
set -euo pipefail
IFS=$'\n\t'
shopt -s nullglob

# ====== CONFIGURATION ======
BASE="/srv/sys"
HOME_BASE="/srv/home"
DEFAULT_CONF_DIR="$BASE/ssh/def_ssh_conf"
SSHD_SNIPPETS_DIR="$BASE/ssh/sshd_config.d"
DEFAULT_CONF="$DEFAULT_CONF_DIR/default_sshd_config_from_share"
SSHD_DIFF_OUT="$DEFAULT_CONF_DIR/sshd_minimal_diff.patch"

KEY_EXPORT_DIR="$BASE/ssh/key-export"
WIN_CONFIG_FILE="$BASE/ssh/win_config/config"
LOG_ROOT="$BASE/ssh"
SESS_ROOT="$LOG_ROOT/ssh_session"
TMP_ROOT="$BASE/tmp"
ARCHIVE_DIR="$BASE/deploy"

IPTABLES_STORE="$BASE/iptables"
IPV4_DIR="$IPTABLES_STORE/v4"
IPV6_DIR="$IPTABLES_STORE/v6"

SSH_FAIL_DIR="$BASE/ssh/ssh_fail2ban"
SSH_FAIL_HITS="$SSH_FAIL_DIR/hits"
SSH_FAIL_LEVEL="$SSH_FAIL_DIR/level"
SSH_BAN_LOG="$SSH_FAIL_DIR/bans.log"
SSH_WHITE_EVENTS="$SSH_FAIL_DIR/white_events.log"

AUDIT_SRC_DIR="$BASE/audit/rules.d"
AUDIT_SRC_FILE="$AUDIT_SRC_DIR/99-ssh-audit.rules"
AUDIT_RULES_PATH="/etc/audit/rules.d/99-ssh-audit.rules"

SYSTEMD_SRC_DIR="$BASE/systemd/system"
SYSTEMD_DST_DIR="/etc/systemd/system"

SUDOERS_SRC="$BASE/sudoers.d"
SUDOERS_DST="/etc/sudoers.d"

PROFILED_SRC="$BASE/etc/profile.d"
PROFILED_DST="/etc/profile.d"

IPSET_BAN="ssh_ban"
IPSET_WHITE="ssh_white"

BAN_DURATIONS=(30 180 900 1800 3600 10800 21600 43200 86400)
HOSTNAME_FQDN="$(hostname -f 2>/dev/null || hostname)"
SERVER_IP="$(hostname -I 2>/dev/null | awk '{print $1}' || echo '127.0.0.1')"

# All available roles
ALL_ROLES=(admin advanced user guest sandbox-isolated fake-admin backup-ops net-ops monitoring readonly-audit mail-admin web-admin db-admin custom-minimal)

# Protocol port mappings
declare -A PROTOCOL_PORTS
PROTOCOL_PORTS[web]="80 443"
PROTOCOL_PORTS[mail]="25 110 143 465 587 993 995"
PROTOCOL_PORTS[dns]="53"
PROTOCOL_PORTS[ftp]="20 21 989 990"
PROTOCOL_PORTS[db]="3306 5432 27017 6379"
PROTOCOL_PORTS[vpn]="1194 51820"
PROTOCOL_PORTS[ntp]="123"
PROTOCOL_PORTS[snmp]="161 162"
PROTOCOL_PORTS[ldap]="389 636"
PROTOCOL_PORTS[nfs]="111 2049"
PROTOCOL_PORTS[monitoring]="8080 8443 9090"

# Tracking arrays
declare -a CREATED_USERS=()
declare -a CREATED_PROTOCOLS=()
declare -a CREATED_PORTS=()
declare -a SSH_USERS=()
DEPLOYED_USERS_FILE="$ARCHIVE_DIR/deployed_users.txt"

# ====== COLORS & LOGGING ======
info(){ printf "\e[1;32m[i]\e[0m %s\n" "$*"; }
warn(){ printf "\e[1;33m[!]\e[0m %s\n" "$*"; }
err(){ printf "\e[1;31m[ERR]\e[0m %s\n" "$*"; exit 1; }
debug(){ if [[ "${DEBUG:-0}" == "1" ]]; then printf "\e[1;34m[D]\e[0m %s\n" "$*"; fi; }

if [[ $(id -u) -ne 0 ]]; then err "Run as root"; fi

# ====== DATE & SID HELPERS ======
date_label(){ date +"%d-%b'%y" | tr 'a-z' 'A-Z'; }
time_HM_dot(){ date +'%H.%M'; }
time_HM(){ date +'%H:%M'; }
sid_build(){
  local ip="$1" user="$2" start="$3"
  local ip_s="${ip//./-}"
  local d="$(date +"%d-%b'%y" | tr 'a-z' 'A-Z')"
  printf "%s_%s_%s_%s" "$ip_s" "$user" "$d" "${start//:/.}"
}
session_filename(){
  local sid="$1" user="$2" start="$3" end="$4"
  printf "%s_%s@%s=%s-%s.log" "$sid" "$user" "$(date_label)" "$start" "$end"
}
tmp_filename(){
  local user="$1" start="$2" sid="$3"
  printf "%s@%s_%s_%s.tmp" "$user" "$(date_label)" "$start" "$sid"
}
format_banlog_date(){ date +"%H:%M:%S -%d-%b'%y"; }

# ====== DIRECTORY PREPARATION ======
info "Creating directories under /srv..."
mkdir -p "$DEFAULT_CONF_DIR" "$SSHD_SNIPPETS_DIR" "$KEY_EXPORT_DIR" "$(dirname "$WIN_CONFIG_FILE")" "$LOG_ROOT" "$SESS_ROOT" "$TMP_ROOT" "$IPTABLES_STORE" "$IPV4_DIR" "$IPV6_DIR" "$SSH_FAIL_HITS" "$SSH_FAIL_LEVEL" "$AUDIT_SRC_DIR" "$SYSTEMD_SRC_DIR" "$SUDOERS_SRC" "$PROFILED_SRC" "$HOME_BASE" "$ARCHIVE_DIR"
chmod 750 "$DEFAULT_CONF_DIR" || true

backup_auth_files(){
  local stamp
  stamp="$(date +'%Y%m%d_%H%M%S')"
  mkdir -p "$BASE/backup_passwd"
  cp -a /etc/passwd /etc/shadow /etc/group /etc/gshadow "$BASE/backup_passwd/passwd.$stamp" || true
  info "Auth files backed up to $BASE/backup_passwd/passwd.$stamp"
}
backup_auth_files

# ====== DEFAULT SSH CONFIG TEMPLATE ======
if [[ ! -f "$DEFAULT_CONF" ]]; then
  if [[ -f /usr/share/openssh/sshd_config ]]; then
    awk '{print "#"$0}' /usr/share/openssh/sshd_config > "$DEFAULT_CONF"
  else
    awk '{print "#"$0}' /etc/ssh/sshd_config > "$DEFAULT_CONF"
  fi
  printf "\nInclude %s/*.conf\n" "$SSHD_SNIPPETS_DIR" >> "$DEFAULT_CONF"
  info "Created default sshd_config template at $DEFAULT_CONF"
else
  info "Default sshd_config template exists"
fi

# ====== SNIPPET MANAGEMENT ======
# Write pair: one active .conf and one inactive .conf.inactive
write_snippet_pair(){
  local name="$1" active="$2" inactive="$3"
  printf "%b\n" "$active" > "$SSHD_SNIPPETS_DIR/${name}.conf"
  printf "%b\n" "$inactive" > "$SSHD_SNIPPETS_DIR/${name}.conf.inactive"
  chmod 644 "$SSHD_SNIPPETS_DIR/${name}.conf" "$SSHD_SNIPPETS_DIR/${name}.conf.inactive"
  debug "Snippet pair: $name"
}

# Write per-user SSH snippet (e.g., 10-user_main.conf)
write_user_ssh_snippet(){
  local user="$1" shell="$2"
  local snippet_name="10-user_${user}"
  local active="# User $user\\nMatch User ${user}\\n  ForceCommand /srv/home/${user}/local/bin/gate_login_wrapper\\n  X11Forwarding no\\n  AllowAgentForwarding no"
  local inactive="# User $user (disabled)\\nMatch User ${user}\\n  # ForceCommand disabled"
  write_snippet_pair "$snippet_name" "$active" "$inactive"
  info "Created SSH snippet for user $user"
}

# Core system snippets
write_core_snippets(){
  write_snippet_pair "00-PermitRootLogin" "PermitRootLogin no" "PermitRootLogin yes"
  write_snippet_pair "01-PasswordAuthentication" "PasswordAuthentication no" "PasswordAuthentication yes"
  write_snippet_pair "02-PubkeyAuthentication" "PubkeyAuthentication yes\\nAuthorizedKeysFile .ssh/authorized_keys" "PubkeyAuthentication no"
  write_snippet_pair "03-UsePAM" "UsePAM yes" "UsePAM no"
  write_snippet_pair "04-ClientAlive" "ClientAliveInterval 3600\\nClientAliveCountMax 3" "ClientAliveInterval 0\\nClientAliveCountMax 0"
  write_snippet_pair "05-AllowTcpForwarding" "AllowTcpForwarding no" "AllowTcpForwarding yes"
  write_snippet_pair "06-Ciphers" "Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com" "Ciphers aes128-ctr,aes256-ctr"
  write_snippet_pair "07-KexAlgorithms" "KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org" "KexAlgorithms diffie-hellman-group14-sha1"
  write_snippet_pair "08-HostKeys" "HostKey /etc/ssh/ssh_host_ed25519_key\\nHostKey /etc/ssh/ssh_host_rsa_key" "HostKey /etc/ssh/ssh_host_dsa_key"
  info "Core SSH snippets written"
}
write_core_snippets

# Symlink snippets directory
mkdir -p /etc/ssh/sshd_config.d
ln -sfn "$SSHD_SNIPPETS_DIR" /etc/ssh/sshd_config.d
info "Linked snippets to /etc/ssh/sshd_config.d"

# ====== IPTABLES MANAGEMENT ======
# Helper to write non-duplicating iptables rules
write_merged_iptables_file(){
  local v4_file="$IPV4_DIR/merged.v4"
  local v6_file="$IPV6_DIR/merged.v6"
  local temp_v4="/tmp/iptables_merged_v4.$$"
  local temp_v6="/tmp/iptables_merged_v6.$$"
  
  # Collect all active v4 rules (excluding duplicates and inactives)
  {
    echo "*filter"
    echo ":INPUT DROP [0:0]"
    echo ":FORWARD ACCEPT [0:0]"
    echo ":OUTPUT ACCEPT [0:0]"
    echo "-A INPUT -i lo -j ACCEPT"
    echo "-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT"
    
    # Collect unique ports from active .v4 files
    local all_ports=()
    for f in "$IPV4_DIR"/*.v4; do
      [[ -f "$f" ]] || continue
      [[ "$f" == *.inactive ]] && continue
      [[ "$f" == *merged* ]] && continue
      # Extract port from file
      local port_line
      port_line=$(grep -E "^\-A INPUT.*--dport" "$f" | head -1 || true)
      if [[ -n "$port_line" ]]; then
        # Only add if not already present
        if ! grep -q "$port_line" "$temp_v4" 2>/dev/null; then
          echo "$port_line"
        fi
      fi
    done
    echo "COMMIT"
  } > "$temp_v4"
  
  # Collect all active v6 rules
  {
    echo "*filter"
    echo ":INPUT DROP [0:0]"
    echo ":FORWARD ACCEPT [0:0]"
    echo ":OUTPUT ACCEPT [0:0]"
    echo "-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT"
    
    local all_ports=()
    for f in "$IPV6_DIR"/*.v6; do
      [[ -f "$f" ]] || continue
      [[ "$f" == *.inactive ]] && continue
      [[ "$f" == *merged* ]] && continue
      local port_line
      port_line=$(grep -E "^\-A INPUT.*--dport" "$f" | head -1 || true)
      if [[ -n "$port_line" ]]; then
        if ! grep -q "$port_line" "$temp_v6" 2>/dev/null; then
          echo "$port_line"
        fi
      fi
    done
    echo "COMMIT"
  } > "$temp_v6"
  
  mv "$temp_v4" "$v4_file"
  mv "$temp_v6" "$v6_file"
  chmod 644 "$v4_file" "$v6_file"
  info "Merged deduped iptables files created"
}

# Quick add port to iptables
add_port_to_iptables(){
  local port="$1" proto="${2:-tcp}"
  CREATED_PORTS+=("$port")
  
  # Just write to merged file - will rebuild at end
  debug "Added port $port to tracking"
}

# Apply iptables rules
apply_iptables_rules(){
  info "Applying iptables rules..."
  write_merged_iptables_file
  
  if command -v iptables >/dev/null 2>&1; then
    local tmp="/tmp/iptables_apply.$$"
    cat "$IPV4_DIR/merged.v4" > "$tmp"
    iptables-restore < "$tmp" || warn "iptables-restore failed"
    rm -f "$tmp"
    save_current_iptables
  fi
}

save_current_iptables(){
  mkdir -p "$IPV4_DIR" "$IPV6_DIR"
  iptables-save > "$IPV4_DIR/rules.v4" || warn "iptables-save failed"
  ip6tables-save > "$IPV6_DIR/rules.v6" 2>/dev/null || true
  info "Saved current iptables state"
}

ensure_ipset(){
  if ! command -v ipset >/dev/null 2>&1; then warn "ipset not installed"; return 1; fi
  ipset create "$IPSET_BAN" hash:ip timeout 0 -exist 2>/dev/null || true
  ipset create "$IPSET_WHITE" hash:ip timeout $((30*24*3600)) -exist 2>/dev/null || true
  info "ipset sets ready"
  return 0
}

# ====== AUDITD RULES ======
install_auditd_rules(){
  mkdir -p "$AUDIT_SRC_DIR"
  cat > "$AUDIT_SRC_FILE" <<'RULES'
# auditd rules for SSH and critical files
-a always,exit -F arch=b64 -S execve -F auid>=1000 -F auid!=4294967295 -k user-exec
-a always,exit -F arch=b32 -S execve -F auid>=1000 -F auid!=4294967295 -k user-exec
-w /usr/bin/sudo -p x -k sudo-exec
-w /bin/su -p x -k su-exec
-w /etc/ssh/sshd_config -p wa -k sshd-config
-w /srv/sys/ssh/sshd_config.d -p wa -k sshd-snippets
-w /etc/passwd -p wa -k passwd-file
-w /etc/shadow -p wa -k shadow-file
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d -p wa -k sudoers-dir
RULES
  chmod 644 "$AUDIT_SRC_FILE"
  mkdir -p "$(dirname "$AUDIT_RULES_PATH")"
  ln -sf "$AUDIT_SRC_FILE" "$AUDIT_RULES_PATH"
  if command -v augenrules >/dev/null 2>&1; then augenrules --load 2>/dev/null || true; fi
  systemctl restart auditd 2>/dev/null || true
  info "Auditd rules installed"
}

# ====== ROLES & RBASH ======
declare -A ROLE_CMDS
ROLE_CMDS[admin]="/bin/ls /bin/ps /bin/df /bin/du /usr/bin/top /usr/bin/ss /sbin/ip /usr/bin/curl /usr/bin/wget /usr/bin/systemctl /usr/bin/rsync /usr/bin/tar /usr/bin/gzip /usr/bin/ssh /usr/bin/ssh-keygen /usr/bin/journalctl"
ROLE_CMDS[advanced]="/bin/ls /bin/ps /bin/df /usr/bin/top /usr/bin/ss /usr/bin/curl /usr/bin/wget /usr/bin/journalctl /usr/bin/tail /usr/bin/grep"
ROLE_CMDS[user]="/bin/ls /bin/ps /bin/df /bin/du /usr/bin/tail /usr/bin/grep /usr/bin/curl /usr/bin/wget /bin/cat"
ROLE_CMDS[guest]="/bin/ls /bin/cat /usr/bin/true /usr/bin/whoami /bin/pwd"
ROLE_CMDS[sandbox-isolated]=""
ROLE_CMDS[fake-admin]="/bin/ls /bin/ps /bin/df /usr/bin/top"
ROLE_CMDS[backup-ops]="/usr/bin/rsync /usr/bin/tar /usr/bin/gzip /bin/ls /bin/ps /usr/bin/ssh"
ROLE_CMDS[net-ops]="/sbin/ip /usr/bin/ss /usr/bin/curl /usr/bin/wget /usr/bin/ssh /usr/bin/ping /bin/traceroute"
ROLE_CMDS[monitoring]="/usr/bin/top /usr/bin/ss /bin/ps /bin/df /usr/bin/curl /usr/bin/journalctl"
ROLE_CMDS[readonly-audit]="/usr/bin/journalctl /usr/bin/auditctl /usr/bin/aureport /bin/cat /usr/bin/grep"
ROLE_CMDS[mail-admin]="/usr/bin/curl /usr/bin/wget /bin/ps /usr/bin/journalctl /usr/bin/tail /usr/bin/grep"
ROLE_CMDS[web-admin]="/bin/ls /bin/ps /usr/bin/curl /usr/bin/wget /usr/bin/journalctl /usr/bin/tail"
ROLE_CMDS[db-admin]="/bin/ps /bin/df /usr/bin/ss /usr/bin/tail /usr/bin/grep /usr/bin/curl"
ROLE_CMDS[custom-minimal]="/bin/ls /usr/bin/whoami"

install_role_rbin(){
  local user="$1" role="$2" base rbin cmd
  base="$HOME_BASE/$user"
  rbin="$base/local/rbin"
  mkdir -p "$rbin"
  chown root:root "$base/local" 2>/dev/null || true
  chmod 755 "$rbin"
  
  if [[ "$role" == "sandbox-isolated" ]]; then
    cat > "$rbin/hello" <<'SH'
#!/usr/bin/env bash
echo "Sandbox: limited environment"
SH
    chmod 755 "$rbin/hello"
    info "Installed sandbox for $user"
    return
  fi
  
  local cmds="${ROLE_CMDS[$role]:-}"
  for cmd in $cmds; do
    if [[ -x "$cmd" ]]; then
      ln -sf "$cmd" "$rbin/$(basename "$cmd")" || true
    fi
  done
  
  cat > "$rbin/last-login" <<'SH'
#!/usr/bin/env bash
last -n 2 -i "$(whoami)" 2>/dev/null | sed -n '2p' || echo "first login"
SH
  chmod 755 "$rbin/last-login"
  info "Installed rbin for $user (role=$role)"
}

ensure_user_dirs(){
  local user="$1"
  mkdir -p "$HOME_BASE/$user" "$HOME_BASE/$user/local" "$HOME_BASE/$user/local/bin" "$HOME_BASE/$user/local/rbin" "$HOME_BASE/$user/.ssh"
  chown -R "$user:$user" "$HOME_BASE/$user" 2>/dev/null || true
  chmod 755 "$HOME_BASE/$user/local" || true
}

# ====== GATE HELPERS ======
install_gate_helpers(){
  local gate="$1"
  ensure_user_dirs "$gate"
  mkdir -p "$HOME_BASE/$gate/local/bin"
  chown root:root "$HOME_BASE/$gate/local" || true
  chmod 755 "$HOME_BASE/$gate/local"

  # enter_as_user.sh
  cat > "$HOME_BASE/$gate/local/bin/enter_as_user.sh" <<'BASH'
#!/usr/bin/env bash
TARGET="$1"
SID="${SID:-unknown}"
DATE_LABEL="$(date +"%d-%b'%y" | tr 'a-z' 'A-Z')"
START_TIME="$(date +'%H:%M')"
TMP_HIST="/srv/sys/ssh/.gate_session_hist.${SID}.${TARGET}.$$"
mkdir -p "/srv/sys/ssh/ssh_session/${DATE_LABEL}"
touch "$TMP_HIST"; chmod 600 "$TMP_HIST"
echo "SID=${SID} GATE=${SUDO_USER:-$USER} TARGET=${TARGET} FROM=${SSH_CONNECTION:-unknown} START=$(date '+%Y-%m-%d %H:%M:%S')" >> "$TMP_HIST"
trap 'lastcmd=$(history 1 | sed "s/^[ ]*[0-9]*[ ]*//"); printf "%s\t%s\t%s\t%s\n" "$(date "+%H:%M:%S")" "$(whoami)" "$TARGET" "$lastcmd" >> "'"$TMP_HIST"'"' DEBUG
exec sudo -u "$TARGET" -i
BASH
  chmod 750 "$HOME_BASE/$gate/local/bin/enter_as_user.sh"
  chown root:root "$HOME_BASE/$gate/local/bin/enter_as_user.sh"

  # gate_login_wrapper (ForceCommand)
  cat > "$HOME_BASE/$gate/local/bin/gate_login_wrapper" <<'BASH'
#!/usr/bin/env bash
REMOTE_IP="$(echo "${SSH_CONNECTION:-}" | awk '{print $1}')"
GATE_USER="${USER:-gate}"
START_TIME="$(date +'%H:%M')"
SID="$(printf "%s_%s_%s_%s" "${REMOTE_IP//./-}" "${GATE_USER}" "$(date +"%d-%b'%y" | tr 'a-z' 'A-Z')" "${START_TIME//:/.}")"
TMP_HIST="/srv/sys/ssh/.gate_session_hist.${SID}.$$"
DATE_LABEL="$(date +"%d-%b'%y" | tr 'a-z' 'A-Z')"
mkdir -p "/srv/sys/ssh/ssh_session/${DATE_LABEL}"
touch "$TMP_HIST"; chmod 600 "$TMP_HIST"
echo "SID=${SID} USER=${USER} FROM=${REMOTE_IP} START=$(date '+%Y-%m-%d %H:%M:%S')" >> "$TMP_HIST"
export HISTFILE="$TMP_HIST"; export HISTSIZE=20000; export HISTFILESIZE=20000; shopt -s histappend 2>/dev/null || true
RUN_WRAPPER="/srv/home/${USER}/.run_rb_${SID}.sh"
cat > "$RUN_WRAPPER" <<'SH'
#!/usr/bin/env bash
export HISTFILE="'"$TMP_HIST"'"
export HISTSIZE=20000
export HISTFILESIZE=20000
shopt -s histappend 2>/dev/null || true
trap 'history -a; /srv/home/'"$USER"'/local/bin/gate_finalize_session '"'"$TMP_HIST"'"' '"'"$SID"'"' '"'"$USER"'"' '"'"$START_TIME"'"' EXIT
exec /bin/rbash -l
SH
chmod 700 "$RUN_WRAPPER" || true
chown "$USER":"$USER" "$RUN_WRAPPER" 2>/dev/null || true
exec /bin/su -l "$USER" -c "$RUN_WRAPPER"
BASH
  chmod 750 "$HOME_BASE/$gate/local/bin/gate_login_wrapper"
  chown root:root "$HOME_BASE/$gate/local/bin/gate_login_wrapper"

  # gate_finalize_session
  cat > "$HOME_BASE/$gate/local/bin/gate_finalize_session" <<'BASH'
#!/usr/bin/env bash
TMP_HIST="$1"; SID="$2"; USERX="$3"; START_TIME="$4"
END_TIME="$(date +'%H:%M')"
DATE_LABEL="$(date +"%d-%b'%y" | tr 'a-z' 'A-Z')"
FINAL_DIR="/srv/sys/ssh/ssh_session/$DATE_LABEL"
mkdir -p "$FINAL_DIR"
FINAL_FILE="$FINAL_DIR/${SID}_${USERX}@${DATE_LABEL}=${START_TIME}-${END_TIME}.log"
if [[ -f "$TMP_HIST" ]]; then
  echo "=== SID=$SID USER=$USERX START=$START_TIME END=$END_TIME ===" >> "$FINAL_FILE"
  cat "$TMP_HIST" >> "$FINAL_FILE"
  rm -f "$TMP_HIST"
fi
exit 0
BASH
  chmod 750 "$HOME_BASE/$gate/local/bin/gate_finalize_session"
  chown root:root "$HOME_BASE/$gate/local/bin/gate_finalize_session"

  info "Gate helpers installed for $gate"
}

# Add user switch command (2<target>) to gate's rbin
add_gate_switch_cmd(){
  local gate="$1" target="$2"
  mkdir -p "$HOME_BASE/$gate/local/rbin"
  cat > "$HOME_BASE/$gate/local/rbin/2${target}" <<EOF
#!/usr/bin/env bash
exec /srv/home/${gate}/local/bin/enter_as_user.sh ${target}
EOF
  chmod 755 "$HOME_BASE/$gate/local/rbin/2${target}"
  chown root:root "$HOME_BASE/$gate/local/rbin/2${target}"
  debug "Created gate switch 2${target}"
}

# Remove user switch command when user deleted
remove_gate_switch_cmd(){
  local gate="$1" target="$2"
  rm -f "$HOME_BASE/$gate/local/rbin/2${target}" || true
  debug "Removed gate switch 2${target}"
}

# Check for deleted users and clean up
cleanup_deleted_users(){
  local gate="$1"
  local rbin_dir="$HOME_BASE/$gate/local/rbin"
  [[ -d "$rbin_dir" ]] || return 0
  
  for symlink in "$rbin_dir"/2*; do
    [[ -L "$symlink" ]] || continue
    local cmd_user=$(basename "$symlink" | sed 's/^2//')
    if ! id "$cmd_user" &>/dev/null; then
      rm -f "$symlink"
      warn "Cleaned up deleted user switch for $cmd_user"
    fi
  done
}

# ====== SSH KEY GENERATION ======
generate_and_install_key(){
  local user="$1"
  local outdir="$KEY_EXPORT_DIR/$user"
  mkdir -p "$outdir"
  
  local ip_label="${SERVER_IP//./-}"
  local date_label=$(date +"%d_%b" | tr 'a-z' 'A-Z')
  local name="${user}@server-${date_label}-${ip_label}"
  
  ssh-keygen -t ed25519 -C "${user}@${HOSTNAME_FQDN}" -f "$outdir/${name}" -N "" -q || true
  
  mkdir -p "$HOME_BASE/$user/.ssh"
  cat "$outdir/${name}.pub" >> "$HOME_BASE/$user/.ssh/authorized_keys" 2>/dev/null || true
  chown -R "$user:$user" "$HOME_BASE/$user" 2>/dev/null || true
  chmod 700 "$HOME_BASE/$user/.ssh" || true
  chmod 600 "$HOME_BASE/$user/.ssh/authorized_keys" || true
  
  SSH_USERS+=("$user")
  info "Generated SSH key for $user: $outdir/${name}"
}

# Update Windows SSH config
update_windows_ssh_config(){
  mkdir -p "$(dirname "$WIN_CONFIG_FILE")"
  {
    echo "# Generated at $(date)"
    echo "# Windows SSH Config for deployment"
    echo ""
    for user_dir in "$KEY_EXPORT_DIR"/*; do
      [[ -d "$user_dir" ]] || continue
      local user="$(basename "$user_dir")"
      local priv_key=$(ls "$user_dir" 2>/dev/null | grep -v '\.pub$' | head -n1 || true)
      [[ -n "$priv_key" ]] || continue
      
      cat <<EOF

Host ${user}
    HostName ${SERVER_IP}
    Port ${SSH_PORT:-22}
    User ${user}
    ProxyJump ${GATE_USER:-gate}@${SERVER_IP}
    IdentityFile C:\\Users\\<your_username>\\.ssh\\${priv_key}
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new

EOF
    done
  } > "$WIN_CONFIG_FILE"
  info "Windows SSH config updated: $WIN_CONFIG_FILE"
}

# ====== MOTD & BANNERS ======
install_gate_motd(){
  mkdir -p "$PROFILED_SRC"
  cat > "$PROFILED_SRC/gate-banner.sh" <<'BASH'
#!/usr/bin/env bash
if [[ "$USER" == "${GATE_USER:-gate}" ]]; then
  cat <<'BANNER'
╔════════════════════════════════════════════════════════════════╗
║         SSH GATE - Restricted Access Environment              ║
║                                                                ║
║  You are in a restricted shell (rbash)                         ║
║  Available commands shown as 2<username> switches              ║
║  Type: 2<user> to switch to that user (if authorized)          ║
╚════════════════════════════════════════════════════════════════╝
BANNER
  echo ""
  echo "Date : $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Host : $(hostname)    IP: $(hostname -I | awk '{print $1}')"
  echo "Uptime: $(uptime -p 2>/dev/null || uptime)"
  echo ""
fi
BASH
  chmod 755 "$PROFILED_SRC/gate-banner.sh"
  ln -sf "$PROFILED_SRC/gate-banner.sh" "$PROFILED_DST/gate-banner.sh"
  info "Installed gate motd banner"
}

# ====== SYSTEMD UNITS ======
install_systemd_units(){
  mkdir -p "$SYSTEMD_SRC_DIR"
  
  # Firewall restore on boot
  cat > "$SYSTEMD_SRC_DIR/iptables-restore.service" <<'UNIT'
[Unit]
Description=Restore iptables firewall from /srv/sys/iptables
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/restore_srv_iptables.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
UNIT

  mkdir -p /usr/local/sbin
  cat > /usr/local/sbin/restore_srv_iptables.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
v4="/srv/sys/iptables/v4/merged.v4"
v6="/srv/sys/iptables/v6/merged.v6"
[[ -f "$v4" ]] && iptables-restore < "$v4" || true
[[ -f "$v6" ]] && ip6tables-restore < "$v6" 2>/dev/null || true
echo "Iptables restored"
SH
  chmod 755 /usr/local/sbin/restore_srv_iptables.sh
  
  # Session maintenance timer
  cat > "$SYSTEMD_SRC_DIR/session-maintenance.service" <<'UNIT'
[Unit]
Description=SSH session maintenance
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/maintain_sessions.sh
UNIT

  cat > "$SYSTEMD_SRC_DIR/session-maintenance.timer" <<'UNIT'
[Unit]
Description=Daily session maintenance

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
UNIT

  mkdir -p "$BASE/scripts"
  cat > /usr/local/sbin/maintain_sessions.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
SESS_ROOT="/srv/sys/ssh/ssh_session"
find "$SESS_ROOT" -type f -name '*.log' -mtime +30 -exec gzip -9 {} \; 2>/dev/null || true
find "$SESS_ROOT" -type f -name '*.tmp' -mtime +1 -delete 2>/dev/null || true
echo "Sessions maintenance completed"
SH
  chmod 755 /usr/local/sbin/maintain_sessions.sh
  
  # Link units
  for f in "$SYSTEMD_SRC_DIR"/*; do
    [[ -f "$f" ]] || continue
    ln -sf "$f" "$SYSTEMD_DST_DIR/$(basename "$f")"
  done
  systemctl daemon-reload || true
  systemctl enable --now iptables-restore.service 2>/dev/null || true
  systemctl enable --now session-maintenance.timer 2>/dev/null || true
  
  info "Systemd units installed"
}

# ====== SSHD CONFIG APPLICATION ======
apply_sshd_and_reload(){
  info "Applying SSHD configuration..."
  
  # Copy base config
  cp -f "$DEFAULT_CONF" /etc/ssh/sshd_config
  
  # Validate
  if sshd -t 2>/dev/null; then
    info "SSHD configuration valid"
    systemctl reload sshd 2>/dev/null || systemctl restart sshd 2>/dev/null || warn "Failed to reload sshd"
    cp -f /etc/ssh/sshd_config "$BASE/ssh/sshd_config.$(date +%s).bak" || true
  else
    warn "SSHD configuration test failed"
    if [[ -f "$BASE/ssh/sshd_config.1.bak" ]]; then
      warn "Restoring last good config"
      cp -f "$BASE/ssh/sshd_config.1.bak" /etc/ssh/sshd_config
      systemctl restart sshd 2>/dev/null || warn "Failed to restart sshd"
    else
      warn "No backup available; manual intervention needed"
    fi
    return 1
  fi
  return 0
}

# ====== DEPLOYMENT ARCHIVE ======
create_deployment_archive(){
  info "Creating deployment archive..."
  
  local archive_name="ssh-gate-deploy-$(date +%Y%m%d_%H%M%S).tar.gz"
  local archive_path="$ARCHIVE_DIR/$archive_name"
  local work_dir="/tmp/ssh_deploy_$$"
  
  mkdir -p "$work_dir/keys" "$work_dir/configs" "$work_dir/docs"
  
  # Copy keys
  if [[ -d "$KEY_EXPORT_DIR" ]]; then
    cp -r "$KEY_EXPORT_DIR"/* "$work_dir/keys/" 2>/dev/null || true
  fi
  
  # Copy configs
  cp "$WIN_CONFIG_FILE" "$work_dir/configs/ssh_config" 2>/dev/null || true
  cp -r "$SSHD_SNIPPETS_DIR"/*.conf "$work_dir/configs/" 2>/dev/null || true
  
  # Create deployment info file
  create_deployment_info > "$work_dir/docs/DEPLOYMENT_INFO.txt"
  
  # Create SCP instructions
  cat > "$work_dir/docs/SCP_INSTRUCTIONS.txt" <<'SCPEOF'
=== DOWNLOAD SSH KEYS AND CONFIG ===

Run these commands on your LOCAL machine:

1. Download archive:
   scp -P <SSH_PORT> <gate_user>@<server_ip>:/srv/sys/deploy/<latest_archive.tar.gz> ./

2. Extract:
   tar -xzf ssh-gate-deploy-*.tar.gz

3. Keys are in ./keys/ directory
4. Configs are in ./configs/ directory

For Windows users (using WSL or Git Bash):
   
   scp -P 22 gate@<server_ip>:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./
   tar -xzf ssh-gate-deploy-*.tar.gz

=== SETUP SSH KEY ON YOUR MACHINE ===

1. Create .ssh directory if needed:
   mkdir -p ~/.ssh && chmod 700 ~/.ssh

2. Copy your private key:
   cp keys/<your_key_file> ~/.ssh/
   chmod 600 ~/.ssh/<your_key_file>

3. Add to ssh config:
   cat configs/ssh_config >> ~/.ssh/config

SCPEOF

  # Create tar archive
  tar -czf "$archive_path" -C "$work_dir" . 2>/dev/null || true
  
  # Cleanup
  rm -rf "$work_dir"
  
  if [[ -f "$archive_path" ]]; then
    chmod 644 "$archive_path"
    local size=$(du -h "$archive_path" | awk '{print $1}')
    info "Archive created: $archive_name ($size)"
    echo "$archive_path"
  else
    warn "Failed to create archive"
    return 1
  fi
}

# ====== DEPLOYMENT INFO ======
create_deployment_info(){
  cat <<EOF
╔════════════════════════════════════════════════════════════════╗
║          SSH GATE DEPLOYMENT INFORMATION                       ║
║          Generated: $(date '+%Y-%m-%d %H:%M:%S')                     ║
╚════════════════════════════════════════════════════════════════╝

SERVER INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hostname:      $HOSTNAME_FQDN
IP Address:    $SERVER_IP
SSH Port:      ${SSH_PORT:-22}

INFRASTRUCTURE PATHS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Base:          $BASE
Home:          $HOME_BASE
SSH Keys:      $KEY_EXPORT_DIR
SSH Config:    $SSHD_SNIPPETS_DIR
Session Logs:  $SESS_ROOT
Firewall:      $IPTABLES_STORE

PROTOCOLS CONFIGURED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$(printf '%s\n' "${CREATED_PROTOCOLS[@]:-none}")

PORTS OPENED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$(printf '%s ' "${CREATED_PORTS[@]:-none}"; echo)

USERS CREATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$(cat "$DEPLOYED_USERS_FILE" 2>/dev/null || echo "No users recorded")

SSH KEYS AVAILABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$(ls -la "$KEY_EXPORT_DIR" 2>/dev/null | grep -v total | awk '{print "  " $NF}' || echo "  No keys generated")

WINDOWS SSH CONFIG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Location: $WIN_CONFIG_FILE
$(head -20 "$WIN_CONFIG_FILE" 2>/dev/null || echo "Config not yet generated")

NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Download SSH keys from deployment archive
2. Place keys in ~/.ssh/ with proper permissions (chmod 600)
3. Use ssh_config template to configure your SSH client
4. Connect via gate user to access other accounts
5. Check session logs at: $SESS_ROOT

IMPORTANT NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Gate user provides restricted access via rbash
- All SSH access is logged with session IDs (SIDs)
- Session IDs format: IP_user_DATE_TIME
- Firewall automatically restores on boot
- Daily session cleanup runs at 03:00 UTC

EOF
}

# ====== PRINT FINAL SUMMARY ======
print_final_summary(){
  info "═══════════════════════════════════════════════════════════════"
  info "                    INSTALLATION COMPLETE                      "
  info "═══════════════════════════════════════════════════════════════"
  echo ""
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║                    DEPLOYMENT SUMMARY                          ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  
  # Server info
  echo "SERVER INFORMATION:"
  printf "  %-25s %s\n" "Hostname:" "$HOSTNAME_FQDN"
  printf "  %-25s %s\n" "IP Address:" "$SERVER_IP"
  printf "  %-25s %s\n" "SSH Port:" "${SSH_PORT:-22}"
  echo ""
  
  # Protocols
  if [[ ${#CREATED_PROTOCOLS[@]} -gt 0 ]]; then
    echo "PROTOCOLS CONFIGURED:"
    for proto in "${CREATED_PROTOCOLS[@]}"; do
      printf "  ✓ %s\n" "$proto"
    done
    echo ""
  fi
  
  # Ports
  if [[ ${#CREATED_PORTS[@]} -gt 0 ]]; then
    echo "FIREWALL PORTS:"
    echo "  Opened: $(printf '%s ' "${CREATED_PORTS[@]}" | sed 's/ /, /g')"
    echo ""
  fi
  
  # Users
  echo "USERS CREATED:"
  if [[ -f "$DEPLOYED_USERS_FILE" ]]; then
    while IFS='|' read -r user role ssh sudo rbash; do
      printf "  %-15s role=%-20s ssh=%-5s sudo=%-5s rbash=%s\n" "$user" "$role" "$ssh" "$sudo" "$rbash"
    done < "$DEPLOYED_USERS_FILE"
  fi
  echo ""
  
  # SSH Keys
  echo "SSH KEYS:"
  if [[ -d "$KEY_EXPORT_DIR" ]]; then
    for userdir in "$KEY_EXPORT_DIR"/*; do
      [[ -d "$userdir" ]] || continue
      user=$(basename "$userdir")
      keys=$(ls -1 "$userdir" | grep -v '.pub$' | wc -l)
      printf "  %-15s Keys: %d\n" "$user" "$keys"
    done
  fi
  echo ""
  
  # Windows SSH Config
  echo "WINDOWS SSH CONFIG:"
  if [[ -f "$WIN_CONFIG_FILE" ]]; then
    printf "  Location: %s\n" "$WIN_CONFIG_FILE"
    printf "  Size: %s bytes\n" "$(wc -c < "$WIN_CONFIG_FILE")"
  fi
  echo ""
  
  # Paths
  echo "INFRASTRUCTURE PATHS:"
  printf "  %-25s %s\n" "Base:" "$BASE"
  printf "  %-25s %s\n" "Home:" "$HOME_BASE"
  printf "  %-25s %s\n" "SSH Keys:" "$KEY_EXPORT_DIR"
  printf "  %-25s %s\n" "SSH Config:" "$SSHD_SNIPPETS_DIR"
  printf "  %-25s %s\n" "Session Logs:" "$SESS_ROOT"
  printf "  %-25s %s\n" "Firewall:" "$IPTABLES_STORE"
  echo ""
  
  # Download instructions
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║                  DOWNLOAD ARCHIVE                              ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Download deployment archive with SSH keys and configs:"
  echo ""
  local latest_archive=$(ls -t "$ARCHIVE_DIR"/ssh-gate-deploy-*.tar.gz 2>/dev/null | head -1)
  if [[ -n "$latest_archive" ]]; then
    local archive_name=$(basename "$latest_archive")
    local archive_size=$(du -h "$latest_archive" | awk '{print $1}')
    printf "  scp -P %s %s@%s:%s ./\n" "${SSH_PORT:-22}" "${GATE_USER:-gate}" "$SERVER_IP" "$latest_archive"
    echo ""
    printf "  Archive: %s (%s)\n" "$archive_name" "$archive_size"
    echo ""
  fi
  echo "After download, extract and follow SCP_INSTRUCTIONS.txt"
  echo ""
  
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║                  NEXT STEPS                                    ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  echo "  1. Download the deployment archive"
  echo "  2. Extract keys to ~/.ssh/ with chmod 600"
  echo "  3. Configure your SSH client with provided config"
  echo "  4. Connect via gate user to access restricted accounts"
  echo "  5. Monitor logs at: $SESS_ROOT"
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo ""
}

# ====== PROTOCOL SELECTION ======
select_protocols(){
  info "Select network protocols to enable (with 2-second auto-confirm):"
  echo ""
  echo "Available protocols:"
  local idx=1
  local proto_list=()
  for proto in "${!PROTOCOL_PORTS[@]}"; do
    proto_list+=("$proto")
    printf "  %2d) %-15s Ports: %s\n" "$idx" "$proto" "${PROTOCOL_PORTS[$proto]}"
    idx=$((idx+1))
  done
  echo ""
  
  local count=0
  local default_yes=("web" "dns")
  for proto in "${default_yes[@]}"; do
    if [[ -v PROTOCOL_PORTS[$proto] ]]; then
      read -t 2 -p "Enable $proto? [Y/n] (auto: yes in 2s): " -r ans || ans="y"
      ans="${ans:-y}"
      if [[ "$ans" =~ ^[Yy]$ ]]; then
        CREATED_PROTOCOLS+=("$proto")
        for port in ${PROTOCOL_PORTS[$proto]}; do
          add_port_to_iptables "$port"
        done
        count=$((count+1))
      fi
    fi
  done
  
  # Optional additional
  for proto in "${proto_list[@]}"; do
    [[ " ${default_yes[@]} " =~ " ${proto} " ]] && continue
    read -t 2 -p "Enable $proto? [y/N] (auto: no in 2s): " -r ans || ans="n"
    ans="${ans:-n}"
    if [[ "$ans" =~ ^[Yy]$ ]]; then
      CREATED_PROTOCOLS+=("$proto")
      for port in ${PROTOCOL_PORTS[$proto]}; do
        add_port_to_iptables "$port"
      done
      count=$((count+1))
    fi
  done
  
  info "Selected $count protocols"
}

# ====== MAIN INTERACTIVE SETUP ======
main_setup(){
  info "╔════════════════════════════════════════════════════════════════╗"
  info "║     SSH GATE ENVIRONMENT - INTERACTIVE SETUP                   ║"
  info "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  
  # SSH Port
  read -rp "Enter SSH port [22]: " SSH_PORT_IN
  SSH_PORT="${SSH_PORT_IN:-22}"
  add_port_to_iptables "$SSH_PORT"
  info "SSH port: $SSH_PORT"
  write_snippet_pair "ZZ-SSH-Port" "Port ${SSH_PORT}" "Port 22"
  echo ""
  
  # Protocol selection
  select_protocols
  echo ""
  
  # Apply firewall
  info "Applying firewall rules..."
  apply_iptables_rules
  ensure_ipset || warn "ipset unavailable - IP banning disabled"
  echo ""
  
  # Audit rules
  info "Installing audit rules..."
  install_auditd_rules
  echo ""
  
  # Gate user
  read -rp "Enter gate username [gate]: " GATE_USER_IN
  GATE_USER="${GATE_USER_IN:-gate}"
  
  # Main user
  read -rp "Enter main admin username [main]: " MAIN_USER_IN
  MAIN_USER="${MAIN_USER_IN:-main}"
  
  info "Gate: $GATE_USER, Main: $MAIN_USER"
  echo ""
  
  # Create users
  create_or_update_user "$MAIN_USER" "admin" "y" "y" "n" "main"
  create_or_update_user "$GATE_USER" "guest" "n" "n" "y" "gate"
  
  # Gate helpers
  install_gate_helpers "$GATE_USER"
  add_gate_switch_cmd "$GATE_USER" "$MAIN_USER"
  write_user_ssh_snippet "$MAIN_USER" "/bin/bash"
  write_user_ssh_snippet "$GATE_USER" "/bin/rbash"
  
  # Cleanup deleted users
  cleanup_deleted_users "$GATE_USER"
  
  # Additional users loop
  while true; do
    read -rp "Add additional user? [y/N]: " resp
    resp="${resp:-N}"
    if [[ ! "$resp" =~ ^[Yy]$ ]]; then break; fi
    
    read -rp "Username: " UN
    UN="$(echo "$UN" | tr -cd 'A-Za-z0-9._-')"
    [[ -n "$UN" ]] || { warn "Empty username"; continue; }
    
    echo "Roles: $(printf '%d=%s ' "${!ALL_ROLES[@]}" "${ALL_ROLES[@]}")"
    read -rp "Role number [0-$((${#ALL_ROLES[@]}-1))]: " RNUM
    [[ "$RNUM" =~ ^[0-9]+$ ]] || { warn "Invalid"; continue; }
    (( RNUM < 0 || RNUM >= ${#ALL_ROLES[@]} )) && { warn "Out of range"; continue; }
    ROLE="${ALL_ROLES[$RNUM]}"
    
    read -t 2 -p "SSH access via gate? [y/N]: " -r sshok || sshok="n"
    sshok="${sshok:-n}"
    read -t 2 -p "Grant sudo? [y/N]: " -r sudook || sudook="n"
    sudook="${sudook:-n}"
    read -t 2 -p "Use rbash? [y/N]: " -r rbashok || rbashok="n"
    rbashok="${rbashok:-n}"
    
    create_or_update_user "$UN" "$ROLE" "$sshok" "$sudook" "$rbashok" "user"
    
    if [[ "$sshok" =~ ^[Yy]$ ]]; then
      add_gate_switch_cmd "$GATE_USER" "$UN"
      write_user_ssh_snippet "$UN" "/bin/bash"
      read -t 2 -p "Generate SSH key now? [y/N]: " -r gk || gk="n"
      gk="${gk:-n}"
      if [[ "$gk" =~ ^[Yy]$ ]]; then
        generate_and_install_key "$UN"
      fi
    fi
  done
  
  # Generate keys for SSH users
  info "Generating SSH keys for SSH-enabled users..."
  for user in "${SSH_USERS[@]}"; do
    generate_and_install_key "$user"
  done
  echo ""
  
  # MOTD
  install_gate_motd
  
  # Systemd units
  install_systemd_units
  
  # Update Windows config
  update_windows_ssh_config
  
  # Apply SSHD
  echo ""
  read -rp "Apply SSHD configuration? [Y/n]: " APPLY
  APPLY="${APPLY:-Y}"
  if [[ "$APPLY" =~ ^[Yy]$ ]]; then
    apply_sshd_and_reload
  else
    info "SSHD configuration skipped"
  fi
  
  # Create archive
  info "Creating deployment archive..."
  create_deployment_archive
  
  # Print summary
  echo ""
  print_final_summary
}

# ====== CREATE OR UPDATE USER ======
create_or_update_user(){
  local user="$1" role="$2" ssh="$3" sudo="$4" rbash="$5" utype="$6"
  
  if id "$user" &>/dev/null; then
    info "User $user exists; updating..."
  else
    useradd -m -d "$HOME_BASE/$user" -s /bin/bash "$user" || true
    info "Created user $user"
  fi
  
  ensure_user_dirs "$user"
  install_role_rbin "$user" "$role"
  
  if [[ "$rbash" =~ ^[Yy]$ ]]; then
    usermod -s /bin/rbash "$user" || true
  fi
  
  if [[ "$sudo" =~ ^[Yy]$ ]]; then
    printf "%s ALL=(ALL) NOPASSWD:ALL\n" "$user" > "$SUDOERS_SRC/$user"
    ln -sf "$SUDOERS_SRC/$user" "$SUDOERS_DST/$user"
    chmod 440 "$SUDOERS_SRC/$user"
  else
    rm -f "$SUDOERS_SRC/$user" "$SUDOERS_DST/$user" || true
  fi
  
  if [[ "$ssh" =~ ^[Yy]$ ]]; then
    SSH_USERS+=("$user")
    write_user_ssh_snippet "$user" "/bin/bash"
  fi
  
  # Record user
  printf "%s|%s|%s|%s|%s\n" "$user" "$role" "$ssh" "$sudo" "$rbash" >> "$DEPLOYED_USERS_FILE"
  
  info "Configured $user (role=$role, ssh=$ssh, sudo=$sudo, rbash=$rbash)"
}

# ====== ENTRY POINT ======
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main_setup
fi
