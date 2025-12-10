#!/usr/bin/env python3
"""
Infrastructure as Code Platform v13.0
Terraform + Pulumi for multi-cloud IaC with GitOps
Complete infrastructure automation
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
IAC_BASE = Path('/var/lib/iac')
TERRAFORM_DIR = IAC_BASE / 'terraform'
PULUMI_DIR = IAC_BASE / 'pulumi'
STATE_DIR = IAC_BASE / 'state'

for directory in [TERRAFORM_DIR, PULUMI_DIR, STATE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

################################################################################
# Terraform Manager
################################################################################

class TerraformManager:
    """Terraform infrastructure management"""
    
    def __init__(self, workspace_dir: Path = TERRAFORM_DIR):
        self.workspace_dir = workspace_dir
    
    def init(self, module_path: Path) -> bool:
        """Initialize Terraform"""
        try:
            result = subprocess.run(
                ['terraform', 'init'],
                cwd=module_path,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Terraform initialized")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform init failed: {e.stderr}")
            return False
    
    def plan(self, module_path: Path, var_file: Optional[Path] = None) -> str:
        """Generate execution plan"""
        cmd = ['terraform', 'plan', '-out=tfplan']
        
        if var_file:
            cmd.extend(['-var-file', str(var_file)])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=module_path,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Terraform plan created")
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform plan failed: {e.stderr}")
            return ""
    
    def apply(self, module_path: Path, auto_approve: bool = False) -> bool:
        """Apply infrastructure changes"""
        cmd = ['terraform', 'apply']
        
        if auto_approve:
            cmd.append('-auto-approve')
        else:
            cmd.append('tfplan')
        
        try:
            result = subprocess.run(
                cmd,
                cwd=module_path,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Terraform applied successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform apply failed: {e.stderr}")
            return False
    
    def destroy(self, module_path: Path, auto_approve: bool = False) -> bool:
        """Destroy infrastructure"""
        cmd = ['terraform', 'destroy']
        
        if auto_approve:
            cmd.append('-auto-approve')
        
        try:
            result = subprocess.run(
                cmd,
                cwd=module_path,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Terraform destroyed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform destroy failed: {e.stderr}")
            return False
    
    def show_state(self, module_path: Path) -> Dict:
        """Show current state"""
        try:
            result = subprocess.run(
                ['terraform', 'show', '-json'],
                cwd=module_path,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Failed to show state: {e}")
            return {}
    
    def validate(self, module_path: Path) -> bool:
        """Validate configuration"""
        try:
            result = subprocess.run(
                ['terraform', 'validate'],
                cwd=module_path,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Terraform configuration valid")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform validation failed: {e.stderr}")
            return False

################################################################################
# Pulumi Manager
################################################################################

class PulumiManager:
    """Pulumi infrastructure management"""
    
    def __init__(self, workspace_dir: Path = PULUMI_DIR):
        self.workspace_dir = workspace_dir
    
    def new_stack(self, stack_name: str, project_name: str) -> bool:
        """Create new Pulumi stack"""
        try:
            subprocess.run(
                ['pulumi', 'stack', 'init', stack_name],
                cwd=self.workspace_dir,
                capture_output=True,
                check=True
            )
            logger.info(f"Pulumi stack created: {stack_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Pulumi stack creation failed: {e}")
            return False
    
    def up(self, stack_name: str, yes: bool = False) -> bool:
        """Deploy infrastructure"""
        cmd = ['pulumi', 'up', '--stack', stack_name]
        
        if yes:
            cmd.append('--yes')
        
        try:
            subprocess.run(
                cmd,
                cwd=self.workspace_dir,
                check=True
            )
            logger.info(f"Pulumi up completed: {stack_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Pulumi up failed: {e}")
            return False
    
    def preview(self, stack_name: str) -> str:
        """Preview changes"""
        try:
            result = subprocess.run(
                ['pulumi', 'preview', '--stack', stack_name],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Pulumi preview failed: {e}")
            return ""
    
    def destroy(self, stack_name: str, yes: bool = False) -> bool:
        """Destroy infrastructure"""
        cmd = ['pulumi', 'destroy', '--stack', stack_name]
        
        if yes:
            cmd.append('--yes')
        
        try:
            subprocess.run(
                cmd,
                cwd=self.workspace_dir,
                check=True
            )
            logger.info(f"Pulumi destroyed: {stack_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Pulumi destroy failed: {e}")
            return False

################################################################################
# IaC Template Generator
################################################################################

class IaCTemplateGenerator:
    """Generate IaC templates"""
    
    @staticmethod
    def generate_terraform_kubernetes(output_dir: Path):
        """Generate Terraform Kubernetes module"""
        
        main_tf = """
terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "app" {
  metadata {
    name = var.namespace_name
  }
}

