#!/usr/bin/env python3
"""
Advanced Secret Management - Iteration 5
HashiCorp Vault integration with automated secret rotation
Comprehensive secrets lifecycle management
"""

import os
import sys
import json
import logging
import hvac
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import schedule
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRETS_BASE = Path('/var/lib/secrets')
POLICIES_DIR = SECRETS_BASE / 'policies'
ROTATION_DIR = SECRETS_BASE / 'rotation'

for directory in [POLICIES_DIR, ROTATION_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

################################################################################
# Vault Manager
################################################################################

class VaultManager:
    """HashiCorp Vault management"""
    
    def __init__(self, url: str = 'http://localhost:8200'):
        self.url = url
        self.token = os.getenv('VAULT_TOKEN')
        self.client = hvac.Client(url=url, token=self.token)
    
    def create_secret(self, path: str, data: Dict) -> bool:
        """Create secret in Vault"""
        
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data
            )
            logger.info(f"Secret created: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create secret: {e}")
            return False
    
    def read_secret(self, path: str) -> Optional[Dict]:
        """Read secret from Vault"""
        
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data']
        except Exception as e:
            logger.error(f"Failed to read secret: {e}")
            return None
    
    def delete_secret(self, path: str) -> bool:
        """Delete secret from Vault"""
        
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)
            logger.info(f"Secret deleted: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret: {e}")
            return False
    
    def create_policy(self, name: str, policy: Dict) -> bool:
        """Create Vault policy"""
        
        policy_hcl = f"""
# Policy for {name}
path "{policy['path']}" {{
  capabilities = {json.dumps(policy['capabilities'])}
}}
"""
        
        try:
            self.client.sys.create_or_update_policy(name=name, policy=policy_hcl)
            logger.info(f"Policy created: {name}")
            
            # Save policy
            (POLICIES_DIR / f'{name}.hcl').write_text(policy_hcl)
            return True
        except Exception as e:
            logger.error(f"Failed to create policy: {e}")
            return False
    
    def enable_database_secrets(self, db_type: str = 'postgresql') -> bool:
        """Enable database secrets engine"""
        
        try:
            self.client.sys.enable_secrets_engine(
                backend_type='database',
                path='database'
            )
            
            # Configure database connection
            self.client.secrets.database.configure(
                name='my-postgresql-database',
                plugin_name='postgresql-database-plugin',
                allowed_roles=['*'],
                connection_url='postgresql://{{username}}:{{password}}@localhost:5432/postgres',
                username=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'password')
            )
            
            logger.info(f"Database secrets engine enabled: {db_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to enable database secrets: {e}")
            return False
    
    def create_dynamic_db_role(self, role_name: str, db_name: str, ttl: str = '1h'):
        """Create dynamic database role"""
        
        creation_statements = [
            f"CREATE ROLE \"{{{{name}}}}\" WITH LOGIN PASSWORD '{{{{password}}}}' VALID UNTIL '{{{{expiration}}}}';",
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{{{name}}}}\";"
        ]
        
        try:
            self.client.secrets.database.create_role(
                name=role_name,
                db_name=db_name,
                creation_statements=creation_statements,
                default_ttl=ttl,
                max_ttl='24h'
            )
            logger.info(f"Dynamic database role created: {role_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create dynamic role: {e}")
            return False
    
    def get_dynamic_credentials(self, role_name: str) -> Optional[Dict]:
        """Get dynamic database credentials"""
        
        try:
            response = self.client.secrets.database.generate_credentials(name=role_name)
            creds = {
                'username': response['data']['username'],
                'password': response['data']['password'],
                'lease_id': response['lease_id'],
                'lease_duration': response['lease_duration']
            }
            logger.info(f"Dynamic credentials generated: {creds['username']}")
            return creds
        except Exception as e:
            logger.error(f"Failed to generate credentials: {e}")
            return None

################################################################################
# Secret Rotation Manager
################################################################################

class SecretRotationManager:
    """Automated secret rotation"""
    
    def __init__(self, vault_manager: VaultManager):
        self.vault = vault_manager
        self.rotation_config = {}
    
    def register_secret(self, secret_path: str, rotation_interval_days: int):
        """Register secret for rotation"""
        
        self.rotation_config[secret_path] = {
            'interval_days': rotation_interval_days,
            'last_rotated': datetime.now()
        }
        
        logger.info(f"Secret registered for rotation: {secret_path} (every {rotation_interval_days} days)")
    
    def rotate_secret(self, secret_path: str) -> bool:
        """Rotate a secret"""
        
        logger.info(f"Rotating secret: {secret_path}")
        
        # Read current secret
        current_secret = self.vault.read_secret(secret_path)
        
        if not current_secret:
            logger.error(f"Cannot read secret for rotation: {secret_path}")
            return False
        
        # Generate new secret value
        import secrets
        new_value = secrets.token_urlsafe(32)
        
        # Update secret
        new_secret = current_secret.copy()
        new_secret['password'] = new_value
        new_secret['rotated_at'] = datetime.now().isoformat()
        
        if self.vault.create_secret(secret_path, new_secret):
            self.rotation_config[secret_path]['last_rotated'] = datetime.now()
            
            # Save rotation event
            rotation_log = {
                'secret_path': secret_path,
                'rotated_at': datetime.now().isoformat(),
                'success': True
            }
            
            log_file = ROTATION_DIR / f'{secret_path.replace("/", "_")}-{datetime.now().strftime("%Y%m%d")}.json'
            log_file.write_text(json.dumps(rotation_log, indent=2))
            
            logger.info(f"Secret rotated successfully: {secret_path}")
            return True
        
        return False
    
    def check_rotation_schedule(self):
        """Check and rotate secrets based on schedule"""
        
        for secret_path, config in self.rotation_config.items():
            days_since_rotation = (datetime.now() - config['last_rotated']).days
            
            if days_since_rotation >= config['interval_days']:
                logger.info(f"Secret due for rotation: {secret_path}")
                self.rotate_secret(secret_path)
    
    def start_rotation_scheduler(self):
        """Start automated rotation scheduler"""
        
        schedule.every().day.at("02:00").do(self.check_rotation_schedule)
        
        logger.info("Secret rotation scheduler started")
        
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour

