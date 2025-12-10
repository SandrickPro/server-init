# SSH Gate v2 - Implementation Checklist & Deployment Guide

## Pre-Installation Checklist

### Server Preparation
- [ ] Server has Ubuntu 20.04 LTS, 22.04 LTS, or 24.04 LTS
- [ ] Root or sudo access available
- [ ] Minimum 500MB free disk space (for /srv/sys/)
- [ ] Network connectivity confirmed
- [ ] Current SSH access works (don't close this session!)

### Planning
- [ ] SSH port decided (e.g., 2222, default is 22)
- [ ] Gate username chosen (default: gate)
- [ ] Main admin username chosen (default: main)
- [ ] List of additional users prepared with roles
- [ ] Protocols/services identified (web, mail, database, etc.)
- [ ] Firewall rules documented
- [ ] Backup of current system created

### Documentation
- [ ] QUICK_START_V2.sh script available
- [ ] V2_ENHANCEMENTS.md documentation read
- [ ] ADMIN_GUIDE_V2.md saved for reference
- [ ] EXAMPLES_V2.md reviewed for your scenario

---

## Installation Phase

### Step 1: Download Script
```bash
# On server
wget https://your-repo/install_ssh_gate_v2.sh
# OR copy file manually to server
```

**Verification:**
- [ ] Script is on server in home directory
- [ ] Script is readable: `ls -la install_ssh_gate_v2.sh`
- [ ] File size ~25 KB

### Step 2: Run Installation
```bash
sudo bash install_ssh_gate_v2.sh
```

**During Installation:**
- [ ] Directories created under /srv/
- [ ] SSH snippets written
- [ ] Firewall rules created

### Step 3: Protocol Selection (2-second timeout)
```
Enable web? [Y/n] (auto: yes in 2s):
```

- [ ] Choose protocols with auto-confirm or manual response
- [ ] Selected all necessary protocols
- [ ] Noted which ports are opened

### Step 4: User Configuration
```
Enter SSH port [22]: 2222
Enter gate username [gate]: gate
Enter main admin username [main]: main
```

- [ ] SSH port confirmed
- [ ] Gate user created
- [ ] Main admin user created

### Step 5: Additional Users Loop
```
Add additional user? [y/N]: y
Username: username
Role number [0-13]: <role>
SSH access via gate? [y/N]: y
Grant sudo? [y/N]: n
Use rbash? [y/N]: y
Generate SSH key now? [y/N]: y
```

Repeat for each user:
- [ ] User 1 created (username, role, options)
- [ ] User 2 created (if needed)
- [ ] User 3 created (if needed)
- [ ] All SSH keys generated or planned for later

### Step 6: SSHD Configuration
```
Apply SSHD configuration? [Y/n]: Y
```

- [ ] Configuration validation passed
- [ ] SSH reloaded successfully
- [ ] No errors in output

### Step 7: Installation Complete
At end of script:

```
╔════════════════════════════════════════════════════════════════╗
║                    DEPLOYMENT SUMMARY                          ║
╚════════════════════════════════════════════════════════════════╝
```

- [ ] Summary displayed with all users
- [ ] SSH keys listed
- [ ] Firewall ports displayed
- [ ] Download archive command shown
- [ ] Archive created in /srv/sys/deploy/

**Post-Installation Verification:**
```bash
# On server
sudo sshd -t                    # Should output nothing (OK)
ls -la /srv/sys/deploy/*.tar.gz  # Archive should exist
cat /srv/sys/deploy/deployed_users.txt  # List users
```

- [ ] SSHD syntax valid
- [ ] Archive file exists and has size > 100KB
- [ ] Users file lists all created users

---

## Archive Download & Setup

### Step 1: Download Archive
```bash
# On LOCAL machine
scp -P 2222 gate@<server_ip>:/srv/sys/deploy/ssh-gate-deploy-*.tar.gz ./

# Verify download
ls -lh ssh-gate-deploy-*.tar.gz
```

- [ ] Archive downloaded successfully
- [ ] Size is > 100KB (contains keys and configs)

### Step 2: Extract Archive
```bash
tar -xzf ssh-gate-deploy-*.tar.gz
ls -la ssh-gate-deploy-*/
```

- [ ] Archive extracted
- [ ] Directories visible: keys/, configs/, docs/
- [ ] docs/DEPLOYMENT_INFO.txt exists
- [ ] docs/SCP_INSTRUCTIONS.txt exists

### Step 3: Review Documentation
```bash
cat ssh-gate-deploy-*/docs/DEPLOYMENT_INFO.txt
cat ssh-gate-deploy-*/docs/SCP_INSTRUCTIONS.txt
```

- [ ] Server information verified
- [ ] Users list matches creation
- [ ] SSH keys present
- [ ] Windows SSH config template present

### Step 4: Install SSH Keys Locally
```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cp ssh-gate-deploy-*/keys/*/* ~/.ssh/
chmod 600 ~/.ssh/*
ls -la ~/.ssh/
```

- [ ] Keys copied to ~/.ssh/
- [ ] Permission is 600 for all keys
- [ ] Public keys (.pub) also present for reference

### Step 5: Configure SSH Client
```bash
cat ssh-gate-deploy-*/configs/ssh_config >> ~/.ssh/config
cat ~/.ssh/config | grep "Host "
```

- [ ] SSH config appended to ~/.ssh/config
- [ ] All users visible as Host entries
- [ ] ProxyJump pointing to gate correctly

### Step 6: Verify SSH Client Config
```bash
# Check syntax
ssh -G <username> 2>&1 | head -10

# Should show:
# hostname 203.0.113.100
# port 2222
# user <username>
# identityfile ~/.ssh/<key>
```

- [ ] SSH config parsed without errors
- [ ] HostName shows server IP
- [ ] Port shows correct SSH port
- [ ] IdentityFile shows correct key path

---

## SSH Connection Testing

### Test 1: Direct SSH to Gate
```bash
ssh -i ~/.ssh/<admin_key> gate@<server_ip> -p 2222

# Should show rbash prompt:
gate>
```

- [ ] SSH connection successful
- [ ] Gate rbash shell active
- [ ] Can type commands
- [ ] Type `exit` to close

### Test 2: Switch to Admin User
```bash
# Inside gate shell
gate> 2admin

# Should show bash prompt:
admin@server:~$
```

- [ ] Switch command available
- [ ] Admin shell active
- [ ] Can run commands like `whoami`, `pwd`, etc.
- [ ] Type `exit` to return to gate

### Test 3: Verify Permissions
```bash
# As admin
admin@server:~$ whoami
# Output: admin

admin@server:~$ sudo whoami
# Output: root (if sudo granted)

admin@server:~$ ls /srv/sys/ssh/ssh_session/
# Output: list of date directories

admin@server:~$ exit
```

- [ ] whoami shows correct user
- [ ] sudo works if granted
- [ ] Can view session logs
- [ ] Exit returns to gate shell

### Test 4: Session Logging
```bash
# As admin - run some commands to create log entry
admin@server:~$ ls
admin@server:~$ ps aux
admin@server:~$ exit

# Back in gate shell - check logs
gate> ls /srv/sys/ssh/ssh_session/
gate> exit
```

- [ ] Session log directory exists
- [ ] Log file created after session
- [ ] Log contains SID (Session ID)

### Test 5: SSH Config Usage
```bash
# If SSH config properly configured
ssh admin
# Should authenticate and connect via gate automatically

# Inside gate shell
gate> 2admin
admin@server:~$
```

- [ ] SSH config Host entry works
- [ ] ProxyJump functions correctly
- [ ] Key authentication automatic

---

## Server-Side Verification

### Verify Installation
```bash
# On server as root
sudo -s

# Check directories
ls -la /srv/sys/
du -sh /srv/sys/

# Check users
grep gate /etc/passwd
grep main /etc/passwd
grep <other_users> /etc/passwd

# Check SSH config
ls -la /srv/sys/ssh/sshd_config.d/10-user_*.conf

# Check iptables
iptables -L INPUT -n | head -20

# Check SSH keys
ls -la /srv/sys/ssh/key-export/*/
```

- [ ] /srv/sys/ exists with proper size
- [ ] All users exist in passwd
- [ ] Per-user SSH snippets exist (10-user_*.conf)
- [ ] Firewall rules loaded
- [ ] SSH keys exported

### Check Session Logs
```bash
# On server
today_dir="/srv/sys/ssh/ssh_session/$(date +%d-%b\'%y | tr a-z A-Z)"
ls -la $today_dir/

# Should show log files like:
# 192-168-1-100_admin_08-JAN'25_14.22_admin@08-JAN'25=14:22-14:45.log
```

- [ ] Session log directory exists
- [ ] Log files created after connections
- [ ] Log names follow SID format
- [ ] Logs contain session data

### Check Firewall
```bash
# On server
sudo iptables -L INPUT -n -v | head -30

# Should show rules for:
# SSH port
# Protocol ports (80, 443 for web, etc.)
```

- [ ] INPUT chain has DROP default
- [ ] ESTABLISHED,RELATED allowed
- [ ] SSH port allowed
- [ ] Protocol ports allowed
- [ ] No duplicate rules (v2 deduplication)

### Check Auditd
```bash
# On server
sudo systemctl status auditd
sudo auditctl -l | head -5

# Should show audit rules
```

- [ ] Auditd service running
- [ ] Rules loaded
- [ ] At least one rule visible

### Check Systemd Units
```bash
# On server
sudo systemctl list-timers | grep -E "session|ban"
sudo systemctl status iptables-restore.service

# Should show:
# session-maintenance.timer    PASSED
# iptables-restore.service     active
```

- [ ] Session maintenance timer configured
- [ ] IPTables restore service enabled
- [ ] No failed units

---

## Backup & Documentation

### Create Server Backup
```bash
# On server
sudo tar -czf /tmp/ssh_gate_initial_$(date +%Y-%m-%d).tar.gz /srv/sys/
sudo cp /tmp/ssh_gate_initial_*.tar.gz /srv/sys/

# Verify backup
sudo ls -lh /srv/sys/ssh_gate_initial_*.tar.gz
```

- [ ] Backup created
- [ ] Size > 1MB
- [ ] Stored on server for recovery

### Backup Local SSH Setup
```bash
# On local machine
tar -czf ssh_keys_backup_$(date +%Y-%m-%d).tar.gz ~/.ssh/
cp ssh_keys_backup_*.tar.gz ~/Documents/

# Verify
ls -lh ~/Documents/ssh_keys_backup_*.tar.gz
```

- [ ] Local backup created
- [ ] Stored in Documents/
- [ ] Can be used for key recovery

### Document Configuration
```bash
# Create documentation file
cat > ~/Documents/ssh_gate_config.txt <<EOF
Server: 203.0.113.100
SSH Port: 2222
Gate User: gate
Admin User: main
Users: admin, mail_admin, net_ops
Protocols: web, mail, dns, db
Archive: ssh-gate-deploy-20250108_143022.tar.gz
Setup Date: $(date)
Backup: ssh_keys_backup_$(date +%Y-%m-%d).tar.gz
EOF
```

- [ ] Configuration documented
- [ ] Saved in safe location
- [ ] Includes all important info

---

## Team Handover

### For Each User

1. **Prepare Package**
```bash
# If multiple users, extract only their keys
mkdir user_package
cp ssh-gate-deploy-*/keys/<username>/* user_package/
cp ssh-gate-deploy-*/docs/SCP_INSTRUCTIONS.txt user_package/
tar -czf <username>_keys.tar.gz user_package/
```
- [ ] User's keys extracted
- [ ] Instructions included
- [ ] Archive created

2. **Send Securely**
```bash
# Use secure method:
# - Encrypted email
# - Secure file transfer
# - In-person delivery
# - Password-protected archive
```
- [ ] Archive sent securely
- [ ] User confirms receipt
- [ ] User sets up locally

3. **Verify User Access**
```bash
# After user sets up locally
ssh gate@server
gate> 2<username>
<username>@server:~$ whoami
# Should output: username
```
- [ ] User can connect
- [ ] User can switch to their account
- [ ] Commands available to role

---

## Monitoring & Maintenance

### Daily Checks
```bash
# Check SSH service
sudo systemctl status ssh

# Check firewall
sudo iptables -L INPUT -n | head -20

# Check recent logins
sudo journalctl -u ssh -n 20

# Monitor active sessions
watch -n 5 'tail -5 /srv/sys/ssh/ssh_session/$(date +%d-%b\'%y | tr a-z A-Z)/*.log'
```

- [ ] SSH service running
- [ ] Firewall rules in place
- [ ] No auth errors
- [ ] Sessions being logged

### Weekly Checks
```bash
# Validate SSHD config
sudo sshd -t

# Check disk usage
du -sh /srv/sys/

# Review failed auth attempts
tail -30 /var/log/auth.log | grep Failed

# Check IPSet bans
sudo ipset list ssh_ban
```

- [ ] SSHD config valid
- [ ] Disk usage < 80%
- [ ] Failed attempts logged
- [ ] No unexpected IP bans

### Monthly Checks
```bash
# Audit users
cat /srv/sys/deploy/deployed_users.txt

# Rotate keys (if old)
sudo ssh-keygen -t ed25519 -C "user@host" \
  -f /srv/sys/ssh/key-export/<user>/newkey -N "" -q

# Check logs for anomalies
grep -E "Failed|error|ERROR" /var/log/auth.log | wc -l

# Backup system
tar -czf /backup/ssh_gate_$(date +%Y-%m-%d).tar.gz /srv/sys/
```

- [ ] User list reviewed
- [ ] Keys rotated if needed
- [ ] Anomalies checked
- [ ] Monthly backup created

### Quarterly Reviews
```bash
# Remove old logs (> 90 days)
find /srv/sys/ssh/ssh_session -type f -name '*.log' -mtime +90 -delete

# Remove old backups (> 6 months)
find /srv/sys/backup -type f -mtime +180 -delete

# Audit role permissions
ls -la /srv/home/*/local/rbin/

# Test disaster recovery
# Simulate key loss and recovery
```

- [ ] Old logs archived/deleted
- [ ] Old backups cleaned
- [ ] Role permissions reviewed
- [ ] Recovery tested

---

## Troubleshooting Checklist

### SSH Connection Issues

**Problem: "Permission denied"**
```bash
# Check 1: Key file permissions
ls -la ~/.ssh/<key>
# Should be: -rw------- (600)

# Check 2: Key in authorized_keys
cat /srv/sys/ssh/key-export/<user>/<key>.pub
grep "$(cat ~/.ssh/<key>.pub)" /srv/home/<user>/.ssh/authorized_keys

# Check 3: SSHD log
sudo journalctl -u ssh -n 50 | grep <username>
```

- [ ] Key has 600 permissions
- [ ] Public key in authorized_keys
- [ ] SSHD logs show authentication

**Problem: "Connection refused"**
```bash
# Check 1: SSH listening
sudo ss -tlnp | grep sshd
# Should show: LISTEN on port 2222

# Check 2: Firewall allows port
sudo iptables -L INPUT -n | grep <port>

# Check 3: SSH service running
sudo systemctl status ssh
```

- [ ] SSH listening on correct port
- [ ] Firewall allows SSH port
- [ ] SSH service is running

### SSHD Configuration Issues

**Problem: "SSHD configuration test failed"**
```bash
# Check syntax
sudo sshd -t

# If error, check snippets
ls -la /srv/sys/ssh/sshd_config.d/*.conf

# Disable problematic snippet
sudo mv /srv/sys/ssh/sshd_config.d/10-user_<user>.conf \
       /srv/sys/ssh/sshd_config.d/10-user_<user>.conf.OFF

# Test again
sudo sshd -t

# Reload if OK
sudo systemctl reload ssh
```

- [ ] Syntax error identified
- [ ] Problematic snippet found
- [ ] Configuration validated
- [ ] Service reloaded

### Session Logging Issues

**Problem: "No session logs created"**
```bash
# Check 1: Session directory exists
ls -la /srv/sys/ssh/ssh_session/

# Check 2: Permissions
sudo ls -la /srv/sys/ssh/ssh_session/*/

# Check 3: Check if gate_login_wrapper is being called
# Make actual SSH connection and check
ssh admin
# Inside
admin@server:~$ ls -ltra /srv/sys/ssh/.gate_session_hist.* 2>/dev/null
admin@server:~$ exit

# Check 1: Session log created
ls -la /srv/sys/ssh/ssh_session/<date>/
```

- [ ] Session directory accessible
- [ ] Proper permissions (755)
- [ ] Wrapper script executing
- [ ] Session files being created

---

## Security Hardening Checklist

### Post-Installation Security
- [ ] Change default SSH port from 22 to custom (e.g., 2222)
- [ ] Verify password authentication is disabled
- [ ] Verify root login is disabled
- [ ] Enable firewall with DROP default
- [ ] Set up IP whitelisting for trusted IPs
- [ ] Configure auditd for compliance
- [ ] Review and limit sudo access
- [ ] Setup fail2ban or equivalent IP banning

### Ongoing Security
- [ ] Monthly SSH key rotation
- [ ] Quarterly audit of user accounts
- [ ] Review session logs for suspicious activity
- [ ] Monitor failed authentication attempts
- [ ] Check firewall rules quarterly
- [ ] Update OpenSSH when patches released
- [ ] Keep system packages updated
- [ ] Monitor disk space for log rotation

### Access Control
- [ ] Document who has which SSH keys
- [ ] Track key distribution and rotation
- [ ] Remove keys when employees leave
- [ ] Periodic access reviews
- [ ] Test role-based command restrictions
- [ ] Verify gateway user isolation

---

## Final Verification

### System Status Check
```bash
# On server
sudo systemctl status ssh
sudo systemctl status auditd
sudo systemctl list-timers

# All should show: active (running)
```
- [ ] SSH active
- [ ] Auditd active
- [ ] Systemd timers configured

### Connectivity Test
```bash
# From local machine
ssh admin                    # Should connect via SSH config
gate> 2admin              # Should switch to admin
admin@server:~$ whoami    # Should return: admin
admin@server:~$ exit
gate> exit
```
- [ ] All users can connect
- [ ] All switches work
- [ ] Commands execute properly
- [ ] Exit works cleanly

### Logging Test
```bash
# After a connection, check
tail -1 /srv/sys/ssh/ssh_session/<date>/*.log
# Should show session details with SID
```
- [ ] Session logged with SID
- [ ] Commands logged
- [ ] Timestamps recorded

---

## Go-Live Readiness

- [ ] All installation steps completed
- [ ] All users tested
- [ ] All protocols/ports working
- [ ] Backups created and verified
- [ ] Documentation complete
- [ ] Team trained on access methods
- [ ] Monitoring set up
- [ ] Disaster recovery tested
- [ ] No open security issues
- [ ] Performance baseline established

**System is READY FOR PRODUCTION** ✅

---

## Post-Go-Live

### Week 1
- [ ] Monitor for issues
- [ ] Verify all users connecting successfully
- [ ] Check session logs daily
- [ ] Review any SSH errors
- [ ] Make any adjustments needed

### Month 1
- [ ] First key rotation
- [ ] Role review
- [ ] Access audit
- [ ] Performance review
- [ ] User feedback collection

### Ongoing
- [ ] Monthly backups
- [ ] Quarterly security audit
- [ ] Document all changes
- [ ] Keep documentation updated
- [ ] Train new team members

---

**System deployment complete. Proceed with confidence!** 🚀