resource "kubernetes_deployment" "app" {
  metadata {
    name      = var.app_name
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = {
        app = var.app_name
      }
    }

    template {
      metadata {
        labels = {
          app = var.app_name
        }
      }

      spec {
        container {
          name  = var.app_name
          image = var.image

          port {
            container_port = var.container_port
          }

          resources {
            limits = {
              cpu    = var.cpu_limit
              memory = var.memory_limit
            }
            requests = {
              cpu    = var.cpu_request
              memory = var.memory_request
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "app" {
  metadata {
    name      = var.app_name
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  spec {
    selector = {
      app = var.app_name
    }

    port {
      port        = 80
      target_port = var.container_port
    }

    type = "LoadBalancer"
  }
}
"""
        
        variables_tf = """
variable "namespace_name" {
  description = "Kubernetes namespace"
  type        = string
  default     = "default"
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "image" {
  description = "Container image"
  type        = string
}

variable "replicas" {
  description = "Number of replicas"
  type        = number
  default     = 3
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8080
}

variable "cpu_limit" {
  description = "CPU limit"
  type        = string
  default     = "500m"
}

variable "memory_limit" {
  description = "Memory limit"
  type        = string
  default     = "512Mi"
}

variable "cpu_request" {
  description = "CPU request"
  type        = string
  default     = "250m"
}

variable "memory_request" {
  description = "Memory request"
  type        = string
  default     = "256Mi"
}
"""
        
        outputs_tf = """
output "namespace" {
  value = kubernetes_namespace.app.metadata[0].name
}

output "deployment_name" {
  value = kubernetes_deployment.app.metadata[0].name
}

output "service_name" {
  value = kubernetes_service.app.metadata[0].name
}

output "service_endpoint" {
  value = kubernetes_service.app.status[0].load_balancer[0].ingress[0].ip
}
"""
        
        # Write files
        output_dir.mkdir(parents=True, exist_ok=True)
        
        (output_dir / 'main.tf').write_text(main_tf)
        (output_dir / 'variables.tf').write_text(variables_tf)
        (output_dir / 'outputs.tf').write_text(outputs_tf)
        
        logger.info(f"Terraform Kubernetes module generated: {output_dir}")

################################################################################
# GitOps Integration
################################################################################

class GitOpsManager:
    """GitOps workflow manager"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def detect_drift(self, live_state: Dict, desired_state: Dict) -> List[str]:
        """Detect infrastructure drift"""
        drifts = []
        
        # Compare states (simplified)
        for key, value in desired_state.items():
            if key not in live_state:
                drifts.append(f"Missing resource: {key}")
            elif live_state[key] != value:
                drifts.append(f"Drift detected in {key}: {live_state[key]} != {value}")
        
        return drifts
    
    def sync_from_git(self) -> bool:
        """Sync infrastructure from Git"""
        try:
            subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=self.repo_path,
                check=True
            )
            logger.info("Synced from Git")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Git sync failed: {e}")
            return False

################################################################################
# IaC Platform
################################################################################

class IaCPlatform:
    """Infrastructure as Code Platform"""
    
    def __init__(self):
        self.terraform = TerraformManager()
        self.pulumi = PulumiManager()
        self.template_gen = IaCTemplateGenerator()
        self.gitops = GitOpsManager(IAC_BASE / 'repo')
    
    def provision_kubernetes_app(self, app_name: str, image: str,
                                replicas: int = 3):
        """Provision Kubernetes app using Terraform"""
        
        # Generate module
        module_dir = TERRAFORM_DIR / app_name
        self.template_gen.generate_terraform_kubernetes(module_dir)
        
        # Create tfvars
        tfvars = {
            'app_name': app_name,
            'image': image,
            'replicas': replicas
        }
        
        tfvars_file = module_dir / 'terraform.tfvars.json'
        tfvars_file.write_text(json.dumps(tfvars, indent=2))
        
        # Deploy
        self.terraform.init(module_dir)
        self.terraform.validate(module_dir)
        self.terraform.plan(module_dir, tfvars_file)
        self.terraform.apply(module_dir)
        
        logger.info(f"Kubernetes app provisioned: {app_name}")

################################################################################
# CLI
################################################################################

def main():
    """Main entry point"""
    logger.info("Infrastructure as Code Platform v13.0")
    
    if '--generate-k8s' in sys.argv:
        gen = IaCTemplateGenerator()
        output = TERRAFORM_DIR / 'kubernetes-app'
        gen.generate_terraform_kubernetes(output)
        print(f"✅ Kubernetes Terraform module generated: {output}")
    
    elif '--test' in sys.argv:
        platform = IaCPlatform()
        platform.provision_kubernetes_app(
            app_name='demo-app',
            image='nginx:latest',
            replicas=2
        )
        print("✅ Test deployment completed")
    
    else:
        print("""
Infrastructure as Code Platform v13.0

Usage:
  --generate-k8s    Generate Kubernetes Terraform module
  --test           Test deployment

Examples:
  python3 iac_platform.py --generate-k8s
  python3 iac_platform.py --test
        """)

if __name__ == '__main__':
    main()