################################################################################
# Kubernetes Integration
################################################################################

class KubernetesSecretsManager:
    """Sync Vault secrets to Kubernetes"""
    
    def __init__(self, vault_manager: VaultManager):
        self.vault = vault_manager
    
    def sync_secret_to_k8s(self, vault_path: str, k8s_secret_name: str, namespace: str = 'default') -> bool:
        """Sync Vault secret to Kubernetes Secret"""
        
        import subprocess
        import base64
        
        # Read from Vault
        secret_data = self.vault.read_secret(vault_path)
        
        if not secret_data:
            logger.error(f"Cannot read secret from Vault: {vault_path}")
            return False
        
        # Encode values for Kubernetes
        encoded_data = {
            key: base64.b64encode(str(value).encode()).decode()
            for key, value in secret_data.items()
        }
        
        # Create Kubernetes Secret manifest
        k8s_secret = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': k8s_secret_name,
                'namespace': namespace
            },
            'type': 'Opaque',
            'data': encoded_data
        }
        
        import yaml
        manifest = yaml.dump(k8s_secret)
        
        manifest_file = SECRETS_BASE / f'{k8s_secret_name}.yaml'
        manifest_file.write_text(manifest)
        
        # Apply to Kubernetes
        result = subprocess.run(
            ['kubectl', 'apply', '-f', str(manifest_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Secret synced to Kubernetes: {k8s_secret_name}")
            return True
        else:
            logger.error(f"Failed to sync secret: {result.stderr}")
            return False

################################################################################
# Secret Management Platform
################################################################################

class SecretManagementPlatform:
    """Complete secret management orchestrator"""
    
    def __init__(self):
        self.vault = VaultManager()
        self.rotation_mgr = SecretRotationManager(self.vault)
        self.k8s_mgr = KubernetesSecretsManager(self.vault)
    
    def setup_complete_secrets_management(self):
        """Setup complete secrets management"""
        
        # Create policies
        self.vault.create_policy('app-read', {
            'path': 'secret/data/app/*',
            'capabilities': ['read', 'list']
        })
        
        self.vault.create_policy('app-write', {
            'path': 'secret/data/app/*',
            'capabilities': ['create', 'read', 'update', 'delete', 'list']
        })
        
        # Enable database secrets
        self.vault.enable_database_secrets('postgresql')
        
        # Create dynamic database role
        self.vault.create_dynamic_db_role(
            role_name='app-db-role',
            db_name='my-postgresql-database',
            ttl='1h'
        )
        
        # Register secrets for rotation
        self.rotation_mgr.register_secret('app/database/credentials', rotation_interval_days=30)
        self.rotation_mgr.register_secret('app/api/keys', rotation_interval_days=90)
        
        logger.info("Complete secrets management configured")
    
    def provision_app_secrets(self, app_name: str) -> Dict:
        """Provision all secrets for an application"""
        
        # Create app secrets in Vault
        secrets = {
            'database_url': 'postgresql://localhost:5432/app',
            'api_key': 'sk-' + os.urandom(32).hex(),
            'jwt_secret': os.urandom(32).hex()
        }
        
        self.vault.create_secret(f'app/{app_name}/config', secrets)
        
        # Sync to Kubernetes
        self.k8s_mgr.sync_secret_to_k8s(
            vault_path=f'app/{app_name}/config',
            k8s_secret_name=f'{app_name}-secrets'
        )
        
        # Get dynamic database credentials
        db_creds = self.vault.get_dynamic_credentials('app-db-role')
        
        logger.info(f"Secrets provisioned for app: {app_name}")
        
        return {
            'static_secrets': secrets,
            'dynamic_credentials': db_creds
        }

################################################################################
# CLI
################################################################################

def main():
    logger.info("🔐 Advanced Secret Management - Iteration 5")
    
    if '--setup' in sys.argv:
        platform = SecretManagementPlatform()
        platform.setup_complete_secrets_management()
        print("✅ Secret management configured")
    
    elif '--provision' in sys.argv:
        platform = SecretManagementPlatform()
        secrets = platform.provision_app_secrets('demo-app')
        print(f"✅ Secrets provisioned: {json.dumps(secrets, indent=2)}")
    
    else:
        print("""
Advanced Secret Management v13.0 - Iteration 5

Usage:
  --setup       Setup complete secrets management
  --provision   Provision app secrets

Features:
  ✓ HashiCorp Vault integration
  ✓ Automated secret rotation
  ✓ Dynamic database credentials
  ✓ Kubernetes secrets sync
  ✓ Policy-based access control
        """)

if __name__ == '__main__':
    main()
