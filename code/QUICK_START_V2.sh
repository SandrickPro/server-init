#!/bin/bash
# SSH Gate v2 - Quick Start Installation Guide
# Interactive walkthrough with examples

cat <<'GUIDE'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                     SSH GATE v2 - QUICK START GUIDE                        ║
║                                                                            ║
║              Enhanced SSH environment with per-user config,               ║
║              automatic protocol selection, and deployment archive         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

PREREQUISITES
════════════════════════════════════════════════════════════════════════════

✓ Ubuntu 20.04 LTS, 22.04 LTS, or 24.04 LTS
✓ Root or sudo access
✓ Public IP address for SSH access
✓ 500MB free disk space (for /srv/sys/)

INSTALLATION STEPS
════════════════════════════════════════════════════════════════════════════

STEP 1: DOWNLOAD AND RUN INSTALLER
────────────────────────────────────

On your server:

    sudo bash install_ssh_gate_v2.sh

Expected output:

    [i] Creating directories under /srv...
    [i] Created default sshd_config template at /srv/sys/ssh/def_ssh_conf/default_sshd_config_from_share
    [i] Core SSH snippets written
    [i] Linked snippets to /etc/ssh/sshd_config.d

STEP 2: PROTOCOL SELECTION (2-second auto-confirm)
────────────────────────────────────────────────────

The installer will ask:

    [i] Select network protocols to enable (with 2-second auto-confirm):

    Available protocols:
       1) web             Ports: 80 443
       2) mail            Ports: 25 110 143 465 587 993 995
       3) dns             Ports: 53
       4) ftp             Ports: 20 21 989 990
       5) db              Ports: 3306 5432 27017 6379
       6) vpn             Ports: 1194 51820
       7) ntp             Ports: 123
       8) snmp            Ports: 161 162
       9) ldap            Ports: 389 636
      10) nfs             Ports: 111 2049
      11) monitoring      Ports: 8080 8443 9090

    Enable web? [Y/n] (auto: yes in 2s):

OPTIONS:
  • Press Y or wait 2 seconds → ENABLE protocol
  • Press n immediately → SKIP protocol

RECOMMENDATIONS FOR DIFFERENT SERVERS:

  Web Server:
    - Say YES to: web, dns, monitoring, ntp
    - Say NO to: mail, ftp, ldap, nfs

  Mail Server:
    - Say YES to: mail, dns, monitoring, web
    - Say NO to: ftp, vpn, ldap, nfs

  Database Server:
    - Say YES to: db, dns, monitoring, ntp
    - Say NO to: mail, web, ftp, ldap

  Multi-purpose:
    - Say YES to most (except nfs, ldap unless needed)

STEP 3: USER CONFIGURATION
────────────────────────────

The installer will ask:

    Enter SSH port [22]: 22
    Enter gate username [gate]: gate
    Enter main admin username [main]: main

WHAT THIS DOES:

  • SSH port: Custom SSH port (default 22) for security
  • Gate user: Jump host with restricted rbash shell
  • Main user: Admin with full sudo access and bash

EXAMPLES:

  Example 1 - Default setup:
    Enter SSH port [22]: [press Enter]
    Enter gate username [gate]: [press Enter]
    Enter main admin username [main]: [press Enter]

  Example 2 - Custom port and users:
    Enter SSH port [22]: 2222
    Enter gate username [gate]: proxy
    Enter main admin username [main]: admin

STEP 4: ADDITIONAL USERS (OPTIONAL)
──────────────────────────────────────

The installer will ask:

    Add additional user? [y/N]: y
    Username: mail_admin
    Role number [0-13]: 10
    SSH access via gate? [y/N]: y
    Grant sudo? [y/N]: n
    Use rbash? [y/N]: y
    Generate SSH key now? [y/N]: y

AVAILABLE ROLES:

    0  = admin                  (full system access)
    1  = advanced               (power user tools)
    2  = user                   (basic tools)
    3  = guest                  (minimal tools)
    4  = sandbox-isolated       (synthetic only)
    5  = fake-admin             (appears like admin, limited)
    6  = backup-ops             (rsync, tar, gzip, ssh)
    7  = net-ops                (network tools: ip, ss, curl, ssh)
    8  = monitoring             (monitoring: top, journalctl, curl)
    9  = readonly-audit         (journalctl, aureport, cat, grep)
    10 = mail-admin             (curl, journalctl, tail, grep)
    11 = web-admin              (ls, ps, curl, journalctl)
    12 = db-admin               (ps, df, ss, tail, curl)
    13 = custom-minimal         (ls, whoami)

