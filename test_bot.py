#!/usr/bin/env python3

import unittest
from datetime import datetime, timedelta
from database import init_db, get_db, User, VPNAccount, Transaction
from xray_manager import XrayManager
import tempfile
import os

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        os.environ['DATABASE_URL'] = f'sqlite:///{self.test_db.name}'
        init_db()
    
    def tearDown(self):
        os.unlink(self.test_db.name)
    
    def test_create_user(self):
        db = get_db()
        user = User(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            is_admin=False,
            balance=0
        )
        db.add(user)
        db.commit()
        
        retrieved_user = db.query(User).filter(User.telegram_id == 123456789).first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "testuser")
        db.close()
    
    def test_create_vpn_account(self):
        db = get_db()
        
        user = User(telegram_id=123456789, username="test", first_name="Test")
        db.add(user)
        db.commit()
        
        account = VPNAccount(
            user_id=user.id,
            telegram_id=123456789,
            protocol="vmess",
            uuid="test-uuid-123",
            email="test@example.com",
            expired_at=datetime.now() + timedelta(days=30),
            connection_type="ws"
        )
        db.add(account)
        db.commit()
        
        retrieved = db.query(VPNAccount).filter(VPNAccount.email == "test@example.com").first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.protocol, "vmess")
        db.close()

class TestXrayManager(unittest.TestCase):
    def setUp(self):
        self.xray = XrayManager()
    
    def test_generate_vmess_link(self):
        link = self.xray.generate_link(
            protocol="vmess",
            uuid="test-uuid",
            email="test@example.com",
            connection_type="ws",
            domain="example.com"
        )
        self.assertTrue(link.startswith("vmess://"))
    
    def test_generate_vless_link(self):
        link = self.xray.generate_link(
            protocol="vless",
            uuid="test-uuid",
            email="test@example.com",
            connection_type="ws_tls",
            domain="example.com"
        )
        self.assertTrue(link.startswith("vless://"))
    
    def test_generate_trojan_link(self):
        link = self.xray.generate_link(
            protocol="trojan",
            uuid="test-password",
            email="test@example.com",
            connection_type="tcp_tls",
            domain="example.com"
        )
        self.assertTrue(link.startswith("trojan://"))

class TestUtils(unittest.TestCase):
    def test_format_price(self):
        from utils import format_price
        result = format_price(10000)
        self.assertEqual(result, "Rp 10,000")
    
    def test_calculate_expiry(self):
        from utils import calculate_expiry
        result = calculate_expiry(30)
        expected = datetime.now() + timedelta(days=30)
        self.assertAlmostEqual(
            result.timestamp(),
            expected.timestamp(),
            delta=1
        )
    
    def test_is_expired(self):
        from utils import is_expired
        past_date = datetime.now() - timedelta(days=1)
        future_date = datetime.now() + timedelta(days=1)
        
        self.assertTrue(is_expired(past_date))
        self.assertFalse(is_expired(future_date))

def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestXrayManager))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
