#!/usr/bin/env python3

import sys
import argparse
from datetime import datetime, timedelta
from database import init_db, get_db, User, VPNAccount, Transaction
from xray_manager import XrayManager

def init_database():
    print("Initializing database...")
    init_db()
    print("✅ Database initialized successfully!")

def add_admin(telegram_id: int):
    db = get_db()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if user:
        user.is_admin = True
        db.commit()
        print(f"✅ User {telegram_id} is now an admin!")
    else:
        new_user = User(
            telegram_id=telegram_id,
            username="admin",
            first_name="Admin",
            is_admin=True
        )
        db.add(new_user)
        db.commit()
        print(f"✅ Admin user {telegram_id} created!")
    
    db.close()

def add_balance(telegram_id: int, amount: float):
    db = get_db()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if user:
        user.balance += amount
        db.commit()
        print(f"✅ Added Rp {amount:,.0f} to user {telegram_id}")
        print(f"   New balance: Rp {user.balance:,.0f}")
    else:
        print(f"❌ User {telegram_id} not found!")
    
    db.close()

def list_users():
    db = get_db()
    users = db.query(User).all()
    
    print("\n👥 ALL USERS")
    print("=" * 80)
    print(f"{'ID':<15} {'Telegram ID':<15} {'Name':<20} {'Balance':<15} {'Admin'}")
    print("=" * 80)
    
    for user in users:
        print(f"{user.id:<15} {user.telegram_id:<15} {user.first_name:<20} Rp {user.balance:<12,.0f} {'Yes' if user.is_admin else 'No'}")
    
    print(f"\nTotal users: {len(users)}")
    db.close()

def list_accounts():
    db = get_db()
    accounts = db.query(VPNAccount).filter(VPNAccount.is_active == True).all()
    
    print("\n🔑 ACTIVE ACCOUNTS")
    print("=" * 100)
    print(f"{'ID':<8} {'Protocol':<12} {'Connection':<15} {'Email':<30} {'Expired':<20}")
    print("=" * 100)
    
    for acc in accounts:
        status = "Active" if acc.expired_at > datetime.now() else "Expired"
        print(f"{acc.id:<8} {acc.protocol:<12} {acc.connection_type:<15} {acc.email:<30} {acc.expired_at.strftime('%Y-%m-%d %H:%M')}")
    
    print(f"\nTotal active accounts: {len(accounts)}")
    db.close()

def delete_account(account_id: int):
    db = get_db()
    account = db.query(VPNAccount).filter(VPNAccount.id == account_id).first()
    
    if account:
        xray = XrayManager()
        xray.remove_client(account.email)
        
        account.is_active = False
        db.commit()
        print(f"✅ Account {account_id} ({account.email}) deleted!")
    else:
        print(f"❌ Account {account_id} not found!")
    
    db.close()

def cleanup_expired():
    db = get_db()
    now = datetime.now()
    
    expired_accounts = db.query(VPNAccount).filter(
        VPNAccount.is_active == True,
        VPNAccount.expired_at < now
    ).all()
    
    xray = XrayManager()
    count = 0
    
    for acc in expired_accounts:
        xray.remove_client(acc.email)
        acc.is_active = False
        count += 1
    
    db.commit()
    print(f"✅ Cleaned up {count} expired accounts")
    db.close()

def show_stats():
    db = get_db()
    
    total_users = db.query(User).count()
    total_accounts = db.query(VPNAccount).filter(VPNAccount.is_active == True).count()
    total_expired = db.query(VPNAccount).filter(
        VPNAccount.is_active == True,
        VPNAccount.expired_at < datetime.now()
    ).count()
    total_transactions = db.query(Transaction).filter(Transaction.status == 'completed').count()
    
    vmess_count = db.query(VPNAccount).filter(
        VPNAccount.protocol == 'vmess',
        VPNAccount.is_active == True
    ).count()
    
    vless_count = db.query(VPNAccount).filter(
        VPNAccount.protocol == 'vless',
        VPNAccount.is_active == True
    ).count()
    
    trojan_count = db.query(VPNAccount).filter(
        VPNAccount.protocol == 'trojan',
        VPNAccount.is_active == True
    ).count()
    
    print("\n📊 STATISTICS")
    print("=" * 50)
    print(f"👥 Total Users: {total_users}")
    print(f"🔑 Active Accounts: {total_accounts}")
    print(f"⏰ Expired Accounts: {total_expired}")
    print(f"💰 Completed Transactions: {total_transactions}")
    print("\n📱 Accounts by Protocol:")
    print(f"  • VMess: {vmess_count}")
    print(f"  • VLess: {vless_count}")
    print(f"  • Trojan: {trojan_count}")
    print("=" * 50)
    
    db.close()

def main():
    parser = argparse.ArgumentParser(description='VPN Bot Management Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    subparsers.add_parser('init', help='Initialize database')
    
    admin_parser = subparsers.add_parser('add-admin', help='Add admin user')
    admin_parser.add_argument('telegram_id', type=int, help='Telegram User ID')
    
    balance_parser = subparsers.add_parser('add-balance', help='Add balance to user')
    balance_parser.add_argument('telegram_id', type=int, help='Telegram User ID')
    balance_parser.add_argument('amount', type=float, help='Amount to add')
    
    subparsers.add_parser('list-users', help='List all users')
    subparsers.add_parser('list-accounts', help='List all active accounts')
    
    delete_parser = subparsers.add_parser('delete-account', help='Delete an account')
    delete_parser.add_argument('account_id', type=int, help='Account ID')
    
    subparsers.add_parser('cleanup', help='Cleanup expired accounts')
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_database()
    elif args.command == 'add-admin':
        add_admin(args.telegram_id)
    elif args.command == 'add-balance':
        add_balance(args.telegram_id, args.amount)
    elif args.command == 'list-users':
        list_users()
    elif args.command == 'list-accounts':
        list_accounts()
    elif args.command == 'delete-account':
        delete_account(args.account_id)
    elif args.command == 'cleanup':
        cleanup_expired()
    elif args.command == 'stats':
        show_stats()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