RECOMMENDED ROLE COMBINATIONS:

  Mail Admin:
    Role: 10 (mail-admin)
    SSH: yes, Sudo: no, rbash: yes

  Network Admin:
    Role: 7 (net-ops)
    SSH: yes, Sudo: maybe, rbash: no

  Backup Operator:
    Role: 6 (backup-ops)
    SSH: yes, Sudo: maybe, rbash: yes

  Monitoring Agent:
    Role: 8 (monitoring)
    SSH: yes, Sudo: no, rbash: yes

STEP 5: SSHD CONFIGURATION
──────────────────────────

The installer will ask:

    Apply SSHD configuration? [Y/n]: Y

This will:
  ✓ Validate SSHD config syntax
  ✓ Reload SSH service
  ✓ Enable auto-restore on boot

STEP 6: DOWNLOAD DEPLOYMENT ARCHIVE
──────────────────────────────────────

The installer will show:

    ╔════════════════════════════════════════════════════════════════╗
    ║                  DOWNLOAD ARCHIVE                              ║
    ╚════════════════════════════════════════════════════════════════╝

    Download deployment archive with SSH keys and configs:

      scp -P 22 gate@192.168.1.100:/srv/sys/deploy/ssh-gate-deploy-20250108_143022.tar.gz ./

      Archive: ssh-gate-deploy-20250108_143022.tar.gz (2.3M)

On your LOCAL machine, run:

    scp -P 22 gate@<server_ip>:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./
    tar -xzf ssh-gate-deploy-*.tar.gz

The archive contains:
  • SSH private keys (for each user)
  • SSH public keys (.pub files)
  • Windows SSH config template
  • Deployment information
  • Setup instructions

STEP 7: LOCAL SETUP (ON YOUR MACHINE)
──────────────────────────────────────

After downloading and extracting:

    cd ssh-gate-deploy-*/
    cat docs/SCP_INSTRUCTIONS.txt

For Linux/Mac:

    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    cp keys/main@server-* ~/.ssh/
    chmod 600 ~/.ssh/main@server-*
    cat configs/ssh_config >> ~/.ssh/config

For Windows (with WSL or Git Bash):

    mkdir -p ~/.ssh
    cp keys/main@server-* ~/.ssh/
    chmod 600 ~/.ssh/main@server-*
    cat configs/ssh_config >> ~/.ssh/config

STEP 8: TEST SSH CONNECTION
──────────────────────────────

First test - via gate to main:

    ssh -i ~/.ssh/main@server-* gate@192.168.1.100
    
    # Inside gate shell, type:
    2main
    
    # You should now be logged in as main user

Verify you're in the right place:

    whoami
    # Should output: main

Check available commands in rbash:

    ls -la /srv/home/main/local/rbin/

EXPECTED OUTPUT AFTER INSTALLATION
════════════════════════════════════════════════════════════════════════════

    ╔════════════════════════════════════════════════════════════════╗
    ║                    DEPLOYMENT SUMMARY                          ║
    ╚════════════════════════════════════════════════════════════════╝

    SERVER INFORMATION:
      Hostname:                  server.example.com
      IP Address:                192.168.1.100
      SSH Port:                  22

    PROTOCOLS CONFIGURED:
      ✓ web
      ✓ dns
      ✓ monitoring

    FIREWALL PORTS:
      Opened: 22, 80, 443, 53, 8080, 8443, 9090

    USERS CREATED:
      main            role=admin                ssh=yes   sudo=yes  rbash=no
      gate            role=guest                ssh=no    sudo=no   rbash=yes

    SSH KEYS:
      main            Keys: 1

    INFRASTRUCTURE PATHS:
      Base:                      /srv/sys
      Home:                      /srv/home
      SSH Keys:                  /srv/sys/ssh/key-export
      SSH Config:                /srv/sys/ssh/sshd_config.d
      Session Logs:              /srv/sys/ssh/ssh_session
      Firewall:                  /srv/sys/iptables

TROUBLESHOOTING
════════════════════════════════════════════════════════════════════════════

Problem: "Permission denied (publickey)"

  Solution:
    1. Check key permissions:
       ls -la ~/.ssh/main@server-*
       (Should show: -rw------- or 600)

    2. If needed, fix permissions:
       chmod 600 ~/.ssh/main@server-*

    3. Test SSH verbose mode:
       ssh -v -i ~/.ssh/main@server-* gate@192.168.1.100

