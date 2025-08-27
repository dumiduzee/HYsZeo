#!/bin/bash

setup_hysteria_scheduler() {
  
    chmod +x /etc/hysteria/core/scripts/scheduler.py

    cat > /etc/systemd/system/hysteria-scheduler.service << 'EOF'
[Unit]
Description=Hysteria2 Scheduler Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/etc/hysteria
ExecStart=/etc/hysteria/hysteria2_venv/bin/python3 /etc/hysteria/core/scripts/scheduler.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hysteria-scheduler

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable hysteria-scheduler.service
    systemctl start hysteria-scheduler.service
    (crontab -l | grep -v "hysteria2_venv.*traffic-status" | grep -v "hysteria2_venv.*backup-hysteria") | crontab -
}

check_scheduler_service() {
    if systemctl is-active --quiet hysteria-scheduler.service; then
        return 0
    else
        return 1
    fi
}

setup_hysteria_auth_server() {
    # chmod +x /etc/hysteria/core/scripts/auth/user_auth

    cat > /etc/systemd/system/hysteria-auth.service << 'EOF'
[Unit]
Description=Hysteria Auth Server
After=network.target

[Service]
Type=simple
User=root
ExecStart=/etc/hysteria/core/scripts/auth/user_auth
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hysteria-Auth

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable hysteria-auth.service
    systemctl start hysteria-auth.service
}

check_auth_server_service() {
    if systemctl is-active --quiet hysteria-auth.service; then
        return 0
    else
        return 1
    fi
}