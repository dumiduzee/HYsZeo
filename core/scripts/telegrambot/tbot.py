
from telebot import types
from utils import *
import threading
import time
import os

def send_backup_to_admins():
    while True:
        try:
            # Generate backup
            backup_command = f"python3 {CLI_PATH} backup-hysteria"
            result = run_cli_command(backup_command)

            # Find latest backup file
            files = [f for f in os.listdir(BACKUP_DIRECTORY) if f.endswith('.zip')]
            files.sort(key=lambda x: os.path.getctime(os.path.join(BACKUP_DIRECTORY, x)), reverse=True)
            latest_backup_file = files[0] if files else None

            if latest_backup_file:
                backup_file_path = os.path.join(BACKUP_DIRECTORY, latest_backup_file)
                for admin_id in ADMIN_USER_IDS:
                    with open(backup_file_path, 'rb') as f:
                        bot.send_document(admin_id, f, caption=f"Scheduled Backup: {latest_backup_file}")
        except Exception as e:
            print(f"[Backup Scheduler] Error: {e}")
        time.sleep(2 * 60 * 60)  # 2 hours

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_admin(message.from_user.id):
        markup = create_main_markup()
        bot.reply_to(message, "Welcome to the User Management Bot!", reply_markup=markup)
    else:
        bot.reply_to(message, "Unauthorized access. You do not have permission to use this bot.")

def monitoring_thread():
    while True:
        monitor_system_resources()
        time.sleep(60)


if __name__ == '__main__':
    monitor_thread = threading.Thread(target=monitoring_thread, daemon=True)
    monitor_thread.start()
    version_thread = threading.Thread(target=version_monitoring, daemon=True)
    version_thread.start()
    # Start scheduled backup thread
    backup_thread = threading.Thread(target=send_backup_to_admins, daemon=True)
    backup_thread.start()
    bot.polling(none_stop=True)