Problem: SSH connection timeout

  Solution:
    1. Check server firewall:
       sudo iptables -L -v -n
       sudo iptables -L INPUT | head -20

    2. Verify SSH service:
       sudo systemctl status ssh

    3. Test port accessibility:
       nc -zv 192.168.1.100 22

Problem: Can't find downloaded archive on server

  Solution:
    1. Check archive location:
       ls -la /srv/sys/deploy/

    2. Create archive manually:
       sudo bash install_ssh_gate_v2.sh
       # Select protocols, users, then at end it creates archive

    3. List latest archive:
       ls -lt /srv/sys/deploy/ssh-gate-deploy-*.tar.gz | head -1

Problem: SSHD validation failed

  Solution:
    1. Check syntax:
       sudo sshd -t

    2. View recent changes:
       ls -ltr /srv/sys/ssh/sshd_config.d/*.conf | tail -5

    3. Disable problematic snippet:
       sudo mv /srv/sys/ssh/sshd_config.d/10-user_<user>.conf \
              /srv/sys/ssh/sshd_config.d/10-user_<user>.conf.inactive

    4. Reload:
       sudo systemctl reload sshd

Problem: rbash: command not found (basic command fails)

  Solution:
    1. Check rbin directory:
       ls -la /srv/home/<user>/local/rbin/

    2. User might not have permission for command
       Edit role in script and reinstall

    3. Or use bash temporarily:
       rbash --noprofile -c "ls"

SECURITY BEST PRACTICES
════════════════════════════════════════════════════════════════════════════

✓ AFTER INSTALLATION:

  1. Change SSH port if using non-standard port (e.g., 2222)
  2. Use key-based authentication only (PasswordAuthentication=no)
  3. Keep /srv/sys/ writable only by root
  4. Review user roles periodically
  5. Monitor session logs: tail -f /srv/sys/ssh/ssh_session/<date>/*.log
  6. Enable auditd: sudo systemctl start auditd
  7. Set up logrotate for session logs
  8. Use firewall to restrict SSH source IPs
  9. Rotate SSH keys monthly
  10. Review MOTD for policy statements

✓ KEY MANAGEMENT:

  • Store private keys in ~/.ssh/ with 600 permissions
  • Never share private keys via unencrypted email
  • Use ssh-agent for passphrase-less access (if safe in your env)
  • Archive old keys: tar -czf ssh_keys_backup_YYYY-MM-DD.tar.gz ~/.ssh/

✓ USER MANAGEMENT:

  • Review created users monthly
  • Remove unused accounts: userdel -r <user>
  • Monitor sudo usage: grep sudo /var/log/auth.log
  • Check session logs for suspicious activity
  • Use different keys for different servers

✓ FIREWALL:

  • Check merged iptables: iptables -L INPUT | head -20
  • Save firewall rules: sudo /usr/local/sbin/restore_srv_iptables.sh save
  • Monitor IP bans: sudo ipset list ssh_ban
  • Review suspicious IPs: tail -50 /srv/sys/ssh/ssh_fail2ban/bans.log

NEXT STEPS
════════════════════════════════════════════════════════════════════════════

After successful installation:

  1. ✓ Create backups of /srv/sys/
  2. ✓ Document SSH port and gate user
  3. ✓ Distribute SSH keys to authorized users
  4. ✓ Set up monitoring for logs
  5. ✓ Schedule regular security audits
  6. ✓ Create runbook for user management
  7. ✓ Test recovery procedures
  8. ✓ Document company policies in MOTD

GETTING HELP
════════════════════════════════════════════════════════════════════════════

For detailed documentation:

  • Read V2_ENHANCEMENTS.md (new features explanation)
  • Check /srv/sys/deploy/DEPLOYMENT_INFO.txt (on server)
  • Review SSH snippets: ls -la /srv/sys/ssh/sshd_config.d/
  • Check session logs: ls -la /srv/sys/ssh/ssh_session/

ADVANCED FEATURES
════════════════════════════════════════════════════════════════════════════

When you're comfortable with basic setup, explore:

  • Dynamic SSH snippets for per-user config
  • IPTables deduplication for firewall management
  • Session recording with SID tracking
  • Auditd rules for compliance
  • MOTD customization
  • Systemd maintenance timers

See V2_ENHANCEMENTS.md for complete details!

════════════════════════════════════════════════════════════════════════════
                          Ready to get started?

                  sudo bash install_ssh_gate_v2.sh

════════════════════════════════════════════════════════════════════════════

GUIDE

# Make this script executable and provide it
chmod +x "$0"
echo "Save this file as: QUICK_START_V2.sh"
echo "Run it to see this guide: bash QUICK_START_V2.sh"
