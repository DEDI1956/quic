#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta
from database import init_db, get_db, User, VPNAccount, Transaction
from xray_manager import XrayManager

def cleanup_expired_accounts():
    print(f"[{datetime.now()}] Starting cleanup of expired accounts...")
    
    db = get_db()
    xray = XrayManager()
    now = datetime.now()
    
    expired_accounts = db.query(VPNAccount).filter(
        VPNAccount.is_active == True,
        VPNAccount.expired_at < now
    ).all()
    
    count = 0
    for account in expired_accounts:
        try:
            xray.remove_client(account.email)
            account.is_active = False
            count += 1
            print(f"  Removed: {account.email} (expired: {account.expired_at})")
        except Exception as e:
            print(f"  Error removing {account.email}: {e}")
    
    db.commit()
    db.close()
    
    print(f"[{datetime.now()}] Cleanup completed: {count} accounts removed")

def send_expiry_reminders():
    print(f"[{datetime.now()}] Checking accounts for expiry reminders...")
    
    db = get_db()
    now = datetime.now()
    reminder_time = now + timedelta(days=1)
    
    expiring_accounts = db.query(VPNAccount).filter(
        VPNAccount.is_active == True,
        VPNAccount.expired_at > now,
        VPNAccount.expired_at < reminder_time
    ).all()
    
    print(f"  Found {len(expiring_accounts)} accounts expiring within 24 hours")
    
    db.close()

def generate_daily_report():
    print(f"[{datetime.now()}] Generating daily report...")
    
    db = get_db()
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    new_users = db.query(User).filter(User.created_at >= yesterday).count()
    new_accounts = db.query(VPNAccount).filter(VPNAccount.created_at >= yesterday).count()
    completed_transactions = db.query(Transaction).filter(
        Transaction.created_at >= yesterday,
        Transaction.status == 'completed'
    ).count()
    
    total_users = db.query(User).count()
    active_accounts = db.query(VPNAccount).filter(VPNAccount.is_active == True).count()
    
    report = f"""
    ====================================
    DAILY REPORT - {now.strftime('%Y-%m-%d')}
    ====================================
    
    📊 Yesterday's Activity:
    • New Users: {new_users}
    • New Accounts: {new_accounts}
    • Completed Transactions: {completed_transactions}
    
    📈 Current Status:
    • Total Users: {total_users}
    • Active Accounts: {active_accounts}
    
    ====================================
    """
    
    print(report)
    
    with open(f"/opt/vpn-bot/reports/daily-{now.strftime('%Y%m%d')}.txt", "w") as f:
        f.write(report)
    
    db.close()

def backup_database():
    print(f"[{datetime.now()}] Creating database backup...")
    
    import shutil
    now = datetime.now()
    backup_dir = "/opt/vpn-bot/backups"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    db_file = "/opt/vpn-bot/vpn_bot.db"
    backup_file = f"{backup_dir}/vpn_bot-{now.strftime('%Y%m%d-%H%M%S')}.db"
    
    try:
        shutil.copy2(db_file, backup_file)
        print(f"  Backup created: {backup_file}")
        
        backup_files = sorted([
            f for f in os.listdir(backup_dir)
            if f.startswith("vpn_bot-") and f.endswith(".db")
        ])
        
        if len(backup_files) > 7:
            for old_backup in backup_files[:-7]:
                os.remove(os.path.join(backup_dir, old_backup))
                print(f"  Removed old backup: {old_backup}")
        
    except Exception as e:
        print(f"  Error creating backup: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cron_tasks.py [cleanup|reminders|report|backup]")
        sys.exit(1)
    
    task = sys.argv[1]
    
    if task == "cleanup":
        cleanup_expired_accounts()
    elif task == "reminders":
        send_expiry_reminders()
    elif task == "report":
        generate_daily_report()
    elif task == "backup":
        backup_database()
    else:
        print(f"Unknown task: {task}")
        sys.exit(1)

if __name__ == '__main__':
    main()
