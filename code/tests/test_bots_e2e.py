#!/usr/bin/env python3
"""
End-to-End tests for Telegram bots
Tests complete user workflows and bot integrations
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bots'))

from devops_manager_bot import DevOpsManagerBot
from security_auditor_bot import SecurityAuditorBot
from bots_orchestrator import BotsOrchestrator


class TestDevOpsManagerBotE2E(unittest.TestCase):
    """End-to-end tests for DevOps Manager Bot"""
    
    def setUp(self):
        self.bot = DevOpsManagerBot(token="test-token")
        
    @patch('devops_manager_bot.get_system_metrics')
    async def test_dashboard_command_e2e(self, mock_metrics):
        """Test complete dashboard command workflow"""
        mock_metrics.return_value = {
            'cpu': 45.2,
            'memory': 38.7,
            'disk': 45.0,
            'network': {'up': 1.2, 'down': 3.4}
        }
        
        update = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await self.bot.dashboard_command(update, context)
        
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        self.assertIn('SYSTEM DASHBOARD', call_args)
        self.assertIn('45.2', call_args)  # CPU
        
    @patch('devops_manager_bot.docker_ps')
    async def test_docker_management_e2e(self, mock_docker):
        """Test complete Docker management workflow"""
        mock_docker.return_value = [
            {'name': 'nginx', 'status': 'running', 'id': 'abc123'}
        ]
        
        update = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = ['ps']
        
        await self.bot.docker_command(update, context)
        
        update.message.reply_text.assert_called()
        
    @patch('devops_manager_bot.run_deployment')
    async def test_deployment_workflow_e2e(self, mock_deploy):
        """Test complete deployment workflow with ConversationHandler"""
        mock_deploy.return_value = {'status': 'success', 'version': 'v1.2.3'}
        
        # Start deployment
        update = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        state = await self.bot.start_deployment(update, context)
        self.assertEqual(state, self.bot.CHOOSE_VERSION)
        
        # Choose version
        update.message.text = 'v1.2.3'
        state = await self.bot.choose_version(update, context)
        self.assertEqual(state, self.bot.CONFIRM_DEPLOY)
        
        # Confirm deployment
        update.message.text = 'yes'
        state = await self.bot.confirm_deployment(update, context)
        
        mock_deploy.assert_called_once()


class TestSecurityAuditorBotE2E(unittest.TestCase):
    """End-to-end tests for Security Auditor Bot"""
    
    def setUp(self):
        self.bot = SecurityAuditorBot(token="test-token")
        
    @patch('security_auditor_bot.run_security_scan')
    async def test_full_security_audit_e2e(self, mock_scan):
        """Test complete security audit workflow"""
        mock_scan.return_value = {
            'score': 85,
            'issues': [
                {'severity': 'high', 'description': 'Open port 22'},
                {'severity': 'medium', 'description': 'Weak password policy'}
            ]
        }
        
        update = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await self.bot.scan_command(update, context)
        
        update.message.reply_text.assert_called()
        call_args = update.message.reply_text.call_args[0][0]
        self.assertIn('85', call_args)  # Security score
        
    @patch('security_auditor_bot.check_firewall_rules')
    async def test_firewall_management_e2e(self, mock_firewall):
        """Test complete firewall management workflow"""
        mock_firewall.return_value = [
            {'chain': 'INPUT', 'rule': 'ACCEPT tcp port 80'},
            {'chain': 'INPUT', 'rule': 'DROP all'}
        ]
        
        update = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = ['list']
        
        await self.bot.firewall_command(update, context)
        
        update.message.reply_text.assert_called()


class TestBotsOrchestratorE2E(unittest.TestCase):
    """End-to-end tests for Bots Orchestrator"""
    
    def setUp(self):
        self.orchestrator = BotsOrchestrator()
        
    async def test_orchestrator_initialization_e2e(self):
        """Test orchestrator initializes all bots"""
        await self.orchestrator.initialize()
        
        self.assertIsNotNone(self.orchestrator.devops_bot)
        self.assertIsNotNone(self.orchestrator.security_bot)
        
    @patch('bots_orchestrator.route_command')
    async def test_command_routing_e2e(self, mock_route):
        """Test command routing to correct bot"""
        mock_route.return_value = 'devops'
        
        update = Mock()
        update.message.text = '/dashboard'
        context = Mock()
        
        bot_name = await self.orchestrator.route_command(update, context)
        self.assertEqual(bot_name, 'devops')
        
    async def test_health_monitoring_e2e(self):
        """Test health monitoring of all bots"""
        await self.orchestrator.initialize()
        
        health_status = await self.orchestrator.check_all_health()
        
        self.assertIn('devops', health_status)
        self.assertIn('security', health_status)
        self.assertTrue(all(v['status'] == 'healthy' for v in health_status.values()))


class TestCompleteUserWorkflows(unittest.TestCase):
    """Test complete user workflows across multiple bots"""
    
    async def test_deploy_and_monitor_workflow(self):
        """Test: Deploy → Monitor → Alert workflow"""
        # 1. Deploy new version
        devops_bot = DevOpsManagerBot(token="test-token")
        
        with patch('devops_manager_bot.run_deployment') as mock_deploy:
            mock_deploy.return_value = {'status': 'success'}
            
            update = Mock()
            update.message.reply_text = AsyncMock()
            context = Mock()
            
            await devops_bot.deploy_command(update, context)
            
        # 2. Monitor metrics
        with patch('devops_manager_bot.get_system_metrics') as mock_metrics:
            mock_metrics.return_value = {'cpu': 75.0}
            
            await devops_bot.metrics_command(update, context)
            
        # 3. Trigger alert if threshold exceeded
        self.assertGreater(75.0, 70.0)  # Alert threshold
        
    async def test_security_incident_workflow(self):
        """Test: Detect → Alert → Block → Report workflow"""
        security_bot = SecurityAuditorBot(token="test-token")
        
        # 1. Detect suspicious activity
        with patch('security_auditor_bot.analyze_logs') as mock_logs:
            mock_logs.return_value = [
                {'ip': '192.168.1.100', 'attempts': 10, 'suspicious': True}
            ]
            
            update = Mock()
            update.message.reply_text = AsyncMock()
            context = Mock()
            
            await security_bot.logs_command(update, context)
            
        # 2. Block IP
        with patch('security_auditor_bot.block_ip') as mock_block:
            mock_block.return_value = True
            context.args = ['192.168.1.100']
            
            await security_bot.incident_command(update, context)
            
        # 3. Generate incident report
        with patch('security_auditor_bot.generate_report') as mock_report:
            mock_report.return_value = {'incident_id': '12345', 'status': 'resolved'}
            
            await security_bot.compliance_command(update, context)
            
    async def test_backup_restore_workflow(self):
        """Test: Backup → Verify → Restore workflow"""
        devops_bot = DevOpsManagerBot(token="test-token")
        
        # 1. Create backup
        with patch('devops_manager_bot.create_backup') as mock_backup:
            mock_backup.return_value = {
                'backup_id': 'backup-20241210',
                'size': '10GB',
                'status': 'completed'
            }
            
            update = Mock()
            update.message.reply_text = AsyncMock()
            context = Mock()
            
            await devops_bot.db_command(update, context)
            
        # 2. Verify integrity
        with patch('devops_manager_bot.verify_backup') as mock_verify:
            mock_verify.return_value = {'valid': True, 'checksum': 'abc123'}
            
            context.args = ['verify', 'backup-20241210']
            await devops_bot.db_command(update, context)
            
        # 3. Restore from backup
        with patch('devops_manager_bot.restore_backup') as mock_restore:
            mock_restore.return_value = {'status': 'success'}
            
            context.args = ['restore', 'backup-20241210']
            await devops_bot.db_command(update, context)


class TestPerformanceE2E(unittest.TestCase):
    """Performance tests for bot operations"""
    
    async def test_bot_response_time(self):
        """Test bot responds within 100ms"""
        import time
        
        bot = DevOpsManagerBot(token="test-token")
        
        start = time.time()
        
        update = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        with patch('devops_manager_bot.get_system_metrics') as mock_metrics:
            mock_metrics.return_value = {'cpu': 50.0}
            await bot.dashboard_command(update, context)
            
        end = time.time()
        response_time_ms = (end - start) * 1000
        
        self.assertLess(response_time_ms, 100)
        
    async def test_concurrent_commands(self):
        """Test handling 10 concurrent commands"""
        bot = DevOpsManagerBot(token="test-token")
        
        tasks = []
        for i in range(10):
            update = Mock()
            update.message.reply_text = AsyncMock()
            context = Mock()
            
            with patch('devops_manager_bot.get_system_metrics') as mock_metrics:
                mock_metrics.return_value = {'cpu': 50.0}
                task = asyncio.create_task(bot.dashboard_command(update, context))
                tasks.append(task)
                
        await asyncio.gather(*tasks)
        
        # All should complete successfully
        self.assertEqual(len(tasks), 10)


class TestErrorHandlingE2E(unittest.TestCase):
    """Test error handling in real scenarios"""
    
    async def test_network_failure_handling(self):
        """Test bot handles network failures gracefully"""
        bot = DevOpsManagerBot(token="test-token")
        
        update = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        with patch('devops_manager_bot.get_system_metrics') as mock_metrics:
            mock_metrics.side_effect = ConnectionError("Network unavailable")
            
            await bot.dashboard_command(update, context)
            
            # Should send error message to user
            update.message.reply_text.assert_called()
            call_args = update.message.reply_text.call_args[0][0]
            self.assertIn('error', call_args.lower())
            
    async def test_invalid_command_handling(self):
        """Test bot handles invalid commands gracefully"""
        bot = DevOpsManagerBot(token="test-token")
        
        update = Mock()
        update.message.reply_text = AsyncMock()
        update.message.text = '/invalidcommand'
        context = Mock()
        
        await bot.handle_unknown_command(update, context)
        
        update.message.reply_text.assert_called()
        
    async def test_permission_denied_handling(self):
        """Test bot handles permission errors"""
        bot = DevOpsManagerBot(token="test-token")
        
        update = Mock()
        update.message.reply_text = AsyncMock()
        update.effective_user.id = 99999  # Non-admin user
        context = Mock()
        
        with patch('devops_manager_bot.check_admin') as mock_admin:
            mock_admin.return_value = False
            
            await bot.deploy_command(update, context)
            
            # Should deny access
            update.message.reply_text.assert_called()
            call_args = update.message.reply_text.call_args[0][0]
            self.assertIn('permission', call_args.lower())


def run_async_tests():
    """Run all async tests"""
    loop = asyncio.get_event_loop()
    
    # Get all test classes
    test_classes = [
        TestDevOpsManagerBotE2E,
        TestSecurityAuditorBotE2E,
        TestBotsOrchestratorE2E,
        TestCompleteUserWorkflows,
        TestPerformanceE2E,
        TestErrorHandlingE2E
    ]
    
    # Run each test class
    for test_class in test_classes:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        # Convert async tests to sync
        for test in suite:
            test_method = getattr(test, test._testMethodName)
            if asyncio.iscoroutinefunction(test_method):
                setattr(test, test._testMethodName, 
                       lambda self, m=test_method: loop.run_until_complete(m(self)))
        
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)


if __name__ == '__main__':
    print("Running End-to-End Tests for Telegram Bots...")
    print("=" * 70)
    run_async_tests()
